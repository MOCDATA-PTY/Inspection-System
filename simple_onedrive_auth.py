#!/usr/bin/env python3
"""
Simple OneDrive Authentication Test
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
                self.wfile.write(b'<html><body><h1>Success! Close this window.</h1></body></html>')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Error: No code received</h1></body></html>')
        else:
            self.send_response(404)
            self.end_headers()

def test_client_secret():
    """Test if the client secret is working."""
    print("🔐 TESTING CLIENT SECRET")
    print("=" * 40)
    
    # Set client secret
    client_secret = ".EF******************"
    os.environ['ONEDRIVE_CLIENT_SECRET'] = client_secret
    
    print(f"Client ID: {settings.ONEDRIVE_CLIENT_ID}")
    print(f"Client Secret: {client_secret[:10]}...")
    print(f"Redirect URI: {settings.ONEDRIVE_REDIRECT_URI}")
    
    # Test with a simple token request
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    # First, let's try to get a new authorization code
    print("\n🌐 Getting authorization URL...")
    
    scopes = [
        'https://graph.microsoft.com/Files.ReadWrite',
        'https://graph.microsoft.com/User.Read',
        'https://graph.microsoft.com/offline_access'
    ]
    
    auth_params = {
        'client_id': settings.ONEDRIVE_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': settings.ONEDRIVE_REDIRECT_URI,
        'scope': ' '.join(scopes),
        'response_mode': 'query',
        'state': 'test'
    }
    
    auth_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{urllib.parse.urlencode(auth_params)}"
    
    print(f"Authorization URL: {auth_url}")
    
    # Start callback server
    server = HTTPServer(('localhost', 8000), CallbackHandler)
    server.auth_code = None
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print("\n🔗 Opening browser for authentication...")
    webbrowser.open(auth_url)
    
    print("⏳ Waiting for authorization code...")
    timeout = 300
    start_time = time.time()
    
    while server.auth_code is None:
        if time.time() - start_time > timeout:
            print("❌ Timeout waiting for authorization")
            server.shutdown()
            return False
        time.sleep(1)
    
    print(f"✅ Got authorization code: {server.auth_code[:20]}...")
    
    # Exchange code for tokens
    print("\n🔄 Exchanging code for tokens...")
    
    token_data = {
        'client_id': settings.ONEDRIVE_CLIENT_ID,
        'client_secret': client_secret,
        'code': server.auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.ONEDRIVE_REDIRECT_URI
    }
    
    print(f"Token request data: {token_data}")
    
    try:
        response = requests.post(token_url, data=token_data)
        print(f"Token response status: {response.status_code}")
        print(f"Token response: {response.text}")
        
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
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        server.shutdown()

if __name__ == "__main__":
    success = test_client_secret()
    if success:
        print("\n🎉 OneDrive authentication successful!")
    else:
        print("\n❌ OneDrive authentication failed")
