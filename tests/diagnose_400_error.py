#!/usr/bin/env python3
"""
Diagnose 400 Error in Token Exchange
"""

import requests
import json

def diagnose_400_error():
    print("🔍 DIAGNOSING 400 ERROR")
    print("=" * 40)
    
    # Your credentials
    tenant_id = "61ab5cbc-cdc4-498a-ba14-4d38595a85ff"
    client_id = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
    client_secret = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
    redirect_uri = "http://localhost:8000/onedrive/callback"
    
    print("Please get a FRESH authorization code from this URL:")
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
    print("⚠️  IMPORTANT: Use a FRESH code (don't reuse an old one)")
    
    auth_code = input("\nEnter the FRESH authorization code: ").strip()
    
    if not auth_code:
        print("❌ No code provided")
        return False
    
    # Test with different configurations
    print(f"\n🧪 Testing with code: {auth_code[:20]}...")
    
    # Configuration 1: Exact match
    print("\n1️⃣ Testing with exact redirect URI match...")
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
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
            print("✅ SUCCESS!")
            tokens = response.json()
            
            # Save tokens
            with open('onedrive_tokens.json', 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print(f"Access Token: {tokens.get('access_token', 'None')[:20]}...")
            print(f"Refresh Token: {tokens.get('refresh_token', 'None')[:20]}...")
            return True
        else:
            try:
                error_data = response.json()
                print(f"❌ Error: {error_data.get('error', 'Unknown')}")
                print(f"Error Description: {error_data.get('error_description', 'None')}")
                
                # Check for specific error codes
                error_codes = error_data.get('error_codes', [])
                if 70008 in error_codes:
                    print("🚨 CODE EXPIRED - Get a fresh authorization code")
                elif 70011 in error_codes:
                    print("🚨 INVALID REDIRECT URI - Check redirect URI match")
                elif 90014 in error_codes:
                    print("🚨 MISSING CLIENT_ID - Check client ID parameter")
                elif 9002313 in error_codes:
                    print("🚨 MALFORMED REQUEST - Check request format")
                
            except:
                print(f"❌ Raw error: {response.text}")
            
            # Try alternative configurations
            print("\n2️⃣ Trying with common endpoint...")
            common_token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            common_response = requests.post(common_token_url, data=token_data)
            print(f"Common endpoint status: {common_response.status_code}")
            print(f"Common endpoint response: {common_response.text}")
            
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = diagnose_400_error()
    if success:
        print("\n🎉 OneDrive is working!")
    else:
        print("\n❌ OneDrive setup failed")
        print("\n💡 TROUBLESHOOTING TIPS:")
        print("1. Make sure you're using a FRESH authorization code")
        print("2. Don't reuse old codes - they expire quickly")
        print("3. Check that the redirect URI matches exactly")
        print("4. Try the authorization flow again if the code expired")
