#!/usr/bin/env python3
"""
Test OneDrive Authentication and Token Refresh
Tests the new persistent token system locally
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.services.onedrive_direct_service import OneDriveDirectUploadService

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def check_token_file():
    """Check if token file exists and show its contents."""
    print_header("Token File Check")

    token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')

    if os.path.exists(token_file):
        print(f"[OK] Token file exists: {token_file}")

        with open(token_file, 'r') as f:
            token_data = json.load(f)

        print("\nToken File Contents:")
        print(f"  - Has access_token: {'Yes' if token_data.get('access_token') else 'No'}")
        print(f"  - Has refresh_token: {'Yes' if token_data.get('refresh_token') else 'No'}")

        expires_at = token_data.get('expires_at', 0)
        if expires_at:
            current_time = datetime.now().timestamp()
            time_until_expiry = expires_at - current_time

            if time_until_expiry > 0:
                hours_remaining = time_until_expiry / 3600
                days_remaining = hours_remaining / 24
                print(f"  - Token expires in: {hours_remaining:.1f} hours ({days_remaining:.1f} days)")

                if days_remaining < 1:
                    print("    [WARNING] Token expires soon - will be refreshed")
                elif days_remaining < 7:
                    print("    [INFO] Token will be proactively refreshed (< 7 days)")
                else:
                    print("    [OK] Token is fresh (> 7 days remaining)")
            else:
                print(f"  - Token status: [EXPIRED] ({abs(time_until_expiry/3600):.1f} hours ago)")

        if token_data.get('last_refreshed'):
            print(f"  - Last refreshed: {token_data.get('last_refreshed')}")

        return True
    else:
        print(f"[FAIL] Token file not found: {token_file}")
        print("\nYou need to authenticate first:")
        print("   1. Go to Settings in the web app")
        print("   2. Navigate to OneDrive Auto-Upload")
        print("   3. Click 'Authenticate' and follow the OAuth flow")
        return False

def test_authentication():
    """Test OneDrive authentication."""
    print_header("Authentication Test")

    print("Creating OneDrive service instance...")
    service = OneDriveDirectUploadService()

    print("Attempting to authenticate with saved tokens...")
    success = service.authenticate_onedrive()

    if success:
        print("[OK] Authentication successful!")
        print(f"   - Access token loaded: {service.access_token[:20] if service.access_token else 'None'}...")
        print(f"   - Authenticated: {service.authenticated}")
        return True
    else:
        print("[FAIL] Authentication failed")
        return False

def test_token_refresh():
    """Test token refresh functionality."""
    print_header("Token Refresh Test")

    token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
    if not os.path.exists(token_file):
        print("[SKIP] Cannot test refresh - no token file exists")
        return False

    with open(token_file, 'r') as f:
        token_data = json.load(f)

    service = OneDriveDirectUploadService()

    print("Testing token refresh...")
    success = service._refresh_token(token_data)

    if success:
        print("[OK] Token refresh successful!")
        print("   Checking updated token file...")

        with open(token_file, 'r') as f:
            new_token_data = json.load(f)

        print(f"   - New access token: {new_token_data.get('access_token', '')[:20] if new_token_data.get('access_token') else 'None'}...")
        print(f"   - Refresh token preserved: {'Yes' if new_token_data.get('refresh_token') else 'No'}")
        print(f"   - Last refreshed: {new_token_data.get('last_refreshed', 'N/A')}")
        return True
    else:
        print("[FAIL] Token refresh failed")
        return False

def test_token_monitor():
    """Test that token monitoring thread is running."""
    print_header("Token Monitor Test")

    service = OneDriveDirectUploadService()

    if service.token_monitor_thread and service.token_monitor_thread.is_alive():
        print("[OK] Token monitoring thread is running!")
        print("   - Thread name:", service.token_monitor_thread.name)
        print("   - Thread daemon:", service.token_monitor_thread.daemon)
        print("   - This thread will keep tokens fresh automatically")
        return True
    else:
        print("[FAIL] Token monitoring thread is not running")
        return False

def test_folder_listing():
    """Test listing OneDrive folders."""
    print_header("OneDrive API Test (List Folders)")

    service = OneDriveDirectUploadService()

    if not service.authenticate_onedrive():
        print("[FAIL] Cannot test API - authentication failed")
        return False

    print("Attempting to list root OneDrive folders...")
    folders = service.list_folders_in_onedrive("")

    if folders:
        print(f"[OK] Successfully retrieved {len(folders)} folders:")
        for folder in folders[:5]:  # Show first 5
            print(f"   - {folder['name']} ({folder.get('file_count', 0)} files)")
        if len(folders) > 5:
            print(f"   ... and {len(folders) - 5} more folders")
        return True
    else:
        print("[WARNING] No folders found or API call failed")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  ONEDRIVE AUTHENTICATION TEST SUITE")
    print("=" * 80)

    results = {
        'Token File Check': check_token_file(),
        'Authentication Test': test_authentication(),
        'Token Refresh Test': test_token_refresh(),
        'Token Monitor Test': test_token_monitor(),
        'OneDrive API Test': test_folder_listing()
    }

    print_header("Test Results Summary")

    passed = 0
    failed = 0

    for test_name, result in results.items():
        status = "[PASSED]" if result else "[FAILED]"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 80)
    print(f"Total: {passed} passed, {failed} failed out of {len(results)} tests")
    print("=" * 80)

    if failed == 0:
        print("\n[SUCCESS] All tests passed! OneDrive authentication is working correctly.")
        print("   Tokens will now be automatically refreshed in the background.")
    else:
        print("\n[WARNING] Some tests failed. Check the output above for details.")

    print("\n")

if __name__ == "__main__":
    main()
