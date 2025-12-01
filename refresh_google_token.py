#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refresh Google OAuth token and prepare it for deployment
"""

import os
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()

from main.services.google_sheets_service import GoogleSheetsService

def refresh_token():
    """Refresh the Google OAuth token"""

    print(f"\n{'='*100}")
    print(f"GOOGLE OAUTH TOKEN REFRESH")
    print(f"{'='*100}\n")

    try:
        # Initialize Google Sheets Service
        sheets_service = GoogleSheetsService()

        print("🔐 Authenticating with Google...")

        # Create a mock request object
        class MockRequest:
            def __init__(self):
                self.session = {}
                self.method = 'GET'
                self.headers = {}

        request = MockRequest()

        # Authenticate (this will refresh token if expired)
        sheets_service.authenticate(request)

        print("✅ Authentication successful!")
        print(f"Token file: {sheets_service.token_path}")

        # Check if token exists
        if os.path.exists(sheets_service.token_path):
            stat = os.stat(sheets_service.token_path)
            print(f"Token size: {stat.st_size} bytes")
            from datetime import datetime
            modified = datetime.fromtimestamp(stat.st_mtime)
            print(f"Last modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"\n{'='*100}")
        print(f"✅ Token refreshed successfully!")
        print(f"{'='*100}\n")

        print("⚠️  SECURITY NOTE:")
        print("   OAuth tokens grant access to your Google account.")
        print("   Only commit this token if you understand the security implications.")
        print("   For production, use service account authentication instead.\n")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*100)
    print("🔄 GOOGLE TOKEN REFRESH UTILITY")
    print("="*100)

    success = refresh_token()

    if success:
        print("\n✅ Ready to commit token to GitHub")
        print("\nNext steps:")
        print("  1. git add -f token.pickle")
        print("  2. git commit -m 'Update Google OAuth token for server sync'")
        print("  3. git push")
        sys.exit(0)
    else:
        print("\n❌ Token refresh failed")
        sys.exit(1)
