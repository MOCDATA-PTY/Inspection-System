#!/usr/bin/env python3
"""
Test Token Exchange with Correct Endpoint
"""

import requests
import json

def test_token_exchange():
    print("🔍 TESTING TOKEN EXCHANGE")
    print("=" * 40)
    
    # Your credentials
    tenant_id = "61ab5cbc-cdc4-498a-ba14-4d38595a85ff"
    client_id = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
    client_secret = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
    redirect_uri = "http://localhost:8000/onedrive/callback"
    
    print("Please go to this URL and get the authorization code:")
    print(f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?")
    print(f"client_id={client_id}&")
    print(f"response_type=code&")
    print(f"redirect_uri={redirect_uri}&")
    print("scope=https://graph.microsoft.com/Files.ReadWrite https://graph.microsoft.com/User.Read https://graph.microsoft.com/offline_access&")
    print("response_mode=query&")
    print("state=test&")
    print("prompt=consent&")
    print("login_hint=anthony.penzes@fsa-pty.co.za")
    print()
    
    auth_code = input("Enter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ No code provided")
        return False
    
    # Test with tenant-specific endpoint
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    
    print(f"\nToken URL: {token_url}")
    print(f"Token Data: {token_data}")
    
    try:
        response = requests.post(token_url, data=token_data)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            tokens = response.json()
            print("✅ SUCCESS!")
            
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

if __name__ == "__main__":
    success = test_token_exchange()
    if success:
        print("\n🎉 OneDrive is working!")
    else:
        print("\n❌ OneDrive setup failed")
