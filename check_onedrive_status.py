#!/usr/bin/env python
"""
Check OneDrive connection status
"""
import os
import sys
import django
import json
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def main():
    print("📊 ONEDRIVE CONNECTION STATUS")
    print("=" * 40)
    
    # Check if tokens file exists
    token_file = os.path.join(os.path.dirname(__file__), 'onedrive_tokens.json')
    if not os.path.exists(token_file):
        print("❌ No tokens file found")
        print("🔗 Need to complete OAuth flow")
        return
    
    # Load and check tokens
    with open(token_file, 'r') as f:
        tokens = json.load(f)
    
    access_token = tokens.get('access_token')
    expires_at = tokens.get('expires_at', 0)
    current_time = datetime.now().timestamp()
    
    print(f"✅ Tokens file exists")
    print(f"✅ Token type: {tokens.get('token_type', 'Unknown')}")
    print(f"✅ Expires at: {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
    
    if current_time >= expires_at:
        print("❌ Token has EXPIRED")
        print("🔗 Need to refresh connection")
        print("\n📋 To refresh OneDrive connection:")
        print("1. Go to: http://localhost:8000/onedrive/callback")
        print("2. Or use the authorization URL from the previous test")
        print("3. Sign in with: anthony.penzes@fsa-pty.co.za")
        print("4. Grant permissions")
        print("5. You'll be redirected back to the callback")
    else:
        print("✅ Token is VALID")
        print("🎉 OneDrive is connected and ready to use!")
    
    print(f"\n🌐 Quick Authorization URL:")
    client_id = getattr(settings, 'ONEDRIVE_CLIENT_ID', '')
    redirect_uri = getattr(settings, 'ONEDRIVE_REDIRECT_URI', '')
    auth_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=offline_access%20Files.ReadWrite.All%20User.Read&prompt=select_account"
    print(auth_url)

if __name__ == "__main__":
    main()
