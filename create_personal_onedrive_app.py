#!/usr/bin/env python
"""
Create personal Microsoft account OneDrive app as alternative
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
    print("🔧 ALTERNATIVE: Personal Microsoft Account App")
    print("=" * 50)
    print("Since admin consent is required for company account,")
    print("we can create a personal Microsoft account app instead.")
    
    print(f"\n🆕 Create New Personal Account App:")
    print("1. Go to: https://portal.azure.com")
    print("2. Navigate to: Azure Active Directory → App registrations")
    print("3. Click 'New registration'")
    print("4. Name: OneDriveAppIntegration-Personal")
    print("5. Supported account types: 'Personal Microsoft accounts only'")
    print("6. Redirect URI: Web → http://localhost:8000/onedrive/callback")
    print("7. Click 'Register'")
    
    print(f"\n🔧 Configure Personal App:")
    print("1. Go to 'Certificates & secrets'")
    print("2. Click 'New client secret'")
    print("3. Description: OneDriveAppIntegration-Personal")
    print("4. Expires: 24 months")
    print("5. Click 'Add' and COPY THE SECRET")
    
    print(f"\n🔧 Add API Permissions:")
    print("1. Go to 'API permissions'")
    print("2. Click 'Add a permission'")
    print("3. Select 'Microsoft Graph'")
    print("4. Choose 'Delegated permissions'")
    print("5. Add: Files.ReadWrite.All, offline_access, User.Read")
    print("6. Click 'Add permissions'")
    
    print(f"\n📋 Get Credentials:")
    print("1. Go to 'Overview'")
    print("2. Copy 'Application (client) ID'")
    print("3. Copy the 'Client secret value'")
    
    print(f"\n✅ Benefits of Personal Account App:")
    print("✅ No admin consent required")
    print("✅ Works with any Microsoft account")
    print("✅ Same OneDrive functionality")
    print("✅ Can be used by anyone in your organization")
    
    print(f"\n🤔 Which option do you prefer?")
    print("1. Get admin consent for company account")
    print("2. Create personal account app (no admin needed)")

if __name__ == "__main__":
    main()
