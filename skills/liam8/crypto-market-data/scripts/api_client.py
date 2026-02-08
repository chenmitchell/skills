#!/usr/bin/env python3
import os
import json
import time
import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError
from datetime import datetime, timezone
import ssl

# Constants
BASE_URL = os.environ.get("API_BASE_URL", "https://api.igent.net/api")
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".token")
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'

ssl_context = ssl.create_default_context()

def _load_token():
    """Load token from local file if valid."""
    if not os.path.exists(TOKEN_FILE):
        return None
    
    try:
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            
        expires_at_str = data.get('expires_at')
        if not expires_at_str:
            return None
            
        # Parse expiry time (handling ISO format with Z or offset)
        # Python 3.7+ fromisoformat handles most, but let's be robust
        if expires_at_str.endswith('Z'):
             expires_at_str = expires_at_str[:-1] + '+00:00'
             
        expires_at = datetime.fromisoformat(expires_at_str)
        
        # Check if expired (with small buffer of 30 seconds)
        if datetime.now(timezone.utc) >= expires_at:
            return None
            
        return data.get('token')
    except Exception as e:
        # If file is corrupt or unreadable, ignore it
        print(f"Warning: Failed to load token file: {e}")
        return None

def _fetch_new_token():
    """Fetch a new token from the server and save it."""
    url = f"{BASE_URL}/token"
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    
    try:
        with urllib.request.urlopen(req, context=ssl_context) as response: # Use the global SSL context
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                
                # Save to file
                with open(TOKEN_FILE, 'w') as f:
                    json.dump(data, f)
                    
                return data.get('token')
            else:
                raise Exception(f"Failed to fetch token. Status: {response.status}")
    except Exception as e:
        raise Exception(f"Error fetching token: {e}")

def get_token():
    """Get a valid token, refreshing if necessary."""
    token = _load_token()
    if token:
        return token
        
    return _fetch_new_token()

def get(endpoint, params=None):
    """
    Make a GET request to the API with token authentication.
    
    Args:
        endpoint (str): API endpoint (e.g., '/crypto/prices').
        params (dict): Query parameters.
        
    Returns:
        dict: valid JSON response or error dict.
    """
    try:
        token = get_token()
    except Exception as e:
        return {"error": str(e)}

    # Construct URL
    url = f"{BASE_URL}{endpoint}"
    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"
        
    headers = {
        'accept': 'application/json',
        'User-Agent': USER_AGENT,
        'X-API-Token': token
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ssl_context) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
            else:
                return {"error": f"API request failed. Status: {response.status}"}
    except HTTPError as e:
        # Attempt to read error body
        try:
             error_body = e.read().decode('utf-8')
             error_json = json.loads(error_body)
             return {"error": f"HTTP Error {e.code}: {error_json.get('error', e.reason)}"}
        except:
             return {"error": f"HTTP Error {e.code}: {e.reason}"}
    except URLError as e:
        return {"error": f"URL Error: {e.reason}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
