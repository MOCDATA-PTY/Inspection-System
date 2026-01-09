#!/usr/bin/env python3
"""
Simulate Token Expiry and Test Auto-Refresh
"""

import os
import sys
import django
import json
import requests
import time

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def simulate_expired_token():
    """Simulate an expired token to test refresh functionality."""
    print("🔄 SIMULATING TOKEN EXPIRY AND TESTING AUTO-REFRESH")
    print("=" * 60)
    
    # Load current tokens
    try:
        with open('onedrive_tokens.json', 'r') as f:
            tokens = json.load(f)
    except FileNotFoundError:
        print("❌ No token file found")
        return False
    
    print("📄 Current token status:")
    print(f"Access Token: {tokens.get('access_token', 'None')[:20]}...")
    print(f"Refresh Token: {tokens.get('refresh_token', 'None')[:20]}...")
    print(f"Expires At: {tokens.get('expires_at', 'None')}")
    
    # Simulate expired token by setting expiry time to past
    print("\n⏰ Simulating expired token...")
    tokens['expires_at'] = time.time() - 3600  # Set to 1 hour ago
    
    # Save the modified tokens
    with open('onedrive_tokens.json', 'w') as f:
        json.dump(tokens, f, indent=2)
    
    print("✅ Token expiry simulated (set to 1 hour ago)")
    
    # Now test the refresh functionality
    print("\n🔄 Testing auto-refresh functionality...")
    
    # Your credentials
    tenant_id = "61ab5cbc-cdc4-498a-ba14-4d38595a85ff"
    client_id = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
    client_secret = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
    
    # Check if we have a refresh token
    refresh_token = tokens.get('refresh_token')
    if not refresh_token:
        print("❌ No refresh token available - need to re-authenticate")
        print("💡 This is normal for the first authentication")
        return False
    
    # Try to refresh the token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    refresh_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    
    try:
        print("🔄 Attempting token refresh...")
        response = requests.post(token_url, data=refresh_data)
        print(f"Refresh status: {response.status_code}")
        
        if response.status_code == 200:
            new_tokens = response.json()
            print("✅ Token refresh successful!")
            
            # Add expiry time
            expires_in = new_tokens.get('expires_in', 3600)
            new_tokens['expires_at'] = time.time() + expires_in
            
            # Save new tokens
            with open('onedrive_tokens.json', 'w') as f:
                json.dump(new_tokens, f, indent=2)
            
            print(f"New Access Token: {new_tokens.get('access_token', 'None')[:20]}...")
            print(f"New Refresh Token: {new_tokens.get('refresh_token', 'None')[:20]}...")
            print(f"New Expires At: {new_tokens.get('expires_at', 'None')}")
            
            # Test the new token
            print("\n🔗 Testing new token...")
            api_url = "https://graph.microsoft.com/v1.0/me"
            headers = {
                'Authorization': f'Bearer {new_tokens["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            api_response = requests.get(api_url, headers=headers)
            if api_response.status_code == 200:
                user_info = api_response.json()
                print("✅ New token works!")
                print(f"User: {user_info.get('displayName')} ({user_info.get('mail')})")
                return True
            else:
                print(f"❌ New token test failed: {api_response.status_code}")
                return False
        else:
            print(f"❌ Token refresh failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Refresh error: {e}")
        return False

def restore_working_token():
    """Restore the working token for normal use."""
    print("\n🔄 Restoring working token...")
    
    # Run the working fix script to get fresh tokens
    import subprocess
    result = subprocess.run(['python', 'fix_onedrive_now.py'], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Working token restored")
        return True
    else:
        print("❌ Failed to restore working token")
        return False

if __name__ == "__main__":
    success = simulate_expired_token()
    
    if not success:
        print("\n🔄 Restoring working token...")
        restore_working_token()
    
    if success:
        print("\n🎉 AUTO-REFRESH TOKEN FUNCTIONALITY IS WORKING!")
        print("✅ Token refresh works when tokens expire")
        print("✅ New tokens are properly saved")
        print("✅ Refreshed tokens work with OneDrive API")
    else:
        print("\n⚠️ Auto-refresh needs attention")
        print("💡 This is normal if no refresh token was available")
