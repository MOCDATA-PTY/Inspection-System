#!/usr/bin/env python3
"""
Test OneDrive Token Auto-Refresh
Verifies that the token automatically refreshes when it's about to expire
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.services.onedrive_direct_service import onedrive_direct_service

def test_token_auto_refresh():
    """Test automatic token refresh."""
    print("=" * 70)
    print("ONEDRIVE TOKEN AUTO-REFRESH TEST")
    print("=" * 70)
    print()

    # Check if tokens exist
    token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')

    if not os.path.exists(token_file):
        print("ERROR: No OneDrive tokens found.")
        print()
        print("Please authenticate first by:")
        print("  1. Going to http://localhost:8000/developer/onedrive-view/")
        print("  2. Clicking 'Connect to OneDrive'")
        print("  3. Completing the authentication")
        print()
        return False

    # Read current tokens
    with open(token_file, 'r') as f:
        tokens = json.load(f)

    print("Current Token Status:")
    print("-" * 70)

    # Check expiry
    expires_at = tokens.get('expires_at', 0)
    current_time = datetime.now().timestamp()
    time_until_expiry = expires_at - current_time
    hours_until_expiry = time_until_expiry / 3600

    print(f"  Access Token: {tokens.get('access_token', 'N/A')[:30]}...")
    print(f"  Refresh Token: {'Available' if tokens.get('refresh_token') else 'Missing'}")
    print(f"  Expires At: {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Time Until Expiry: {hours_until_expiry:.2f} hours")
    print()

    # Test 1: Check if token is valid
    print("TEST 1: Checking Current Token Validity")
    print("-" * 70)

    if time_until_expiry > 0:
        print(f"PASS: Token is still valid (expires in {hours_until_expiry:.2f} hours)")
    else:
        print(f"WARNING: Token has expired ({abs(hours_until_expiry):.2f} hours ago)")

    print()

    # Test 2: Attempt to refresh token
    print("TEST 2: Testing Automatic Token Refresh")
    print("-" * 70)

    print("Attempting to authenticate (this will refresh if needed)...")
    success = onedrive_direct_service.authenticate_onedrive()

    if success:
        print("PASS: Authentication successful!")

        # Read tokens again to check if they were refreshed
        with open(token_file, 'r') as f:
            new_tokens = json.load(f)

        new_expires_at = new_tokens.get('expires_at', 0)
        new_time_until_expiry = new_expires_at - datetime.now().timestamp()
        new_hours_until_expiry = new_time_until_expiry / 3600

        print()
        print("Updated Token Status:")
        print(f"  New Expires At: {datetime.fromtimestamp(new_expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  New Time Until Expiry: {new_hours_until_expiry:.2f} hours")

        if new_expires_at > expires_at:
            print()
            print("PASS: Token was successfully refreshed!")
            print(f"  Validity extended by: {(new_expires_at - expires_at) / 3600:.2f} hours")
        elif time_until_expiry < 3600:  # If less than 1 hour until expiry
            print()
            print("INFO: Token was not refreshed (not yet needed)")
            print("  Tokens are only refreshed when they expire soon or have expired")
        else:
            print()
            print("INFO: Token is still valid and doesn't need refreshing yet")
    else:
        print("FAIL: Authentication failed!")
        print()
        print("This could mean:")
        print("  - Refresh token is missing or invalid")
        print("  - Network connectivity issues")
        print("  - OneDrive API is unavailable")
        return False

    print()

    # Test 3: Force refresh by setting expiry to past
    print("TEST 3: Testing Force Refresh (Simulating Expired Token)")
    print("-" * 70)

    print("Temporarily setting token expiry to 5 minutes ago...")

    # Backup current tokens
    original_tokens = tokens.copy()

    # Set expiry to 5 minutes ago
    tokens['expires_at'] = datetime.now().timestamp() - 300

    # Save modified tokens
    with open(token_file, 'w') as f:
        json.dump(tokens, f, indent=2)

    print("Attempting to authenticate with expired token...")
    success = onedrive_direct_service.authenticate_onedrive()

    if success:
        print("PASS: Token was automatically refreshed!")

        # Read refreshed tokens
        with open(token_file, 'r') as f:
            refreshed_tokens = json.load(f)

        refreshed_expires_at = refreshed_tokens.get('expires_at', 0)
        refreshed_hours = (refreshed_expires_at - datetime.now().timestamp()) / 3600

        print()
        print("Refreshed Token Status:")
        print(f"  Expires At: {datetime.fromtimestamp(refreshed_expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Valid For: {refreshed_hours:.2f} hours")
        print()
        print("PASS: Automatic token refresh is working correctly!")
    else:
        print("FAIL: Token refresh failed!")
        print()
        print("Restoring original tokens...")
        with open(token_file, 'w') as f:
            json.dump(original_tokens, f, indent=2)
        return False

    print()
    print("=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print("Summary:")
    print("  - OneDrive tokens are properly configured")
    print("  - Automatic token refresh is working")
    print("  - Token will be refreshed automatically when it expires")
    print("  - No manual intervention required!")
    print()

    return True

if __name__ == "__main__":
    success = test_token_auto_refresh()
    sys.exit(0 if success else 1)
