"""
Force reload script - Clear ALL caches and force page re-render
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

def force_reload():
    """Clear ALL caches to force complete page re-render"""

    print("="*80)
    print("FORCE RELOAD - CLEARING ALL CACHES")
    print("="*80)

    print("\n🧹 Clearing ALL cache entries...")

    try:
        # Clear the entire cache
        cache.clear()
        print("   ✅ All cache entries cleared!")

        print("\n" + "="*80)
        print("✅ CACHE COMPLETELY CLEARED!")
        print("="*80)
        print("\n🔄 NOW REFRESH YOUR BROWSER:")
        print("   1. Close ALL browser tabs")
        print("   2. Reopen the browser")
        print("   3. Go to the shipment list page")
        print("   4. The page will be re-rendered with fresh data")
        print("\n✨ The dropdown should now be enabled!")

        return True

    except Exception as e:
        print(f"\n❌ Error clearing cache: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n🚀 Starting force reload...\n")

    success = force_reload()

    if success:
        print("\n✅ Force reload completed successfully!")
    else:
        print("\n❌ Force reload failed!")

    sys.exit(0 if success else 1)
