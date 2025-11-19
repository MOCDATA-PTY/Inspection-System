"""
Find and fix all client names with 'mobile-' prefix that break compliance document detection
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection
from django.db.models import Q

def find_and_fix_mobile_prefix_names():
    """Find all client names with mobile- prefix and fix them"""

    print("=" * 100)
    print("FINDING AND FIXING MOBILE- PREFIX IN CLIENT NAMES")
    print("=" * 100)
    print()

    # Find all inspections with client names starting with 'mobile-'
    mobile_inspections = FoodSafetyAgencyInspection.objects.filter(
        Q(client_name__istartswith='mobile-')
    )

    print(f"Found {mobile_inspections.count()} inspections with 'mobile-' prefix in client name")
    print()

    if mobile_inspections.count() == 0:
        print("✓ No inspections found with 'mobile-' prefix in database")
        print()
        print("The issue might be in the JavaScript/frontend code, not the database.")
        print("Checking media folders for any 'mobile-' prefixed folders...")
        print()

        # Check media folders
        inspection_folder = os.path.join(settings.MEDIA_ROOT, 'inspection')
        if os.path.exists(inspection_folder):
            mobile_folders = []
            for year in os.listdir(inspection_folder):
                year_path = os.path.join(inspection_folder, year)
                if os.path.isdir(year_path):
                    for month in os.listdir(year_path):
                        month_path = os.path.join(year_path, month)
                        if os.path.isdir(month_path):
                            for client_folder in os.listdir(month_path):
                                if client_folder.startswith('mobile-'):
                                    mobile_folders.append(os.path.join(year, month, client_folder))

            if mobile_folders:
                print(f"Found {len(mobile_folders)} folders with 'mobile-' prefix:")
                print("-" * 100)
                for folder in mobile_folders:
                    print(f"  - {folder}")
                print()
                print("These folders should be renamed to remove the 'mobile-' prefix")
            else:
                print("✓ No folders found with 'mobile-' prefix")

        return

    # Group by client name to see unique names
    unique_mobile_names = mobile_inspections.values_list('client_name', flat=True).distinct()

    print("Unique client names with 'mobile-' prefix:")
    print("-" * 100)
    for name in unique_mobile_names:
        count = mobile_inspections.filter(client_name=name).count()
        cleaned_name = name.replace('mobile-', '', 1)  # Remove first occurrence
        print(f"  '{name}' ({count} inspections) → '{cleaned_name}'")
    print()

    # Ask for confirmation
    response = input("Do you want to fix these names by removing 'mobile-' prefix? (yes/no): ").strip().lower()

    if response != 'yes':
        print("Operation cancelled")
        return

    print()
    print("=" * 100)
    print("FIXING CLIENT NAMES")
    print("=" * 100)
    print()

    fixed_count = 0
    for inspection in mobile_inspections:
        old_name = inspection.client_name
        new_name = old_name.replace('mobile-', '', 1)

        inspection.client_name = new_name
        inspection.save()

        fixed_count += 1
        print(f"✓ Fixed: '{old_name}' → '{new_name}' (Inspection ID: {inspection.id})")

    print()
    print("=" * 100)
    print(f"DONE - Fixed {fixed_count} inspections")
    print("=" * 100)
    print()
    print("Please restart Gunicorn:")
    print("  sudo systemctl restart gunicorn")
    print()
    print("And clear Redis cache:")
    print("  redis-cli FLUSHALL")

if __name__ == '__main__':
    find_and_fix_mobile_prefix_names()
