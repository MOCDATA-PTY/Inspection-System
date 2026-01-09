"""
Direct token exchange using requests - bypass the state validation issue.
"""
import os
import json
import pickle
import requests

# Configuration
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'
REDIRECT_URI = 'http://127.0.0.1:8000/google-sheets/oauth2callback/'

# Authorization code from the URL
AUTH_CODE = '4/0Ab32j92uGA24aP68Z4eqZl5bla2A0YlEaJaYRyfclBUiWtWTLgiqbtJvr-EO5Ym3aTmRDg'

def main():
    print("\n" + "="*80)
    print("Direct Token Exchange")
    print("="*80 + "\n")

    try:
        # Load credentials.json
        with open(CREDENTIALS_FILE, 'r') as f:
            creds_data = json.load(f)

        if 'web' in creds_data:
            client_config = creds_data['web']
        elif 'installed' in creds_data:
            client_config = creds_data['installed']
        else:
            print("[ERROR] Invalid credentials.json format")
            return False

        client_id = client_config['client_id']
        client_secret = client_config['client_secret']
        token_uri = client_config['token_uri']

        print(f"[INFO] Client ID: {client_id[:30]}...")
        print(f"[INFO] Using authorization code: {AUTH_CODE[:30]}...")

        # Exchange authorization code for tokens
        print("[INFO] Exchanging code for access token...")

        token_data = {
            'code': AUTH_CODE,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }

        response = requests.post(token_uri, data=token_data)

        if response.status_code != 200:
            print(f"[ERROR] Token exchange failed with status {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return False

        token_response = response.json()

        print("[SUCCESS] Successfully obtained tokens!")

        # Create credentials object
        from google.oauth2.credentials import Credentials

        creds = Credentials(
            token=token_response['access_token'],
            refresh_token=token_response.get('refresh_token'),
            token_uri=token_uri,
            client_id=client_id,
            client_secret=client_secret,
            scopes=token_response.get('scope', '').split()
        )

        # Save the credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

        print(f"[SUCCESS] Token saved to: {os.path.abspath(TOKEN_FILE)}")

        # Verify
        if os.path.exists(TOKEN_FILE):
            file_size = os.path.getsize(TOKEN_FILE)
            print(f"[VERIFY] Token file exists: {file_size} bytes")

        print("\n" + "="*80)
        print("AUTHENTICATION SUCCESSFUL!")
        print("="*80)
        print("\nYour Google API credentials are now configured.\n")

        return True

    except FileNotFoundError:
        print(f"[ERROR] {CREDENTIALS_FILE} not found!")
        return False
    except Exception as e:
        print(f"\n[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
