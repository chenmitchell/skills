#!/usr/bin/env python3
import sys
import json
import api_client

def get_coin_details(coin_id):
    """
    Get detailed information about a specific coin.
    
    Args:
        coin_id (str): The coin ID (e.g., 'bitcoin').
        
    Returns:
        dict: Coin details or error message.
    """
    return api_client.get(f'/crypto/coins/{coin_id}')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": "python3 get_coin_details.py <coin_id>",
            "example": "python3 get_coin_details.py bitcoin"
        }, indent=2))
        sys.exit(1)

    coin_id = sys.argv[1]
    result = get_coin_details(coin_id)
    print(json.dumps(result, indent=2))
