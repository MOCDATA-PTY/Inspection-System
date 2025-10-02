#!/usr/bin/env python
"""
Fix Azure app registration for company account
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
    print("🏢 FIXING AZURE APP FOR COMPANY ACCOUNT")
    print("=" * 50)
    print("Account: anthony.penzes@fsa-pty.co.za")
    print("Current Issue: Azure app only supports personal Microsoft accounts")
    
    print(f"\n🔧 STEP 1: Update Azure App Registration")
    print("1. Go to: https://portal.azure.com")
    print("2. Navigate to: Azure Active Directory → App registrations")
    print("3. Find your app: OneDriveAppIntegration")
    print("4. Click on it → Authentication")
    print("5. Under 'Supported account types', change from:")
    print("   ❌ 'Personal Microsoft accounts only'")
    print("   ✅ 'Accounts in any organizational directory (Any Microsoft Entra ID tenant - Multitenant)'")
    print("6. Click 'Save'")
    
    print(f"\n🔧 STEP 2: Update API Permissions")
    print("1. Go to: API permissions")
    print("2. Add these Delegated permissions:")
    print("   - Microsoft Graph → Files.ReadWrite.All")
    print("   - Microsoft Graph → offline_access") 
    print("   - Microsoft Graph → User.Read")
    print("3. Click 'Grant admin consent' (if required by your organization)")
    
    print(f"\n🔧 STEP 3: Test with Company Account")
    print("After updating Azure, use this URL:")
    
    client_id = getattr(settings, 'ONEDRIVE_CLIENT_ID', '')
    redirect_uri = getattr(settings, 'ONEDRIVE_REDIRECT_URI', '')
    
    # Use common endpoint for work/school accounts
    auth_url = (
        f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope=offline_access%20Files.ReadWrite.All%20User.Read"
        f"&prompt=select_account"
    )
    
    print(f"\n🌐 Authorization URL (after Azure update):")
    print(auth_url)
    
    print(f"\n📋 What happens after Azure update:")
    print("1. Sign in with: anthony.penzes@fsa-pty.co.za")
    print("2. Grant permissions to the app")
    print("3. Redirected to: http://localhost:8000/onedrive/callback")
    print("4. onedrive_tokens.json will be created")
    
    print(f"\n⚠️  IMPORTANT:")
    print("Your current Azure app is configured for personal accounts only.")
    print("You MUST update it to support work/school accounts first!")
    print("The error you saw confirms this: 'Application is configured for use by Microsoft Account users only'")

if __name__ == "__main__":
    main()
