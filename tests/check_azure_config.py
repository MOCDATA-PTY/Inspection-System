#!/usr/bin/env python3
"""
Check Azure App Configuration for OneDrive
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def check_azure_config():
    """Check Azure app configuration."""
    print("🔍 Checking Azure App Configuration")
    print("=" * 50)
    
    print(f"✅ Client ID: {settings.ONEDRIVE_CLIENT_ID}")
    print(f"✅ Client Secret: {'*' * len(settings.ONEDRIVE_CLIENT_SECRET) if settings.ONEDRIVE_CLIENT_SECRET else 'Not set'}")
    print(f"✅ Redirect URI: {settings.ONEDRIVE_REDIRECT_URI}")
    print(f"✅ OneDrive Enabled: {getattr(settings, 'ONEDRIVE_ENABLED', False)}")
    
    print("\n📋 Required Azure App Configuration:")
    print("1. App Registration in Azure Portal")
    print("2. Redirect URI: http://localhost:8000/onedrive/callback")
    print("3. API Permissions: Files.ReadWrite.All")
    print("4. Supported account types: Personal Microsoft accounts only")
    print("5. Client Secret configured")
    
    print("\n🔧 Common Issues:")
    print("- Missing API permissions")
    print("- Wrong redirect URI")
    print("- App not configured for personal accounts")
    print("- Client secret expired or invalid")
    
    print("\n💡 Next Steps:")
    print("1. Go to Azure Portal > App Registrations")
    print("2. Find your app: " + settings.ONEDRIVE_CLIENT_ID)
    print("3. Check API Permissions tab")
    print("4. Ensure Files.ReadWrite.All is granted")
    print("5. Check Authentication tab for redirect URI")
    print("6. Verify Client Secret is valid")

if __name__ == "__main__":
    check_azure_config()
