#!/usr/bin/env python3
"""
Get public companies Bitcoin or Ethereum holdings.
"""
import sys
import json
import api_client

def get_public_companies_holdings(coin_id):
    """
    Fetches public companies holdings of Bitcoin or Ethereum.
    
    Args:
        coin_id (str): Coin ID - must be either 'bitcoin' or 'ethereum'.
        
    Returns:
        dict: valid JSON response or error dict.
    """
    if coin_id not in ['bitcoin', 'ethereum']:
        return {"error": "coin_id must be either 'bitcoin' or 'ethereum'"}
    
    return api_client.get(f'/crypto/companies/holdings', {'coin_id': coin_id})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": "python3 get_public_companies_holdings.py <coin_id>",
            "example": "python3 get_public_companies_holdings.py bitcoin",
            "note": "coin_id must be either 'bitcoin' or 'ethereum'"
        }, indent=2))
        sys.exit(1)

    coin_id = sys.argv[1].lower()
    result = get_public_companies_holdings(coin_id)
    print(json.dumps(result, indent=2))
