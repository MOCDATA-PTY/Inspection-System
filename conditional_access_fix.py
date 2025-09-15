#!/usr/bin/env python3
"""
Fix OneDrive for Company with Conditional Access
"""

import os
import sys
import django
import json
import requests
import webbrowser
import urllib.parse

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def get_company_tenant_id():
    """Get the tenant ID for the company."""
    # For single tenant apps, we need to find the actual tenant ID
    # Let's try to discover it using the company domain
    
    company_domain = "fsa-pty.co.za"
    
    # Try to get tenant info
    try:
        discovery_url = f"https://login.microsoftonline.com/{company_domain}/v2.0/.well-known/openid_configuration"
        response = requests.get(discovery_url)
        if response.status_code == 200:
            print(f"✅ Found tenant configuration for {company_domain}")
            return company_domain
    except:
        pass
    
    # If that doesn't work, we'll need to use the tenant ID directly
    # You'll need to get this from your Azure admin
    return None

def generate_company_auth_url():
    """Generate authorization URL for company account."""
    client_id = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
    redirect_uri = "http://localhost:8000/onedrive/callback"
    
    # For company accounts with conditional access, we need to be more specific
    scopes = [
        'https://graph.microsoft.com/Files.ReadWrite',
        'https://graph.microsoft.com/User.Read',
        'https://graph.microsoft.com/offline_access'
    ]
    
    # Try to get tenant ID
    tenant_id = get_company_tenant_id()
    
    if tenant_id:
        base_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
    else:
        # Use common endpoint but with specific parameters for company accounts
        base_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes),
        'response_mode': 'query',
        'state': 'company_auth',
        'prompt': 'consent',
        'login_hint': 'anthony.penzes@fsa-pty.co.za'  # This helps with company account
    }
    
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return auth_url, tenant_id

def test_token_exchange_with_tenant(auth_code, tenant_id):
    """Test token exchange with specific tenant."""
    client_id = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
    client_secret = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
    redirect_uri = "http://localhost:8000/onedrive/callback"
    
    # Use tenant-specific token endpoint
    if tenant_id:
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    else:
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    
    print(f"Token URL: {token_url}")
    print(f"Token Data: {token_data}")
    
    try:
        response = requests.post(token_url, data=token_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            tokens = response.json()
            print("✅ Token exchange successful!")
            
            # Save tokens
            with open('onedrive_tokens.json', 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print(f"Access Token: {tokens.get('access_token', 'None')[:20]}...")
            print(f"Refresh Token: {tokens.get('refresh_token', 'None')[:20]}...")
            
            # Test API
            print("\n🔗 Testing API connection...")
            api_url = "https://graph.microsoft.com/v1.0/me"
            headers = {
                'Authorization': f'Bearer {tokens["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            api_response = requests.get(api_url, headers=headers)
            if api_response.status_code == 200:
                user_info = api_response.json()
                print("✅ API connection successful!")
                print(f"User: {user_info.get('displayName', 'Unknown')}")
                print(f"Email: {user_info.get('mail', 'Unknown')}")
                return True
            else:
                print(f"❌ API test failed: {api_response.status_code}")
                print(f"API response: {api_response.text}")
                return False
        else:
            try:
                error_data = response.json()
                print(f"❌ Error: {error_data.get('error', 'Unknown')}")
                print(f"Error Description: {error_data.get('error_description', 'None')}")
                
                # Check for conditional access error
                if '53003' in error_data.get('error_codes', []):
                    print("\n🚨 CONDITIONAL ACCESS BLOCKED")
                    print("Your company has conditional access policies that are blocking this request.")
                    print("You need to:")
                    print("1. Contact your IT administrator")
                    print("2. Ask them to add an exception for this app")
                    print("3. Or ask them to temporarily disable conditional access for testing")
                
            except:
                print(f"❌ Raw error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🏢 ONEDRIVE COMPANY ACCOUNT WITH CONDITIONAL ACCESS")
    print("=" * 60)
    print("Account: anthony.penzes@fsa-pty.co.za")
    print("Company: Food Safety Agency (Pty) Ltd")
    
    # Generate authorization URL
    auth_url, tenant_id = generate_company_auth_url()
    print(f"\nAuthorization URL: {auth_url}")
    print(f"Tenant ID: {tenant_id or 'Using common endpoint'}")
    
    # Open browser
    print("\n🌐 Opening browser for authentication...")
    webbrowser.open(auth_url)
    
    print("\nPlease complete the authentication in your browser.")
    print("Make sure you're logged in as: anthony.penzes@fsa-pty.co.za")
    print("After authentication, you'll be redirected to localhost:8000/onedrive/callback")
    print("Copy the 'code' parameter from the URL and paste it below.")
    
    # Get authorization code from user
    auth_code = input("\nEnter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return False
    
    print(f"\n🔄 Testing token exchange with code: {auth_code[:20]}...")
    return test_token_exchange_with_tenant(auth_code, tenant_id)

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 OneDrive authentication successful!")
    else:
        print("\n❌ OneDrive authentication failed")
        print("\n💡 TROUBLESHOOTING TIPS:")
        print("1. Make sure you're logged in as anthony.penzes@fsa-pty.co.za")
        print("2. Check if your company has conditional access policies blocking this")
        print("3. Contact your IT administrator if you see conditional access errors")
        print("4. Try using a different browser or incognito mode")
