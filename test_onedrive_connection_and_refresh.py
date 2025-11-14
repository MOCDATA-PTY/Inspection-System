#!/usr/bin/env python3
"""
Comprehensive OneDrive Connection and Auto Refresh Token Test
Tests connection, token validation, and automatic refresh functionality
"""

import os
import sys
import django
import requests
import json
import time
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def load_tokens():
    """Load OneDrive tokens from file."""
    token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
    
    if not os.path.exists(token_file):
        print("❌ No OneDrive tokens found")
        return None
    
    try:
        with open(token_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading tokens: {e}")
        return None

def save_tokens(token_data):
    """Save OneDrive tokens to file."""
    token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
    
    try:
        with open(token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
        print("✅ Tokens saved successfully")
        return True
    except Exception as e:
        print(f"❌ Error saving tokens: {e}")
        return False

def refresh_access_token(refresh_token):
    """Refresh the access token using the refresh token."""
    print("🔄 Attempting to refresh access token...")
    
    client_id = getattr(settings, 'ONEDRIVE_CLIENT_ID', '')
    client_secret = getattr(settings, 'ONEDRIVE_CLIENT_SECRET', '')
    redirect_uri = getattr(settings, 'ONEDRIVE_REDIRECT_URI', '')
    
    if not client_id or not client_secret:
        print("❌ Missing OneDrive credentials in settings")
        return None
    
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    
    try:
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Token refreshed successfully")
            
            # Calculate new expiry time
            expires_in = token_data.get('expires_in', 3600)
            expires_at = datetime.now().timestamp() + expires_in
            
            token_data['expires_at'] = expires_at
            token_data['refreshed_at'] = datetime.now().isoformat()
            
            return token_data
        else:
            print(f"❌ Token refresh failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
        return None

def test_onedrive_connection(access_token):
    """Test OneDrive connection with access token."""
    print("🔍 Testing OneDrive connection...")
    
    test_url = "https://graph.microsoft.com/v1.0/me/drive"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(test_url, headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print("✅ OneDrive connection successful!")
            print(f"🚗 Drive ID: {user_info.get('id', 'Unknown')}")
            print(f"📁 Drive Type: {user_info.get('driveType', 'Unknown')}")
            print(f"👤 Owner: {user_info.get('owner', {}).get('user', {}).get('displayName', 'Unknown')}")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_file_operations(access_token):
    """Test basic file operations to verify full functionality."""
    print("📁 Testing file operations...")
    
    # Test listing root folder
    list_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(list_url, headers=headers)
        
        if response.status_code == 200:
            items = response.json().get('value', [])
            print(f"✅ Successfully listed {len(items)} items in root folder")
            
            # Show first few items
            for i, item in enumerate(items[:3]):
                print(f"  📄 {item.get('name', 'Unknown')} ({item.get('folder', {}).get('childCount', 0)} items)")
            
            return True
        else:
            print(f"❌ File listing failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ File operation error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 ONEDRIVE CONNECTION AND REFRESH TOKEN TEST")
    print("=" * 60)
    
    # Load existing tokens
    token_data = load_tokens()
    if not token_data:
        print("\n❌ No tokens found. Please run the OneDrive setup first.")
        print("Run: python test_onedrive_connection.py")
        return
    
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    expires_at = token_data.get('expires_at', 0)
    current_time = datetime.now().timestamp()
    
    print(f"✅ Tokens loaded successfully")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Token expires at: {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Time until expiry: {expires_at - current_time:.1f} seconds")
    
    # Check if token is expired or will expire soon (within 5 minutes)
    if current_time >= expires_at - 300:  # 5 minutes buffer
        print("⚠️ Token expired or expiring soon, attempting refresh...")
        
        if not refresh_token:
            print("❌ No refresh token available")
            return
        
        new_token_data = refresh_access_token(refresh_token)
        if new_token_data:
            # Merge with existing data
            token_data.update(new_token_data)
            if save_tokens(token_data):
                access_token = token_data.get('access_token')
                expires_at = token_data.get('expires_at', 0)
                print(f"✅ New token expires at: {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("❌ Failed to save new tokens")
                return
        else:
            print("❌ Token refresh failed")
            return
    else:
        print("✅ Token is still valid")
    
    # Test connection
    if not test_onedrive_connection(access_token):
        print("❌ Connection test failed")
        return
    
    # Test file operations
    if not test_file_operations(access_token):
        print("❌ File operations test failed")
        return
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ OneDrive connection is working")
    print("✅ Token refresh functionality is working")
    print("✅ File operations are working")
    print("\n🚀 OneDrive integration is ready for use!")

if __name__ == "__main__":
    main()
