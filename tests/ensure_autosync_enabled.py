"""
Ensure auto_sync_enabled is set to True in SystemSettings
This ensures the background sync service always starts
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import SystemSettings

print("=" * 80)
print("ENSURING AUTO-SYNC IS ALWAYS ENABLED")
print("=" * 80)
print()

# Get or create settings
settings = SystemSettings.get_settings()

print(f"Current auto_sync_enabled: {settings.auto_sync_enabled}")
print(f"Current sql_server_enabled: {settings.sql_server_enabled}")
print(f"Current google_sheets_enabled: {settings.google_sheets_enabled}")
print()

# Update to ensure all are enabled
changed = False

if not settings.auto_sync_enabled:
    settings.auto_sync_enabled = True
    changed = True
    print("[UPDATE] Set auto_sync_enabled = True")

if not settings.sql_server_enabled:
    settings.sql_server_enabled = True
    changed = True
    print("[UPDATE] Set sql_server_enabled = True")

if not settings.google_sheets_enabled:
    settings.google_sheets_enabled = True
    changed = True
    print("[UPDATE] Set google_sheets_enabled = True")

if changed:
    settings.save()
    print()
    print("[OK] Settings updated successfully!")
else:
    print("[OK] All sync settings already enabled - no changes needed")

print()
print("Background sync will ALWAYS run automatically when Django starts")
print("This ensures inspection data is never missed")
print()
print("=" * 80)
