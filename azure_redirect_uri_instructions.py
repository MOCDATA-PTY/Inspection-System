#!/usr/bin/env python3
"""
Azure App Registration Redirect URI Configuration Instructions
============================================================

This script provides instructions for updating the Azure app registration
to include the correct redirect URI for OneDrive authentication.
"""

def print_instructions():
    print("🔧 Azure App Registration Redirect URI Fix")
    print("=" * 50)
    print()
    print("❌ CURRENT ERROR:")
    print("   The redirect URI 'http://127.0.0.1:8000/onedrive/callback/'")
    print("   is not registered in your Azure app 'e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f'")
    print()
    print("✅ SOLUTION:")
    print("   Add the following redirect URI to your Azure app registration:")
    print()
    print("   📋 REDIRECT URI TO ADD:")
    print("   http://127.0.0.1:8000/onedrive/callback/")
    print()
    print("   📋 ADDITIONAL REDIRECT URIs (recommended):")
    print("   http://localhost:8000/onedrive/callback/")
    print("   http://localhost:8000/onedrive/callback")
    print("   http://127.0.0.1:8000/onedrive/callback")
    print()
    print("🔧 STEPS TO FIX:")
    print("1. Go to Azure Portal: https://portal.azure.com")
    print("2. Navigate to 'Azure Active Directory'")
    print("3. Click 'App registrations'")
    print("4. Find your app: 'e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f'")
    print("5. Click on the app name")
    print("6. Click 'Authentication' in the left menu")
    print("7. Under 'Redirect URIs', click 'Add URI'")
    print("8. Add: http://127.0.0.1:8000/onedrive/callback/")
    print("9. Click 'Save'")
    print()
    print("🔧 ALTERNATIVE: Use existing redirect URI")
    print("   If you prefer to use the existing redirect URI, update the settings:")
    print("   Change ONEDRIVE_REDIRECT_URI to: http://localhost:8000/onedrive/callback")
    print()
    print("📝 CURRENT APP DETAILS:")
    print("   App ID: e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f")
    print("   Current Redirect URI: http://localhost:8000/onedrive/callback")
    print("   Required Redirect URI: http://127.0.0.1:8000/onedrive/callback/")
    print()
    print("✅ After updating the redirect URI, run the OneDrive authentication again.")

if __name__ == "__main__":
    print_instructions()
