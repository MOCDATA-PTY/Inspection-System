"""
Clear OneDrive service cache
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.cache import cache

print("Clearing OneDrive service cache...")

# Clear OneDrive running status
cache.delete('onedrive_direct_service:running')
print("  - Cleared: onedrive_direct_service:running")

# Clear OneDrive stats
cache.delete('onedrive_direct_service:stats')
print("  - Cleared: onedrive_direct_service:stats")

print("\nOneDrive cache cleared successfully!")
print("OneDrive will no longer auto-start with Django")
