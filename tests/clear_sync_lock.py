import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.cache import cache

def clear_sync_locks():
    """Clear all sync locks from the cache"""

    print("Clearing sync locks...")
    print()

    # Clear client sync lock
    client_lock = cache.get('client_sync_running')
    if client_lock:
        print("  Found stuck CLIENT sync lock - clearing it")
        cache.delete('client_sync_running')
    else:
        print("  No client sync lock found")

    # Clear inspection sync lock
    inspection_lock = cache.get('inspection_sync_running')
    if inspection_lock:
        print("  Found stuck INSPECTION sync lock - clearing it")
        cache.delete('inspection_sync_running')
    else:
        print("  No inspection sync lock found")

    # Also try the background_sync_running lock
    bg_lock = cache.get('background_sync_running')
    if bg_lock:
        print("  Found stuck BACKGROUND sync lock - clearing it")
        cache.delete('background_sync_running')
    else:
        print("  No background sync lock found")

    print()
    print("All sync locks cleared successfully!")
    print("You can now try clicking 'Sync Everything' again.")

if __name__ == '__main__':
    clear_sync_locks()
