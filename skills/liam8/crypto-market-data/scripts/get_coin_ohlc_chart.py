#!/usr/bin/env python3
"""
Get coin OHLC (Open, High, Low, Close) chart data.
"""
import sys
import json
import api_client

VALID_DAYS = ['1', '7', '14', '30', '90', '180', '365']

def get_coin_ohlc_chart(coin_id, vs_currency='usd', days='7', precision=None):
    """
    Fetches OHLC chart data for a coin.
    
    Args:
        coin_id (str): Coin ID (e.g., 'bitcoin', 'ethereum').
        vs_currency (str): Target currency of price data (e.g., 'usd', 'eur').
        days (str): Data up to number of days ago. Only '1', '7', '14', '30', '90', '180', '365' are allowed.
        precision (str): Optional decimal place for currency price value.
        
    Returns:
        list: Arrays of [timestamp, open, high, low, close] or error dict.
    """
    if days not in VALID_DAYS:
        return {"error": f"days must be one of: {', '.join(VALID_DAYS)}"}
    
    params = {
        'vs_currency': vs_currency,
        'days': days
    }
    
    if precision:
        params['precision'] = precision
    
    return api_client.get(f'/crypto/coins/{coin_id}/ohlc', params)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": "python3 get_coin_ohlc_chart.py <coin_id> [--currency=usd] [--days=7] [--precision=2]",
            "example": "python3 get_coin_ohlc_chart.py bitcoin --currency=usd --days=30",
            "valid_days": VALID_DAYS
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

    result = get_coin_ohlc_chart(coin_id, vs_currency, days, precision)
    print(json.dumps(result, indent=2))
