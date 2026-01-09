import os
import sys
import django
import time

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.scheduled_sync_service import scheduled_sync_service
from django.core.cache import cache
from main.models import FoodSafetyAgencyInspection

def test_server_sync():
    """Test inspection sync on the server with detailed logging"""

    print("\n" + "="*80)
    print("SERVER SYNC TEST - Direct Inspection Sync")
    print("="*80)

    # Clear cache (including sync locks to allow fresh sync)
    print("\n1. Clearing cache and sync locks...")
    cache.delete('sync_progress')
    cache.delete('sync_result')
    cache.delete('inspection_sync_lock')
    cache.delete('sync_google_sheets_lock')
    cache.delete('sync_sql_server_lock')
    print("   Cache cleared")

    # Get initial count
    initial_count = FoodSafetyAgencyInspection.objects.count()
    print(f"\n2. Initial inspection count: {initial_count}")

    # Use global service instance (don't create a new one!)
    print("\n3. Using global ScheduledSyncService instance...")
    try:
        sync_service = scheduled_sync_service
        print("   Service ready")
    except Exception as e:
        print(f"   [ERROR] Failed to get service: {e}")
        import traceback
        traceback.print_exc()
        return

    # Run sync with timing
    print("\n4. Starting sync (this will show all progress)...")
    print(f"   Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)

    start_time = time.time()

    try:
        result = sync_service.sync_sql_server()

        elapsed = time.time() - start_time

        print("-" * 80)
        print(f"\n5. Sync completed!")
        print(f"   End time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Duration: {elapsed:.2f} seconds")
        print(f"   Result: {result}")

        # Get final count
        final_count = FoodSafetyAgencyInspection.objects.count()
        print(f"\n6. Final inspection count: {final_count}")
        print(f"   Change: {final_count - initial_count:+d}")

        # Check cache
        sync_progress = cache.get('sync_progress')
        sync_result = cache.get('sync_result')

        if sync_progress:
            print(f"\n7. Cache progress: {sync_progress}")
        if sync_result:
            print(f"   Cache result: {sync_result}")

        if result:
            print("\n" + "="*80)
            print("[SUCCESS] Sync completed successfully!")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("[FAILED] Sync returned False")
            print("="*80)

    except Exception as e:
        elapsed = time.time() - start_time

        print("-" * 80)
        print(f"\n[ERROR] Sync failed after {elapsed:.2f} seconds")
        print(f"   Error: {e}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()

        # Check cache for error
        sync_result = cache.get('sync_result')
        if sync_result:
            print(f"\nCache error: {sync_result}")

if __name__ == '__main__':
    test_server_sync()
