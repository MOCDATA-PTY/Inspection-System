#!/usr/bin/env python3
"""
Test OneDrive Authentication with Time Check
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

def test_onedrive_auth():
    """Test OneDrive authentication with saved tokens."""
    print("🧪 Testing OneDrive Authentication")
    print("=" * 50)
    
    try:
        # Load saved tokens
        token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
        
        if not os.path.exists(token_file):
            print("❌ No OneDrive tokens found")
            return False
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        access_token = token_data.get('access_token')
        expires_at = token_data.get('expires_at', 0)
        current_time = datetime.now().timestamp()
        
        if not access_token:
            print("❌ No access token found")
            return False
        
        print(f"✅ Access token found")
        print(f"⏰ Current time: {current_time}")
        print(f"⏰ Token expires at: {expires_at}")
        print(f"⏰ Time until expiry: {expires_at - current_time:.1f} seconds")
        
        if current_time > expires_at:
            print("❌ Token has expired!")
            return False
        
        # Test the token
        test_url = "https://graph.microsoft.com/v1.0/me/drive"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("🔍 Testing token with Microsoft Graph API...")
        response = requests.get(test_url, headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print("✅ OneDrive authentication successful!")
            print(f"🚗 Drive ID: {user_info.get('id', 'Unknown')}")
            print(f"📁 Drive Type: {user_info.get('driveType', 'Unknown')}")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_onedrive_auth()
    if success:
        print("\n🎉 OneDrive authentication is working!")
        print("🚀 You can now start the OneDrive Direct Upload Service")
    else:
        print("\n❌ OneDrive authentication failed")
