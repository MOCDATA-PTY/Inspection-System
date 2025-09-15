#!/usr/bin/env python3
"""
OneDrive Business Account Test and Setup
For anthony.penzes@fsa-pty.co.za (business account)
"""

import os
import sys
import django
import requests
import json
import webbrowser
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def check_current_config():
    """Check current OneDrive configuration."""
    print("🔍 CHECKING CURRENT ONEDRIVE CONFIGURATION")
    print("=" * 60)
    
    client_id = getattr(settings, 'ONEDRIVE_CLIENT_ID', '')
    client_secret = getattr(settings, 'ONEDRIVE_CLIENT_SECRET', '')
    redirect_uri = getattr(settings, 'ONEDRIVE_REDIRECT_URI', '')
    
    print(f"✅ Client ID: {client_id[:8]}...{client_id[-8:] if len(client_id) > 16 else client_id}")
    print(f"✅ Client Secret: {'Set (' + str(len(client_secret)) + ' chars)' if client_secret else '❌ NOT SET'}")
    print(f"✅ Redirect URI: {redirect_uri}")
    print(f"✅ OneDrive Enabled: {getattr(settings, 'ONEDRIVE_ENABLED', False)}")
    
    # Check if tokens exist
    token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
    if os.path.exists(token_file):
        print(f"✅ Token file exists: {token_file}")
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            print(f"✅ Access token: {'Present' if token_data.get('access_token') else 'Missing'}")
            print(f"✅ Refresh token: {'Present' if token_data.get('refresh_token') else 'Missing'}")
            
            expires_at = token_data.get('expires_at', 0)
            current_time = datetime.now().timestamp()
            if expires_at > current_time:
                print(f"✅ Token expires: {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"❌ Token expired: {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"❌ Error reading token file: {e}")
    else:
        print(f"❌ No token file found: {token_file}")
    
    return client_id, client_secret, redirect_uri

def test_existing_connection():
    """Test existing OneDrive connection if tokens exist."""
    print("\n🧪 TESTING EXISTING CONNECTION")
    print("=" * 40)
    
    token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
    if not os.path.exists(token_file):
        print("❌ No tokens found - need to authenticate first")
        return False
    
    try:
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        access_token = token_data.get('access_token')
        if not access_token:
            print("❌ No access token found")
            return False
        
        # Test connection
        test_url = "https://graph.microsoft.com/v1.0/me/drive"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("🔍 Testing connection to Microsoft Graph API...")
        response = requests.get(test_url, headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print("✅ Connection successful!")
            print(f"🚗 Drive ID: {user_info.get('id', 'Unknown')}")
            print(f"📁 Drive Type: {user_info.get('driveType', 'Unknown')}")
            print(f"👤 Owner: {user_info.get('owner', {}).get('user', {}).get('displayName', 'Unknown')}")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def generate_auth_url_for_business():
    """Generate authorization URL for business account."""
    print("\n🌐 GENERATING AUTHORIZATION URL FOR BUSINESS ACCOUNT")
    print("=" * 60)
    
    client_id = getattr(settings, 'ONEDRIVE_CLIENT_ID', '')
    redirect_uri = getattr(settings, 'ONEDRIVE_REDIRECT_URI', '')
    
    if not client_id:
        print("❌ Client ID not configured")
        return None
    
    # Use common endpoint for work/school accounts
    auth_url = (
        f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope=offline_access%20Files.ReadWrite.All%20User.Read"
        f"&prompt=select_account"
    )
    
    print(f"✅ Authorization URL generated:")
    print(auth_url)
    
    return auth_url

def check_azure_app_requirements():
    """Check Azure app registration requirements."""
    print("\n🔧 AZURE APP REGISTRATION REQUIREMENTS")
    print("=" * 50)
    
    print("📋 Your Azure app MUST be configured for business accounts:")
    print("1. Go to: https://portal.azure.com")
    print("2. Navigate to: Azure Active Directory → App registrations")
    print("3. Find your app (Client ID: " + getattr(settings, 'ONEDRIVE_CLIENT_ID', '')[:8] + "...)")
    print("4. Click on it → Authentication")
    print("5. Under 'Supported account types', select:")
    print("   ✅ 'Accounts in any organizational directory (Any Microsoft Entra ID tenant - Multitenant)'")
    print("   OR")
    print("   ✅ 'Accounts in this organizational directory only'")
    print("6. Click 'Save'")
    
    print("\n📋 API Permissions required:")
    print("1. Go to: API permissions")
    print("2. Add these Delegated permissions:")
    print("   - Microsoft Graph → Files.ReadWrite.All")
    print("   - Microsoft Graph → offline_access")
    print("   - Microsoft Graph → User.Read")
    print("3. Click 'Grant admin consent' (if required)")
    
    print("\n📋 Client Secret required:")
    print("1. Go to: Certificates & secrets")
    print("2. Click 'New client secret'")
    print("3. Add description: 'OneDrive Integration'")
    print("4. Set expiration (recommend 24 months)")
    print("5. Copy the secret VALUE (not the ID)")
    print("6. Update your Django settings with the secret")

def main():
    """Main test function."""
    print("🏢 ONEDRIVE BUSINESS ACCOUNT TEST")
    print("=" * 60)
    print("Account: anthony.penzes@fsa-pty.co.za")
    print("Type: Business/Work account")
    
    # Check current configuration
    client_id, client_secret, redirect_uri = check_current_config()
    
    # Test existing connection if possible
    if test_existing_connection():
        print("\n🎉 OneDrive is already working!")
        return
    
    # Check if we have the required configuration
    if not client_secret:
        print("\n❌ CLIENT SECRET MISSING!")
        print("You need to set up a client secret in Azure and update your settings.")
        check_azure_app_requirements()
        return
    
    # Generate authorization URL
    auth_url = generate_auth_url_for_business()
    if not auth_url:
        return
    
    print(f"\n📋 NEXT STEPS:")
    print("1. Ensure your Azure app supports business accounts (see requirements above)")
    print("2. Make sure you have a valid client secret")
    print("3. Click the authorization URL below")
    print("4. Sign in with: anthony.penzes@fsa-pty.co.za")
    print("5. Grant permissions to the app")
    print("6. You'll be redirected to the callback URL")
    print("7. Check for onedrive_tokens.json file")
    
    # Try to open browser
    try:
        print(f"\n🔗 Opening browser...")
        webbrowser.open(auth_url)
        print("✅ Browser opened with authorization URL")
    except Exception as e:
        print(f"⚠️ Could not open browser: {e}")
        print("Please copy and paste the URL above into your browser")

if __name__ == "__main__":
    main()
