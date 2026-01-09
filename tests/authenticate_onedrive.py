#!/usr/bin/env python3
"""
OneDrive Authentication Script
Authenticate with OneDrive and save refresh tokens
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
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

class CallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress server logs

    def do_GET(self):
        if '/onedrive/callback' in self.path:
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)

            if 'code' in params:
                self.server.auth_code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = b'''
                <html>
                <head><title>OneDrive Auth Success</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: #10b981;">Success!</h1>
                    <p>OneDrive authentication complete. You can close this window.</p>
                    <script>setTimeout(() => window.close(), 3000);</script>
                </body>
                </html>
                '''
                self.wfile.write(html)
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = b'<html><body><h1>Error: No authorization code received</h1></body></html>'
                self.wfile.write(html)
        else:
            self.send_response(404)
            self.end_headers()

def authenticate_onedrive():
    """Authenticate with OneDrive and save refresh tokens."""
    print("=" * 70)
    print("ONEDRIVE AUTHENTICATION UTILITY")
    print("=" * 70)
    print()

    # Get settings from environment
    client_id = settings.ONEDRIVE_CLIENT_ID
    client_secret = settings.ONEDRIVE_CLIENT_SECRET
    redirect_uri = "http://localhost:8000/onedrive/callback"  # Use localhost for authentication

    if not client_id or not client_secret:
        print("ERROR: OneDrive credentials not configured in .env file")
        print()
        print("Please add the following to your .env file:")
        print("  ONEDRIVE_CLIENT_ID=your_client_id")
        print("  ONEDRIVE_CLIENT_SECRET=your_client_secret")
        return False

    print("Configuration:")
    print(f"  Client ID: {client_id[:20]}...")
    print(f"  Client Secret: ***{client_secret[-5:]}")
    print(f"  Redirect URI: {redirect_uri}")
    print()

    # Start local callback server
    print("Starting local server for OAuth callback...")
    server = HTTPServer(('localhost', 8000), CallbackHandler)
    server.auth_code = None
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print("Server started on http://localhost:8000")
    print()

    # Generate authorization URL
    auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': 'https://graph.microsoft.com/Files.ReadWrite.All offline_access',
        'response_mode': 'query',
        'prompt': 'consent'
    }

    full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"

    print("Opening browser for authentication...")
    print()
    print("IMPORTANT: Please sign in with your OneDrive account and grant permissions.")
    print()

    # Open browser
    webbrowser.open(full_auth_url)

    print("Waiting for authentication (timeout: 5 minutes)...")

    # Wait for authorization code
    timeout = 300
    start_time = time.time()

    while server.auth_code is None:
        if time.time() - start_time > timeout:
            print()
            print("ERROR: Authentication timeout (5 minutes expired)")
            server.shutdown()
            return False
        time.sleep(0.5)

    print()
    print("Authorization code received!")
    print()

    # Exchange code for tokens
    print("Exchanging authorization code for access tokens...")

    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': server.auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'scope': 'https://graph.microsoft.com/Files.ReadWrite.All offline_access'
    }

    try:
        response = requests.post(token_url, data=token_data, timeout=30)

        if response.status_code == 200:
            tokens = response.json()

            # Add expiry timestamp
            expires_in = tokens.get('expires_in', 3600)
            tokens['expires_at'] = datetime.now().timestamp() + expires_in
            tokens['last_refreshed'] = datetime.now().isoformat()

            # Save tokens to file
            token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
            with open(token_file, 'w') as f:
                json.dump(tokens, f, indent=2)

            print("SUCCESS! Tokens saved to onedrive_tokens.json")
            print()

            # Test the connection
            print("Testing OneDrive connection...")
            api_url = "https://graph.microsoft.com/v1.0/me"
            headers = {'Authorization': f'Bearer {tokens["access_token"]}'}

            api_response = requests.get(api_url, headers=headers, timeout=10)

            if api_response.status_code == 200:
                user_info = api_response.json()
                print()
                print("=" * 70)
                print("AUTHENTICATION SUCCESSFUL!")
                print("=" * 70)
                print()
                print(f"  User: {user_info.get('displayName', 'N/A')}")
                print(f"  Email: {user_info.get('mail') or user_info.get('userPrincipalName', 'N/A')}")
                print(f"  Token expires in: {expires_in / 3600:.1f} hours")
                print(f"  Refresh token: {'Available' if tokens.get('refresh_token') else 'Not available'}")
                print()
                print("OneDrive is now connected and ready to use!")
                print("=" * 70)
                return True
            else:
                print(f"ERROR: OneDrive API test failed ({api_response.status_code})")
                print(f"Response: {api_response.text}")
                return False
        else:
            print(f"ERROR: Token exchange failed ({response.status_code})")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False
    finally:
        server.shutdown()

if __name__ == "__main__":
    success = authenticate_onedrive()
    sys.exit(0 if success else 1)
