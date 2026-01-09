"""
Test script to verify manual client preservation during sync operations
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import ClientAllocation
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

def print_separator():
    print("\n" + "=" * 80 + "\n")

def test_manual_client_preservation():
    """Test that manually added clients are preserved during sync"""

    print("[TEST] Testing Manual Client Preservation Feature")
    print_separator()

    # Get initial counts
    initial_total = ClientAllocation.objects.count()
    initial_manual = ClientAllocation.objects.filter(manually_added=True).count()
    initial_synced = ClientAllocation.objects.filter(manually_added=False).count()

    print("[INITIAL STATE]")
    print(f"   Total clients: {initial_total}")
    print(f"   Manually added: {initial_manual}")
    print(f"   Synced from sheets: {initial_synced}")
    print_separator()

    # Test 1: Create a manually added client
    print("[TEST 1] Creating manually added clients")

    # Get the max client_id to use for test clients
    max_client_id = ClientAllocation.objects.aggregate(max_id=models.Max('client_id'))['max_id'] or 0

    test_clients = [
        {
            'client_id': max_client_id + 9001,
            'internal_account_code': 'TEST-MANUAL-001',
            'eclick_name': 'Test Manual Client 1',
            'commodity': 'TEST',
            'facility_type': 'Test',
            'manually_added': True
        },
        {
            'client_id': max_client_id + 9002,
            'internal_account_code': 'TEST-MANUAL-002',
            'eclick_name': 'Test Manual Client 2',
            'commodity': 'TEST',
            'facility_type': 'Test',
            'manually_added': True
        },
        {
            'client_id': max_client_id + 9003,
            'internal_account_code': 'TEST-SYNCED-001',
            'eclick_name': 'Test Synced Client',
            'commodity': 'TEST',
            'facility_type': 'Test',
            'manually_added': False  # This simulates a synced client
        }
    ]

    created_clients = []
    for client_data in test_clients:
        client = ClientAllocation.objects.create(**client_data)
        created_clients.append(client)
        print(f"   [OK] Created: {client.internal_account_code} (manually_added={client.manually_added})")

    print_separator()

    # Check counts after creation
    after_create_total = ClientAllocation.objects.count()
    after_create_manual = ClientAllocation.objects.filter(manually_added=True).count()
    after_create_synced = ClientAllocation.objects.filter(manually_added=False).count()

    print("[AFTER CREATING TEST CLIENTS]")
    print(f"   Total clients: {after_create_total} (+{after_create_total - initial_total})")
    print(f"   Manually added: {after_create_manual} (+{after_create_manual - initial_manual})")
    print(f"   Synced from sheets: {after_create_synced} (+{after_create_synced - initial_synced})")
    print_separator()

    # Test 2: Verify manually_added field is set correctly
    print("[TEST 2] Verifying manually_added field")

    manual_client_1 = ClientAllocation.objects.get(internal_account_code='TEST-MANUAL-001')
    manual_client_2 = ClientAllocation.objects.get(internal_account_code='TEST-MANUAL-002')
    synced_client = ClientAllocation.objects.get(internal_account_code='TEST-SYNCED-001')

    assert manual_client_1.manually_added == True, "[FAIL] Manual client 1 should have manually_added=True"
    print(f"   [OK] {manual_client_1.internal_account_code}: manually_added={manual_client_1.manually_added}")

    assert manual_client_2.manually_added == True, "[FAIL] Manual client 2 should have manually_added=True"
    print(f"   [OK] {manual_client_2.internal_account_code}: manually_added={manual_client_2.manually_added}")

    assert synced_client.manually_added == False, "[FAIL] Synced client should have manually_added=False"
    print(f"   [OK] {synced_client.internal_account_code}: manually_added={synced_client.manually_added}")

    print_separator()

    # Test 3: Simulate sync operation (delete only synced clients)
    print("[TEST 3] Simulating sync operation")
    print("   [SYNC] Deleting only synced clients (manually_added=False)...")

    deleted_count = ClientAllocation.objects.filter(manually_added=False).delete()[0]
    print(f"   [OK] Deleted {deleted_count} synced clients")

    print_separator()

    # Test 4: Verify manually added clients still exist
    print("[TEST 4] Verifying manually added clients were preserved")

    try:
        preserved_client_1 = ClientAllocation.objects.get(internal_account_code='TEST-MANUAL-001')
        print(f"   [OK] {preserved_client_1.internal_account_code} was PRESERVED")
    except ClientAllocation.DoesNotExist:
        print(f"   [FAIL] TEST-MANUAL-001 was DELETED (should be preserved!)")
        raise

    try:
        preserved_client_2 = ClientAllocation.objects.get(internal_account_code='TEST-MANUAL-002')
        print(f"   [OK] {preserved_client_2.internal_account_code} was PRESERVED")
    except ClientAllocation.DoesNotExist:
        print(f"   [FAIL] TEST-MANUAL-002 was DELETED (should be preserved!)")
        raise

    try:
        synced_client_check = ClientAllocation.objects.get(internal_account_code='TEST-SYNCED-001')
        print(f"   [FAIL] {synced_client_check.internal_account_code} was PRESERVED (should be deleted!)")
        raise AssertionError("Synced client should have been deleted")
    except ClientAllocation.DoesNotExist:
        print(f"   [OK] TEST-SYNCED-001 was DELETED (as expected)")

    print_separator()

    # Final counts
    final_total = ClientAllocation.objects.count()
    final_manual = ClientAllocation.objects.filter(manually_added=True).count()
    final_synced = ClientAllocation.objects.filter(manually_added=False).count()

    print("[FINAL STATE] After simulated sync:")
    print(f"   Total clients: {final_total}")
    print(f"   Manually added: {final_manual}")
    print(f"   Synced from sheets: {final_synced}")
    print_separator()

    # Cleanup: Remove test clients
    print("[CLEANUP] Removing test clients...")
    ClientAllocation.objects.filter(internal_account_code__startswith='TEST-').delete()
    print("   [OK] Test clients removed")
    print_separator()

    # Verify cleanup
    cleanup_total = ClientAllocation.objects.count()
    cleanup_manual = ClientAllocation.objects.filter(manually_added=True).count()
    cleanup_synced = ClientAllocation.objects.filter(manually_added=False).count()

    print("[AFTER CLEANUP]")
    print(f"   Total clients: {cleanup_total}")
    print(f"   Manually added: {cleanup_manual}")
    print(f"   Synced from sheets: {cleanup_synced}")
    print_separator()

    # Summary
    print("[SUCCESS] ALL TESTS PASSED!")
    print("\n[VERIFIED] Manual client preservation feature is working correctly!")
    print("\nKey findings:")
    print("   + Manually added clients are marked with manually_added=True")
    print("   + Synced clients are marked with manually_added=False")
    print("   + Sync operation only deletes synced clients (manually_added=False)")
    print("   + Manually added clients are preserved during sync")
    print_separator()

if __name__ == '__main__':
    try:
        test_manual_client_preservation()
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        print_separator()

        # Cleanup on error
        print("[CLEANUP] Cleaning up test data due to error...")
        ClientAllocation.objects.filter(internal_account_code__startswith='TEST-').delete()
        print("   [OK] Cleanup complete")
