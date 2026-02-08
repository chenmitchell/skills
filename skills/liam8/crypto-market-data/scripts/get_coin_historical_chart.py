#!/usr/bin/env python3
"""
Get historical chart data for a coin.
"""
import sys
import json
import api_client

def get_coin_historical_chart(coin_id, vs_currency='usd', days='7', precision=None):
    """
    Fetches historical chart data for a coin.
    
    Args:
        coin_id (str): Coin ID (e.g., 'bitcoin', 'ethereum').
        vs_currency (str): Target currency of market data (e.g., 'usd', 'eur').
        days (str): Data up to number of days ago (e.g., '1', '7', '30', '365').
        precision (str): Optional decimal place for currency price value.
        
    Returns:
        dict: Contains 'prices', 'market_caps', and 'total_volumes' arrays or error dict.
    """
    params = {
        'vs_currency': vs_currency,
        'days': days,
        'interval': 'daily'
    }
    
    if precision:
        params['precision'] = precision
    
    return api_client.get(f'/crypto/coins/{coin_id}/market_chart', params)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": "python3 get_coin_historical_chart.py <coin_id> [--currency=usd] [--days=7] [--precision=2]",
            "example": "python3 get_coin_historical_chart.py bitcoin --currency=usd --days=30"
        }, indent=2))
        sys.exit(1)

    coin_id = sys.argv[1]
    vs_currency = 'usd'
    days = '7'
    precision = None
    
    for arg in sys.argv[2:]:
        if arg.startswith('--currency='):
            vs_currency = arg.split('=')[1]
        elif arg.startswith('--days='):
            days = arg.split('=')[1]
        elif arg.startswith('--precision='):
            precision = arg.split('=')[1]

    result = get_coin_historical_chart(coin_id, vs_currency, days, precision)
    print(json.dumps(result, indent=2))
