#!/usr/bin/env python3
"""
Set OneDrive Client Secret and Test Connection
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def set_client_secret():
    """Set the client secret temporarily."""
    print("🔐 SETTING ONEDRIVE CLIENT SECRET")
    print("=" * 50)
    
    # Get client secret from user input
    print("Please enter your OneDrive client secret from Azure:")
    print("(You can find this in Azure Portal > App Registrations > Your App > Certificates & secrets)")
    print()
    
    client_secret = input("Enter client secret: ").strip()
    
    if not client_secret:
        print("❌ No client secret provided")
        return False
    
    # Set environment variable
    os.environ['ONEDRIVE_CLIENT_SECRET'] = client_secret
    
    print(f"✅ Client secret set (length: {len(client_secret)} characters)")
    
    # Test the configuration
    print("\n🧪 Testing configuration...")
    from django.conf import settings
    
    # Reload settings to get the new secret
    settings._wrapped = None
    from django.conf import settings
    
    if settings.ONEDRIVE_CLIENT_SECRET:
        print("✅ Client secret loaded successfully")
        return True
    else:
        print("❌ Failed to load client secret")
        return False

def test_connection():
    """Test OneDrive connection with the new secret."""
    print("\n🔍 TESTING ONEDRIVE CONNECTION")
    print("=" * 40)
    
    try:
        from main.services.onedrive_direct_service import OneDriveDirectService
        
        service = OneDriveDirectService()
        
        # Try to refresh the token
        print("🔄 Attempting to refresh expired token...")
        success = service.refresh_access_token()
        
        if success:
            print("✅ Token refreshed successfully!")
            
            # Test connection
            print("🔍 Testing connection...")
            if service.test_connection():
                print("✅ OneDrive connection successful!")
                print("🎉 Everything is working!")
                return True
            else:
                print("❌ Connection test failed")
                return False
        else:
            print("❌ Token refresh failed")
            print("💡 You may need to re-authenticate")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main function."""
    print("🚀 ONEDRIVE SETUP AND TEST")
    print("=" * 50)
    print("Account: anthony.penzes@fsa-pty.co.za")
    print()
    
    # Set client secret
    if not set_client_secret():
        return
    
    # Test connection
    if test_connection():
        print("\n🎉 SUCCESS! OneDrive is working!")
        print("✅ Client secret is set")
        print("✅ Token is refreshed")
        print("✅ Connection is working")
        print("\n💡 To make this permanent, update your settings.py file")
    else:
        print("\n❌ Setup failed")
        print("💡 You may need to:")
        print("1. Check your client secret")
        print("2. Verify Azure app configuration")
        print("3. Re-authenticate with OneDrive")

if __name__ == "__main__":
    main()
