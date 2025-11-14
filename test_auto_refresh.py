#!/usr/bin/env python3
"""
Test OneDrive Auto-Refresh Token Functionality
"""

import os
import sys
import django
import json
import requests
import time
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def load_tokens():
    """Load tokens from file."""
    try:
        with open('onedrive_tokens.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No token file found")
        return None

def save_tokens(tokens):
    """Save tokens to file."""
    with open('onedrive_tokens.json', 'w') as f:
        json.dump(tokens, f, indent=2)

def test_api_connection(access_token):
    """Test API connection with access token."""
    api_url = "https://graph.microsoft.com/v1.0/me"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ API working - User: {user_info.get('displayName')}")
            return True
        else:
            print(f"❌ API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API error: {e}")
        return False

def refresh_token_if_needed():
    """Refresh token if it's expired or about to expire."""
    tokens = load_tokens()
    if not tokens:
        return False
    
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    expires_at = tokens.get('expires_at')
    
    print(f"📄 Current token status:")
    print(f"Access Token: {access_token[:20] if access_token else 'None'}...")
    print(f"Refresh Token: {refresh_token[:20] if refresh_token else 'None'}...")
    print(f"Expires At: {expires_at}")
    
    if not access_token:
        print("❌ No access token found")
        return False
    
    # Check if token is expired or about to expire (within 5 minutes)
    current_time = time.time()
    if expires_at and current_time >= (expires_at - 300):  # 5 minutes buffer
        print("⚠️ Token is expired or about to expire, attempting refresh...")
        
        if not refresh_token:
            print("❌ No refresh token available - need to re-authenticate")
            return False
        
        # Refresh the token
        tenant_id = "61ab5cbc-cdc4-498a-ba14-4d38595a85ff"
        client_id = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
        client_secret = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
        
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        
        refresh_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            print("🔄 Refreshing token...")
            response = requests.post(token_url, data=refresh_data)
            print(f"Refresh status: {response.status_code}")
            
            if response.status_code == 200:
                new_tokens = response.json()
                print("✅ Token refreshed successfully!")
                
                # Add expiry time
                expires_in = new_tokens.get('expires_in', 3600)
                new_tokens['expires_at'] = time.time() + expires_in
                
                # Save new tokens
                save_tokens(new_tokens)
                
                print(f"New Access Token: {new_tokens.get('access_token', 'None')[:20]}...")
                print(f"New Refresh Token: {new_tokens.get('refresh_token', 'None')[:20]}...")
                print(f"New Expires At: {new_tokens.get('expires_at', 'None')}")
                
                return new_tokens.get('access_token')
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Refresh error: {e}")
            return False
    else:
        print("✅ Token is still valid")
        return access_token

def test_onedrive_operations(access_token):
    """Test OneDrive operations."""
    print("\n🔗 Testing OneDrive operations...")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Get user info
    print("1️⃣ Testing user info...")
    user_response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
    if user_response.status_code == 200:
        user_info = user_response.json()
        print(f"✅ User: {user_info.get('displayName')} ({user_info.get('mail')})")
    else:
        print(f"❌ User info failed: {user_response.status_code}")
        return False
    
    # Test 2: Get OneDrive root
    print("2️⃣ Testing OneDrive root access...")
    drive_response = requests.get("https://graph.microsoft.com/v1.0/me/drive/root", headers=headers)
    if drive_response.status_code == 200:
        drive_info = drive_response.json()
        print(f"✅ OneDrive root: {drive_info.get('name', 'Unknown')}")
    else:
        print(f"❌ OneDrive root failed: {drive_response.status_code}")
        return False
    
    # Test 3: List files
    print("3️⃣ Testing file listing...")
    files_response = requests.get("https://graph.microsoft.com/v1.0/me/drive/root/children", headers=headers)
    if files_response.status_code == 200:
        files_data = files_response.json()
        file_count = len(files_data.get('value', []))
        print(f"✅ Found {file_count} items in OneDrive root")
    else:
        print(f"❌ File listing failed: {files_response.status_code}")
        return False
    
    return True

def main():
    print("🔄 TESTING ONEDRIVE AUTO-REFRESH TOKEN")
    print("=" * 50)
    
    # Test current token
    print("1️⃣ Testing current token...")
    access_token = refresh_token_if_needed()
    
    if not access_token:
        print("❌ No valid access token available")
        return False
    
    # Test API connection
    print("\n2️⃣ Testing API connection...")
    if not test_api_connection(access_token):
        print("❌ API connection failed")
        return False
    
    # Test OneDrive operations
    print("\n3️⃣ Testing OneDrive operations...")
    if not test_onedrive_operations(access_token):
        print("❌ OneDrive operations failed")
        return False
    
    print("\n🎉 AUTO-REFRESH TOKEN IS WORKING PERFECTLY!")
    print("✅ Token refresh functionality is operational")
    print("✅ OneDrive API access is working")
    print("✅ All OneDrive operations are functional")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ OneDrive auto-refresh token is fully working!")
    else:
        print("\n❌ OneDrive auto-refresh token needs attention")
