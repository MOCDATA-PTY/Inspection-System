"""
FOR SERVER: Find lab file "-2025-11-03-lab.pdf" in media folder
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


def find_lab_file():
    """Find the lab file -2025-11-03-lab.pdf"""

    print("\n" + "="*100)
    print("SEARCHING FOR LAB FILE: -2025-11-03-lab.pdf")
    print("="*100 + "\n")

    media_root = settings.MEDIA_ROOT
    print(f"Media Root: {media_root}\n")

    # Search for the file in the media folder
    found_files = []

    for root, dirs, files in os.walk(media_root):
        for filename in files:
            if "-2025-11-03-lab.pdf" in filename or filename == "-2025-11-03-lab.pdf":
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, media_root)
                found_files.append({
                    'filename': filename,
                    'full_path': file_path,
                    'relative_path': relative_path
                })

    if found_files:
        print(f"Found {len(found_files)} file(s):\n")
        for f in found_files:
            print(f"  File: {f['filename']}")
            print(f"  Path: {f['relative_path']}")
            print(f"  Full: {f['full_path']}")
            print()
    else:
        print("File not found in media folder.")

    # Check if file belongs to inspections with client name '-'
    print(f"\n{'-'*100}")
    print("CHECKING INSPECTIONS WITH CLIENT NAME '-' ON NOV 14")
    print(f"{'-'*100}\n")

    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name="-",
        date_of_inspection="2025-11-14"
    )

    if inspections.exists():
        print(f"Found {inspections.count()} inspection(s) with client name '-' on Nov 14:\n")
        for idx, inspection in enumerate(inspections, 1):
            print(f"Inspection #{idx}:")
            print(f"  Remote ID: {inspection.remote_id}")
            print(f"  Client: {inspection.client_name}")
            print(f"  Date: {inspection.date_of_inspection}")
            print(f"  Commodity: {inspection.commodity}")
            print()
    else:
        print("No inspections found with client name '-' on Nov 14.")

    print("="*100 + "\n")


if __name__ == "__main__":
    try:
        find_lab_file()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
