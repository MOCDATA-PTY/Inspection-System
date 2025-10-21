"""
Script to clear the compliance status cache for Hume International inspection
This will allow the "Sent" status dropdown to be enabled
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
from main.models import FoodSafetyAgencyInspection

def clear_cache_for_hume():
    """Clear compliance status cache for Hume International"""

    print("="*60)
    print("CLEARING CACHE FOR HUME INTERNATIONAL")
    print("="*60)

    try:
        # Find the Hume International inspection
        print("\n1. Searching for Hume International inspection...")

        inspection = FoodSafetyAgencyInspection.objects.filter(
            client_name__icontains='Hume International',
            date_of_inspection__year=2025,
            date_of_inspection__month=10,
            date_of_inspection__day=17
        ).first()

        if not inspection:
            print("   ❌ Hume International inspection not found!")
            return False

        print(f"   ✅ Found inspection:")
        print(f"      ID: {inspection.id}")
        print(f"      Client: {inspection.client_name}")
        print(f"      Date: {inspection.date_of_inspection}")

        # Clear compliance status cache
        print("\n2. 🔄 Clearing compliance status cache...")
        cache_key = f"compliance_status_{inspection.client_name}_{inspection.date_of_inspection}"
        cache.delete(cache_key)
        print(f"   ✅ Cleared: {cache_key}")

        onedrive_cache_key = f"onedrive_compliance_{inspection.client_name}_{inspection.date_of_inspection}"
        cache.delete(onedrive_cache_key)
        print(f"   ✅ Cleared: {onedrive_cache_key}")

        # Also clear local compliance cache
        local_cache_key = f"local_compliance_{inspection.client_name}_{inspection.date_of_inspection}"
        cache.delete(local_cache_key)
        print(f"   ✅ Cleared: {local_cache_key}")

        # Clear shipment list cache (this is the CRITICAL one!)
        print("\n3. 🔄 Clearing shipment list cache...")

        # We need to clear for all users since we don't know which user is viewing
        # Get all users to clear their shipment list cache
        from django.contrib.auth import get_user_model
        User = get_user_model()

        users = User.objects.all()
        cleared_count = 0
        for user in users:
            # Clear for each role the user might have
            for role in ['admin', 'inspector', 'scientist', 'administrator']:
                shipment_cache_key = f"shipment_list_{user.id}_{role}"
                cache.delete(shipment_cache_key)
                cleared_count += 1

        print(f"   ✅ Cleared {cleared_count} shipment list cache entries")

        # Also clear filter options and other related caches
        cache.delete("filter_options")
        cache.delete("inspection_files_cache")
        cache.delete("page_clients_status_cache")
        print(f"   ✅ Cleared filter_options, inspection_files_cache, page_clients_status_cache")

        print("\n" + "="*60)
        print("✅ CACHE CLEARED SUCCESSFULLY!")
        print("="*60)
        print("\n🔄 REFRESH YOUR BROWSER (F5) to see the updated status:")
        print("   ✅ The 'Sent Status' dropdown should now be enabled")
        print("   ✅ You should be able to select 'Sent' from the dropdown")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n🚀 Starting cache clearing process...\n")

    success = clear_cache_for_hume()

    if success:
        print("\n✅ Process completed successfully!")
        print("\n👉 NEXT STEP: Refresh your browser (F5) to see the enabled dropdown!")
    else:
        print("\n❌ Process failed. Please check the errors above.")

    sys.exit(0 if success else 1)
