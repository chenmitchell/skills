#!/usr/bin/env python3
import json
import api_client

def get_global_market_data():
    """
    Get global cryptocurrency market data.
    Includes total market cap, volume, and market cap percentage.
    
    Returns:
        dict: valid JSON response or error dict.
    """
    return api_client.get('/crypto/global')

if __name__ == "__main__":
    result = get_global_market_data()
    print(json.dumps(result, indent=2))
