import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.scheduled_sync_service import ScheduledSyncService
from django.core.cache import cache
from django.utils import timezone

def test_inspection_sync():
    """Test the inspection sync service directly"""

    print("\nTesting Inspection Sync Service...")
    print("=" * 80)

    # Clear any existing progress/result
    cache.delete('sync_progress')
    cache.delete('sync_result')

    print("\n1. Initializing ScheduledSyncService...")
    try:
        sync_service = ScheduledSyncService()
        print("   [OK] Service initialized")
    except Exception as e:
        print(f"   [ERROR] Failed to initialize: {e}")
        return

    print("\n2. Starting inspection sync (this may take a few minutes)...")
    print(f"   Start time: {timezone.now().isoformat()}")

    try:
        # This will sync inspections from SQL Server
        result = sync_service.sync_sql_server()

        print(f"\n3. Sync completed!")
        print(f"   End time: {timezone.now().isoformat()}")
        print(f"   Result: {result}")

        # Check cache for progress
        sync_progress = cache.get('sync_progress')
        if sync_progress:
            print(f"\n4. Final Progress from cache:")
            print(f"   Status: {sync_progress.get('status')}")
            print(f"   Current: {sync_progress.get('current')}")
            print(f"   Total: {sync_progress.get('total')}")
            print(f"   Percent: {sync_progress.get('percent')}%")

        # Check for inspection count
        from main.models import FoodSafetyAgencyInspection
        total_count = FoodSafetyAgencyInspection.objects.count()
        print(f"\n5. Database check:")
        print(f"   Total inspections in DB: {total_count}")

        if result:
            print("\n[OK] Sync completed successfully!")
        else:
            print("\n[ERROR] Sync returned False - check logs above for errors")

    except Exception as e:
        print(f"\n[ERROR] Sync failed with exception: {e}")
        import traceback
        traceback.print_exc()

        # Check if error is in cache
        sync_result = cache.get('sync_result')
        if sync_result:
            print(f"\nCache error: {sync_result}")

if __name__ == '__main__':
    test_inspection_sync()
