import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.cache import cache

print("Clearing all cache...")
cache.clear()
print("Cache cleared successfully!")
print("\nYou can now refresh the browser page and the compliance status warning should be gone.")
