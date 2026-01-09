"""
Simple sync test - manually disable auto-restart first
"""
import os
import sys
import django

# Fix encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.cache import cache
from main.models import FoodSafetyAgencyInspection
from main.services.scheduled_sync_service import ScheduledSyncService
from django.db.models import Count

print("=" * 100)
print("SIMPLE SYNC TEST - PRODUCT SPLITTING FIX")
print("=" * 100)

# Clear cache to prevent auto-restart
print("\n1. Clearing background service cache...")
cache.delete('scheduled_sync_service:running')
cache.delete('scheduled_sync_service:heartbeat')
print("   ✅ Cache cleared")

# Clear existing inspections
print("\n2. Clearing existing inspections...")
old_count = FoodSafetyAgencyInspection.objects.count()
FoodSafetyAgencyInspection.objects.all().delete()
print(f"   ✅ Deleted {old_count:,} inspections")

# Run sync
print("\n3. Running sync...")
print("=" * 100)
service = ScheduledSyncService()
success = service.sync_sql_server()

# Check results
print("\n" + "=" * 100)
print("RESULTS")
print("=" * 100)

if success:
    total = FoodSafetyAgencyInspection.objects.count()
    fake_ids = FoodSafetyAgencyInspection.objects.filter(remote_id__contains='_').count()
    real_ids = FoodSafetyAgencyInspection.objects.exclude(remote_id__contains='_').count()

    print(f"\n✅ Sync successful!")
    print(f"   Total inspections: {total:,}")
    print(f"   Real IDs (no underscore): {real_ids:,}")
    print(f"   Fake IDs (with underscore): {fake_ids:,}")

    if fake_ids == 0:
        print(f"\n   ✅ PRODUCT SPLITTING FIX WORKING!")
    else:
        print(f"\n   ❌ Still has fake IDs!")

    # Check if count is in expected range
    if 3700 <= total <= 3750:
        print(f"\n   ✅ COUNT IS CORRECT! (~3,719 expected)")
    else:
        print(f"\n   ❌ Count is {total:,}, expected ~3,719")

    # Sample with multiple products
    multi_product = FoodSafetyAgencyInspection.objects.filter(
        product_name__contains=','
    ).first()

    if multi_product:
        print(f"\n   Sample multi-product inspection:")
        print(f"   - ID: {multi_product.remote_id}")
        print(f"   - Products: {multi_product.product_name}")
        print(f"   ✅ Multiple products stored as comma-separated!")

else:
    print(f"\n❌ Sync failed!")

print("\n" + "=" * 100)
