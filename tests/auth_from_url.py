"""
Complete Google OAuth using the full redirect URL.
"""
import os
import pickle
import sys
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import Flow

# Configuration - include all possible scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.send'
]
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'
REDIRECT_URI = 'http://127.0.0.1:8000/google-sheets/oauth2callback/'

# The full redirect URL from the browser
REDIRECT_URL = 'http://127.0.0.1:8000/google-sheets/oauth2callback/?state=qH8WyMBUYiekEjbPrFGFX53rBQ6xIp&code=4/0Ab32j91rWlA48MisxEoNRBXCV7MmTg4GbuXkeiuLXzGr7lk0gkcCQ8YhHTXkNeu3XauFzg&scope=https://www.googleapis.com/auth/spreadsheets.readonly%20https://www.googleapis.com/auth/drive.readonly%20https://www.googleapis.com/auth/drive%20https://www.googleapis.com/auth/gmail.send'

def main():
    print("\n" + "="*80)
    print("Completing Google API Authentication from Redirect URL")
    print("="*80 + "\n")

    try:
        # Parse the URL to extract the code
        parsed = urlparse(REDIRECT_URL)
        params = parse_qs(parsed.query)

        if 'code' not in params:
            print("[ERROR] No authorization code found in the URL!")
            return False

        auth_code = params['code'][0]
        state = params.get('state', [''])[0]

        print(f"[INFO] Extracted authorization code: {auth_code[:30]}...")
        print(f"[INFO] State: {state}")

        # Create the flow with state
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
            state=state
        )

        print("[INFO] Exchanging authorization code for access token...")

        # Use fetch_token with the full authorization response
        flow.fetch_token(code=auth_code)
        creds = flow.credentials

        print("[SUCCESS] Successfully obtained credentials!")

        # Display what scopes we got
        if hasattr(creds, 'scopes'):
            print(f"[INFO] Granted scopes: {', '.join(creds.scopes)}")

        # Save the credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

        print(f"[SUCCESS] Credentials saved to {TOKEN_FILE}")
        print("\n" + "="*80)
        print("Authentication completed successfully!")
        print("="*80 + "\n")
        print(f"[INFO] Token file location: {os.path.abspath(TOKEN_FILE)}")
        print("[INFO] Your application can now access Google APIs.")
        print("\n")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to complete authentication: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
