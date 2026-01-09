import os, django, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.cache import cache
from main.services.scheduled_sync_service import get_scheduled_sync_service_status, scheduled_sync_service
from main.models import SystemSettings

# Check settings
settings = SystemSettings.objects.first()
print("\nSystem Settings:")
print(f"  Auto Sync Enabled: {settings.auto_sync_enabled}")
print(f"  Sync Interval: {settings.sync_interval_hours} hours")

# Check service status
status = get_scheduled_sync_service_status()
print("\nService Status:")
print(f"  Running: {status.get('is_running', False)}")
print(f"  Auto Sync Enabled: {status.get('auto_sync_enabled', False)}")

# Check cache
is_running_cache = cache.get('scheduled_sync_service:running', False)
print(f"  Cache says running: {is_running_cache}")

# Try to start if not running
if not status.get('is_running', False):
    print("\nAttempting to start service...")
    try:
        import io, sys
        sys.stdout = io.StringIO()  # Suppress Unicode print errors
        success, message = scheduled_sync_service.start_background_service()
        sys.stdout = sys.__stdout__
        print(f"  Started: {success}")
        if not success:
            print(f"  Message: {message}")
    except Exception as e:
        sys.stdout = sys.__stdout__
        print(f"  Error: {e}")

    # Check again
    status = get_scheduled_sync_service_status()
    print(f"\nAfter start attempt:")
    print(f"  Running: {status.get('is_running', False)}")
else:
    print("\nService is already running!")

print("\nDone!")
