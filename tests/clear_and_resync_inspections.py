"""
Clear old duplicate inspection data and resync from SQL Server
Run this ONCE to remove old duplicates and get fresh data
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 80)
print("CLEAR AND RESYNC INSPECTION DATA")
print("=" * 80)

# Check current count
current_count = FoodSafetyAgencyInspection.objects.count()
print(f"\nCurrent inspection records: {current_count:,}")

# Confirm before deleting
print("\nThis will DELETE all inspection records and they will be re-synced")
print("from Google Sheets on the next scheduled sync.")
print("\nAre you sure you want to continue? (yes/no)")

response = input("> ").strip().lower()

if response == 'yes':
    print("\nDeleting all inspection records...")
    deleted_count, _ = FoodSafetyAgencyInspection.objects.all().delete()
    print(f"[OK] Deleted {deleted_count:,} inspection records")

    remaining = FoodSafetyAgencyInspection.objects.count()
    print(f"[OK] Remaining records: {remaining:,}")

    print("\n" + "=" * 80)
    print("DONE!")
    print("=" * 80)
    print("""
Next steps:
1. The inspection table is now empty
2. Wait for the next scheduled Google Sheets sync (or trigger it manually)
3. The sync will use the fixed query (no more GPS duplicates)
4. You should see ~3,717 inspections instead of 6,883

The fixed query ensures:
- One inspection with 9 GPS records = 1 row (not 9)
- Directions will sync properly
- No more duplicate inspections
""")
else:
    print("\n[CANCELLED] No data was deleted")

print("=" * 80)
