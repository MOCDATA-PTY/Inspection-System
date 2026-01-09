#!/usr/bin/env python3
"""
Test script for compliance documents sync
Tests that the 3-hour compliance sync works correctly
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.scheduled_sync_service import scheduled_sync_service


def test_compliance_sync():
    """Test the compliance documents sync."""
    print("="*80)
    print("TESTING COMPLIANCE DOCUMENTS SYNC")
    print("="*80)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check current service status
    print("[INFO] Checking service status...")
    status = scheduled_sync_service.get_service_status()
    print(f"   - Service running: {status.get('is_running', False)}")
    print(f"   - Service alive: {status.get('service_alive', False)}")

    # Check last sync times
    last_sync_times = scheduled_sync_service.last_sync_times
    print("\n[INFO] Last sync times:")
    for sync_type, last_time in last_sync_times.items():
        if last_time:
            print(f"   - {sync_type}: {last_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"   - {sync_type}: Never")

    # Test should_run_sync for compliance_documents
    print("\n[TEST] Checking if compliance sync should run...")
    should_run = scheduled_sync_service.should_run_sync('compliance_documents')
    print(f"   - Should run compliance sync: {should_run}")

    # Run manual compliance sync
    print("\n[TEST] Running manual compliance documents sync...")
    print("="*80)

    try:
        success, message = scheduled_sync_service.run_manual_sync('compliance_documents')

        print("\n" + "="*80)
        print("[RESULT] Test completed!")
        print("="*80)
        print(f"\n   Success: {success}")
        print(f"   Message: {message}")

        # Check updated last sync time
        last_compliance_sync = scheduled_sync_service.last_sync_times.get('compliance_documents')
        if last_compliance_sync:
            print(f"   Last compliance sync: {last_compliance_sync.strftime('%Y-%m-%d %H:%M:%S')}")

        if success:
            print("\n[PASS] COMPLIANCE SYNC TEST PASSED!")
        else:
            print("\n[FAIL] COMPLIANCE SYNC TEST FAILED!")

    except Exception as e:
        print("\n" + "="*80)
        print("[ERROR] Test failed with exception!")
        print("="*80)
        print(f"\n   Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n[FAIL] COMPLIANCE SYNC TEST FAILED!")

    print("\n" + "="*80)
    print(f"Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)


if __name__ == "__main__":
    test_compliance_sync()
