#!/usr/bin/env python3
"""
Get supported currencies.
"""
import sys
import json
import api_client

def get_supported_currencies():
    """
    Fetches the list of supported vs_currencies.
    These are the currencies that can be used as target currencies when fetching prices.
    
    Returns:
        list: List of supported currency codes or error dict.
    """
    return api_client.get('/crypto/supported-currencies')

if __name__ == "__main__":
    result = get_supported_currencies()
    print(json.dumps(result, indent=2))
