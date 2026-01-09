"""
Clear the Google Drive files cache so it rescans with the new folder
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.cache import cache

print("Clearing Google Drive files cache...")

cache_key = 'drive_files_lookup_v3'
result = cache.delete(cache_key)

if result:
    print("[OK] Cache cleared successfully")
else:
    print("[INFO] Cache was already empty or didn't exist")

print("\nNext time the compliance pull runs, it will scan the new 2025 folder structure:")
print("  - November 2025 (with 1,403 zip files)")
print("  - October 2025")
print("  - September 2025")
print("  - And other month folders")
