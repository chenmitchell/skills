#!/usr/bin/env python3
import sys
import json
import api_client

def get_crypto_price(coin_ids, currency='usd'):
    """
    Fetches the current price of cryptocurrencies.
    
    Args:
        coin_ids (list): List of coin IDs (e.g., ['bitcoin', 'ethereum']).
        currency (str): Target currency (e.g., 'usd').
        
    Returns:
        dict: valid JSON response or error dict.
    """
    # Join coin IDs with commas
    ids_str = ",".join(coin_ids)
    
    params = {
        'ids': ids_str,
        'vs_currencies': currency,
        'include_market_cap': 'true',
        'include_24hr_vol': 'true',
        'include_24hr_change': 'true',
        'include_last_updated_at': 'true'
    }
    
    return api_client.get('/crypto/prices', params)

if __name__ == "__main__":
    # Default to bitcoin if no arguments provided
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": "python3 get_crypto_price.py [coin_id_1] [coin_id_2] ... [--currency=usd]",
            "example": "python3 get_crypto_price.py bitcoin ethereum --currency=usd"
        }, indent=2))
        sys.exit(1)

    args = sys.argv[1:]
    currency = 'usd'
    coin_ids = []

    for arg in args:
        if arg.startswith('--currency='):
            currency = arg.split('=')[1]
        else:
            coin_ids.append(arg)
            
    if not coin_ids:
        coin_ids = ['bitcoin']

    result = get_crypto_price(coin_ids, currency)
    print(json.dumps(result, indent=2))
