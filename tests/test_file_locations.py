#!/usr/bin/env python
"""Test to find where uploaded files are actually going"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from datetime import datetime
import re

print("=" * 100)
print("FILE LOCATION DIAGNOSTIC TEST")
print("=" * 100)

# Test with a recent inspection
test_client = "Food Lover's Market - Knysna"
test_date = datetime(2025, 11, 26).date()

print(f"\nTest client: {test_client}")
print(f"Test date: {test_date}")

# Check settings
inspection_base = os.path.join(settings.MEDIA_ROOT, 'inspection')
print(f"\n1. File storage path (MEDIA_ROOT/inspection): {inspection_base}")
print(f"   Absolute path: {os.path.abspath(inspection_base)}")
print(f"   Exists: {os.path.exists(inspection_base)}")

# Get year and month
year = test_date.strftime('%Y')
month = test_date.strftime('%B')
print(f"\n2. Year/Month path: {year}/{month}")

# Test folder name sanitization (same as backend)
def create_folder_name(name):
    if not name:
        return "unknown_client"
    clean_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)
    clean_name = clean_name.replace(' ', '_').replace('-', '_')
    clean_name = re.sub(r'_+', '_', clean_name)
    clean_name = clean_name.strip('_').lower()
    return clean_name or "unknown_client"

sanitized = create_folder_name(test_client)
name_with_spaces = test_client.replace("'", ' ')
sanitized_apostrophe = create_folder_name(name_with_spaces)

print(f"\n3. Client name variations:")
print(f"   Original: {test_client}")
print(f"   Sanitized: {sanitized}")
print(f"   With apostrophe replaced: {sanitized_apostrophe}")

# Check all possible paths
parent_path = os.path.join(inspection_base, year, month)
print(f"\n4. Parent path: {parent_path}")
print(f"   Exists: {os.path.exists(parent_path)}")

if os.path.exists(parent_path):
    print(f"\n5. Folders in {parent_path}:")
    try:
        folders = [f for f in os.listdir(parent_path) if os.path.isdir(os.path.join(parent_path, f))]
        for folder in sorted(folders):
            print(f"   - {folder}")

            # Check if this could be our client
            folder_lower = folder.lower()
            if 'food' in folder_lower or 'lover' in folder_lower or 'knysna' in folder_lower:
                print(f"     ^^^ POSSIBLE MATCH!")

                # Check what's inside
                folder_path = os.path.join(parent_path, folder)
                print(f"     Contents:")
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isdir(item_path):
                        # Check if RFI folder
                        if item.upper() in ['RFI', 'INVOICE', 'LAB', 'COMPLIANCE']:
                            file_count = len([f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))])
                            print(f"       {item}/ ({file_count} files)")
                        else:
                            print(f"       {item}/")
                    else:
                        print(f"       {item}")
    except Exception as e:
        print(f"   Error listing: {e}")
else:
    print(f"\n5. Parent path doesn't exist!")
    print(f"   Checking if year folder exists: {os.path.exists(os.path.join(inspection_base, year))}")
    if os.path.exists(os.path.join(inspection_base, year)):
        print(f"   Folders in year:")
        for folder in os.listdir(os.path.join(inspection_base, year)):
            print(f"     - {folder}")

# Check for client folders with different variations
print(f"\n6. Testing specific client folder paths:")
for variation in [sanitized, sanitized_apostrophe, test_client]:
    test_path = os.path.join(parent_path, variation)
    print(f"   {variation}:")
    print(f"     Path: {test_path}")
    print(f"     Exists: {os.path.exists(test_path)}")

    if os.path.exists(test_path):
        # Check for RFI files
        for rfi_var in ['RFI', 'rfi']:
            rfi_path = os.path.join(test_path, rfi_var)
            if os.path.exists(rfi_path):
                files = [f for f in os.listdir(rfi_path) if os.path.isfile(os.path.join(rfi_path, f))]
                print(f"     {rfi_var}/ folder exists with {len(files)} files")
                if files:
                    print(f"       Files: {files}")

# Search for ANY recent files uploaded today
print(f"\n7. Searching for files uploaded today in {inspection_base}:")
today = datetime.now().date()
recent_files = []

def find_recent_files(path, max_depth=4, current_depth=0):
    if current_depth > max_depth or not os.path.exists(path):
        return []

    files = []
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                # Check if modified today
                mtime = datetime.fromtimestamp(os.path.getmtime(item_path)).date()
                if mtime == today:
                    files.append(item_path)
            elif os.path.isdir(item_path):
                files.extend(find_recent_files(item_path, max_depth, current_depth + 1))
    except Exception as e:
        pass
    return files

recent = find_recent_files(inspection_base)
if recent:
    print(f"   Found {len(recent)} files modified today:")
    for f in recent[:10]:  # Show first 10
        rel_path = os.path.relpath(f, inspection_base)
        size = os.path.getsize(f)
        print(f"   - {rel_path} ({size} bytes)")
else:
    print("   No files found from today")

print("\n" + "=" * 100)
print("END OF DIAGNOSTIC")
print("=" * 100)
