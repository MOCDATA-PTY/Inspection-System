#!/usr/bin/env python3
"""
Test Direct OneDrive Upload with Existing Auth Code
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

def test_direct_onedrive_upload_with_code():
    """Test uploading directly to OneDrive using the existing auth code."""
    print("🚀 Testing Direct OneDrive Upload with Auth Code")
    print("=" * 60)
    
    try:
        # Check if OneDrive is enabled
        if not getattr(settings, 'ONEDRIVE_ENABLED', False):
            print("❌ OneDrive integration is not enabled in settings")
            return False
        
        print(f"✅ OneDrive enabled: {settings.ONEDRIVE_ENABLED}")
        print(f"✅ Client ID: {settings.ONEDRIVE_CLIENT_ID}")
        print(f"✅ OneDrive folder: {getattr(settings, 'ONEDRIVE_FOLDER', 'Legal-System-Media')}")
        
        # Use the authorization code we received
        auth_code = "M.C554_BAY.2.U.8d5e95a5-0868-8ead-f873-598f0c1ca38c"
        print(f"✅ Using existing auth code: {auth_code}")
        
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
            if access_token:
                print("✅ Access token received successfully!")
                
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
                
                # Upload directly to OneDrive
                filename = f"direct_test_inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                onedrive_path = f"{getattr(settings, 'ONEDRIVE_FOLDER', 'Legal-System-Media')}/test/{filename}"
                
                print(f"\n📤 Uploading directly to OneDrive: {onedrive_path}")
                
                upload_success = upload_to_onedrive_direct(test_content, onedrive_path, access_token)
                
                if upload_success:
                    print("✅ File uploaded directly to OneDrive successfully!")
                    print(f"📁 File saved to OneDrive: {onedrive_path}")
                    print(f"📄 File name: {filename}")
                    print("🎉 Direct OneDrive upload is working!")
                    return True
                else:
                    print("❌ Direct OneDrive upload failed")
                    return False
            else:
                print("❌ No access token received")
                return False
        else:
            print(f"❌ Token exchange failed: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def upload_to_onedrive_direct(content, onedrive_path, access_token):
    """Upload content directly to OneDrive without local file."""
    try:
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
    print("🧪 Direct OneDrive Upload Test (with Auth Code)")
    print("=" * 60)
    
    success = test_direct_onedrive_upload_with_code()
    
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
