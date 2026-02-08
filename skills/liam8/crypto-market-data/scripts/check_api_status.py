#!/usr/bin/env python3
"""
Check API server status.
"""
import sys
import json
import api_client

def check_api_status():
    """
    Checks the API server status.
    
    Returns:
        dict: Status message or error dict.
    """
    return api_client.get('/status')

if __name__ == "__main__":
    result = check_api_status()
    print(json.dumps(result, indent=2))
