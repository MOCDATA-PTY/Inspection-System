"""
Test the fixed sync WITHOUT background service interference
"""
import os
import sys
import django

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from main.services.scheduled_sync_service import ScheduledSyncService, stop_scheduled_sync_service
from django.db.models import Count

print("=" * 100)
print("TESTING FIXED SYNC (NO PRODUCT SPLITTING)")
print("=" * 100)

# 1. STOP background service to prevent race conditions
print("\n1. Stopping background sync service...")
try:
    stop_scheduled_sync_service()
    print("   ✅ Background service stopped")
except Exception as e:
    print(f"   ⚠️  {e}")

# 2. Show current count
current = FoodSafetyAgencyInspection.objects.count()
print(f"\n2. Current inspections in database: {current:,}")

# 3. Run manual sync
print("\n3. Running manual SQL Server sync...")
print("=" * 100)

service = ScheduledSyncService()
success = service.sync_sql_server()

# 4. Check results
print("\n" + "=" * 100)
print("RESULTS")
print("=" * 100)

if success:
    final_count = FoodSafetyAgencyInspection.objects.count()
    print(f"\n✅ Sync completed successfully!")
    print(f"   Total inspections: {final_count:,}")

    # Check for fake IDs
    fake_ids = FoodSafetyAgencyInspection.objects.filter(remote_id__contains='_').count()
    real_ids = FoodSafetyAgencyInspection.objects.exclude(remote_id__contains='_').count()

    print(f"\n   Remote ID Analysis:")
    print(f"   - Real IDs (no underscore): {real_ids:,}")
    print(f"   - Fake IDs (with underscore): {fake_ids:,}")

    if fake_ids == 0:
        print(f"\n   ✅ SUCCESS! No product splitting - all IDs are real!")
    else:
        print(f"\n   ❌ PROBLEM! Found {fake_ids} fake IDs")

    # Check for duplicates
    duplicates = FoodSafetyAgencyInspection.objects.values('commodity', 'remote_id').annotate(
        count=Count('id')
    ).filter(count__gt=1).count()

    print(f"\n   Duplicate Check:")
    print(f"   - Duplicate (commodity, remote_id) pairs: {duplicates:,}")

    if duplicates == 0:
        print(f"   ✅ No duplicates!")
    else:
        print(f"   ❌ Found {duplicates} duplicates!")

    # Show expected vs actual
    expected = 3719
    print(f"\n   Expected Count:")
    print(f"   - SQL Server query returns: ~{expected:,} inspections")
    print(f"   - Django database has: {final_count:,} inspections")

    if 3700 <= final_count <= 3750:
        print(f"   ✅ PERFECT! Count matches expected range!")
    else:
        diff = abs(final_count - expected)
        print(f"   ⚠️  Difference: {diff:,} inspections")

    # Sample inspection with products
    sample = FoodSafetyAgencyInspection.objects.filter(
        product_name__isnull=False
    ).exclude(product_name='').first()

    if sample:
        print(f"\n   Sample Inspection:")
        print(f"   - ID: {sample.remote_id}")
        print(f"   - Client: {sample.client_name}")
        print(f"   - Products: {sample.product_name}")
        print(f"   - Date: {sample.date_of_inspection}")

        if ',' in (sample.product_name or ''):
            print(f"   ✅ Multiple products stored as comma-separated!")

else:
    print(f"\n❌ Sync failed!")

print("\n" + "=" * 100)
