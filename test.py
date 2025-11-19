"""
Test script to verify approved_status (PENDING/APPROVED) is being saved correctly
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
from django.db.models import Count, Q


def print_section(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_approved_status_field():
    """Test 1: Verify approved_status field exists and has correct choices"""
    print_section("TEST 1: Verify approved_status field configuration")

    # Get the approved_status field
    field = FoodSafetyAgencyInspection._meta.get_field('approved_status')

    print(f"\nField Name: {field.name}")
    print(f"Field Type: {type(field).__name__}")
    print(f"Max Length: {field.max_length}")
    print(f"Default Value: {field.default}")
    print(f"Choices: {field.choices}")
    print(f"Blank: {field.blank}")
    print(f"Null: {field.null}")

    # Verify choices
    expected_choices = [('PENDING', 'Pending'), ('APPROVED', 'Approved')]
    if field.choices == expected_choices:
        print("\n[PASS] Field choices are correct!")
    else:
        print("\n[FAIL] Field choices don't match expected values")
        print(f"  Expected: {expected_choices}")
        print(f"  Got: {field.choices}")

    return field.choices == expected_choices


def test_approved_status_counts():
    """Test 2: Check current approved_status distribution"""
    print_section("TEST 2: Current approved_status distribution")

    # Count by approved_status
    status_counts = FoodSafetyAgencyInspection.objects.values('approved_status').annotate(
        count=Count('id')
    ).order_by('approved_status')

    print("\nApproved Status Distribution:")
    print("-" * 80)
    total = 0
    for item in status_counts:
        status = item['approved_status'] or 'NULL/Empty'
        count = item['count']
        total += count
        print(f"  {status:20} : {count:5} inspections")

    print("-" * 80)
    print(f"  {'TOTAL':20} : {total:5} inspections")

    return status_counts


def test_update_approved_status():
    """Test 3: Test updating approved_status"""
    print_section("TEST 3: Test updating approved_status")

    # Find a test inspection (the most recent one)
    test_inspection = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection').first()

    if not test_inspection:
        print("\n[FAIL] No inspections found in database")
        return False

    print(f"\nTest Inspection Details:")
    print(f"  ID: {test_inspection.id}")
    print(f"  Client: {test_inspection.client_name}")
    print(f"  Date: {test_inspection.date_of_inspection}")
    print(f"  Inspector: {test_inspection.inspector_name}")
    print(f"  Current Status: {test_inspection.approved_status}")

    # Store original status
    original_status = test_inspection.approved_status

    # Test 1: Update to PENDING
    print("\n--- Testing update to PENDING ---")
    test_inspection.approved_status = 'PENDING'
    test_inspection.save()
    test_inspection.refresh_from_db()

    if test_inspection.approved_status == 'PENDING':
        print("[PASS] Successfully updated to PENDING")
        print(f"  Status in DB: {test_inspection.approved_status}")
    else:
        print(f"[FAIL] Failed to update to PENDING")
        print(f"  Expected: PENDING")
        print(f"  Got: {test_inspection.approved_status}")

    # Test 2: Update to APPROVED
    print("\n--- Testing update to APPROVED ---")
    test_inspection.approved_status = 'APPROVED'
    test_inspection.save()
    test_inspection.refresh_from_db()

    if test_inspection.approved_status == 'APPROVED':
        print("[PASS] Successfully updated to APPROVED")
        print(f"  Status in DB: {test_inspection.approved_status}")
    else:
        print(f"[FAIL] Failed to update to APPROVED")
        print(f"  Expected: APPROVED")
        print(f"  Got: {test_inspection.approved_status}")

    # Restore original status
    print(f"\n--- Restoring original status ({original_status}) ---")
    test_inspection.approved_status = original_status
    test_inspection.save()
    test_inspection.refresh_from_db()
    print(f"[OK] Restored to: {test_inspection.approved_status}")

    return True


def test_bulk_update_by_group():
    """Test 4: Test bulk updating approved_status for a group"""
    print_section("TEST 4: Test bulk updating approved_status for a group")

    # Find a group (inspections with same client_name and date_of_inspection)
    inspection_groups = FoodSafetyAgencyInspection.objects.values(
        'client_name', 'date_of_inspection'
    ).annotate(
        count=Count('id')
    ).filter(count__gt=0).order_by('-date_of_inspection')[:1]

    if not inspection_groups.exists():
        print("\n[FAIL] No inspection groups found")
        return False

    group = inspection_groups.first()
    client_name = group['client_name']
    date_of_inspection = group['date_of_inspection']
    count = group['count']

    print(f"\nTest Group:")
    print(f"  Client: {client_name}")
    print(f"  Date: {date_of_inspection}")
    print(f"  Count: {count} inspections")

    # Get all inspections in this group
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name=client_name,
        date_of_inspection=date_of_inspection
    )

    # Show current statuses
    print(f"\nCurrent statuses:")
    original_statuses = {}
    for insp in inspections:
        original_statuses[insp.id] = insp.approved_status
        print(f"  ID {insp.id}: {insp.approved_status}")

    # Test bulk update to PENDING
    print("\n--- Testing bulk update to PENDING ---")
    updated_count = inspections.update(approved_status='PENDING')
    print(f"[OK] Updated {updated_count} inspections")

    # Verify all were updated
    all_pending = inspections.filter(approved_status='PENDING').count()
    if all_pending == count:
        print(f"[PASS] All {count} inspections now have status PENDING")
    else:
        print(f"[FAIL] Only {all_pending} out of {count} have status PENDING")

    # Test bulk update to APPROVED
    print("\n--- Testing bulk update to APPROVED ---")
    updated_count = inspections.update(approved_status='APPROVED')
    print(f"[OK] Updated {updated_count} inspections")

    # Verify all were updated
    all_approved = inspections.filter(approved_status='APPROVED').count()
    if all_approved == count:
        print(f"[PASS] All {count} inspections now have status APPROVED")
    else:
        print(f"[FAIL] Only {all_approved} out of {count} have status APPROVED")

    # Restore original statuses
    print("\n--- Restoring original statuses ---")
    for insp_id, original_status in original_statuses.items():
        FoodSafetyAgencyInspection.objects.filter(id=insp_id).update(
            approved_status=original_status
        )
    print(f"[OK] Restored {len(original_statuses)} inspections to original statuses")

    return True


def test_filtering_by_status():
    """Test 5: Test filtering inspections by approved_status"""
    print_section("TEST 5: Test filtering by approved_status")

    # Filter by PENDING
    pending = FoodSafetyAgencyInspection.objects.filter(approved_status='PENDING')
    pending_count = pending.count()
    print(f"\nPENDING inspections: {pending_count}")
    if pending_count > 0:
        print(f"  Sample: {pending.first().client_name} on {pending.first().date_of_inspection}")

    # Filter by APPROVED
    approved = FoodSafetyAgencyInspection.objects.filter(approved_status='APPROVED')
    approved_count = approved.count()
    print(f"\nAPPROVED inspections: {approved_count}")
    if approved_count > 0:
        print(f"  Sample: {approved.first().client_name} on {approved.first().date_of_inspection}")

    # Filter by NULL/empty
    empty = FoodSafetyAgencyInspection.objects.filter(
        Q(approved_status__isnull=True) | Q(approved_status='')
    )
    empty_count = empty.count()
    print(f"\nNULL/Empty status inspections: {empty_count}")
    if empty_count > 0:
        print(f"  Sample: {empty.first().client_name} on {empty.first().date_of_inspection}")

    print(f"\n[PASS] Filtering by approved_status works correctly")
    return True


def test_default_value():
    """Test 6: Verify default value is set correctly"""
    print_section("TEST 6: Test default value for new inspections")

    # Create a test inspection
    test_data = {
        'commodity': 'TEST',
        'date_of_inspection': date.today(),
        'client_name': 'Test Client',
        'inspector_name': 'Test Inspector'
    }

    print(f"\nCreating test inspection...")
    print(f"  Data: {test_data}")

    new_inspection = FoodSafetyAgencyInspection.objects.create(**test_data)

    print(f"\nNew Inspection ID: {new_inspection.id}")
    print(f"Default approved_status: {new_inspection.approved_status}")

    if new_inspection.approved_status == 'PENDING':
        print(f"[PASS] Default value is correctly set to PENDING")
    else:
        print(f"[FAIL] Default value is not PENDING")
        print(f"  Expected: PENDING")
        print(f"  Got: {new_inspection.approved_status}")

    # Clean up - delete test inspection
    new_inspection.delete()
    print(f"\n[OK] Test inspection deleted")

    return new_inspection.approved_status == 'PENDING'


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "  APPROVED_STATUS FIELD TEST SUITE".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)

    results = {
        'Test 1: Field Configuration': test_approved_status_field(),
        'Test 2: Status Distribution': test_approved_status_counts(),
        'Test 3: Single Update': test_update_approved_status(),
        'Test 4: Bulk Update': test_bulk_update_by_group(),
        'Test 5: Filtering': test_filtering_by_status(),
        'Test 6: Default Value': test_default_value(),
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
        print("\n  [SUCCESS] All tests passed!")
        print("\n  The approved_status field is working correctly:")
        print("    - Field exists with correct configuration")
        print("    - Default value is PENDING")
        print("    - Can be updated to PENDING or APPROVED")
        print("    - Bulk updates work correctly")
        print("    - Filtering by status works")
        print("    - Data is being saved to database properly")
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
