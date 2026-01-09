"""
Enable background sync and start the service
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import SystemSettings
from main.services.scheduled_sync_service import scheduled_sync_service, get_scheduled_sync_service_status


def enable_auto_sync():
    """Enable auto sync in system settings"""
    print("\n" + "="*80)
    print("  ENABLING BACKGROUND SYNC")
    print("="*80)

    try:
        # Get or create system settings
        settings, created = SystemSettings.objects.get_or_create(pk=1)

        if created:
            print("\n[INFO] Created new SystemSettings")

        # Update settings
        settings.auto_sync_enabled = True
        settings.sync_interval_hours = 24  # Sync every 24 hours
        settings.google_sheets_enabled = True
        settings.sql_server_enabled = True
        settings.save()

        print("\n[SUCCESS] System Settings Updated:")
        print(f"  Auto Sync Enabled: {settings.auto_sync_enabled}")
        print(f"  Sync Interval: {settings.sync_interval_hours} hours")
        print(f"  Google Sheets Enabled: {settings.google_sheets_enabled}")
        print(f"  SQL Server Enabled: {settings.sql_server_enabled}")

        return True

    except Exception as e:
        print(f"\n[ERROR] Failed to enable auto sync: {e}")
        import traceback
        traceback.print_exc()
        return False


def start_background_service():
    """Start the background sync service"""
    print("\n" + "="*80)
    print("  STARTING BACKGROUND SERVICE")
    print("="*80)

    try:
        # Check current status
        status = get_scheduled_sync_service_status()

        if status.get('is_running', False):
            print("\n[INFO] Service is already running!")
            return True

        # Start the service
        print("\n[ACTION] Starting background sync service...")
        success, message = scheduled_sync_service.start_background_service()

        if success:
            print(f"\n[SUCCESS] {message}")
            print("\nThe service will now:")
            print("  1. Run in the background automatically")
            print("  2. Sync Google Sheets and SQL Server every 24 hours")
            print("  3. Auto-restart if Django server restarts")
            print("  4. Keep running even after page refreshes")
            return True
        else:
            print(f"\n[FAILED] {message}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Failed to start service: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_service_running():
    """Verify the service is running"""
    print("\n" + "="*80)
    print("  VERIFICATION")
    print("="*80)

    try:
        import time
        print("\n[INFO] Waiting 2 seconds for service to initialize...")
        time.sleep(2)

        status = get_scheduled_sync_service_status()

        print("\nService Status:")
        print(f"  Running: {status.get('is_running', False)}")
        print(f"  Auto Sync Enabled: {status.get('auto_sync_enabled', False)}")

        if status.get('is_running', False):
            print("\n[SUCCESS] Background sync service is running!")
            print("\nNext sync times:")

            next_sync_times = status.get('next_sync_times', {})
            for sync_type, next_time in next_sync_times.items():
                if next_time:
                    print(f"  {sync_type}: {next_time}")
                else:
                    print(f"  {sync_type}: Will run at next check")

            return True
        else:
            print("\n[WARNING] Service may not be running yet")
            print("  - Check Django console for errors")
            print("  - Service should auto-start on next page load")
            return False

    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        return False


def main():
    print("\n" + "#"*80)
    print("#" + " "*78 + "#")
    print("#" + "  ENABLE & START BACKGROUND SYNC SERVICE".center(78) + "#")
    print("#" + " "*78 + "#")
    print("#"*80)

    # Step 1: Enable auto sync in settings
    if not enable_auto_sync():
        print("\n[FAILED] Could not enable auto sync")
        return

    # Step 2: Start the background service
    if not start_background_service():
        print("\n[FAILED] Could not start background service")
        return

    # Step 3: Verify service is running
    verify_service_running()

    # Summary
    print("\n" + "="*80)
    print("  SETUP COMPLETE")
    print("="*80)

    print("\nBackground sync is now ENABLED and RUNNING!")
    print("\nWhat happens next:")
    print("  - Google Sheets sync: Every 24 hours")
    print("  - SQL Server sync: Every 24 hours")
    print("  - Syncs client data and inspection data automatically")
    print("  - No manual intervention needed!")

    print("\nTo check status at any time:")
    print("  python test_background_sync.py")

    print("\nTo run a manual sync:")
    print("  Go to Settings page -> Manual Sync button")

    print("\n" + "#"*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Script failed: {e}")
        import traceback
        traceback.print_exc()
