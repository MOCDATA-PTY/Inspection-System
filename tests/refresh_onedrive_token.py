#!/usr/bin/env python3
"""
Refresh OneDrive Token
Simple script to refresh the OneDrive access token
"""

import os
import sys
import django

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.onedrive_direct_service import onedrive_direct_service

def main():
    print("=" * 60)
    print("ONEDRIVE TOKEN REFRESH UTILITY")
    print("=" * 60)
    print()

    try:
        # Attempt to authenticate (which will refresh token if needed)
        print("Attempting to authenticate with OneDrive...")
        print()

        success = onedrive_direct_service.authenticate_onedrive()

        print()
        print("=" * 60)
        if success:
            print("SUCCESS! OneDrive token refreshed and authenticated")
            print()
            print("Token Status:")
            print("   - Authentication: Connected")
            print("   - Access Token: Available")
            print()
            print("You can now use OneDrive features in the application.")
        else:
            print("FAILED! Could not refresh OneDrive token")
            print()
            print("Next Steps:")
            print("   1. Go to Settings in the web application")
            print("   2. Navigate to OneDrive Auto-Upload section")
            print("   3. Click 'Re-authenticate with OneDrive'")
            print("   4. Complete the authentication flow")
        print("=" * 60)

    except Exception as e:
        print()
        print("=" * 60)
        print(f"ERROR: {str(e)}")
        print("=" * 60)
        return 1

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
