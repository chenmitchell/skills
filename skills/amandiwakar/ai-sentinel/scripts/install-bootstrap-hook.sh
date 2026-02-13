#!/usr/bin/env bash
# =============================================================================
# Install AI Sentinel bootstrap hook as a standalone OpenClaw gateway hook.
#
# This is an alternative to the plugin's built-in before_agent_start hook.
# Use this if you want the bootstrap hook without the full plugin, or if you
# need the hook to run at the gateway level rather than as a plugin hook.
#
# Usage: ./install-bootstrap-hook.sh
# =============================================================================

set -euo pipefail

HOOK_DIR="$HOME/.openclaw/hooks/ai-sentinel-bootstrap"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(dirname "$SCRIPT_DIR")/bootstrap"

echo "[ai-sentinel] Installing bootstrap hook..."

# Create hook directory
mkdir -p "$HOOK_DIR"

# Copy handler
cp "$SOURCE_DIR/handler.ts" "$HOOK_DIR/handler.ts"

# Create hook manifest
cat > "$HOOK_DIR/hook.json" <<'EOF'
{
  "name": "ai-sentinel-bootstrap",
  "version": "0.1.0",
  "description": "Injects AI Sentinel security awareness into agent bootstrap",
  "events": ["agent:bootstrap"],
  "entry": "./handler.ts"
}
EOF

echo "[ai-sentinel] Bootstrap hook installed to $HOOK_DIR"
echo "[ai-sentinel] Enable with: openclaw hooks enable ai-sentinel-bootstrap"
