#!/bin/bash

# MCP WebSearch Tool Script
# Usage: ./mcp-websearch.sh <query> [count]
# Example: ./mcp-websearch.sh "上海天气" 5

# Check if DASHSCOPE_API_KEY is set
if [ -z "$DASHSCOPE_API_KEY" ]; then
  echo "Error: DASHSCOPE_API_KEY environment variable is not set"
  exit 1
fi

# Parse command line arguments
QUERY="${1:-上海天气}"  # Default query if not provided
COUNT="${2:-5}"         # Default count if not provided

# Validate count is a number
if ! [[ "$COUNT" =~ ^[0-9]+$ ]]; then
  echo "Error: count must be a number"
  echo "Usage: $0 <query> [count]"
  exit 1
fi

echo "Search query: $QUERY"
echo "Result count: $COUNT"
echo ""

BASE_URL="https://dashscope.aliyuncs.com"
SSE_URL="${BASE_URL}/api/v1/mcps/WebSearch/sse"

echo "=== MCP WebSearch Searching ==="
echo ""

# Use a temp file in current directory (sandbox-compatible)
SSE_RESPONSE_FILE="mcp_sse_response.txt"
rm -f "$SSE_RESPONSE_FILE"
touch "$SSE_RESPONSE_FILE"

# Function to cleanup
cleanup() {
  if [ -n "$SSE_CURL_PID" ]; then
    kill $SSE_CURL_PID 2>/dev/null
    wait $SSE_CURL_PID 2>/dev/null
  fi
  rm -f "$SSE_RESPONSE_FILE"
}
trap cleanup EXIT

echo "Step 1: Establishing SSE connection..."
# Start SSE connection in background
# The first event will be the endpoint event
curl -N -s --connect-timeout 60 \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Accept: text/event-stream" \
  "$SSE_URL" >> "$SSE_RESPONSE_FILE" &
SSE_CURL_PID=$!

# Wait for the endpoint event
sleep 2

# Read the endpoint from SSE response
ENDPOINT_LINE=$(grep "^data:" "$SSE_RESPONSE_FILE" | head -n 1)
MESSAGE_PATH=$(echo "$ENDPOINT_LINE" | sed 's/data:[[:space:]]*//' | tr -d '\r\n')

if [ -z "$MESSAGE_PATH" ]; then
  echo "Error: Failed to get message endpoint"
  exit 1
fi

# Construct full message URL
FULL_MESSAGE_URL="${BASE_URL}${MESSAGE_PATH}"
echo "  Message endpoint: $FULL_MESSAGE_URL"
echo ""

# Track current line count for reading new responses
get_line_count() {
  cat "$SSE_RESPONSE_FILE" 2>/dev/null | wc -l || echo 0
}

# Function to send JSON-RPC request and get response
send_request() {
  local req_json="$1"
  local req_id=$(echo "$req_json" | jq -r '.id')
  
  # Get current line count before sending request
  local start_line=$(get_line_count)
  
  # Send POST request
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$FULL_MESSAGE_URL" \
    -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$req_json")
  
  if [ "$HTTP_STATUS" != "202" ] && [ "$HTTP_STATUS" != "200" ]; then
    echo "Error: HTTP $HTTP_STATUS"
    return 1
  fi
  
  # Wait for response
  sleep 3
  
  # Debug: show new lines in file
  # echo "Debug: New lines in SSE file:" >&2
  # tail -n +$((start_line + 1)) "$SSE_RESPONSE_FILE" >&2
  
  # Read new lines from SSE response file and find matching response
  local found_response=""
  
  while IFS= read -r line; do
    if [[ "$line" == data:* ]]; then
      json_data=$(echo "$line" | sed 's/data:[[:space:]]*//' | tr -d '\r\n')
      if [ -n "$json_data" ] && echo "$json_data" | jq -e . >/dev/null 2>&1; then
        # Check if this response matches our request ID
        resp_id=$(echo "$json_data" | jq -r '.id // empty')
        if [ "$resp_id" = "$req_id" ]; then
          found_response="$json_data"
          break
        fi
      fi
    fi
  done < <(tail -n +$((start_line + 1)) "$SSE_RESPONSE_FILE")
  
  if [ -n "$found_response" ]; then
    echo "$found_response" | jq .
  else
    echo "No response received for request id $req_id (searched from line $((start_line + 1)))"
  fi
}

echo "Step 2: Sending initialize request..."
INIT_REQ='{
  "jsonrpc": "2.0",
  "id": 0,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "curl-client", "version": "1.0.0"}
  }
}'

send_request "$INIT_REQ"
echo ""

echo "Step 3: Sending initialized notification..."
# Send notifications/initialized (no response expected)
curl -s -o /dev/null -X POST "$FULL_MESSAGE_URL" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
echo "  Notification sent"
sleep 1
echo ""

echo "Step 4: Listing available tools..."
LIST_TOOLS_REQ='{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}'

send_request "$LIST_TOOLS_REQ"
echo ""

echo "Step 5: Calling web search tool..."
# Build tool request with user-provided query and count
TOOL_REQ=$(jq -n \
  --arg query "$QUERY" \
  --argjson count "$COUNT" \
  '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "bailian_web_search",
      "arguments": {
        "query": $query,
        "count": $count
      }
    }
  }')

send_request "$TOOL_REQ"
echo ""

echo "=== Search Complete ==="
