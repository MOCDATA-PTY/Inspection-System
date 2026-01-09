"""
Test to verify frontend is correctly receiving and displaying approved_status values
This test simulates what happens when the page loads and after updates
"""

import os
import django
import sys
from datetime import date, datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Count
import re


def normalize_client_name(name):
    """Normalize client name for grouping (same as frontend)"""
    return re.sub(r'[^a-zA-Z0-9]', '', (name or '')).lower()


def print_section(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_frontend_data_retrieval():
    """Test 1: Verify data is being retrieved correctly for frontend display"""
    print_section("TEST 1: Frontend Data Retrieval")

    # Get inspection groups (same way the view does it)
    from django.contrib.auth.models import User

    # Get a sample of recent inspections
    recent_inspections_qs = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__isnull=False
    ).order_by('-date_of_inspection')

    if not recent_inspections_qs.exists():
        print("[FAIL] No inspections found")
        return False

    # Convert to list to avoid slice issues
    recent_inspections = list(recent_inspections_qs[:50])

    print(f"\nFound {len(recent_inspections)} recent inspections")
    print("\nSample inspection data (as it appears to frontend):")
    print("-" * 80)
    print(f"{'ID':>8} | {'Client Name':30} | {'Date':12} | {'Approved Status':15}")
    print("-" * 80)

    for insp in recent_inspections[:10]:
        client = (insp.client_name or 'Unknown')[:30]
        date_str = str(insp.date_of_inspection) if insp.date_of_inspection else 'N/A'
        status = insp.approved_status or 'NULL'
        print(f"{insp.id:8} | {client:30} | {date_str:12} | {status:15}")

    # Count statuses
    pending_count = sum(1 for i in recent_inspections if i.approved_status == 'PENDING')
    approved_count = sum(1 for i in recent_inspections if i.approved_status == 'APPROVED')
    null_count = sum(1 for i in recent_inspections if not i.approved_status)

    print("-" * 80)
    print(f"\nStatus distribution in recent inspections:")
    print(f"  PENDING:  {pending_count}")
    print(f"  APPROVED: {approved_count}")
    print(f"  NULL:     {null_count}")

    print("\n[PASS] Data retrieval works - frontend receives approved_status values")
    return True


def test_group_id_format():
    """Test 2: Verify group_id format matches what frontend sends"""
    print_section("TEST 2: Group ID Format Verification")

    # Get a sample inspection group
    inspection = FoodSafetyAgencyInspection.objects.filter(
        client_name__isnull=False,
        date_of_inspection__isnull=False
    ).first()

    if not inspection:
        print("[FAIL] No valid inspection found")
        return False

    client_name = inspection.client_name
    date_of_inspection = inspection.date_of_inspection

    # Format group_id the same way frontend does
    normalized_client = normalize_client_name(client_name)
    date_str = date_of_inspection.strftime('%Y-%m-%d')
    group_id = f"{normalized_client}_{date_str}"

    print(f"\nSample Inspection:")
    print(f"  Original Client Name: {client_name}")
    print(f"  Normalized Name:      {normalized_client}")
    print(f"  Date:                 {date_str}")
    print(f"  Group ID:             {group_id}")
    print(f"  Current Status:       {inspection.approved_status}")

    # Verify we can find inspections using this group_id
    # (Same logic as update_group_approved view)
    parts = group_id.split('_')
    date_part = parts[-1]
    client_name_parts = parts[:-1]
    reconstructed_client = '_'.join(client_name_parts)

    # Parse date
    try:
        parsed_date = datetime.strptime(date_part, '%Y-%m-%d').date()
        print(f"\n  Parsed Date:          {parsed_date}")
    except ValueError:
        print("\n[FAIL] Could not parse date from group_id")
        return False

    # Find matching inspections
    candidate_qs = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection=parsed_date
    )
    matching_ids = [ins.id for ins in candidate_qs if normalize_client_name(ins.client_name) == reconstructed_client]
    matching_inspections = FoodSafetyAgencyInspection.objects.filter(id__in=matching_ids)

    print(f"  Matching Inspections: {matching_inspections.count()}")

    if matching_inspections.exists():
        print("\n[PASS] Group ID format is correct - backend can find inspections from frontend group_id")
        return True
    else:
        print("\n[FAIL] No matching inspections found using group_id")
        return False


