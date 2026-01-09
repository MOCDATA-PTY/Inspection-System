#!/usr/bin/env python
"""
OneDrive setup for company/work accounts
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
    print("🏢 OneDrive Integration for Company Account")
    print("=" * 50)
    print("Account: anthony.penzes@fsa-pty.co.za")
    
    # Check current configuration
    client_id = getattr(settings, 'ONEDRIVE_CLIENT_ID', '')
    client_secret = getattr(settings, 'ONEDRIVE_CLIENT_SECRET', '')
    redirect_uri = getattr(settings, 'ONEDRIVE_REDIRECT_URI', '')
    
    print(f"✅ Client ID: {client_id[:8]}...")
    print(f"✅ Client Secret: {'Set' if client_secret else 'Not set'}")
    print(f"✅ Redirect URI: {redirect_uri}")
    
    # Generate authorization URL for work/school accounts
    auth_url = (
        f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope=offline_access%20Files.ReadWrite.All%20User.Read"
        f"&prompt=select_account"
    )
    
    print(f"\n🌐 Authorization URL for Company Account:")
    print(auth_url)
    
    print(f"\n📋 Next Steps:")
    print("1. Click the URL above or copy it to your browser")
    print("2. Sign in with: anthony.penzes@fsa-pty.co.za")
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
    
    print(f"\n⚠️  IMPORTANT: Azure App Registration Update Needed")
    print("Your Azure app needs to support work/school accounts:")
    print("1. Go to Azure Portal → App registrations → OneDriveAppIntegration")
    print("2. Go to Authentication")
    print("3. Under 'Supported account types', select:")
    print("   'Accounts in any organizational directory (Any Microsoft Entra ID tenant - Multitenant)'")
    print("4. Save the changes")
    print("5. Then use the authorization URL above")

if __name__ == "__main__":
    main()
