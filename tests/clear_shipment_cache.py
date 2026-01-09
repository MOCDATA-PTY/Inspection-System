#!/usr/bin/env python3
"""
Clear Shipment List Cache
==========================
Clears all cached shipment list data to show fresh inspection data.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.cache import cache


def clear_all_shipment_caches():
    """Clear all shipment list related caches."""

    print(f"\n{'='*80}")
    print(f"CLEARING SHIPMENT LIST CACHES")
    print(f"{'='*80}\n")

    # Cache keys used in shipment_list view
    cache_keys = [
        'drive_files_lookup_v2',
        'page_clients_status_cache',
    ]

    # Clear known cache keys
    for key in cache_keys:
        cache.delete(key)
        print(f"Cleared: {key}")

    # Clear user-specific caches (pattern: shipment_list_{user_id}_{role})
    # We'll clear for common roles
    from django.contrib.auth.models import User

    users = User.objects.all()
    cleared_count = 0

    for user in users:
        role = getattr(user, 'role', 'unknown')
        cache_key = f"shipment_list_{user.id}_{role}"
        cache.delete(cache_key)
        cleared_count += 1

    print(f"\nCleared {cleared_count} user-specific shipment list caches")

    # Also clear any inspection-related caches
    print("\nClearing inspection-related caches...")

    # Pattern for local files cache: local_files:{client_folder}:{year_folder}:{month_folder}
    # We can't delete by pattern easily, so clear the entire cache
    cache.clear()

    print("\nFull cache cleared!")

    print(f"\n{'='*80}")
    print(f"CACHE CLEARING COMPLETE")
    print(f"{'='*80}")
    print("\nAll users will now see fresh data on next page load.")
    print("Latest inspections (Nov 26-27) should now be visible.")
    print()


if __name__ == '__main__':
    clear_all_shipment_caches()
