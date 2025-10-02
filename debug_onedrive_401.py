#!/usr/bin/env python3
"""
Debug OneDrive 401 Error
"""

import os
import sys
import django
import json
import requests

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def debug_onedrive_config():
    """Debug the OneDrive configuration."""
    print("🔍 DEBUGGING ONEDRIVE 401 ERROR")
    print("=" * 50)
    
    # Set client secret
    client_secret = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
    os.environ['ONEDRIVE_CLIENT_SECRET'] = client_secret
    
    print(f"Client ID: {settings.ONEDRIVE_CLIENT_ID}")
    print(f"Client Secret: {client_secret}")
    print(f"Redirect URI: {settings.ONEDRIVE_REDIRECT_URI}")
    
    # Test different token endpoints
    endpoints = [
        "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "https://login.microsoftonline.com/organizations/oauth2/v2.0/token",
        "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
    ]
    
    # Test data
    test_data = {
        'client_id': settings.ONEDRIVE_CLIENT_ID,
        'client_secret': client_secret,
        'code': 'test_code',  # This will fail but we can see the error
        'grant_type': 'authorization_code',
        'redirect_uri': settings.ONEDRIVE_REDIRECT_URI
    }
    
    print(f"\nTest data: {test_data}")
    
    for endpoint in endpoints:
        print(f"\n🧪 Testing endpoint: {endpoint}")
        try:
            response = requests.post(endpoint, data=test_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 400:
                error_data = response.json()
                if 'error_description' in error_data:
                    print(f"Error Description: {error_data['error_description']}")
                if 'error' in error_data:
                    print(f"Error: {error_data['error']}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Test client credentials flow
    print(f"\n🔑 Testing client credentials flow...")
    client_creds_data = {
        'client_id': settings.ONEDRIVE_CLIENT_ID,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials'
    }
    
    try:
        response = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token", data=client_creds_data)
        print(f"Client credentials status: {response.status_code}")
        print(f"Client credentials response: {response.text[:200]}...")
    except Exception as e:
        print(f"Client credentials error: {e}")

def test_manual_token_exchange():
    """Test manual token exchange with a real auth code."""
    print(f"\n🔗 MANUAL TOKEN EXCHANGE TEST")
    print("=" * 40)
    
    # Get auth code from user
    print("Please go to this URL and get the authorization code:")
    print("https://login.microsoftonline.com/common/oauth2/v2.0/authorize?")
    print("client_id=e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f&")
    print("response_type=code&")
    print("redirect_uri=http://localhost:8000/onedrive/callback&")
    print("scope=https://graph.microsoft.com/Files.ReadWrite https://graph.microsoft.com/User.Read https://graph.microsoft.com/offline_access&")
    print("response_mode=query&")
    print("state=manual_test&")
    print("prompt=consent")
    print()
    
    auth_code = input("Enter the authorization code: ").strip()
    
    if not auth_code:
        print("No authorization code provided")
        return
    
    # Test token exchange
    client_secret = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
    
    token_data = {
        'client_id': 'e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f',
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:8000/onedrive/callback'
    }
    
    print(f"\nToken request data: {token_data}")
    
    # Try different endpoints
    endpoints = [
        "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "https://login.microsoftonline.com/organizations/oauth2/v2.0/token"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting {endpoint}")
        try:
            response = requests.post(endpoint, data=token_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                tokens = response.json()
                print("✅ Success!")
                print(f"Access Token: {tokens.get('access_token', 'None')[:20]}...")
                print(f"Refresh Token: {tokens.get('refresh_token', 'None')[:20]}...")
                
                # Save tokens
                with open('onedrive_tokens.json', 'w') as f:
                    json.dump(tokens, f, indent=2)
                
                return True
            else:
                error_data = response.json()
                print(f"Error: {error_data}")
        except Exception as e:
            print(f"Error: {e}")
    
    return False

if __name__ == "__main__":
    debug_onedrive_config()
    print("\n" + "="*50)
    test_manual_token_exchange()
