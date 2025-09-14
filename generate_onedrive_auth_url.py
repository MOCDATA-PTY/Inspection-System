#!/usr/bin/env python3
"""
Generate OneDrive Authorization URL with Refresh Token Support
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def generate_onedrive_auth_url():
    """Generate OneDrive authorization URL with refresh token support."""
    print("🔐 OneDrive Authorization URL Generator")
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
        
        # Generate authorization URL with refresh token support
        auth_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize"
        auth_params = {
            'client_id': settings.ONEDRIVE_CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': 'Files.ReadWrite.All',
            'response_mode': 'query',
            'prompt': 'consent'  # This ensures we get a refresh token
        }
        
        # Build the authorization URL
        auth_url_with_params = f"{auth_url}?{'&'.join([f'{k}={v}' for k, v in auth_params.items()])}"
        
        print("\n🔗 Authorization URL (with refresh token support):")
        print(auth_url_with_params)
        print("\n📋 Instructions:")
        print("1. Copy and paste the URL above into your browser")
        print("2. Sign in with your Microsoft account")
        print("3. Grant permissions to the app")
        print("4. You'll be redirected to localhost:8000 with the authorization code")
        print("5. The callback will automatically exchange the code for tokens with refresh token")
        print("\n💡 This URL includes 'prompt=consent' to ensure you get a refresh token")
        print("💡 The refresh token will allow the service to automatically renew access")
        
        return True
            
    except Exception as e:
        print(f"❌ URL generation failed with error: {e}")
        return False

if __name__ == "__main__":
    success = generate_onedrive_auth_url()
    if success:
        print("\n✅ Authorization URL generated successfully!")
        print("🌐 Visit the URL above to authenticate with refresh token support")
    else:
        print("\n❌ Failed to generate authorization URL")
