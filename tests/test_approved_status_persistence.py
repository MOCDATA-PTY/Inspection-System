"""
Test to diagnose why approved_status reverts to PENDING after page refresh
"""

import os
import django
import sys
from datetime import datetime
import re

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.test import RequestFactory


def normalize_client_name(name):
    """Normalize client name (same as backend)"""
    return re.sub(r'[^a-zA-Z0-9]', '', (name or '')).lower()


def simulate_update_group_approved(group_id, approved_status):
    """Simulate the update_group_approved view function"""
    print(f"\n{'='*80}")
    print(f"SIMULATING UPDATE")
    print(f"{'='*80}")
    print(f"Group ID: {group_id}")
    print(f"New Status: {approved_status}")

    # Parse group_id (same logic as view)
    if '_' not in group_id:
        print("ERROR: Invalid group ID format")
        return False

    parts = group_id.split('_')
    if len(parts) < 2:
        print("ERROR: Invalid group ID format")
        return False

    date_part = parts[-1]
    client_name_parts = parts[:-1]
    client_name = '_'.join(client_name_parts)

    print(f"\nParsed from group_id:")
    print(f"  Client Name: {client_name}")
    print(f"  Date Part: {date_part}")

    # Convert date string to date object
    date_of_inspection = None
    for fmt in ('%Y-%m-%d', '%Y%m%d'):
        try:
            date_of_inspection = datetime.strptime(date_part, fmt).date()
            break
        except ValueError:
            continue

    if not date_of_inspection:
        print(f"ERROR: Invalid date format: {date_part}")
        return False

    print(f"  Parsed Date: {date_of_inspection}")

    # Find matching inspections (same logic as view)
    raw_key = normalize_client_name(client_name)
    print(f"  Normalized Key: {raw_key}")

    candidate_qs = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection=date_of_inspection
    )
    print(f"  Candidates on date: {candidate_qs.count()}")

    matching_ids = [ins.id for ins in candidate_qs if normalize_client_name(ins.client_name) == raw_key]
    inspections = FoodSafetyAgencyInspection.objects.filter(id__in=matching_ids)

    print(f"\nMatching Inspections: {inspections.count()}")
    for insp in inspections:
        print(f"  ID {insp.id}: {insp.client_name} - Current Status: {insp.approved_status}")

    if not inspections.exists():
        print("ERROR: No matching inspections found!")
        return False

    # Update
    print(f"\nUpdating {inspections.count()} inspections to {approved_status}...")
    updated_count = inspections.update(approved_status=approved_status)
    print(f"Updated: {updated_count} inspections")

    # Verify update
    print("\nVerifying update in database...")
    for insp_id in matching_ids:
        refreshed = FoodSafetyAgencyInspection.objects.get(id=insp_id)
        print(f"  ID {refreshed.id}: Status = {refreshed.approved_status}")
        if refreshed.approved_status != approved_status:
            print(f"    ❌ ERROR: Status is {refreshed.approved_status}, expected {approved_status}")
            return False

    print("\n✅ Update successful and verified!")
    return True


def simulate_page_load(client_name, date_of_inspection):
    """Simulate loading the page and retrieving data"""
    print(f"\n{'='*80}")
    print(f"SIMULATING PAGE LOAD")
    print(f"{'='*80}")
    print(f"Client: {client_name}")
    print(f"Date: {date_of_inspection}")

    # Find inspections the same way the view does
    normalized_client = normalize_client_name(client_name)

    candidate_qs = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection=date_of_inspection
    )

    matching_ids = [ins.id for ins in candidate_qs if normalize_client_name(ins.client_name) == normalized_client]
    inspections = FoodSafetyAgencyInspection.objects.filter(id__in=matching_ids)

    print(f"\nInspections retrieved for display:")
    print(f"  Total: {inspections.count()}")

    for insp in inspections:
        print(f"\n  Inspection ID: {insp.id}")
        print(f"    Client: {insp.client_name}")
        print(f"    Date: {insp.date_of_inspection}")
        print(f"    Approved Status: {insp.approved_status}")
        print(f"    (This is what the dropdown will show)")

    return inspections


