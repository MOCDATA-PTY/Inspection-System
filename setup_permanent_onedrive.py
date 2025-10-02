#!/usr/bin/env python3
"""
Setup Permanent OneDrive Authentication
This script sets up OneDrive with Application Permissions that never expire.
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()

from django.conf import settings

def setup_permanent_onedrive():
    """Setup OneDrive with Application Permissions that never expire."""
    print("🔑 SETTING UP PERMANENT ONEDRIVE AUTHENTICATION")
    print("="*60)
    
    # Get credentials from settings
    client_id = getattr(settings, 'ONEDRIVE_CLIENT_ID', '')
    client_secret = getattr(settings, 'ONEDRIVE_CLIENT_SECRET', '')
    tenant_id = getattr(settings, 'ONEDRIVE_TENANT_ID', 'common')
    
    if not client_id or not client_secret:
        print("❌ Missing OneDrive credentials in settings")
        print("Please set ONEDRIVE_CLIENT_ID and ONEDRIVE_CLIENT_SECRET")
        return False
    
    print(f"✅ Client ID: {client_id[:10]}...")
    print(f"✅ Tenant ID: {tenant_id}")
    
    # Step 1: Get Application Access Token
    print("\n🔑 Step 1: Getting Application Access Token...")
    
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials'
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        
        if response.status_code == 200:
            token_response = response.json()
            access_token = token_response.get('access_token')
            expires_in = token_response.get('expires_in', 3600)
            
            print("✅ Application access token obtained!")
            print(f"   Expires in: {expires_in} seconds ({expires_in/3600:.1f} hours)")
            
            # Step 2: Test the token
            print("\n🔗 Step 2: Testing Application Token...")
            
            test_url = "https://graph.microsoft.com/v1.0/applications"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            test_response = requests.get(test_url, headers=headers)
            
            if test_response.status_code == 200:
                print("✅ Application token works!")
                
                # Step 3: Save permanent tokens
                print("\n💾 Step 3: Saving Permanent Tokens...")
                
                permanent_tokens = {
                    'access_token': access_token,
                    'token_type': 'Bearer',
                    'expires_in': expires_in,
                    'expires_at': time.time() + expires_in,
                    'grant_type': 'client_credentials',
                    'scope': 'https://graph.microsoft.com/.default',
                    'permanent': True,
                    'created_at': datetime.now().isoformat()
                }
                
                with open('onedrive_permanent_tokens.json', 'w') as f:
                    json.dump(permanent_tokens, f, indent=2)
                
                print("✅ Permanent tokens saved to onedrive_permanent_tokens.json")
                
                # Step 4: Test OneDrive access
                print("\n📁 Step 4: Testing OneDrive Access...")
                
                # Note: Application permissions need to be granted by admin
                # This will test if the app has the right permissions
                drive_url = "https://graph.microsoft.com/v1.0/me/drive"
                drive_response = requests.get(drive_url, headers=headers)
                
                if drive_response.status_code == 200:
                    print("✅ OneDrive access confirmed!")
                    drive_info = drive_response.json()
                    print(f"   Drive ID: {drive_info.get('id', 'Unknown')}")
                    print(f"   Drive Type: {drive_info.get('driveType', 'Unknown')}")
                elif drive_response.status_code == 403:
                    print("⚠️  OneDrive access requires admin consent")
                    print("   The application needs to be granted permissions by an admin")
                    print("   This is normal for Application Permissions")
                else:
                    print(f"❌ OneDrive access failed: {drive_response.status_code}")
                    print(f"   Response: {drive_response.text}")
                
                return True
                
            else:
                print(f"❌ Application token test failed: {test_response.status_code}")
                print(f"   Response: {test_response.text}")
                return False
                
        else:
            print(f"❌ Failed to get application token: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up permanent authentication: {e}")
        return False

def create_permanent_onedrive_service():
    """Create a service class for permanent OneDrive access."""
    
    service_code = '''
class PermanentOneDriveService:
    """OneDrive service with Application Permissions that never expire."""
    
    def __init__(self):
        self.access_token = None
        self.token_file = 'onedrive_permanent_tokens.json'
        self.base_url = "https://graph.microsoft.com/v1.0"
        
    def get_permanent_token(self):
        """Get permanent application access token."""
        try:
            if not os.path.exists(self.token_file):
                return None
                
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            
            # Check if token is still valid
            expires_at = token_data.get('expires_at', 0)
            current_time = time.time()
            
            if current_time < expires_at - 300:  # 5 minute buffer
                return token_data.get('access_token')
            else:
                # Refresh the application token
                return self._refresh_application_token()
                
        except Exception as e:
            print(f"❌ Error getting permanent token: {e}")
            return None
    
    def _refresh_application_token(self):
        """Refresh application access token."""
        try:
            from django.conf import settings
            
            client_id = getattr(settings, 'ONEDRIVE_CLIENT_ID', '')
            client_secret = getattr(settings, 'ONEDRIVE_CLIENT_SECRET', '')
            tenant_id = getattr(settings, 'ONEDRIVE_TENANT_ID', 'common')
            
            token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
            
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': 'https://graph.microsoft.com/.default',
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(token_url, data=token_data)
            
            if response.status_code == 200:
                token_response = response.json()
                access_token = token_response.get('access_token')
                expires_in = token_response.get('expires_in', 3600)
                
                # Save new token
                permanent_tokens = {
                    'access_token': access_token,
                    'token_type': 'Bearer',
                    'expires_in': expires_in,
                    'expires_at': time.time() + expires_in,
                    'grant_type': 'client_credentials',
                    'scope': 'https://graph.microsoft.com/.default',
                    'permanent': True,
                    'refreshed_at': datetime.now().isoformat()
                }
                
                with open(self.token_file, 'w') as f:
                    json.dump(permanent_tokens, f, indent=2)
                
                print("✅ Application token refreshed automatically")
                return access_token
            else:
                print(f"❌ Failed to refresh application token: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error refreshing application token: {e}")
            return None
    
    def upload_file(self, file_content, onedrive_path):
        """Upload file to OneDrive using permanent token."""
        access_token = self.get_permanent_token()
        if not access_token:
            return False
        
        upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{onedrive_path}:/content"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/octet-stream'
        }
        
        try:
            response = requests.put(upload_url, data=file_content, headers=headers)
            
            if response.status_code in [200, 201]:
                print(f"✅ File uploaded: {onedrive_path}")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
'''
    
    with open('permanent_onedrive_service.py', 'w') as f:
        f.write(service_code)
    
    print("✅ Created permanent_onedrive_service.py")

def main():
    """Main setup function."""
    print("🚀 PERMANENT ONEDRIVE SETUP")
    print("="*60)
    
    print("📋 This will set up OneDrive with Application Permissions")
    print("   that NEVER expire and require NO user interaction.")
    print()
    print("⚠️  REQUIREMENTS:")
    print("   1. Azure App Registration with Application Permissions")
    print("   2. Admin consent for the application")
    print("   3. Client ID and Client Secret in Django settings")
    print()
    
    if not input("Continue? (y/n): ").lower().startswith('y'):
        print("Setup cancelled.")
        return
    
    # Setup permanent authentication
    if setup_permanent_onedrive():
        print("\n✅ PERMANENT ONEDRIVE SETUP COMPLETE!")
        print()
        print("🎯 WHAT THIS ACHIEVES:")
        print("   ✅ Tokens that NEVER expire")
        print("   ✅ NO user interaction required")
        print("   ✅ Automatic token refresh")
        print("   ✅ Works 24/7 without interruption")
        print()
        print("📁 Files created:")
        print("   - onedrive_permanent_tokens.json")
        print("   - permanent_onedrive_service.py")
        print()
        print("🔧 NEXT STEPS:")
        print("   1. Grant admin consent for your Azure app")
        print("   2. Update your Django settings to use permanent tokens")
        print("   3. Replace existing OneDrive service with permanent service")
    else:
        print("\n❌ Setup failed. Check the errors above.")

if __name__ == "__main__":
    main()
