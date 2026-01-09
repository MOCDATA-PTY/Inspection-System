"""
Clean up EGGS inspections with empty product names
These were synced due to the bug in the SQL query (now fixed)
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 80)
print("CLEANUP: EGGS INSPECTIONS WITH EMPTY PRODUCT NAMES")
print("=" * 80)
print()

# Find all EGGS inspections with empty product names
bad_eggs = FoodSafetyAgencyInspection.objects.filter(
    commodity='EGGS',
    product_name__in=['', None]
)

count = bad_eggs.count()
print(f"Found {count} EGGS inspections without product names")
print()

if count == 0:
    print("[OK] No bad EGGS inspections to clean up!")
else:
    print("Sample of inspections to be deleted:")
    for i, insp in enumerate(bad_eggs[:10], 1):
        print(f"  {i}. {insp.unique_inspection_id} | {insp.date_of_inspection} | {insp.inspector_name} | {insp.client_name}")

    if count > 10:
        print(f"  ... and {count - 10} more")

    print()
    print("[WARNING] These inspections will be PERMANENTLY DELETED")
    print("They have no product name and provide no useful data")
    print()

    response = input(f"Delete all {count} incomplete EGGS inspections? (yes/no): ").strip().lower()

    if response in ['yes', 'y']:
        print(f"\nDeleting {count} inspections...")
        bad_eggs.delete()
        print(f"[OK] Deleted {count} incomplete EGGS inspections")
        print()

        # Show new total
        remaining = FoodSafetyAgencyInspection.objects.count()
        eggs_remaining = FoodSafetyAgencyInspection.objects.filter(commodity='EGGS').count()
        print(f"Database now has:")
        print(f"  Total inspections: {remaining}")
        print(f"  EGGS inspections: {eggs_remaining} (all with product names)")
    else:
        print("\n[CANCELLED] No inspections deleted")

print()
print("=" * 80)