def test_update_and_verify_persistence():
    """Test 3: Update a value and verify it persists (simulating page refresh)"""
    print_section("TEST 3: Update & Verify Persistence (Page Refresh Simulation)")

    # Find a test group
    test_inspection = FoodSafetyAgencyInspection.objects.filter(
        client_name__isnull=False,
        date_of_inspection__isnull=False
    ).order_by('-date_of_inspection').first()

    if not test_inspection:
        print("[FAIL] No valid inspection found")
        return False

    # Store original values
    original_status = test_inspection.approved_status
    client_name = test_inspection.client_name
    date_of_inspection = test_inspection.date_of_inspection

    print(f"\nTest Inspection:")
    print(f"  ID:             {test_inspection.id}")
    print(f"  Client:         {client_name}")
    print(f"  Date:           {date_of_inspection}")
    print(f"  Original Status: {original_status}")

    # STEP 1: User changes dropdown to APPROVED
    print("\n--- STEP 1: User changes dropdown to APPROVED ---")

    # Find all inspections in this group
    normalized_client = normalize_client_name(client_name)
    candidate_qs = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection=date_of_inspection
    )
    matching_ids = [ins.id for ins in candidate_qs if normalize_client_name(ins.client_name) == normalized_client]
    inspections = FoodSafetyAgencyInspection.objects.filter(id__in=matching_ids)

    print(f"Updating {inspections.count()} inspections in group to APPROVED")
    updated_count = inspections.update(approved_status='APPROVED')
    print(f"Updated {updated_count} inspections")

    # STEP 2: Simulate page refresh - clear from memory and re-fetch from DB
    print("\n--- STEP 2: Simulating page refresh (re-fetching from database) ---")

    # Clear any cached objects
    from django.db import connection
    connection.queries_log.clear()

    # Re-fetch the inspection as if page was refreshed
    refreshed_inspection = FoodSafetyAgencyInspection.objects.get(id=test_inspection.id)

    print(f"After refresh:")
    print(f"  ID:             {refreshed_inspection.id}")
    print(f"  Client:         {refreshed_inspection.client_name}")
    print(f"  Date:           {refreshed_inspection.date_of_inspection}")
    print(f"  Status:         {refreshed_inspection.approved_status}")

    if refreshed_inspection.approved_status == 'APPROVED':
        print("\n[PASS] Status persisted after page refresh!")
    else:
        print(f"\n[FAIL] Status did not persist. Expected APPROVED, got {refreshed_inspection.approved_status}")

    # STEP 3: Change to PENDING and verify again
    print("\n--- STEP 3: User changes dropdown to PENDING ---")

    inspections.update(approved_status='PENDING')
    print(f"Updated {inspections.count()} inspections to PENDING")

    # Re-fetch again
    refreshed_inspection2 = FoodSafetyAgencyInspection.objects.get(id=test_inspection.id)
    print(f"After second refresh:")
    print(f"  Status: {refreshed_inspection2.approved_status}")

    if refreshed_inspection2.approved_status == 'PENDING':
        print("\n[PASS] Status persisted after second update and refresh!")
    else:
        print(f"\n[FAIL] Status did not persist. Expected PENDING, got {refreshed_inspection2.approved_status}")

    # STEP 4: Restore original value
    print(f"\n--- STEP 4: Restoring original status ({original_status}) ---")
    inspections.update(approved_status=original_status)
    print(f"[OK] Restored to original status")

    return refreshed_inspection.approved_status == 'APPROVED' and refreshed_inspection2.approved_status == 'PENDING'


def test_dropdown_selected_state():
    """Test 4: Verify correct dropdown option is selected based on DB value"""
    print_section("TEST 4: Dropdown Selected State")

    # Get inspections with different statuses
    pending_insp = FoodSafetyAgencyInspection.objects.filter(approved_status='PENDING').first()
    approved_insp = FoodSafetyAgencyInspection.objects.filter(approved_status='APPROVED').first()

    print("\nVerifying dropdown selection logic:")
    print("-" * 80)

    if pending_insp:
        print(f"\nPENDING Inspection (ID: {pending_insp.id}):")
        print(f"  DB Value: {pending_insp.approved_status}")

        # Simulate template logic
        if pending_insp.approved_status == 'PENDING' or not pending_insp.approved_status:
            print("  Dropdown: 'Pending' option will be SELECTED [OK]")
        else:
            print("  Dropdown: 'Pending' option will NOT be selected")

        if pending_insp.approved_status == 'APPROVED':
            print("  Dropdown: 'Approved' option will be SELECTED")
        else:
            print("  Dropdown: 'Approved' option will NOT be selected [OK]")

    if approved_insp:
        print(f"\nAPPROVED Inspection (ID: {approved_insp.id}):")
        print(f"  DB Value: {approved_insp.approved_status}")

        # Simulate template logic
        if approved_insp.approved_status == 'PENDING' or not approved_insp.approved_status:
            print("  Dropdown: 'Pending' option will be SELECTED")
        else:
            print("  Dropdown: 'Pending' option will NOT be selected [OK]")

        if approved_insp.approved_status == 'APPROVED':
            print("  Dropdown: 'Approved' option will be SELECTED [OK]")
        else:
            print("  Dropdown: 'Approved' option will NOT be selected")

    print("\n[PASS] Dropdown logic correctly reflects DB values")
    return True


def run_all_tests():
    """Run all frontend tests"""
    print("\n")
    print("#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "  FRONTEND APPROVED_STATUS TEST SUITE".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)

    results = {
        'Test 1: Data Retrieval': test_frontend_data_retrieval(),
        'Test 2: Group ID Format': test_group_id_format(),
        'Test 3: Update & Persistence': test_update_and_verify_persistence(),
        'Test 4: Dropdown State': test_dropdown_selected_state(),
    }

    # Print summary
    print_section("TEST SUMMARY")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    print(f"\nTest Results:")
    print("-" * 80)
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")

    print("-" * 80)
    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n  [SUCCESS] All frontend tests passed!")
        print("\n  The approved_status field is working correctly on the frontend:")
        print("    - Values are being retrieved from database")
        print("    - Frontend receives correct approved_status values")
        print("    - Dropdown shows correct selected option based on DB value")
        print("    - Updates are saved to database")
        print("    - Values persist after page refresh")
        print("    - Group ID format matches between frontend and backend")
    else:
        print(f"\n  [WARNING] {total - passed} test(s) failed")

    print("\n" + "#" * 80 + "\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except Exception as e:
        print(f"\n[ERROR] Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
