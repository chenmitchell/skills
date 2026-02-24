#!/bin/bash
# Wrapper for Model Manager Skill
# Usage: ./run.sh <list|enable> [target]

# Ensure we have requests library
if ! python3 -c "import requests" &> /dev/null; then
    pip install requests > /dev/null
fi

python3 skills/model-manager/manage_models.py "$@"
