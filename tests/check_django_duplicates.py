"""
Check if Django database actually has duplicates right now
"""
import os
import sys
import django

sys.path.insert(0, '/root/Inspection-System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Count

print("=" * 80)
print("CHECKING DJANGO DATABASE FOR DUPLICATES")
print("=" * 80)

total = FoodSafetyAgencyInspection.objects.count()
print(f"\nTotal records in Django: {total:,}")

# Check for duplicates by (commodity, remote_id)
duplicates = FoodSafetyAgencyInspection.objects.values('commodity', 'remote_id').annotate(
    count=Count('id')
).filter(count__gt=1).order_by('-count')

duplicate_count = duplicates.count()

if duplicate_count == 0:
    print(f"\n✓ No duplicates found")
    print(f"  All {total:,} records are unique")
else:
    print(f"\n❌ Found {duplicate_count:,} duplicate (commodity, remote_id) pairs!")

    # Calculate how many extra records
    extra_records = sum(dup['count'] - 1 for dup in duplicates)
    unique_records = total - extra_records

    print(f"\n  Unique inspections: {unique_records:,}")
    print(f"  Duplicate records: {extra_records:,}")
    print(f"  Total in database: {total:,}")

    print(f"\n❌ This means {extra_records:,} records should be deleted!")

    print(f"\nTop 10 duplicates:")
    print(f"{'Commodity':<10} {'Remote ID':<10} {'Count':<10} {'Should Be':<10}")
    print("-" * 45)

    for dup in duplicates[:10]:
        commodity = dup['commodity']
        remote_id = dup['remote_id']
        count = dup['count']

        print(f"{commodity:<10} {remote_id:<10} {count:<10} 1")

    # Show details of first duplicate
    if duplicates:
        first_dup = duplicates[0]
        commodity = first_dup['commodity']
        remote_id = first_dup['remote_id']

        print(f"\n{'='*80}")
        print(f"DETAILED LOOK AT FIRST DUPLICATE: {commodity}-{remote_id}")
        print(f"{'='*80}")

        dup_records = FoodSafetyAgencyInspection.objects.filter(
            commodity=commodity,
            remote_id=remote_id
        )

        print(f"\nFound {dup_records.count()} records for this inspection:")
        print(f"\n{'ID':<8} {'Product':<30} {'Client':<30} {'GPS':<25}")
        print("-" * 100)

        for record in dup_records:
            prod = (record.product_name or 'N/A')[:28]
            client = (record.client_name or 'N/A')[:28]
            gps = f"({record.latitude}, {record.longitude})"[:23]

            print(f"{record.id:<8} {prod:<30} {client:<30} {gps:<25}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

if duplicate_count == 0:
    print(f"\n✓ Django database is clean - no duplicates")
    print(f"  SQL Server returns 3,719 rows")
    print(f"  Django has {total:,} rows")

    if total != 3719:
        print(f"\n❓ But counts don't match! Difference: {abs(total - 3719):,}")
        print(f"   Possible reasons:")
        print(f"   - Sync hasn't run since server restart")
        print(f"   - Different time ranges in query")
        print(f"   - Data changed between tests")
else:
    print(f"\n❌ Django database HAS duplicates!")
    print(f"  SQL Server returns 3,719 unique rows (correct)")
    print(f"  Django has {total:,} rows with {duplicate_count:,} duplicates")
    print(f"\n  Root cause: Django is creating duplicate records during sync")
    print(f"  This means:")
    print(f"  1. Sync is running multiple times, OR")
    print(f"  2. Composite key constraint isn't enforcing, OR")
    print(f"  3. Multiple workers are syncing simultaneously")

print("=" * 80)
