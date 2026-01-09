#!/usr/bin/env python
"""
Get a new Google OAuth token for Google Sheets access
"""
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes required for Google Sheets access
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly'
]

print("=" * 80)
print("GOOGLE OAUTH TOKEN GENERATOR")
print("=" * 80)

# Delete old token if exists
if os.path.exists('token.pickle'):
    print("\nRemoving old token.pickle...")
    os.remove('token.pickle')
    print("[OK] Old token removed")

# Check for credentials file
creds_file = 'main/client_secret_2_398487258596-31egpmquh9p5k7a4dslkdlbmorcehc7r.apps.googleusercontent.com.json'
if not os.path.exists(creds_file):
    print(f"\nERROR: {creds_file} not found!")
    print("Please ensure the OAuth credentials file exists")
    exit(1)

print("\nStarting OAuth flow...")
print("Your browser will open to authorize the app")
print("Please sign in and grant access to Google Sheets")

try:
    # Run OAuth flow (let library auto-configure redirect URI)
    flow = InstalledAppFlow.from_client_secrets_file(
        creds_file,
        SCOPES
    )

    # This will open a browser window
    # The library will automatically use http://localhost:PORT/ as redirect
    creds = flow.run_local_server(
        port=55691,  # Using port from authorized redirect URIs
        prompt='consent',
        authorization_prompt_message='Please visit this URL to authorize: {url}',
        success_message='Authentication successful! You can close this window.',
        open_browser=True
    )

    # Save the credentials
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

    print("\n" + "=" * 80)
    print("[SUCCESS]")
    print("=" * 80)
    print("\nNew token saved to: token.pickle")
    print("Token expires: " + str(creds.expiry))
    print("\nYou can now run the restore script!")

except Exception as e:
    print(f"\nERROR during authentication: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
