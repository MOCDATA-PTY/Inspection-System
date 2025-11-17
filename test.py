"""
Find inspection with client name "-." and show what's in its directory
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection


def find_dash_inspection():
    """Find inspection with client name '-.' and show its files"""

    print("\n" + "="*100)
    print("SEARCHING FOR INSPECTION WITH CLIENT NAME '-.'")
    print("="*100 + "\n")

    # Search for inspection with client name "-."
    inspections = FoodSafetyAgencyInspection.objects.filter(client_name="-.")

    print(f"Found {inspections.count()} inspection(s) with client name '-.'")

    if inspections.count() == 0:
        print("\nNo inspections found with that client name.")
        return

    # Show each inspection
    for idx, inspection in enumerate(inspections, start=1):
        print(f"\n{'-'*100}")
        print(f"INSPECTION #{idx}")
        print(f"{'-'*100}")
        print(f"Remote ID: {inspection.remote_id}")
        print(f"Client Name: '{inspection.client_name}'")
        print(f"Internal Account Code: {inspection.internal_account_code or 'N/A'}")
        print(f"Commodity: {inspection.commodity or 'N/A'}")
        print(f"Date: {inspection.date_of_inspection or 'N/A'}")
        print(f"Inspector: {inspection.inspector_name or 'N/A'}")

        # Try to find files in media folder
        media_root = settings.MEDIA_ROOT

        # Possible folder names
        possible_folders = [
            os.path.join(media_root, 'inspection', '2025', 'November', '-'),
            os.path.join(media_root, 'inspection', '2025', 'November', '-.'),
            os.path.join(media_root, 'inspection', '2025', 'October', '-'),
            os.path.join(media_root, 'inspection', '2025', 'October', '-.'),
        ]

        print(f"\nSearching for files in media folder...")
        found_files = False

        for folder in possible_folders:
            if os.path.exists(folder):
                print(f"\nFound folder: {folder}")
                found_files = True

                # List all files recursively
                for root, dirs, files in os.walk(folder):
                    if files:
                        relative_path = os.path.relpath(root, media_root)
                        print(f"\n  Directory: {relative_path}")
                        for file in files:
                            file_path = os.path.join(root, file)
                            file_size = os.path.getsize(file_path)
                            size_kb = file_size / 1024
                            print(f"    - {file} ({size_kb:.2f} KB)")

        # Also search entire media folder for any "-" related folders
        print(f"\nSearching entire media folder for any folders with '-' in name...")
        inspection_base = os.path.join(media_root, 'inspection')

        if os.path.exists(inspection_base):
            for year_folder in os.listdir(inspection_base):
                year_path = os.path.join(inspection_base, year_folder)
                if os.path.isdir(year_path):
                    for month_folder in os.listdir(year_path):
                        month_path = os.path.join(year_path, month_folder)
                        if os.path.isdir(month_path):
                            for client_folder in os.listdir(month_path):
                                # Check if folder name is just "-" or "-." or similar
                                if client_folder in ['-', '-.', '-_']:
                                    client_path = os.path.join(month_path, client_folder)
                                    print(f"\n  Found suspicious folder: {os.path.relpath(client_path, media_root)}")
                                    found_files = True

                                    # List all files in this folder
                                    for root, dirs, files in os.walk(client_path):
                                        if files:
                                            relative_path = os.path.relpath(root, media_root)
                                            print(f"    Directory: {relative_path}")
                                            for file in files:
                                                file_path = os.path.join(root, file)
                                                file_size = os.path.getsize(file_path)
                                                size_kb = file_size / 1024
                                                print(f"      - {file} ({size_kb:.2f} KB)")

        if not found_files:
            print("\n  No files found in media folder for this inspection.")

    print(f"\n{'='*100}")
    print("SEARCH COMPLETE")
    print("="*100 + "\n")


if __name__ == "__main__":
    try:
        find_dash_inspection()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
