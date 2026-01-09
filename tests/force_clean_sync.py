"""
Force a clean sync - delete ALL old data and resync with OUTER APPLY query
"""
import os
import sys
import django

sys.path.insert(0, '/root/Inspection-System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from main.services.scheduled_sync_service import ScheduledSyncService

print("=" * 80)
print("FORCING CLEAN SYNC WITH OUTER APPLY QUERY")
print("=" * 80)

# 1. Show current count
current = FoodSafetyAgencyInspection.objects.count()
print(f"\nCurrent records in Django: {current:,}")

# 2. DELETE ALL
print(f"\nDeleting all {current:,} old records...")
FoodSafetyAgencyInspection.objects.all().delete()
print(f"✓ Deleted all records")

# 3. Verify deletion
after_delete = FoodSafetyAgencyInspection.objects.count()
print(f"✓ Current count after delete: {after_delete:,}")

# 4. Sync with OUTER APPLY query
print(f"\n{'='*80}")
print(f"SYNCING WITH FIXED OUTER APPLY QUERY")
print(f"{'='*80}")

sync_service = ScheduledSyncService()

print(f"\nRunning SQL Server sync...")
success = sync_service.sync_sql_server()

if success:
    # 5. Check final count
    final_count = FoodSafetyAgencyInspection.objects.count()

    print(f"\n{'='*80}")
    print(f"SYNC COMPLETE")
    print(f"{'='*80}")
    print(f"\n✓ Sync successful!")
    print(f"  Records in Django: {final_count:,}")
    print(f"  Expected from SQL Server: 3,719")

    if final_count == 3719:
        print(f"\n✅ PERFECT! Counts match exactly!")
        print(f"   The OUTER APPLY fix is working correctly!")
    elif 3700 <= final_count <= 3750:
        print(f"\n✓ GOOD! Count is within expected range")
        print(f"  Small difference likely due to new data since test")
    else:
        print(f"\n❌ WARNING! Count doesn't match")
        print(f"  Difference: {abs(final_count - 3719):,}")

    # Check for duplicates
    from django.db.models import Count
    duplicates = FoodSafetyAgencyInspection.objects.values('commodity', 'remote_id').annotate(
        count=Count('id')
    ).filter(count__gt=1).count()

    if duplicates == 0:
        print(f"\n✓ No duplicates - composite key working!")
    else:
        print(f"\n❌ Found {duplicates:,} duplicates!")

else:
    print(f"\n❌ SYNC FAILED!")
    print(f"  Check server logs for errors")

print(f"\n{'='*80}")
