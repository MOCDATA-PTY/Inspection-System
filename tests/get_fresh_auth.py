"""
Generate a fresh Google OAuth URL for authentication.
Run this and immediately use the URL in your browser.
"""
from google_auth_oauthlib.flow import Flow

# Configuration - include all scopes your app needs
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
]
CREDENTIALS_FILE = 'credentials.json'
REDIRECT_URI = 'http://127.0.0.1:8000/google-sheets/oauth2callback/'

def main():
    print("\n" + "="*80)
    print("Google API Authentication - Fresh Authorization URL")
    print("="*80 + "\n")

    # Create the flow
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

    print("[STEP 1] Copy and visit this URL in your browser:")
    print("-"*80)
    print(auth_url)
    print("-"*80)
    print("\n[STEP 2] After authorizing, you'll see a 404 error page.")
    print("         Copy the ENTIRE URL from your browser's address bar.")
    print("\n[STEP 3] The URL will look like:")
    print("         http://127.0.0.1:8000/google-sheets/oauth2callback/?state=...&code=...")
    print("\n[STEP 4] Send that URL to me and I'll complete the authentication.")
    print("\n" + "="*80)
    print(f"State value (for verification): {state}")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
