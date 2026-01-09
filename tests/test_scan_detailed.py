"""
Test the scan_inspection_folders function in detail to see exact output structure
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from pathlib import Path
from main.views.core_views import scan_inspection_folders

print("=" * 100)
print("DETAILED TEST - EXACT OUTPUT STRUCTURE")
print("=" * 100)
print()

client_name = "Roots Butchery Tzaneen"
media_root = Path(settings.MEDIA_ROOT)
base_path = media_root / "inspection" / "2025" / "November" / client_name

seen_files = set()
files_list = scan_inspection_folders(str(base_path), seen_files)

print("Raw output from scan_inspection_folders():")
print("-" * 100)
print(json.dumps(files_list, indent=2, default=str))
print()

print("=" * 100)
print("COMPLIANCE FILES DETAIL")
print("=" * 100)

if 'compliance' in files_list:
    compliance_files = files_list['compliance']
    print(f"Total compliance files: {len(compliance_files)}")
    print()

    for i, file_dict in enumerate(compliance_files, 1):
        print(f"File {i}:")
        for key, value in file_dict.items():
            print(f"  {key}: {value}")
        print()
else:
    print("WARNING: No 'compliance' key in results!")

print("=" * 100)
print("TEST COMPLETE")
print("=" * 100)
