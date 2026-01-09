"""
Complete the Google OAuth authentication using the provided code.
"""
import os
import pickle
from google_auth_oauthlib.flow import Flow

# Configuration - Accept all scopes that Google provides
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.send'
]
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'
REDIRECT_URI = 'http://127.0.0.1:8000/google-sheets/oauth2callback/'

# The authorization code from the URL
AUTH_CODE = '4/0Ab32j91rWlA48MisxEoNRBXCV7MmTg4GbuXkeiuLXzGr7lk0gkcCQ8YhHTXkNeu3XauFzg'

def main():
    print("\n" + "="*80)
    print("Completing Google API Authentication")
    print("="*80 + "\n")

    try:
        # Create the flow
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )

        print(f"[INFO] Using authorization code: {AUTH_CODE[:30]}...")

        # Exchange the authorization code for credentials
        print("[INFO] Exchanging authorization code for access token...")
        flow.fetch_token(code=AUTH_CODE)
        creds = flow.credentials

        print("[SUCCESS] Successfully obtained credentials!")

        # Save the credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

        print(f"[SUCCESS] Credentials saved to {TOKEN_FILE}")
        print("\n" + "="*80)
        print("Authentication completed successfully!")
        print("="*80 + "\n")
        print(f"[INFO] Token file location: {os.path.abspath(TOKEN_FILE)}")
        print("[INFO] You can now use Google Sheets and Drive APIs in your application.")
        print("\n")

    except Exception as e:
        print(f"[ERROR] Failed to complete authentication: {e}")
        print("\n[INFO] This might happen if:")
        print("  - The authorization code has already been used")
        print("  - The authorization code has expired (they expire after a few minutes)")
        print("  - There's a network connectivity issue")
        print("\n[SOLUTION] Please run authenticate_google_simple.py again to get a fresh code.")
        return False

    return True

if __name__ == '__main__':
    success = main()
    if not success:
        exit(1)