def check_for_sync_or_reset():
    """Check if there's any sync process that might reset the value"""
    print(f"\n{'='*80}")
    print(f"CHECKING FOR SYNC/RESET PROCESSES")
    print(f"{'='*80}")

    # Check if there are any scheduled tasks or signals
    import glob

    # Look for sync files
    sync_files = glob.glob('main/services/*sync*.py')
    print(f"\nFound {len(sync_files)} sync service files:")
    for f in sync_files:
        print(f"  - {f}")

    # Look for management commands
    mgmt_files = glob.glob('main/management/commands/*.py')
    print(f"\nFound {len(mgmt_files)} management command files")

    print("\nNOTE: Check if any of these might be resetting approved_status field")


def main():
    print("\n" + "#"*80)
    print("#" + " "*78 + "#")
    print("#" + "  APPROVED_STATUS PERSISTENCE DIAGNOSTIC".center(78) + "#")
    print("#" + " "*78 + "#")
    print("#"*80)

    # Use the actual group from the console log
    group_id = "Marang_Layers_Farming_Enterprises_t_a_Maranga_Eggs_20251119"
    client_name = "Marang Layers Farming Enterprises t/a Maranga Eggs"
    date_str = "2025-11-19"
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

    print("\n\nTEST SCENARIO:")
    print("  User changes dropdown to APPROVED")
    print("  System saves successfully")
    print("  User refreshes page")
    print("  Dropdown shows PENDING again")
    print("\nLet's trace through this scenario step by step...\n")

    # STEP 1: Get current state
    print(f"\n{'='*80}")
    print(f"STEP 1: INITIAL STATE")
    print(f"{'='*80}")
    initial_inspections = simulate_page_load(client_name, date_obj)
    initial_statuses = {insp.id: insp.approved_status for insp in initial_inspections}

    # STEP 2: User changes dropdown to APPROVED
    print(f"\n\n{'='*80}")
    print(f"STEP 2: USER CHANGES DROPDOWN TO APPROVED")
    print(f"{'='*80}")
    success = simulate_update_group_approved(group_id, 'APPROVED')

    if not success:
        print("\n❌ UPDATE FAILED - This is the problem!")
        return

    # STEP 3: Simulate page refresh (load data again)
    print(f"\n\n{'='*80}")
    print(f"STEP 3: USER REFRESHES PAGE")
    print(f"{'='*80}")
    refreshed_inspections = simulate_page_load(client_name, date_obj)

    # Compare
    print(f"\n\n{'='*80}")
    print(f"ANALYSIS")
    print(f"{'='*80}")

    all_match = True
    for insp in refreshed_inspections:
        if insp.approved_status != 'APPROVED':
            print(f"❌ PROBLEM FOUND!")
            print(f"   Inspection ID {insp.id} has status: {insp.approved_status}")
            print(f"   Expected: APPROVED")
            all_match = False

    if all_match:
        print("✅ All inspections show APPROVED status after refresh")
        print("\nThe database persistence is working correctly!")
        print("\nIf the frontend still shows PENDING, the issue is:")
        print("  1. Caching in the browser")
        print("  2. The frontend is not reading the correct field")
        print("  3. There's a sync process running after page load")
    else:
        print("\n❌ Database is NOT persisting the value correctly!")
        print("\nPossible causes:")
        print("  1. Group ID matching is incorrect")
        print("  2. Transaction is rolling back")
        print("  3. There's a sync process overwriting the value")

    # STEP 4: Restore original values
    print(f"\n\n{'='*80}")
    print(f"STEP 4: RESTORING ORIGINAL VALUES")
    print(f"{'='*80}")
    for insp_id, original_status in initial_statuses.items():
        FoodSafetyAgencyInspection.objects.filter(id=insp_id).update(
            approved_status=original_status
        )
        print(f"  Restored ID {insp_id} to {original_status}")

    # STEP 5: Check for sync processes
    check_for_sync_or_reset()

    print("\n" + "#"*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
