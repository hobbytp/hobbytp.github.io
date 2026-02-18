#!/usr/bin/env python3
"""
GitHub Token Validation Script
Tests if the GITHUB_TOKEN environment variable is valid.
"""

import os
import requests
from dotenv import load_dotenv

def test_github_token():
    """Test GitHub token validity."""
    load_dotenv()
    
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("[ERROR] GITHUB_TOKEN is not set in environment variables.")
        print("       Please add it to your .env file.")
        return False
    
    print(f"[INFO] Found GITHUB_TOKEN (length: {len(token)})")
    
    # Test with a simple API call
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test 1: Check rate limit (always works, shows auth status)
    print("\n[TEST] Checking API rate limit...")
    response = requests.get('https://api.github.com/rate_limit', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        core_limit = data.get('resources', {}).get('core', {})
        remaining = core_limit.get('remaining', 0)
        limit = core_limit.get('limit', 0)
        
        if limit > 60:  # Authenticated users get 5000, unauthenticated get 60
            print(f"[OK] Token is VALID (Authenticated)")
            print(f"     Rate Limit: {remaining}/{limit} requests remaining")
            return True
        else:
            print(f"[WARNING] Token may be invalid (Unauthenticated rate limit)")
            print(f"          Rate Limit: {remaining}/{limit}")
            return False
    elif response.status_code == 401:
        print(f"[ERROR] Token is INVALID (401 Unauthorized)")
        print(f"        Response: {response.json().get('message', 'No message')}")
        return False
    else:
        print(f"[ERROR] Unexpected response: {response.status_code}")
        print(f"        Response: {response.text[:200]}")
        return False


def test_search_api():
    """Test if the token can access search API."""
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        return False
    
    print("\n[TEST] Testing Search API access...")
    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': 'AI agent', 'per_page': 1}
    
    response = requests.get(
        'https://api.github.com/search/repositories',
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        print("[OK] Search API is accessible")
        return True
    elif response.status_code == 401:
        print("[ERROR] Search API returned 401 - Token invalid")
        return False
    elif response.status_code == 403:
        print("[ERROR] Search API returned 403 - Rate limited or forbidden")
        print(f"        Message: {response.json().get('message', 'No message')}")
        return False
    else:
        print(f"[ERROR] Search API returned {response.status_code}")
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("GitHub Token Validation")
    print("=" * 50)
    
    token_valid = test_github_token()
    search_valid = test_search_api() if token_valid else False
    
    print("\n" + "=" * 50)
    if token_valid and search_valid:
        print("[RESULT] All tests PASSED - Token is working correctly")
    elif token_valid:
        print("[RESULT] Token valid but Search API has issues")
    else:
        print("[RESULT] Token is INVALID - Please update GITHUB_TOKEN in .env")
    print("=" * 50)
