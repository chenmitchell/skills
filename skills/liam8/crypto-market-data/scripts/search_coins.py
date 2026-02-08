#!/usr/bin/env python3
import sys
import json
import api_client

def search_coins(query):
    """
    Search for coins by name or symbol.
    
    Args:
        query (str): Search query (coin name or symbol).
        
    Returns:
        dict: valid JSON response or error dict.
    """
    return api_client.get('/crypto/search', params={'query': query})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": "python3 search_coins.py <query>",
            "example": "python3 search_coins.py bitcoin"
        }, indent=2))
        sys.exit(1)

    query = ' '.join(sys.argv[1:])
    result = search_coins(query)
    print(json.dumps(result, indent=2))
