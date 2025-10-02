#!/usr/bin/env python
"""
Instructions for creating a new OneDrive app for company account
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
    print("🗑️  DELETING OLD APP & CREATING NEW ONE")
    print("=" * 50)
    print("Account: anthony.penzes@fsa-pty.co.za")
    
    print(f"\n🗑️  STEP 1: Delete Current App")
    print("1. Go to: https://portal.azure.com")
    print("2. Navigate to: Azure Active Directory → App registrations")
    print("3. Find: OneDriveAppIntegration")
    print("4. Click on it → Overview")
    print("5. Click 'Delete' button")
    print("6. Confirm deletion")
    
    print(f"\n🆕 STEP 2: Create New App")
    print("1. Click 'New registration'")
    print("2. Name: OneDriveAppIntegration")
    print("3. Supported account types: 'Accounts in any organizational directory (Any Microsoft Entra ID tenant - Multitenant)'")
    print("4. Redirect URI: Web → http://localhost:8000/onedrive/callback")
    print("5. Click 'Register'")
    
    print(f"\n🔧 STEP 3: Configure New App")
    print("1. Go to 'Certificates & secrets'")
    print("2. Click 'New client secret'")
    print("3. Description: OneDriveAppIntegration")
    print("4. Expires: 24 months")
    print("5. Click 'Add'")
    print("6. COPY THE SECRET VALUE IMMEDIATELY")
    
    print(f"\n🔧 STEP 4: Add API Permissions")
    print("1. Go to 'API permissions'")
    print("2. Click 'Add a permission'")
    print("3. Select 'Microsoft Graph'")
    print("4. Choose 'Delegated permissions'")
    print("5. Add these permissions:")
    print("   - Files.ReadWrite.All")
    print("   - offline_access")
    print("   - User.Read")
    print("6. Click 'Add permissions'")
    print("7. Click 'Grant admin consent' (if required)")
    
    print(f"\n📋 STEP 5: Get New Credentials")
    print("1. Go to 'Overview'")
    print("2. Copy 'Application (client) ID'")
    print("3. Copy the 'Client secret value' from step 3")
    
    print(f"\n🔧 STEP 6: Update Settings")
    print("After getting new credentials, I'll update your settings with:")
    print("- ONEDRIVE_CLIENT_ID = 'your-new-client-id'")
    print("- ONEDRIVE_CLIENT_SECRET = 'your-new-secret'")
    print("- ONEDRIVE_REDIRECT_URI = 'http://localhost:8000/onedrive/callback'")
    
    print(f"\n✅ STEP 7: Test OAuth Flow")
    print("After updating settings, I'll generate the correct authorization URL")
    print("and test the complete OAuth flow with your company account.")
    
    print(f"\n🚀 Ready to start? Let me know when you've created the new app!")

if __name__ == "__main__":
    main()
