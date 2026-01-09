"""Check background sync service configuration and status"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import SystemSettings
from django.core.cache import cache
from datetime import datetime

print("=" * 100)
print("BACKGROUND SYNC SERVICE DIAGNOSTICS")
print("=" * 100)

# Check SystemSettings
try:
    settings = SystemSettings.objects.first()
    if settings:
        print("\n[1] SYSTEM SETTINGS:")
        print(f"    auto_sync_enabled: {settings.auto_sync_enabled}")
        print(f"    sync_interval_hours: {settings.sync_interval_hours}")

        # Check if last_sync_time attribute exists
        if hasattr(settings, 'last_sync_time') and settings.last_sync_time:
            print(f"    last_sync_time: {settings.last_sync_time}")
            time_since_sync = datetime.now() - settings.last_sync_time
            hours_since = time_since_sync.total_seconds() / 3600
            print(f"    Hours since last sync: {hours_since:.2f}")
        else:
            print(f"    last_sync_time: (field not available)")
            hours_since = None
    else:
        print("\n[1] SYSTEM SETTINGS: No settings found in database!")
except Exception as e:
    print(f"\n[1] ERROR reading SystemSettings: {e}")

# Check cache values
print("\n[2] SERVICE STATUS (from cache):")
service_running = cache.get('scheduled_sync_service:running')
service_heartbeat = cache.get('scheduled_sync_service:heartbeat')

print(f"    Service Running Flag: {service_running}")
print(f"    Service Heartbeat: {service_heartbeat}")

if service_heartbeat:
    heartbeat_time = datetime.fromisoformat(service_heartbeat)
    time_since_heartbeat = datetime.now() - heartbeat_time
    print(f"    Time since heartbeat: {time_since_heartbeat.total_seconds():.1f} seconds")

    if time_since_heartbeat.total_seconds() > 120:
        print("    [WARNING] Service hasn't sent heartbeat in over 2 minutes - may be stopped!")
    else:
        print("    [OK] Service is alive")
else:
    print("    [WARNING] No heartbeat found - service may not be running!")

# Check if sync is currently running
sync_in_progress = cache.get('scheduled_sync_service:sync_in_progress')
print(f"\n[3] SYNC STATUS:")
print(f"    Sync in progress: {sync_in_progress}")

# Diagnose issues
print("\n" + "=" * 100)
print("[4] DIAGNOSIS:")
print("=" * 100)

if not settings:
    print("[X] PROBLEM: No SystemSettings record exists")
    print("   FIX: Create SystemSettings with auto_sync_enabled=True")
elif not settings.auto_sync_enabled:
    print("[X] PROBLEM: auto_sync_enabled is False")
    print("   FIX: Set auto_sync_enabled to True in SystemSettings")
elif not service_running:
    print("[X] PROBLEM: Service is not running")
    print("   FIX: Start the service by restarting Django application")
elif not service_heartbeat or (service_heartbeat and time_since_heartbeat.total_seconds() > 120):
    print("[X] PROBLEM: Service started but appears to have stopped")
    print("   FIX: Check Django logs for errors, restart application")
elif settings.sync_interval_hours > 1:
    print(f"[!] NOTICE: Sync interval is {settings.sync_interval_hours} hours (not 1 hour)")
    print(f"   The service IS working, but it only syncs every {settings.sync_interval_hours} hours")
    print(f"   To sync every hour, set sync_interval_hours to 1")
else:
    print("[OK] Everything looks configured correctly")
    if hours_since and hours_since < settings.sync_interval_hours:
        print(f"  Service is waiting for interval to pass ({hours_since:.2f}/{settings.sync_interval_hours} hours)")

print("=" * 100)
