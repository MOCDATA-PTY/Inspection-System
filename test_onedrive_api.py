#!/usr/bin/env python
"""
Test OneDrive API connection with existing tokens
"""
import os
import sys
import django
import json
import requests
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def main():
    print("🔗 TESTING ONEDRIVE API CONNECTION")
    print("=" * 40)
    
    # Load tokens
    token_file = os.path.join(os.path.dirname(__file__), 'onedrive_tokens.json')
    if not os.path.exists(token_file):
        print("❌ No tokens file found")
        return
    
    with open(token_file, 'r') as f:
        tokens = json.load(f)
    
    access_token = tokens.get('access_token')
    expires_at = tokens.get('expires_at', 0)
    
    print(f"✅ Tokens loaded successfully")
    print(f"✅ Token type: {tokens.get('token_type', 'Unknown')}")
    print(f"✅ Expires at: {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if token is expired
    current_time = datetime.now().timestamp()
    if current_time >= expires_at:
        print("❌ Token has expired - need to refresh")
        return
    
    print(f"✅ Token is still valid")
    
    # Test OneDrive API connection
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Get user info
    print(f"\n🔍 Testing user info...")
    try:
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User: {user_data.get('displayName', 'Unknown')}")
            print(f"✅ Email: {user_data.get('mail', 'Unknown')}")
        else:
            print(f"❌ User info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User info error: {e}")
    
    # Test 2: Get OneDrive root
    print(f"\n🔍 Testing OneDrive access...")
    try:
        response = requests.get('https://graph.microsoft.com/v1.0/me/drive/root', headers=headers)
        if response.status_code == 200:
            drive_data = response.json()
            print(f"✅ OneDrive accessible")
            print(f"✅ Drive name: {drive_data.get('name', 'Unknown')}")
            print(f"✅ Drive ID: {drive_data.get('id', 'Unknown')[:20]}...")
        else:
            print(f"❌ OneDrive access failed: {response.status_code}")
    except Exception as e:
        print(f"❌ OneDrive access error: {e}")
    
    # Test 3: List root items
    print(f"\n🔍 Testing file listing...")
    try:
        response = requests.get('https://graph.microsoft.com/v1.0/me/drive/root/children', headers=headers)
        if response.status_code == 200:
            items = response.json().get('value', [])
            print(f"✅ Found {len(items)} items in OneDrive root")
            for item in items[:5]:  # Show first 5 items
                print(f"   - {item.get('name', 'Unknown')} ({item.get('folder', {}).get('childCount', 0)} items)")
        else:
            print(f"❌ File listing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ File listing error: {e}")
    
    print(f"\n🎉 OneDrive connection test complete!")

if __name__ == "__main__":
    main()
