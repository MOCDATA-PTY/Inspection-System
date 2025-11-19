"""
Debug script to diagnose why compliance documents aren't being detected
Run this on the server to see exactly what's happening
"""
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection

# Import the create_folder_name function
import sys
sys.path.append('/root/Inspection-System/main/views')
from core_views import create_folder_name

def debug_compliance_detection():
    """Debug why compliance documents aren't showing for specific inspection"""

    print("=" * 100)
    print("COMPLIANCE DOCUMENT DETECTION DEBUG")
    print("=" * 100)
    print()

    # Test with Roots Butchery Tzaneen on 2025-11-07
    client_name = "Roots Butchery Tzaneen"
    inspection_date = "2025-11-07"

    print(f"Testing: {client_name} on {inspection_date}")
    print()

    # Show what the code does
    print("-" * 100)
    print("STEP 1: What the code looks for")
    print("-" * 100)

    date_obj = django.utils.dateparse.parse_date(inspection_date)
    year_folder = date_obj.strftime('%Y')
    month_folder = date_obj.strftime('%B')
    converted_client_folder = create_folder_name(client_name)

    print(f"Original client name: '{client_name}'")
    print(f"Converted by create_folder_name(): '{converted_client_folder}'")
    print(f"Year folder: {year_folder}")
    print(f"Month folder: {month_folder}")
    print()

    # Build paths
    base_inspection_path = os.path.join(
        settings.MEDIA_ROOT,
        'inspection',
        year_folder,
        month_folder
    )

    print(f"Base inspection path: {base_inspection_path}")
    print(f"Base path exists: {os.path.exists(base_inspection_path)}")
    print()

    # Check what actually exists
    print("-" * 100)
    print("STEP 2: What actually exists on disk")
    print("-" * 100)

    if os.path.exists(base_inspection_path):
        actual_folders = os.listdir(base_inspection_path)
        print(f"Folders in {month_folder} {year_folder}:")
        for folder in sorted(actual_folders):
            folder_path = os.path.join(base_inspection_path, folder)
            if os.path.isdir(folder_path):
                print(f"  - '{folder}'")
        print()
    else:
        print("Base inspection path doesn't exist!")
        print()

    # Try both paths
    print("-" * 100)
    print("STEP 3: Testing path lookups")
    print("-" * 100)

    # Path with original name
    path_with_original = os.path.join(base_inspection_path, client_name)
    print(f"Path with original name: {path_with_original}")
    print(f"Exists: {os.path.exists(path_with_original)}")

    if os.path.exists(path_with_original):
        subfolders = os.listdir(path_with_original)
        print(f"Subfolders: {subfolders}")
    print()

    # Path with converted name
    path_with_converted = os.path.join(base_inspection_path, converted_client_folder)
    print(f"Path with converted name: {path_with_converted}")
    print(f"Exists: {os.path.exists(path_with_converted)}")

    if os.path.exists(path_with_converted):
        subfolders = os.listdir(path_with_converted)
        print(f"Subfolders: {subfolders}")
    print()

    # Determine which path to use
    if os.path.exists(path_with_original):
        client_path = path_with_original
        print(f"USING: Original name path")
    elif os.path.exists(path_with_converted):
        client_path = path_with_converted
        print(f"USING: Converted name path")
    else:
        print("ERROR: Neither path exists!")
        client_path = None
    print()

    # Check for compliance folder
    if client_path:
        print("-" * 100)
        print("STEP 4: Looking for compliance documents")
        print("-" * 100)

        compliance_path = os.path.join(client_path, 'compliance')
        compliance_path_caps = os.path.join(client_path, 'Compliance')

        print(f"Checking lowercase 'compliance': {compliance_path}")
        print(f"Exists: {os.path.exists(compliance_path)}")

        print(f"Checking capitalized 'Compliance': {compliance_path_caps}")
        print(f"Exists: {os.path.exists(compliance_path_caps)}")
        print()

        # Show all subfolders
        print("All subfolders in client path:")
        for item in os.listdir(client_path):
            item_path = os.path.join(client_path, item)
            if os.path.isdir(item_path):
                file_count = len([f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))])
                print(f"  - '{item}/' ({file_count} files)")
        print()

        # Check which compliance folder exists and show contents
        compliance_folder_to_use = None
        if os.path.exists(compliance_path_caps):
            compliance_folder_to_use = compliance_path_caps
            print(f"Found capitalized 'Compliance' folder")
        elif os.path.exists(compliance_path):
            compliance_folder_to_use = compliance_path
            print(f"Found lowercase 'compliance' folder")

        if compliance_folder_to_use:
            print(f"Contents of compliance folder:")
            for root, dirs, files in os.walk(compliance_folder_to_use):
                level = root.replace(compliance_folder_to_use, '').count(os.sep)
                indent = '  ' * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = '  ' * (level + 1)
                for file in files:
                    file_path = os.path.join(root, file)
                    size_kb = os.path.getsize(file_path) / 1024
                    print(f"{subindent}- {file} ({size_kb:.1f} KB)")
        else:
            print("No compliance folder found!")

    print()
    print("=" * 100)
    print("DIAGNOSIS COMPLETE")
    print("=" * 100)
    print()
    print("The issue is likely:")
    print("1. Folder name mismatch (spaces vs underscores)")
    print("2. Case sensitivity ('Compliance' vs 'compliance')")
    print("3. Files in different location than expected")

if __name__ == '__main__':
    debug_compliance_detection()
