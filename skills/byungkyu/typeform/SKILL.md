---
name: typeform
description: |
  Typeform API integration with managed OAuth. Create forms, manage responses, and access insights. Use this skill when users want to interact with Typeform surveys and responses.
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
---

# Typeform

Access the Typeform API with managed OAuth authentication. Create and manage forms, retrieve responses, and access insights.

## Quick Start

```bash
# List forms
curl -s -X GET 'https://gateway.maton.ai/typeform/forms?page_size=10' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

## Base URL

```
https://gateway.maton.ai/typeform/{endpoint}
```

The gateway proxies requests to `api.typeform.com` and automatically injects your OAuth token.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Typeform OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
curl -s -X GET 'https://ctrl.maton.ai/connections?app=typeform&status=ACTIVE' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

### Create Connection

```bash
curl -s -X POST 'https://ctrl.maton.ai/connections' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -d '{"app": "typeform"}'
```

### Get Connection

```bash
curl -s -X GET 'https://ctrl.maton.ai/connections/{connection_id}' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

**Response:**
```json
{
  "connection": {
    "connection_id": "21fd90f9-5935-43cd-b6c8-bde9d915ca80",
    "status": "ACTIVE",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "typeform"
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
curl -s -X DELETE 'https://ctrl.maton.ai/connections/{connection_id}' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```

## API Reference

### User

```bash
GET /typeform/me
```

### Forms

#### List Forms

```bash
GET /typeform/forms?page_size=10
```

#### Get Form

```bash
GET /typeform/forms/{formId}
```

#### Create Form

```bash
POST /typeform/forms
Content-Type: application/json

{
  "title": "Customer Survey",
  "fields": [
    {"type": "short_text", "title": "What is your name?"},
    {"type": "email", "title": "What is your email?"}
  ]
}
```

#### Update Form

```bash
PUT /typeform/forms/{formId}
Content-Type: application/json

{
  "title": "Updated Survey Title",
  "fields": [...]
}
```

#### Delete Form

```bash
DELETE /typeform/forms/{formId}
```

### Responses

#### List Responses

```bash
GET /typeform/forms/{formId}/responses?page_size=25
```

With filters:

```bash
GET /typeform/forms/{formId}/responses?since=2024-01-01T00:00:00Z&until=2024-12-31T23:59:59Z&completed=true
```

### Insights

```bash
GET /typeform/insights/{formId}/summary
```

### Workspaces

```bash
GET /typeform/workspaces
GET /typeform/workspaces/{workspaceId}
```

## Field Types

- `short_text` - Single line text
- `long_text` - Multi-line text
- `email` - Email address
- `number` - Numeric input
- `rating` - Star rating
- `opinion_scale` - 0-10 scale
- `multiple_choice` - Single or multiple selection
- `yes_no` - Boolean
- `date` - Date picker
- `dropdown` - Dropdown selection

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/typeform/forms?page_size=10',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/typeform/forms',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'page_size': 10}
)
```

## Notes

- Form IDs are alphanumeric strings
- Response pagination uses `before` token
- Timestamps are in ISO 8601 format
- DELETE operations return HTTP 204

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Typeform connection |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited (10 req/sec per account) |
| 4xx/5xx | Passthrough error from Typeform API |

## Resources

- [Typeform API Overview](https://www.typeform.com/developers/get-started)
- [Forms](https://www.typeform.com/developers/create/reference/retrieve-forms)
- [Responses](https://www.typeform.com/developers/responses/reference/retrieve-responses)
- [Workspaces](https://www.typeform.com/developers/create/reference/retrieve-workspaces)
