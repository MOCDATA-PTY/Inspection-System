#!/usr/bin/env python
"""
Test OneDrive connection with current credentials
"""
import os
import sys
import django
import webbrowser

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def main():
    print("🔗 TESTING ONEDRIVE CONNECTION")
    print("=" * 40)
    print("Account: anthony.penzes@fsa-pty.co.za")
    
    # Check current configuration
    client_id = getattr(settings, 'ONEDRIVE_CLIENT_ID', '')
    client_secret = getattr(settings, 'ONEDRIVE_CLIENT_SECRET', '')
    redirect_uri = getattr(settings, 'ONEDRIVE_REDIRECT_URI', '')
    
    print(f"✅ Client ID: {client_id[:8]}...")
    print(f"✅ Client Secret: {'Set' if client_secret else 'Not set'}")
    print(f"✅ Redirect URI: {redirect_uri}")
    
    # Generate authorization URL
    auth_url = (
        f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope=offline_access%20Files.ReadWrite.All%20User.Read"
        f"&prompt=select_account"
    )
    
    print(f"\n🌐 OneDrive Authorization URL:")
    print(auth_url)
    
    print(f"\n📋 Steps to Connect:")
    print("1. Click the URL above")
    print("2. Sign in with: anthony.penzes@fsa-pty.co.za")
    print("3. If you see admin consent error, contact your IT admin")
    print("4. If successful, you'll be redirected to the callback")
    print("5. Check for onedrive_tokens.json file")
    
    # Check if tokens already exist
    token_file = os.path.join(os.path.dirname(__file__), 'onedrive_tokens.json')
    if os.path.exists(token_file):
        print(f"\n✅ Found existing tokens file: {token_file}")
        print("OneDrive may already be connected!")
    else:
        print(f"\n❌ No tokens file found - need to complete OAuth flow")
    
    # Try to open the URL
    try:
        print(f"\n🔗 Opening browser...")
        webbrowser.open(auth_url)
        print("✅ Browser opened with authorization URL")
    except Exception as e:
        print(f"⚠️ Could not open browser: {e}")
        print("Please copy and paste the URL above into your browser")

if __name__ == "__main__":
    main()
