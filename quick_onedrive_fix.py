#!/usr/bin/env python3
"""
Quick OneDrive Fix with Tenant ID
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

def main():
    print("🚀 QUICK ONEDRIVE FIX")
    print("=" * 30)
    
    # Your tenant ID
    tenant_id = "61ab5cbc-cdc4-498a-ba14-4d38595a85ff"
    client_id = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
    client_secret = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
    redirect_uri = "http://localhost:8000/onedrive/callback"
    
    print(f"Tenant ID: {tenant_id}")
    print(f"Client ID: {client_id}")
    print(f"Client Secret: {client_secret[:10]}...")
    
    # Generate auth URL with tenant ID
    auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': 'https://graph.microsoft.com/Files.ReadWrite https://graph.microsoft.com/User.Read https://graph.microsoft.com/offline_access',
        'response_mode': 'query',
        'state': 'quick_fix',
        'prompt': 'consent',
        'login_hint': 'anthony.penzes@fsa-pty.co.za'
    }
    
    full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    print(f"\nAuth URL: {full_auth_url}")
    
    # Open browser
    webbrowser.open(full_auth_url)
    
    print("\n🌐 Complete authentication in browser")
    print("Copy the 'code' parameter from the redirect URL")
    
    auth_code = input("\nEnter auth code: ").strip()
    
    if not auth_code:
        print("❌ No code provided")
        return False
    
    # Exchange for tokens
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    
    print(f"\n🔄 Exchanging tokens...")
    response = requests.post(token_url, data=token_data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        tokens = response.json()
        print("✅ Success!")
        
        # Save tokens
        with open('onedrive_tokens.json', 'w') as f:
            json.dump(tokens, f, indent=2)
        
        print(f"Access Token: {tokens.get('access_token', 'None')[:20]}...")
        print(f"Refresh Token: {tokens.get('refresh_token', 'None')[:20]}...")
        
        # Test API
        print("\n🔗 Testing API...")
        api_url = "https://graph.microsoft.com/v1.0/me"
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        
        api_response = requests.get(api_url, headers=headers)
        if api_response.status_code == 200:
            user_info = api_response.json()
            print("✅ API works!")
            print(f"User: {user_info.get('displayName')}")
            print(f"Email: {user_info.get('mail')}")
            return True
        else:
            print(f"❌ API failed: {api_response.status_code}")
            return False
    else:
        print(f"❌ Token exchange failed: {response.status_code}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 OneDrive is working!")
    else:
        print("\n❌ OneDrive setup failed")