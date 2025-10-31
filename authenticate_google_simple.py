"""
Simple script to authenticate with Google APIs and generate token.pickle
Run this with: python authenticate_google_simple.py
"""
import os
import sys
import pickle
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'
REDIRECT_URI = 'http://127.0.0.1:8000/google-sheets/oauth2callback/'

def main():
    """Authenticate with Google and save credentials."""
    print("\n" + "="*80)
    print("Google API Authentication")
    print("="*80 + "\n")

    # Check if credentials.json exists
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"[ERROR] {CREDENTIALS_FILE} not found!")
        print("Please make sure credentials.json is in the same directory as this script.")
        sys.exit(1)

    creds = None

    # Check if token already exists
    if os.path.exists(TOKEN_FILE):
        print(f"[INFO] Found existing {TOKEN_FILE}")
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
        print("[INFO] Loaded existing credentials")

    # If credentials are invalid or don't exist, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[INFO] Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("[SUCCESS] Token refreshed successfully!")
            except Exception as e:
                print(f"[ERROR] Failed to refresh token: {e}")
                print("[INFO] Need to re-authenticate...")
                creds = None

        if not creds:
            print("[INFO] Starting OAuth flow...")
            flow = Flow.from_client_secrets_file(
                CREDENTIALS_FILE,
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )

            # Generate the authorization URL
            auth_url, state = flow.authorization_url(
                prompt='consent',
                access_type='offline',
                include_granted_scopes='true'
            )

            print("\n" + "="*80)
            print("[STEP 1] Visit this URL in your browser:")
            print("="*80)
            print(auth_url)
            print("\n" + "="*80)
            print("[STEP 2] After authorizing, you'll be redirected to a URL like:")
            print("         http://127.0.0.1:8000/google-sheets/oauth2callback/?code=...")
            print("[STEP 3] Copy the ENTIRE URL and paste it below")
            print("="*80 + "\n")

            # Get the full redirect URL from user
            redirect_response = input("Paste the full redirect URL here: ").strip()

            # Extract the code from the URL
            if 'code=' in redirect_response:
                # Handle the full URL
                code = redirect_response.split('code=')[1].split('&')[0]
            else:
                # User might have pasted just the code
                code = redirect_response

            print(f"\n[INFO] Using authorization code: {code[:20]}...")

            try:
                # Exchange the authorization code for credentials
                flow.fetch_token(code=code)
                creds = flow.credentials
                print("[SUCCESS] Successfully exchanged code for credentials!")
            except Exception as e:
                print(f"[ERROR] Failed to exchange code: {e}")
                sys.exit(1)

        # Save the credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print(f"[SUCCESS] Credentials saved to {TOKEN_FILE}")
    else:
        print("[SUCCESS] Existing credentials are valid!")

    print("\n" + "="*80)
    print("Authentication completed successfully!")
    print("="*80 + "\n")
    print(f"[INFO] Token file location: {os.path.abspath(TOKEN_FILE)}")
    print("[INFO] You can now use Google Sheets and Drive APIs in your application.")
    print("\n")

if __name__ == '__main__':
    main()
