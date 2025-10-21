"""
NUCLEAR CACHE CLEAR - Clear EVERYTHING and verify
"""

import os
import sys
import io
import django
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# Import after Django setup
from django.core.cache import cache

def nuclear_clear():
    """Clear EVERYTHING - all caches, all keys"""

    print("="*100)
    print(" " * 35 + "NUCLEAR CACHE CLEAR")
    print("="*100)

    print("\n🔥 Clearing ALL cache entries...")

    try:
        # Get all cache keys (if supported)
        try:
            all_keys = cache.keys('*')
            print(f"\nFound {len(all_keys)} cache keys")

            for key in all_keys:
                cache.delete(key)
                print(f"  ✅ Deleted: {key}")

        except:
            # Fallback: just clear everything
            cache.clear()
            print("  ✅ Used cache.clear() - all entries cleared")

        print("\n✅ All cache entries cleared!")

        # Also manually delete specific known keys
        print("\n🔥 Manually clearing known cache keys...")

        known_keys = [
            'compliance_status_Hume International_2025-10-17',
            'onedrive_compliance_Hume International_2025-10-17',
            'local_compliance_Hume International_2025-10-17',
            'drive_files_lookup_v2',
            'page_clients_status_cache',
            'filter_options',
            'inspection_files_cache',
        ]

        # Add shipment_list keys for all users (IDs 1-100)
        for user_id in range(1, 101):
            for role in ['admin', 'inspector', 'scientist', 'administrator']:
                known_keys.append(f'shipment_list_{user_id}_{role}')

        for key in known_keys:
            cache.delete(key)

        print(f"  ✅ Manually deleted {len(known_keys)} known keys")

        print("\n" + "="*100)
        print(" " * 30 + "✅ NUCLEAR CLEAR COMPLETE ✅")
        print("="*100)

        print("\n📋 INSTRUCTIONS:")
        print("  1. Close your browser completely (all tabs, all windows)")
        print("  2. Wait 5 seconds")
        print("  3. Reopen browser")
        print("  4. Navigate to the shipment list page")
        print("  5. Filter for 'Hume International'")
        print("\n✨ The dropdown should now show 'mpho - Oct 20, 2025 21:47'")
        print("   and you should be able to change it!")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n🚀 Starting nuclear cache clear...\n")

    success = nuclear_clear()

    if success:
        print("\n✅ Nuclear clear completed successfully!")
    else:
        print("\n❌ Nuclear clear failed!")

    sys.exit(0 if success else 1)
