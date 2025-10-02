#!/usr/bin/env python3
"""
Setup OneDrive Client Secret for Business Account
This script will help you set up the client secret that was working last night
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def main():
    print("🔐 ONEDRIVE CLIENT SECRET SETUP")
    print("=" * 50)
    print("Account: anthony.penzes@fsa-pty.co.za")
    print("Since it worked last night, we need to restore the client secret")
    
    print(f"\n📋 Current Configuration:")
    print(f"✅ Client ID: {settings.ONEDRIVE_CLIENT_ID}")
    print(f"❌ Client Secret: {'Set' if settings.ONEDRIVE_CLIENT_SECRET else 'Not set'}")
    print(f"✅ Redirect URI: {settings.ONEDRIVE_REDIRECT_URI}")
    
    print(f"\n🔧 TO GET YOUR CLIENT SECRET:")
    print("1. Go to: https://portal.azure.com")
    print("2. Navigate to: Azure Active Directory → App registrations")
    print("3. Find your app: OneDriveAppIntegration")
    print("4. Click on it → Certificates & secrets")
    print("5. If you see an existing secret, copy its VALUE")
    print("6. If no secret exists, click 'New client secret'")
    print("7. Add description: 'OneDrive Integration'")
    print("8. Set expiration: 24 months")
    print("9. Click 'Add' and copy the VALUE")
    
    print(f"\n💾 TO SET THE CLIENT SECRET:")
    print("Option 1 - Set environment variable (temporary):")
    print("  set ONEDRIVE_CLIENT_SECRET=your_secret_here")
    print("\nOption 2 - Update settings.py (permanent):")
    print("  Change line 181 in mysite/settings.py from:")
    print("  ONEDRIVE_CLIENT_SECRET = env('ONEDRIVE_CLIENT_SECRET', default='')")
    print("  to:")
    print("  ONEDRIVE_CLIENT_SECRET = env('ONEDRIVE_CLIENT_SECRET', default='your_secret_here')")
    
    print(f"\n🧪 AFTER SETTING THE SECRET:")
    print("Run: python test_onedrive_business_account.py")
    print("This will test the connection and refresh the expired token")
    
    print(f"\n⚠️  IMPORTANT:")
    print("The client secret is sensitive information!")
    print("Don't commit it to version control.")
    print("Use environment variables for production.")

if __name__ == "__main__":
    main()
