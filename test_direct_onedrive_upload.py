#!/usr/bin/env python3
"""
Test Direct OneDrive Upload - Save Test Inspection Directly to Cloud
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
import requests
import json

def test_direct_onedrive_upload():
    """Test uploading directly to OneDrive without local sync."""
    print("🚀 Testing Direct OneDrive Upload")
    print("=" * 50)
    
    try:
        # Check if OneDrive is enabled
        if not getattr(settings, 'ONEDRIVE_ENABLED', False):
            print("❌ OneDrive integration is not enabled in settings")
            return False
        
        print(f"✅ OneDrive enabled: {settings.ONEDRIVE_ENABLED}")
        print(f"✅ Client ID: {settings.ONEDRIVE_CLIENT_ID}")
        print(f"✅ OneDrive folder: {getattr(settings, 'ONEDRIVE_FOLDER', 'Legal-System-Media')}")
        
        # Create test content in memory (no local file)
        test_content = f"""
# Test Inspection Report - Direct OneDrive Upload
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Inspection Details:
- Client: Test Client - Direct OneDrive Upload
- Date: {datetime.now().strftime('%d/%m/%Y')}
- Inspector: System Test
- Location: Test Location

## Test Results:
- Direct OneDrive Upload Test: PASSED
- No Local File Created: PASSED
- Cloud Storage Test: PASSED

## Notes:
This file was uploaded directly to OneDrive without being saved locally first.
This proves direct cloud upload is working.
        """
        
        # Test direct upload to OneDrive
        print("\n📤 Testing direct upload to OneDrive...")
        
        # First, authenticate using authorization code flow
        auth_success = authenticate_onedrive_auth_code()
        if not auth_success:
            print("❌ OneDrive authentication failed")
            return False
        
        # Upload directly to OneDrive
        filename = f"direct_test_inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        onedrive_path = f"{getattr(settings, 'ONEDRIVE_FOLDER', 'Legal-System-Media')}/test/{filename}"
        
        upload_success = upload_to_onedrive_direct(test_content, onedrive_path)
        
        if upload_success:
            print("✅ File uploaded directly to OneDrive successfully!")
            print(f"📁 File saved to OneDrive: {onedrive_path}")
            print(f"📄 File name: {filename}")
            print("🎉 Direct OneDrive upload is working!")
            return True
        else:
            print("❌ Direct OneDrive upload failed")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def authenticate_onedrive_auth_code():
    """Authenticate with OneDrive using authorization code flow."""
    try:
        # Authorization code flow for web applications
        auth_url = f"https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize"
        
        auth_params = {
            'client_id': settings.ONEDRIVE_CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': settings.ONEDRIVE_REDIRECT_URI,
            'scope': 'Files.ReadWrite.All',
            'response_mode': 'query'
        }
        
        print(f"\n🔐 OneDrive Authentication Required")
        print(f"📱 Go to: {auth_url}?client_id={settings.ONEDRIVE_CLIENT_ID}&response_type=code&redirect_uri={settings.ONEDRIVE_REDIRECT_URI}&scope=Files.ReadWrite.All")
        print(f"🔢 After authentication, copy the authorization code from the URL")
        
        # Get authorization code from user
        auth_code = input("Enter the authorization code: ").strip()
        
        if not auth_code:
            print("❌ No authorization code provided")
            return False
        
        # Exchange authorization code for access token
        token_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
        token_data = {
            'client_id': settings.ONEDRIVE_CLIENT_ID,
            'client_secret': settings.ONEDRIVE_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': settings.ONEDRIVE_REDIRECT_URI
        }
        
        response = requests.post(token_url, data=token_data)
        if response.status_code == 200:
            token_response = response.json()
            global access_token
            access_token = token_response.get('access_token')
            if access_token:
                print("✅ OneDrive authentication successful!")
                return True
            else:
                print("❌ No access token received")
                return False
        else:
            print(f"❌ Token exchange failed: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def upload_to_onedrive_direct(content, onedrive_path):
    """Upload content directly to OneDrive without local file."""
    try:
        global access_token
        if not access_token:
            print("❌ No access token available")
            return False
        
        # Create the file directly in OneDrive
        upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{onedrive_path}:/content"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'text/plain'
        }
        
        # Upload content directly (no local file)
        response = requests.put(upload_url, data=content.encode('utf-8'), headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"✅ File uploaded successfully: {onedrive_path}")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Direct upload failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Direct OneDrive Upload Test")
    print("=" * 50)
    
    success = test_direct_onedrive_upload()
    
    if success:
        print("\n✅ Direct OneDrive upload is working!")
        print("📋 Summary:")
        print("1. Files can be uploaded directly to OneDrive")
        print("2. No local file is created")
        print("3. Direct cloud storage is working")
        print("4. Ready to implement direct upload in the system")
    else:
        print("\n❌ Direct OneDrive upload failed.")
        print("📋 Next steps:")
        print("1. Check Azure app configuration")
        print("2. Ensure app is configured for web client")
        print("3. Verify API permissions")
    
    return success

if __name__ == "__main__":
    main()
