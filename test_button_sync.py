#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to simulate the button click and sync process
"""
import os
import sys
import django
import time

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.core.cache import cache
from main.views.core_views import refresh_inspections, check_sync_status

User = get_user_model()

def test_sync_button():
    """Test the sync button endpoint"""
    print("\n" + "="*80)
    print("TESTING SYNC BUTTON ENDPOINT")
    print("="*80)

    # Clear any existing sync results
    cache.delete('sync_result')
    print("✓ Cleared existing sync results from cache")

    # Get a user to test with
    try:
        user = User.objects.get(username='lwandilemaqina')
        print(f"✓ Using user: {user.username} (Role: {user.role})")
    except User.DoesNotExist:
        print("✗ User 'lwandilemaqina' not found")
        user = User.objects.first()
        if user:
            print(f"  Using first available user: {user.username}")
        else:
            print("  No users found in database!")
            return

    # Create a fake request
    factory = RequestFactory()
    request = factory.post('/refresh-inspections/')
    request.user = user
    request.session = {}
    request.headers = {'X-Requested-With': 'XMLHttpRequest'}
    request._messages = []

    print("\n" + "-"*80)
    print("Step 1: Calling refresh_inspections endpoint...")
    print("-"*80)

    try:
        response = refresh_inspections(request)
        response_data = response.content.decode('utf-8')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response_data}")

        import json
        data = json.loads(response_data)

        if data.get('success') and data.get('status') == 'started':
            print("✓ Sync started successfully!")

            print("\n" + "-"*80)
            print("Step 2: Waiting for sync to complete...")
            print("-"*80)

            # Poll for status
            max_polls = 60  # 2 minutes max
            poll_count = 0

            while poll_count < max_polls:
                poll_count += 1
                time.sleep(2)  # Wait 2 seconds between polls

                # Check cache directly
                sync_result = cache.get('sync_result')

                if sync_result:
                    print(f"\n✓ Sync completed after {poll_count * 2} seconds!")
                    print(f"\nSync Result:")
                    print(f"  Success: {sync_result.get('success')}")
                    if sync_result.get('success'):
                        print(f"  Message: {sync_result.get('message')}")
                        print(f"  Deleted: {sync_result.get('deleted_count', 0)}")
                        print(f"  Created: {sync_result.get('created_count', 0)}")
                        print(f"  Processed: {sync_result.get('total_processed', 0)}")
                    else:
                        print(f"  Error: {sync_result.get('error')}")
                    break
                else:
                    if poll_count % 5 == 0:
                        print(f"  Still running... ({poll_count * 2}s elapsed)")

            if poll_count >= max_polls:
                print(f"\n✗ Sync timed out after {max_polls * 2} seconds")
                print("  The sync might still be running in the background")
        else:
            print(f"✗ Sync failed to start: {data}")

    except Exception as e:
        print(f"✗ Error testing sync button: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

def check_current_sync_status():
    """Check if there's a sync currently running"""
    print("\n" + "="*80)
    print("CHECKING CURRENT SYNC STATUS")
    print("="*80)

    sync_result = cache.get('sync_result')
    if sync_result:
        print("\n✓ Found sync result in cache:")
        print(f"  Success: {sync_result.get('success')}")
        if sync_result.get('success'):
            print(f"  Message: {sync_result.get('message')}")
            print(f"  Deleted: {sync_result.get('deleted_count', 0)}")
            print(f"  Created: {sync_result.get('created_count', 0)}")
            print(f"  Processed: {sync_result.get('total_processed', 0)}")
        else:
            print(f"  Error: {sync_result.get('error')}")
    else:
        print("\n✓ No sync result in cache (either no sync running or sync hasn't completed yet)")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        check_current_sync_status()
    else:
        print("\nThis will test the sync button endpoint and wait for completion.")
        print("Press Ctrl+C to cancel.\n")

        try:
            test_sync_button()
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n\nFATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
