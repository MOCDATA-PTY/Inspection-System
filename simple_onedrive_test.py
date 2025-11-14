#!/usr/bin/env python3
"""
Simple OneDrive Test - Manual Authorization
"""

import os
import sys
import django
import json
import requests
import webbrowser
import urllib.parse

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def generate_auth_url():
    """Generate a proper authorization URL."""
    client_id = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
    redirect_uri = "http://localhost:8000/onedrive/callback"
    
    scopes = [
        'https://graph.microsoft.com/Files.ReadWrite',
        'https://graph.microsoft.com/User.Read',
        'https://graph.microsoft.com/offline_access'
    ]
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes),
        'response_mode': 'query',
        'state': 'test_auth',
        'prompt': 'consent'
    }
    
    base_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    return auth_url

def test_token_exchange(auth_code):
    """Test token exchange with the authorization code."""
    client_id = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
    client_secret = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
    redirect_uri = "http://localhost:8000/onedrive/callback"
    
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    
    print(f"Token URL: {token_url}")
    print(f"Token Data: {token_data}")
    
    try:
        response = requests.post(token_url, data=token_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            tokens = response.json()
            print("✅ Token exchange successful!")
            
            # Save tokens
            with open('onedrive_tokens.json', 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print(f"Access Token: {tokens.get('access_token', 'None')[:20]}...")
            print(f"Refresh Token: {tokens.get('refresh_token', 'None')[:20]}...")
            
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
                print(f"❌ Error: {error_data.get('error', 'Unknown')}")
                print(f"Error Description: {error_data.get('error_description', 'None')}")
            except:
                print(f"❌ Raw error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🔐 SIMPLE ONEDRIVE TEST")
    print("=" * 40)
    
    # Generate authorization URL
    auth_url = generate_auth_url()
    print(f"Authorization URL: {auth_url}")
    
    # Open browser
    print("\n🌐 Opening browser for authentication...")
    webbrowser.open(auth_url)
    
    print("\nPlease complete the authentication in your browser.")
    print("After authentication, you'll be redirected to localhost:8000/onedrive/callback")
    print("Copy the 'code' parameter from the URL and paste it below.")
    
    # Get authorization code from user
    auth_code = input("\nEnter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return False
    
    print(f"\n🔄 Testing token exchange with code: {auth_code[:20]}...")
    return test_token_exchange(auth_code)

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 OneDrive authentication successful!")
    else:
        print("\n❌ OneDrive authentication failed")
