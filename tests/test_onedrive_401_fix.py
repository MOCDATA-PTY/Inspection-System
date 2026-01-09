#!/usr/bin/env python3
"""
Test OneDrive 401 Error Fix
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

def test_token_exchange():
    """Test token exchange with different configurations."""
    print("🔍 TESTING ONEDRIVE 401 ERROR")
    print("=" * 50)
    
    client_secret = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
    client_id = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
    redirect_uri = "http://localhost:8000/onedrive/callback"
    
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:10]}...")
    print(f"Redirect URI: {redirect_uri}")
    
    # Test with a dummy auth code to see the exact error
    dummy_auth_code = "dummy_code_for_testing"
    
    # Test different endpoints
    endpoints = [
        "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "https://login.microsoftonline.com/organizations/oauth2/v2.0/token",
        "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
    ]
    
    for endpoint in endpoints:
        print(f"\n🧪 Testing endpoint: {endpoint}")
        
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': dummy_auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        try:
            response = requests.post(endpoint, data=token_data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"Error: {error_data.get('error', 'Unknown')}")
                    print(f"Error Description: {error_data.get('error_description', 'None')}")
                except:
                    pass
        except Exception as e:
            print(f"Error: {e}")
    
    # Test client credentials flow
    print(f"\n🔑 Testing client credentials flow...")
    client_creds_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials'
    }
    
    try:
        response = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token", data=client_creds_data)
        print(f"Client credentials status: {response.status_code}")
        print(f"Client credentials response: {response.text}")
    except Exception as e:
        print(f"Client credentials error: {e}")

def test_with_real_auth_code():
    """Test with a real authorization code."""
    print(f"\n🔗 TESTING WITH REAL AUTH CODE")
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
        return False
    
    # Test token exchange with different endpoints
    client_secret = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
    client_id = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
    redirect_uri = "http://localhost:8000/onedrive/callback"
    
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
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
                
                # Test API
                print("\n🔗 Testing API connection...")
                api_url = "https://graph.microsoft.com/v1.0/me"
                headers = {
                    'Authorization': f'Bearer {tokens["access_token"]}',
                    'Content-Type': 'application/json'
                }
                
                api_response = requests.get(api_url, headers=headers)
                if api_response.status_code == 200:
                    user_info = api_response.json()
                    print("✅ API connection successful!")
                    print(f"User: {user_info.get('displayName', 'Unknown')}")
                    print(f"Email: {user_info.get('mail', 'Unknown')}")
                    return True
                else:
                    print(f"❌ API test failed: {api_response.status_code}")
                    print(f"API response: {api_response.text}")
                    return False
            else:
                try:
                    error_data = response.json()
                    print(f"Error: {error_data.get('error', 'Unknown')}")
                    print(f"Error Description: {error_data.get('error_description', 'None')}")
                except:
                    pass
        except Exception as e:
            print(f"Error: {e}")
    
    return False

if __name__ == "__main__":
    test_token_exchange()
    print("\n" + "="*50)
    test_with_real_auth_code()
