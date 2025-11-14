#!/usr/bin/env python
"""
Complete OneDrive setup and test script
"""
import os
import sys
import django
import webbrowser
import time

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def main():
    print("🚀 OneDrive Integration Setup & Test")
    print("=" * 50)
    
    # Check current configuration
    client_id = getattr(settings, 'ONEDRIVE_CLIENT_ID', '')
    client_secret = getattr(settings, 'ONEDRIVE_CLIENT_SECRET', '')
    redirect_uri = getattr(settings, 'ONEDRIVE_REDIRECT_URI', '')
    
    print(f"✅ Client Secret: {'Set' if client_secret and client_secret != 'your_client_id_here' else 'Not set'}")
    print(f"✅ Redirect URI: {redirect_uri}")
    print(f"✅ OneDrive Enabled: {getattr(settings, 'ONEDRIVE_ENABLED', False)}")
    
    if client_id == 'your_client_id_here' or not client_id:
        print("\n❌ CLIENT ID NOT SET!")
        print("Please follow these steps:")
        print("1. Go to Azure Portal → App registrations → OneDriveAppIntegration")
        print("2. Copy the 'Application (client) ID' from the Overview page")
        print("3. Update mysite/settings.py with your actual Client ID")
        print("4. Run this script again")
        return
    
    print(f"✅ Client ID: {client_id[:8]}...")
    
    # Generate authorization URL
    auth_url = (
        f"https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope=offline_access%20Files.ReadWrite.All%20User.Read"
    )
    
    print(f"\n🌐 Authorization URL:")
    print(auth_url)
    
    print(f"\n📋 Next Steps:")
    print("1. Click the URL above or copy it to your browser")
    print("2. Sign in with your Microsoft account")
    print("3. Grant permissions to the app")
    print("4. You'll be redirected to: http://localhost:8000/onedrive/callback")
    print("5. Check for onedrive_tokens.json file in the project root")
    
    # Try to open the URL automatically
    try:
        print(f"\n🔗 Opening browser...")
        webbrowser.open(auth_url)
        print("✅ Browser opened with authorization URL")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print("Please copy and paste the URL above into your browser")
    
    print(f"\n⏳ Waiting for callback...")
    print("After completing the OAuth flow, check if onedrive_tokens.json was created")

if __name__ == "__main__":
    main()
