import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.cache import cache

print("\nClearing server status cache...")

# Clear all status caches
cache.delete('status_postgresql')
cache.delete('status_sql_server')
cache.delete('status_google_sheets')

print("Done! The following cache keys have been cleared:")
print("  - status_postgresql")
print("  - status_sql_server")
print("  - status_google_sheets")
print("\nPlease refresh your dashboard to see updated status.\n")
