#!/usr/bin/env python3
import json
import api_client

def get_trending_coins():
    """
    Fetches the trending coins in the last 24 hours.
    
    Returns:
        dict: valid JSON response or error dict.
    """
    return api_client.get('/crypto/search/trending')

if __name__ == "__main__":
    result = get_trending_coins()
    print(json.dumps(result, indent=2))
