#!/usr/bin/env python3
import sys
import json
import api_client

def get_top_coins(vs_currency='usd', per_page=10, page=1, order='market_cap_desc'):
    """
    Fetches the top cryptocurrencies by market capitalization.
    
    Args:
        vs_currency (str): Target currency (e.g., 'usd').
        per_page (int): Number of results per page (1-250).
        page (int): Page number.
        order (str): Sort order (market_cap_desc, volume_desc, etc.).
        
    Returns:
        dict: valid JSON response or error dict.
    """
    params = {
        'vs_currency': vs_currency,
        'per_page': per_page,
        'page': page,
        'order': order
    }
    return api_client.get('/crypto/coins/markets', params=params)

if __name__ == "__main__":
    # Parse command line arguments
    vs_currency = 'usd'
    per_page = 10
    page = 1
    order = 'market_cap_desc'
    
    for arg in sys.argv[1:]:
        if arg.startswith('--currency='):
            vs_currency = arg.split('=')[1]
        elif arg.startswith('--per_page='):
            per_page = int(arg.split('=')[1])
        elif arg.startswith('--page='):
            page = int(arg.split('=')[1])
        elif arg.startswith('--order='):
            order = arg.split('=')[1]

    result = get_top_coins(vs_currency, per_page, page, order)
    print(json.dumps(result, indent=2))
