#!/usr/bin/env python3
"""
Re-authenticate OneDrive with Client Secret
This will help you get a new access token and refresh token
"""

import os
import sys
import django
import json
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

class OneDriveCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/onedrive/callback'):
            # Parse the authorization code from the URL
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            if 'code' in query_params:
                self.server.auth_code = query_params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    <script>setTimeout(() => window.close(), 3000);</script>
                </body>
                </html>
                ''')
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html>
                <body>
                    <h1>Authorization Failed</h1>
                    <p>No authorization code received. Please try again.</p>
                </body>
                </html>
                ''')
        else:
            self.send_response(404)
            self.end_headers()

def start_callback_server():
    """Start a local server to receive the OAuth callback."""
    server = HTTPServer(('localhost', 8000), OneDriveCallbackHandler)
    server.auth_code = None
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return server

def get_authorization_url():
    """Generate the OneDrive authorization URL."""
    client_id = settings.ONEDRIVE_CLIENT_ID
    redirect_uri = settings.ONEDRIVE_REDIRECT_URI
    
    # Scopes for OneDrive access
    scopes = [
        'https://graph.microsoft.com/Files.ReadWrite',
        'https://graph.microsoft.com/User.Read',
        'https://graph.microsoft.com/offline_access'  # This is crucial for getting refresh tokens
    ]
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes),
        'response_mode': 'query',
        'state': 'onedrive_auth'
    }
    
    base_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    return auth_url

def exchange_code_for_tokens(auth_code, client_secret):
    """Exchange the authorization code for access and refresh tokens."""
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    data = {
        'client_id': settings.ONEDRIVE_CLIENT_ID,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.ONEDRIVE_REDIRECT_URI
    }
    
    import requests
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        
        # Calculate expiry time
        expires_in = tokens.get('expires_in', 3600)
        expires_at = time.time() + expires_in
        
        # Add expiry time to tokens
        tokens['expires_at'] = expires_at
        
        # Save tokens
        with open('onedrive_tokens.json', 'w') as f:
            json.dump(tokens, f, indent=2)
        
        return tokens
    else:
        print(f"❌ Token exchange failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def main():
    print("🔐 ONEDRIVE RE-AUTHENTICATION")
    print("=" * 50)
    
    # Set the client secret
    client_secret = ".EF******************"  # Your second secret
    os.environ['ONEDRIVE_CLIENT_SECRET'] = client_secret
    
    print(f"✅ Client ID: {settings.ONEDRIVE_CLIENT_ID}")
    print(f"✅ Client Secret: Set")
    print(f"✅ Redirect URI: {settings.ONEDRIVE_REDIRECT_URI}")
    
    # Start callback server
    print("\n🌐 Starting callback server on localhost:8000...")
    server = start_callback_server()
    
    # Generate authorization URL
    auth_url = get_authorization_url()
    print(f"\n🔗 Authorization URL generated")
    print(f"Opening browser for authentication...")
    
    # Open browser
    webbrowser.open(auth_url)
    
    print("\n⏳ Waiting for authorization...")
    print("Please complete the authentication in your browser.")
    print("The browser will redirect to localhost:8000/onedrive/callback")
    
    # Wait for authorization code
    timeout = 300  # 5 minutes
    start_time = time.time()
    
    while server.auth_code is None:
        if time.time() - start_time > timeout:
            print("\n❌ Timeout waiting for authorization")
            server.shutdown()
            return False
        
        time.sleep(1)
    
    print(f"\n✅ Authorization code received: {server.auth_code[:20]}...")
    
    # Exchange code for tokens
    print("🔄 Exchanging code for tokens...")
    tokens = exchange_code_for_tokens(server.auth_code, client_secret)
    
    # Shutdown server
    server.shutdown()
    
    if tokens:
        print("✅ Tokens obtained successfully!")
        print(f"Access Token: {tokens.get('access_token', 'None')[:20]}...")
        print(f"Refresh Token: {tokens.get('refresh_token', 'None')[:20]}...")
        print(f"Expires At: {tokens.get('expires_at', 'None')}")
        
        # Test the connection
        print("\n🔗 Testing API connection...")
        import requests
        
        api_url = "https://graph.microsoft.com/v1.0/me"
        headers = {
            'Authorization': f'Bearer {tokens["access_token"]}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                user_info = response.json()
                print("✅ API connection successful!")
                print(f"User: {user_info.get('displayName', 'Unknown')}")
                print(f"Email: {user_info.get('mail', 'Unknown')}")
                print("\n🎉 OneDrive authentication complete!")
                return True
            else:
                print(f"❌ API test failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API test error: {e}")
            return False
    else:
        print("❌ Failed to obtain tokens")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ OneDrive is now ready to use!")
    else:
        print("\n❌ OneDrive setup failed")
