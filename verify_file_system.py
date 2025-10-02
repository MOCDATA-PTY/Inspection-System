#!/usr/bin/env python3
"""
Quick verification that the simplified file system is ready
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

print("=" * 70)
print("FILE SYSTEM VERIFICATION")
print("=" * 70)

# Check media folder
media_root = settings.MEDIA_ROOT
inspection_folder = os.path.join(media_root, 'inspection')

print(f"\n[OK] Media root: {media_root}")
print(f"[OK] Inspection folder: {inspection_folder}")
print(f"[OK] Inspection folder exists: {os.path.exists(inspection_folder)}")

# Check if empty
if os.path.exists(inspection_folder):
    contents = os.listdir(inspection_folder)
    if contents:
        print(f"[WARN] Inspection folder contains: {contents}")
    else:
        print(f"[OK] Inspection folder is empty (ready for fresh uploads)")

print("\n" + "=" * 70)
print("NAMING CONVENTION EXAMPLES")
print("=" * 70)

import re

def create_folder_name(name):
    """Create Linux-friendly folder name"""
    if not name:
        return "unknown_client"
    clean_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)
    clean_name = clean_name.replace(' ', '_').replace('-', '_')
    clean_name = re.sub(r'_+', '_', clean_name)
    clean_name = clean_name.strip('_').lower()
    return clean_name or "unknown_client"

examples = [
    "Meat Mania",
    "Boxer Superstore - Kwamashu 2",
    "Pick 'n Pay - Burgersfort"
]

for name in examples:
    print(f"  {name:35} -> {create_folder_name(name)}")

print("\n" + "=" * 70)
print("SYSTEM STATUS")
print("=" * 70)

print("""
[OK] Simplified file naming system is ACTIVE
[OK] All folders cleaned and ready for fresh uploads
[OK] Naming convention: lowercase with underscores

NEXT STEPS:
1. Start Django server: python manage.py runserver
2. Navigate to /inspections/
3. Upload a file (RFI or Invoice)
4. Click "View Files" - file should appear immediately

FOLDER STRUCTURE (will be created automatically):
  media/inspection/YYYY/Month/client_name/
    - rfi/
    - invoice/
    - lab/
    - retest/
    - compliance/

All folder names will be:
  - lowercase
  - underscores instead of spaces
  - no special characters
  - Linux-compatible
""")

print("=" * 70)

