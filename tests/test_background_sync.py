import os
import sys
import django
import threading
import time

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.cache import cache
from main.services.scheduled_sync_service import ScheduledSyncService

def test_background_sync():
    """Test sync running in background thread (like production)"""

    print("\nTesting Background Thread Sync (Production Simulation)...")
    print("=" * 80)

    # Clear cache
    cache.delete('sync_progress')
    cache.delete('sync_result')
    cache.delete('inspection_sync_lock')

    # Simulate the background thread approach
    def run_sync():
        """This runs in background thread - same as production"""
        try:
            print("\n[THREAD] Background sync started")

            # Acquire lock
            sync_lock_key = 'inspection_sync_lock'
            cache.set(sync_lock_key, time.time(), 900)
            print("[THREAD] Lock acquired")

            # Initialize service
            sync_service = ScheduledSyncService()
            print("[THREAD] Service initialized")

            # Run sync
            print("[THREAD] Starting SQL Server sync...")
            result = sync_service.sync_sql_server()

            if result:
                # Get count
                from main.models import FoodSafetyAgencyInspection
                total_count = FoodSafetyAgencyInspection.objects.count()

                print(f"[THREAD] Sync successful! Total: {total_count}")

                # Store result
                cache.set('sync_result', {
                    'success': True,
                    'message': f'Successfully synced {total_count} inspections!',
                    'created_count': total_count,
                    'total_processed': total_count
                }, 300)
            else:
                print("[THREAD] Sync failed!")
                cache.set('sync_result', {
                    'success': False,
                    'error': 'Sync returned False'
                }, 300)

        except Exception as e:
            print(f"[THREAD] Exception: {e}")
            import traceback
            traceback.print_exc()

            cache.set('sync_result', {
                'success': False,
                'error': str(e)
            }, 300)

        finally:
            # Release lock
            cache.delete(sync_lock_key)
            print("[THREAD] Lock released")

    # Start background thread (daemon=True like production)
    print("\n1. Starting background thread...")
    thread = threading.Thread(target=run_sync)
    thread.daemon = True
    thread.start()

    print("2. Thread started, now polling for progress...\n")

    # Simulate frontend polling
    poll_count = 0
    max_polls = 120  # 2 minutes max (1 second intervals)

    while poll_count < max_polls:
        poll_count += 1
        time.sleep(1)

        # Check progress
        sync_progress = cache.get('sync_progress')
        sync_result = cache.get('sync_result')

        if sync_result:
            print(f"\n[POLL {poll_count}] Sync completed!")
            print(f"   Result: {sync_result}")
            break
        elif sync_progress:
            status = sync_progress.get('status', 'unknown')
            current = sync_progress.get('current', 0)
            total = sync_progress.get('total', 0)
            percent = sync_progress.get('percent', 0)

            print(f"[POLL {poll_count}] Status: {status} | Progress: {current}/{total} ({percent}%)")
        else:
            print(f"[POLL {poll_count}] No progress yet...")

    if poll_count >= max_polls:
        print("\n[TIMEOUT] Polling timed out after 2 minutes")

    # Wait for thread to finish
    print("\nWaiting for thread to complete...")
    thread.join(timeout=5)

    if thread.is_alive():
        print("[WARNING] Thread still running after timeout")
    else:
        print("[OK] Thread completed")

    # Final check
    final_result = cache.get('sync_result')
    if final_result:
        print(f"\nFinal Result: {final_result}")
    else:
        print("\n[ERROR] No final result in cache")

if __name__ == '__main__':
    test_background_sync()
