"""
Test script to verify occurrence file functionality
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import date

def test_occurrence_files():
    """Test if occurrence files are being retrieved correctly"""

    print("=" * 80)
    print("OCCURRENCE FILE TEST")
    print("=" * 80)

    # Test parameters
    client_name = "Bosco Food Town"
    inspection_date = date(2025, 10, 29)

    print(f"\n1. Searching for inspections:")
    print(f"   Client: {client_name}")
    print(f"   Date: {inspection_date}")

    # Find inspections
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name=client_name,
        date_of_inspection=inspection_date
    )

    print(f"\n2. Found {inspections.count()} inspections")

    if inspections.count() == 0:
        print("   [ERROR] No inspections found!")
        return

    # Check for occurrence files
    print("\n3. Checking occurrence file paths:")
    has_occurrence = False

    for inspection in inspections:
        print(f"\n   Inspection ID: {inspection.id}")
        print(f"   Product: {inspection.product_name}")

        # Check occurrence_file field
        if hasattr(inspection, 'occurrence_file') and inspection.occurrence_file:
            print(f"   [YES] Has occurrence_file: {inspection.occurrence_file}")
            print(f"      File path: {inspection.occurrence_file.path if hasattr(inspection.occurrence_file, 'path') else 'N/A'}")
            print(f"      File exists: {os.path.exists(inspection.occurrence_file.path) if hasattr(inspection.occurrence_file, 'path') else False}")
            has_occurrence = True
        else:
            print(f"   [NO] No occurrence_file field or file is None")

    # Check media directory for occurrence files
    print("\n4. Checking media directory for occurrence files:")
    media_root = os.path.join(os.path.dirname(__file__), 'media', 'inspection', '2025', 'October')

    if os.path.exists(media_root):
        print(f"   Media root: {media_root}")

        # Look for occurrence files
        occurrence_files = []
        for root, dirs, files in os.walk(media_root):
            for file in files:
                if 'occurrence' in file.lower() and client_name.replace(' ', '_').lower() in root.lower():
                    file_path = os.path.join(root, file)
                    occurrence_files.append(file_path)
                    print(f"    Found: {file_path}")

        if not occurrence_files:
            print(f"    No occurrence files found in media directory")
    else:
        print(f"    Media root doesn't exist: {media_root}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)

    if has_occurrence:
        print(" Occurrence files found in database")
    else:
        print(" No occurrence files in database")

    if occurrence_files:
        print(f" {len(occurrence_files)} occurrence file(s) found in media directory")
    else:
        print(" No occurrence files found in media directory")

    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("=" * 80)

    if has_occurrence and occurrence_files:
        print(" Fix is working! Occurrence files are being saved and can be retrieved.")
    elif occurrence_files and not has_occurrence:
        print("  Files exist but not linked to inspections in database")
        print("   Check if the upload view is properly updating the inspection records")
    elif has_occurrence and not occurrence_files:
        print("  Database has references but files are missing")
        print("   Files may have been deleted or path is wrong")
    else:
        print(" No occurrence files found anywhere")
        print("   Upload may have failed or files are being saved to wrong location")

if __name__ == "__main__":
    test_occurrence_files()
