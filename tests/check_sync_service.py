"""
Check if the background sync service is running and start it if needed
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.cache import cache
from main.services.scheduled_sync_service import start_scheduled_sync_service
from main.models import SystemSettings

print("=" * 80)
print("BACKGROUND SYNC SERVICE STATUS")
print("=" * 80)
print()

# Check system settings
settings = SystemSettings.get_settings()
print("System Settings:")
print(f"  Auto Sync Enabled: {settings.auto_sync_enabled}")
print(f"  SQL Server Enabled: {settings.sql_server_enabled}")
print(f"  Google Sheets Enabled: {settings.google_sheets_enabled}")
print(f"  Sync Interval: {settings.sync_interval_hours} hours")
print()

# Check service status
running = cache.get('scheduled_sync_service:running')
heartbeat = cache.get('scheduled_sync_service:heartbeat')

print("Service Status:")
print(f"  Running: {running}")
print(f"  Last Heartbeat: {heartbeat}")
print()

if not running:
    print("[WARNING] Background sync service is NOT running!")
    print()

    if settings.auto_sync_enabled:
        response = input("Auto-sync is enabled. Start the service now? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            print("\nStarting background sync service...")
            success, message = start_scheduled_sync_service()
            if success:
                print(f"[OK] {message}")
                print("\nThe service is now running in the background.")
                print("It will automatically sync:")
                print("  - SQL Server inspections")
                print("  - Google Sheets clients")
                print(f"  Every {settings.sync_interval_hours} hours")
            else:
                print(f"[ERROR] {message}")
        else:
            print("\n[INFO] Service not started. You can start it from the Settings page in the web UI.")
    else:
        print("[INFO] Auto-sync is disabled in system settings.")
        print("      Enable it from the Settings page to use automatic background sync.")
else:
    print("[OK] Background sync service is running!")
    print("     Inspections will be automatically synced from SQL Server.")

print()
print("=" * 80)
