#!/bin/bash
# Miniflux CLI Wrapper
# Manage Miniflux - Modern minimalist feed reader

# Set default values if not already set
: "${MINIFLUX_URL:="https://reader.etereo.cloud"}"

# Check required environment variables
if [ -z "$MINIFLUX_TOKEN" ]; then
    echo "Error: MINIFLUX_TOKEN environment variable must be set."
    echo "Get your token from Settings > API Keys in Miniflux UI"
    exit 1
fi

# Export variables for Python script
export MINIFLUX_URL
export MINIFLUX_TOKEN

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if miniflux package is installed
if ! python3 -c "import miniflux" 2>/dev/null; then
    echo "Error: miniflux Python package not installed."
    echo "Installing with uv..."
    uv pip install miniflux || {
        echo "Failed to install miniflux package."
        echo "Install manually: uv pip install miniflux"
        exit 1
    }
fi

# Run Python script
python3 "$SCRIPT_DIR/miniflux-cli.py" "$@"
