#!/usr/bin/env python3
"""
OneDrive with Refresh Token Support
"""

import os
import sys
import django
import json
import requests
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if '/onedrive/callback' in self.path:
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            
            if 'code' in params:
                self.server.auth_code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Success! OneDrive with refresh token is ready.</h1><script>setTimeout(() => window.close(), 2000);</script></body></html>')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Error: No code received</h1></body></html>')
        else:
            self.send_response(404)
            self.end_headers()

def get_onedrive_with_refresh():
    """Get OneDrive tokens with refresh token support."""
    print("🔄 GETTING ONEDRIVE WITH REFRESH TOKEN")
    print("=" * 50)
    
    # Your credentials
    tenant_id = "61ab5cbc-cdc4-498a-ba14-4d38595a85ff"
    client_id = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
    client_secret = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
    redirect_uri = "http://localhost:8000/onedrive/callback"
    
    print(f"✅ Tenant ID: {tenant_id}")
    print(f"✅ Client ID: {client_id}")
    print(f"✅ Client Secret: {client_secret[:10]}...")
    
    # Start callback server
    server = HTTPServer(('localhost', 8000), CallbackHandler)
    server.auth_code = None
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Generate auth URL with specific parameters for refresh token
    auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': 'https://graph.microsoft.com/Files.ReadWrite https://graph.microsoft.com/User.Read https://graph.microsoft.com/offline_access',
        'response_mode': 'query',
        'state': 'refresh_token_auth',
        'prompt': 'consent',
        'login_hint': 'anthony.penzes@fsa-pty.co.za',
        'access_type': 'offline'  # This should help get refresh token
    }
    
    full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    print(f"\n🌐 Opening browser for authentication with refresh token...")
    print(f"URL: {full_auth_url}")
    
    # Open browser
    webbrowser.open(full_auth_url)
    
    print("⏳ Waiting for authentication...")
    print("Please complete the authentication in your browser.")
    print("Make sure to grant all permissions for offline access.")
    
    # Wait for auth code
    timeout = 300
    start_time = time.time()
    
    while server.auth_code is None:
        if time.time() - start_time > timeout:
            print("❌ Timeout waiting for authentication")
            server.shutdown()
            return False
        time.sleep(1)
    
    print(f"✅ Got authorization code: {server.auth_code[:20]}...")
    
    # Exchange for tokens
    print("🔄 Exchanging code for tokens...")
    
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': server.auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        print(f"Token exchange status: {response.status_code}")
        print(f"Token response: {response.text}")
        
        if response.status_code == 200:
            tokens = response.json()
            print("✅ Token exchange successful!")
            
            # Check if we got a refresh token
            refresh_token = tokens.get('refresh_token')
            if refresh_token:
                print(f"✅ Refresh Token: {refresh_token[:20]}...")
            else:
                print("⚠️ No refresh token received")
                print("This might be due to Azure app configuration")
            
            # Add expiry time
            expires_in = tokens.get('expires_in', 3600)
            tokens['expires_at'] = time.time() + expires_in
            
            # Save tokens
            with open('onedrive_tokens.json', 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print(f"✅ Access Token: {tokens.get('access_token', 'None')[:20]}...")
            print(f"✅ Expires At: {tokens.get('expires_at', 'None')}")
            
            # Test API
            print("🔗 Testing OneDrive API...")
            api_url = "https://graph.microsoft.com/v1.0/me"
            headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
            
            api_response = requests.get(api_url, headers=headers)
            if api_response.status_code == 200:
                user_info = api_response.json()
                print("✅ OneDrive API working!")
                print(f"✅ User: {user_info.get('displayName')} ({user_info.get('mail')})")
                
                if refresh_token:
                    print("🎉 SUCCESS! OneDrive with refresh token is working!")
                    return True
                else:
                    print("⚠️ OneDrive is working but no refresh token available")
                    print("💡 You may need to update your Azure app configuration")
                    return True
            else:
                print(f"❌ API test failed: {api_response.status_code}")
                return False
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        server.shutdown()

if __name__ == "__main__":
    success = get_onedrive_with_refresh()
    if success:
        print("\n✅ OneDrive authentication complete!")
        print("✅ You can now use OneDrive features")
        if json.load(open('onedrive_tokens.json')).get('refresh_token'):
            print("✅ Auto-refresh will work when tokens expire")
        else:
            print("⚠️ Auto-refresh may not work - check Azure app configuration")
    else:
        print("\n❌ OneDrive setup failed")
