#!/usr/bin/env python3
"""
Quick OneDrive Token Setup using existing authorization code
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def setup_tokens_with_code():
    """Setup OneDrive tokens using the existing authorization code."""
    print("🔐 Setting up OneDrive tokens with existing authorization code")
    print("=" * 60)
    
    # Use the authorization code from the callback
    auth_code = "M.C554_BAY.2.U.4d487c4e-aaea-4122-36c2-daef70ed352f"
    print(f"✅ Using authorization code: {auth_code}")
    
    try:
        # Exchange authorization code for access token
        token_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
        token_data = {
            'client_id': settings.ONEDRIVE_CLIENT_ID,
            'client_secret': settings.ONEDRIVE_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': settings.ONEDRIVE_REDIRECT_URI
        }
        
        print("\n🔑 Exchanging auth code for access token...")
        response = requests.post(token_url, data=token_data)
        
        if response.status_code == 200:
            token_response = response.json()
            access_token = token_response.get('access_token')
            refresh_token = token_response.get('refresh_token')
            
            if access_token:
                print("✅ Access token received successfully!")
                print(f"✅ Token expires in: {token_response.get('expires_in', 'unknown')} seconds")
                
                # Save tokens to file for the service to use
                token_data = {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_in': token_response.get('expires_in'),
                    'token_type': token_response.get('token_type'),
                    'expires_at': datetime.now().timestamp() + token_response.get('expires_in', 3600)
                }
                
                token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
                with open(token_file, 'w') as f:
                    json.dump(token_data, f, indent=2)
                
                print(f"✅ Tokens saved to: {token_file}")
                print("✅ OneDrive authentication setup complete!")
                
                # Test the connection
                print("\n🧪 Testing OneDrive connection...")
                test_success = test_onedrive_connection()
                
                if test_success:
                    print("\n🎉 OneDrive is now ready for direct upload!")
                    print("✅ You can now use the 'Upload ALL Documents to OneDrive' button")
                    return True
                else:
                    print("\n❌ Connection test failed")
                    return False
            else:
                print("❌ No access token received")
                return False
        else:
            print(f"❌ Token exchange failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        return False

def test_onedrive_connection():
    """Test OneDrive connection with saved tokens."""
    try:
        token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
        
        if not os.path.exists(token_file):
            print("❌ No token file found")
            return False
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        access_token = token_data.get('access_token')
        if not access_token:
            print("❌ No access token found in token file")
            return False
        
        # Test connection by getting user info
        test_url = "https://graph.microsoft.com/v1.0/me"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(test_url, headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ OneDrive connection successful!")
            print(f"👤 User: {user_info.get('displayName', 'Unknown')}")
            print(f"📧 Email: {user_info.get('userPrincipalName', 'Unknown')}")
            return True
        else:
            print(f"❌ OneDrive connection failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Quick OneDrive Token Setup")
    print("=" * 60)
    
    success = setup_tokens_with_code()
    
    if success:
        print("\n✅ OneDrive authentication is now permanent!")
        print("✅ The service will automatically refresh tokens when needed")
        print("✅ You can now use the OneDrive Direct Upload Service")
    else:
        print("\n❌ Setup failed")
    
    return success

if __name__ == "__main__":
    main()
