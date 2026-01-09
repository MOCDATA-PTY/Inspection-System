"""
Complete Google OAuth using the fresh redirect URL.
"""
import os
import pickle
import sys
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import Flow

# Configuration - match all scopes that Google returned
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.send'
]
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'
REDIRECT_URI = 'http://127.0.0.1:8000/google-sheets/oauth2callback/'

# Fresh redirect URL from browser
REDIRECT_URL = 'http://127.0.0.1:8000/google-sheets/oauth2callback/?state=RwLA01lZ2FGioz8NCu9VqCJraUDsHO&code=4/0Ab32j92uGA24aP68Z4eqZl5bla2A0YlEaJaYRyfclBUiWtWTLgiqbtJvr-EO5Ym3aTmRDg&scope=https://www.googleapis.com/auth/spreadsheets.readonly%20https://www.googleapis.com/auth/drive.readonly%20https://www.googleapis.com/auth/drive%20https://www.googleapis.com/auth/gmail.send'

def main():
    print("\n" + "="*80)
    print("Completing Google API Authentication")
    print("="*80 + "\n")

    try:
        # Parse the URL to extract code and state
        parsed = urlparse(REDIRECT_URL)
        params = parse_qs(parsed.query)

        if 'code' not in params:
            print("[ERROR] No authorization code found!")
            return False

        auth_code = params['code'][0]
        state = params.get('state', [''])[0]

        print(f"[INFO] Authorization code: {auth_code[:30]}...")
        print(f"[INFO] State: {state}")

        # Create flow with the state
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
            state=state
        )

        print("[INFO] Exchanging code for credentials...")

        # Exchange code for token
        flow.fetch_token(code=auth_code)
        creds = flow.credentials

        print("[SUCCESS] Successfully obtained credentials!")

        # Save credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

        print(f"[SUCCESS] Token saved to: {os.path.abspath(TOKEN_FILE)}")

        # Verify the token file
        if os.path.exists(TOKEN_FILE):
            file_size = os.path.getsize(TOKEN_FILE)
            print(f"[VERIFY] Token file exists: {file_size} bytes")

        print("\n" + "="*80)
        print("AUTHENTICATION SUCCESSFUL!")
        print("="*80)
        print("\nYour Google Sheets and Drive API access is now configured.")
        print("The application will automatically use these credentials.\n")

        return True

    except Exception as e:
        print(f"\n[ERROR] Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
