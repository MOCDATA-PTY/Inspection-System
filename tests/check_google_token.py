#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check and refresh Google Sheets token
"""

import os
import sys
import pickle

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow

# Path to token file
TOKEN_PATH = 'token.pickle'
CREDENTIALS_PATH = 'credentials.json'
REDIRECT_URI = 'http://127.0.0.1:8000/google-sheets/oauth2callback/'

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def check_token():
    """Check the current token status"""
    print("=" * 80)
    print("GOOGLE SHEETS TOKEN STATUS CHECK")
    print("=" * 80)

    if not os.path.exists(TOKEN_PATH):
        print("❌ Token file not found: token.pickle")
        print("   You need to authenticate with Google first.")
        return False

    if not os.path.exists(CREDENTIALS_PATH):
        print("❌ Credentials file not found: credentials.json")
        print("   You need to download it from Google Cloud Console.")
        return False

    print("✅ Token file exists: token.pickle")
    print("✅ Credentials file exists: credentials.json")

    # Load the token
    try:
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

        print("\n" + "=" * 80)
        print("TOKEN DETAILS")
        print("=" * 80)
        print(f"Valid: {creds.valid}")
        print(f"Expired: {creds.expired if hasattr(creds, 'expired') else 'N/A'}")
        print(f"Has Refresh Token: {bool(creds.refresh_token)}")

        if hasattr(creds, 'expiry'):
            print(f"Expiry: {creds.expiry}")

        if hasattr(creds, 'scopes'):
            print(f"Scopes: {', '.join(creds.scopes)}")

        # Try to refresh if expired
        if not creds.valid:
            print("\n" + "=" * 80)
            print("TOKEN REFRESH ATTEMPT")
            print("=" * 80)

            if creds.expired and creds.refresh_token:
                try:
                    print("🔄 Attempting to refresh token...")
                    creds.refresh(Request())
                    print("✅ Token refreshed successfully!")

                    # Save the refreshed token
                    with open(TOKEN_PATH, 'wb') as token:
                        pickle.dump(creds, token)
                    print("✅ Refreshed token saved to token.pickle")

                    return True
                except Exception as e:
                    print(f"❌ Token refresh failed: {e}")
                    print("\n⚠️  You need to re-authenticate:")
                    print("   1. Delete token.pickle")
                    print("   2. Run: python authenticate_google_simple.py")
                    print("   OR use the web interface to authenticate")
                    return False
            else:
                print("❌ Token is invalid and cannot be refreshed")
                print("   Missing refresh_token - you need to re-authenticate")
                print("\n⚠️  To fix this:")
                print("   1. Delete token.pickle")
                print("   2. Run: python authenticate_google_simple.py")
                print("   OR use the web interface to authenticate")
                return False
        else:
            print("\n✅ Token is valid and ready to use!")
            return True

    except Exception as e:
        print(f"\n❌ Error checking token: {e}")
        print("\n⚠️  Token may be corrupted. Try:")
        print("   1. Delete token.pickle")
        print("   2. Run: python authenticate_google_simple.py")
        return False

def create_new_token():
    """Create a new token with proper scopes"""
    print("\n" + "=" * 80)
    print("CREATE NEW TOKEN")
    print("=" * 80)

    if not os.path.exists(CREDENTIALS_PATH):
        print("❌ credentials.json not found")
        print("   Download it from Google Cloud Console first")
        return False

    try:
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_PATH,
            SCOPES,
            redirect_uri=REDIRECT_URI
        )

        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true'
        )

        print("\n📋 Please visit this URL to authorize:")
        print(f"\n{auth_url}\n")
        print("After authorization, you'll be redirected to:")
        print(f"{REDIRECT_URI}")
        print("\nCopy the 'code' parameter from the URL and paste below.")

        auth_code = input("\nEnter authorization code: ").strip()

        if not auth_code:
            print("❌ No code provided")
            return False

        print("\n🔄 Exchanging code for token...")
        flow.fetch_token(code=auth_code)
        creds = flow.credentials

        print("✅ Token obtained successfully!")
        print(f"   Has Refresh Token: {bool(creds.refresh_token)}")

        # Save the token
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

        print(f"✅ Token saved to {TOKEN_PATH}")
        print("\n✅ Google Sheets authentication complete!")
        print("   You can now use the Sync Everything button")

        return True

    except Exception as e:
        print(f"❌ Error creating token: {e}")
        return False

if __name__ == "__main__":
    print("\n")

    # Check current token
    is_valid = check_token()

    if not is_valid:
        print("\n" + "=" * 80)
        response = input("\nWould you like to create a new token now? (y/n): ").strip().lower()

        if response == 'y':
            create_new_token()
        else:
            print("\n⚠️  To sync clients, you need a valid Google token.")
            print("   Run this script again and choose 'y' to create one.")

    print("\n" + "=" * 80)
    print("Done!")
    print("=" * 80 + "\n")
