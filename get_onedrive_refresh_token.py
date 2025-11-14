#!/usr/bin/env python3
"""
Get OneDrive tokens with proper refresh token support
This will replace the current token with one that can auto-refresh
"""
import os
import json
import webbrowser
import urllib.parse
import requests
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# OneDrive credentials (from your settings)
TENANT_ID = "61ab5cbc-cdc4-498a-ba14-4d38595a85ff"
CLIENT_ID = "e6e7e71e-9f96-41ac-a4c2-5ae0f347e56f"
CLIENT_SECRET = "4lO8Q~qthbwKblvtCKyFjZhSw2bSS-R5RDjfPa~l"
REDIRECT_URI = "http://localhost:8000/onedrive/callback"

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/onedrive/callback'):
            # Extract the authorization code
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code = query_params.get('code', [None])[0]
            
            if code:
                self.server.auth_code = code
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                <html>
                <head><title>OneDrive Authentication</title></head>
                <body>
                <h1>OneDrive Authentication Successful!</h1>
                <p>Authorization code received. Processing tokens...</p>
                <p>You can close this window.</p>
                </body>
                </html>
                """)
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"<html><body><h1>No authorization code received</h1></body></html>")
        else:
            self.send_response(404)
            self.end_headers()

def get_onedrive_refresh_token():
    """Get OneDrive tokens with refresh token support."""
    print("🔄 GETTING ONEDRIVE REFRESH TOKEN")
    print("=" * 50)
    
    print(f"✅ Tenant ID: {TENANT_ID}")
    print(f"✅ Client ID: {CLIENT_ID}")
    print(f"✅ Client Secret: {CLIENT_SECRET[:10]}...")
    
    # Start callback server
    server = HTTPServer(('localhost', 8000), CallbackHandler)
    server.auth_code = None
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Generate auth URL with specific parameters for refresh token
    auth_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'https://graph.microsoft.com/Files.ReadWrite https://graph.microsoft.com/User.Read https://graph.microsoft.com/offline_access',
        'response_mode': 'query',
        'state': 'refresh_token_auth',
        'prompt': 'consent',  # Force consent to get refresh token
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
            print("❌ Authentication timeout")
            server.shutdown()
            return False
        time.sleep(1)
    
    auth_code = server.auth_code
    print(f"✅ Authorization code received: {auth_code[:20]}...")
    
    # Exchange code for tokens
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    token_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    print("🔄 Exchanging code for tokens...")
    response = requests.post(token_url, data=token_data)
    
    if response.status_code == 200:
        token_response = response.json()
        access_token = token_response.get('access_token')
        refresh_token = token_response.get('refresh_token')
        
        if access_token and refresh_token:
            # Save tokens to file
            token_data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': token_response.get('expires_in'),
                'token_type': token_response.get('token_type'),
                'expires_at': datetime.now().timestamp() + token_response.get('expires_in', 3600)
            }
            
            token_file = 'onedrive_tokens.json'
            with open(token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            print(f"✅ Tokens saved to: {token_file}")
            print(f"✅ Access token: {access_token[:20]}...")
            print(f"✅ Refresh token: {refresh_token[:20]}...")
            print(f"✅ Expires in: {token_response.get('expires_in')} seconds")
            print("✅ OneDrive authentication with refresh token complete!")
            
            server.shutdown()
            return True
        else:
            print("❌ No refresh token received")
            print(f"Response: {token_response}")
            server.shutdown()
            return False
    else:
        print(f"❌ Token exchange failed: {response.status_code}")
        print(f"Response: {response.text}")
        server.shutdown()
        return False

if __name__ == "__main__":
    success = get_onedrive_refresh_token()
    if success:
        print("\n🎉 OneDrive refresh token setup complete!")
        print("The token will now auto-refresh like Google Sheets.")
    else:
        print("\n❌ Failed to get refresh token. Please try again.")
