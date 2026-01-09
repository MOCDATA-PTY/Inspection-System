"""
Test the scan_inspection_folders function locally with fake data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from pathlib import Path

# Import the function from core_views
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'main', 'views'))

print("=" * 100)
print("TESTING scan_inspection_folders() FUNCTION LOCALLY")
print("=" * 100)
print()

# Test the scan_inspection_folders function
client_name = "Roots Butchery Tzaneen"
inspection_date = "2025-11-07"

# Build the path
media_root = Path(settings.MEDIA_ROOT)
base_path = media_root / "inspection" / "2025" / "November" / client_name

print(f"Testing: {client_name}")
print(f"Base path: {base_path}")
print(f"Base path exists: {base_path.exists()}")
print()

# Check what's in the Inspection-2784 folder
if base_path.exists():
    inspection_folders = [d for d in base_path.iterdir() if d.name.lower().startswith('inspection-') and d.is_dir()]
    print(f"Found {len(inspection_folders)} inspection folder(s):")
    for folder in inspection_folders:
        print(f"  - {folder.name}")
        # Check what's inside
        subfolders = [d for d in folder.iterdir() if d.is_dir()]
        print(f"    Subfolders: {[d.name for d in subfolders]}")

        # Check specifically for Compliance folder (case sensitive)
        compliance_caps = folder / "Compliance"
        compliance_lower = folder / "compliance"

        print(f"    'Compliance' (capitalized) exists: {compliance_caps.exists()}")
        print(f"    'compliance' (lowercase) exists: {compliance_lower.exists()}")

        if compliance_caps.exists():
            print(f"    Contents of Compliance folder:")
            for item in compliance_caps.rglob('*.pdf'):
                print(f"      - {item.relative_to(compliance_caps)}")
    print()

# Now test the actual scan_inspection_folders function
print("=" * 100)
print("CALLING scan_inspection_folders() FUNCTION")
print("=" * 100)
print()

# Read the function directly from core_views.py and test it
from main.views.core_views import scan_inspection_folders

seen_files = set()
files_list = scan_inspection_folders(str(base_path), seen_files)

print("Results from scan_inspection_folders():")
print("-" * 100)
for category, files in files_list.items():
    print(f"{category}: {len(files)} files")
    if files:
        for file in files[:5]:  # Show first 5
            print(f"  - {file.get('file_name', 'N/A')}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more files")
print()

print("=" * 100)
print("TEST COMPLETE")
print("=" * 100)
