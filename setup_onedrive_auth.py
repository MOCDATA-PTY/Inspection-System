#!/usr/bin/env python3
"""
Setup OneDrive Authentication for Direct Upload Service
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

def setup_onedrive_auth():
    """Setup OneDrive authentication using authorization code flow."""
    print("🔐 Setting up OneDrive Authentication")
    print("=" * 50)
    
    try:
        # Check if OneDrive is enabled
        if not getattr(settings, 'ONEDRIVE_ENABLED', False):
            print("❌ OneDrive integration is not enabled in settings")
            return False
        
        print(f"✅ OneDrive enabled: {settings.ONEDRIVE_ENABLED}")
        print(f"✅ Client ID: {settings.ONEDRIVE_CLIENT_ID}")
        print(f"✅ OneDrive folder: {getattr(settings, 'ONEDRIVE_FOLDER', 'Legal-System-Media')}")
        
        # Use the registered redirect URI from settings
        redirect_uri = settings.ONEDRIVE_REDIRECT_URI
        print(f"✅ Redirect URI: {redirect_uri}")
        
        # Generate authorization URL
        auth_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize"
        auth_params = {
            'client_id': settings.ONEDRIVE_CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': 'Files.ReadWrite.All',
            'response_mode': 'query'
        }
        
        # Build the authorization URL
        auth_url_with_params = f"{auth_url}?{'&'.join([f'{k}={v}' for k, v in auth_params.items()])}"
        
        print("\n🔗 Authorization URL:")
        print(auth_url_with_params)
        print("\n📋 Instructions:")
        print("1. Copy and paste the URL above into your browser")
        print("2. Sign in with your Microsoft account")
        print("3. Grant permissions to the app")
        print("4. You'll be redirected to localhost:8000 with the authorization code")
        print("5. Copy the authorization code from the URL and paste it below")
        print("\n💡 Tip: Look for 'code=' in the URL after authorization")
        print("💡 Example: http://localhost:8000/onedrive/callback?code=M.C554_BAY.2.U.8d5e95a5-0868-8ead-f873-598f0c1ca38c")
        
        # Get authorization code from user
        auth_code = input("\n🔢 Enter the authorization code: ").strip()
        
        if not auth_code:
            print("❌ No authorization code provided")
            return False
        
        print(f"✅ Authorization code received: {auth_code}")
        
        # Exchange authorization code for access token
        token_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
        token_data = {
            'client_id': settings.ONEDRIVE_CLIENT_ID,
            'client_secret': settings.ONEDRIVE_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_uri
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
                print("\n🚀 You can now run the OneDrive Direct Upload Service")
                return True
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
    print("\n🧪 Testing OneDrive Connection")
    print("=" * 30)
    
    try:
        token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
        
        if not os.path.exists(token_file):
            print("❌ No token file found. Please run setup first.")
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
    print("🚀 OneDrive Authentication Setup")
    print("=" * 50)
    
    # Check if tokens already exist
    token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
    
    if os.path.exists(token_file):
        print("🔍 Found existing token file")
        test_success = test_onedrive_connection()
        
        if test_success:
            print("\n✅ OneDrive is already authenticated and working!")
            return True
        else:
            print("\n⚠️ Existing tokens are invalid or expired")
            choice = input("Do you want to set up new authentication? (y/n): ").strip().lower()
            if choice != 'y':
                return False
    
    # Setup new authentication
    success = setup_onedrive_auth()
    
    if success:
        print("\n🧪 Testing the connection...")
        test_success = test_onedrive_connection()
        
        if test_success:
            print("\n🎉 OneDrive authentication setup complete!")
            print("✅ Ready to run the Direct Upload Service")
            return True
        else:
            print("\n❌ Authentication setup failed")
            return False
    else:
        print("\n❌ Authentication setup failed")
        return False

if __name__ == "__main__":
    main()
