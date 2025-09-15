#!/usr/bin/env python3
"""
Test OneDrive Connection with Client Secret
"""

import os
import sys
import django
import json
import requests
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def test_onedrive_connection():
    """Test OneDrive connection with the client secret."""
    print("🔐 TESTING ONEDRIVE CONNECTION")
    print("=" * 50)
    
    # Set the client secret
    client_secret = ".EF******************"  # Your second secret
    os.environ['ONEDRIVE_CLIENT_SECRET'] = client_secret
    
    print(f"✅ Client ID: {settings.ONEDRIVE_CLIENT_ID}")
    print(f"✅ Client Secret: {'Set' if client_secret else 'Not set'}")
    print(f"✅ Redirect URI: {settings.ONEDRIVE_REDIRECT_URI}")
    
    # Load existing tokens
    token_file = 'onedrive_tokens.json'
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            tokens = json.load(f)
        print(f"\n📄 Existing tokens loaded from {token_file}")
        print(f"Access Token: {tokens.get('access_token', 'None')[:20]}...")
        refresh_token = tokens.get('refresh_token')
        print(f"Refresh Token: {refresh_token[:20] + '...' if refresh_token else 'None'}")
        print(f"Expires At: {tokens.get('expires_at', 'None')}")
        
        # Check if token is expired
        if tokens.get('expires_at'):
            # Handle both float timestamp and ISO string formats
            if isinstance(tokens['expires_at'], (int, float)):
                expires_at = datetime.fromtimestamp(tokens['expires_at'])
            else:
                expires_at = datetime.fromisoformat(tokens['expires_at'].replace('Z', '+00:00'))
            
            if datetime.now() >= expires_at:
                print("⚠️  Access token is expired, attempting refresh...")
                if refresh_token:
                    return refresh_token_and_test(client_secret, tokens)
                else:
                    print("❌ No refresh token available for renewal")
                    return False
            else:
                print("✅ Access token is still valid")
                return test_api_connection(tokens['access_token'])
        else:
            print("⚠️  No expiry time found, testing current token...")
            return test_api_connection(tokens['access_token'])
    else:
        print(f"❌ No token file found at {token_file}")
        print("You need to complete the OAuth flow first")
        return False

def refresh_token_and_test(client_secret, tokens):
    """Refresh the token and test the connection."""
    print("\n🔄 REFRESHING TOKEN...")
    
    refresh_token = tokens.get('refresh_token')
    if not refresh_token:
        print("❌ No refresh token available")
        return False
    
    # Refresh token endpoint
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    data = {
        'client_id': settings.ONEDRIVE_CLIENT_ID,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    
    try:
        response = requests.post(token_url, data=data)
        print(f"Token refresh response: {response.status_code}")
        
        if response.status_code == 200:
            new_tokens = response.json()
            print("✅ Token refreshed successfully!")
            
            # Save new tokens
            with open('onedrive_tokens.json', 'w') as f:
                json.dump(new_tokens, f, indent=2)
            
            # Test API connection
            return test_api_connection(new_tokens['access_token'])
        else:
            print(f"❌ Token refresh failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
        return False

def test_api_connection(access_token):
    """Test the OneDrive API connection."""
    print("\n🔗 TESTING API CONNECTION...")
    
    # Test endpoint
    api_url = "https://graph.microsoft.com/v1.0/me"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        print(f"API test response: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print("✅ API connection successful!")
            print(f"User: {user_info.get('displayName', 'Unknown')}")
            print(f"Email: {user_info.get('mail', 'Unknown')}")
            return True
        else:
            print(f"❌ API connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    success = test_onedrive_connection()
    if success:
        print("\n🎉 OneDrive connection is working!")
    else:
        print("\n❌ OneDrive connection failed")
