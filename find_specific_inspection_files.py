#!/usr/bin/env python
"""Find all files for a specific inspection across all possible locations"""
import os
import django
import re
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

print("=" * 120)
print("FIND FILES FOR SPECIFIC INSPECTION")
print("=" * 120)

# Target inspection
TARGET_CLIENT = "Food Lover's Market - Knysna"
TARGET_DATE = datetime(2025, 11, 26).date()

print(f"\nSearching for files:")
print(f"  Client: {TARGET_CLIENT}")
print(f"  Date: {TARGET_DATE}")
print(f"  Year: {TARGET_DATE.strftime('%Y')}")
print(f"  Month: {TARGET_DATE.strftime('%B')}")

# Client name sanitization function (from backend)
def create_folder_name(name):
    if not name:
        return "unknown_client"
    clean_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)
    clean_name = clean_name.replace(' ', '_').replace('-', '_')
    clean_name = re.sub(r'_+', '_', clean_name)
    clean_name = clean_name.strip('_').lower()
    return clean_name or "unknown_client"

# Get all possible client name variations
sanitized_client = create_folder_name(TARGET_CLIENT)
name_with_apostrophe_removed = TARGET_CLIENT.replace("'", ' ')
sanitized_apostrophe = create_folder_name(name_with_apostrophe_removed)

client_variations = [
    TARGET_CLIENT,  # Original with apostrophe
    sanitized_client,  # Sanitized
    sanitized_apostrophe,  # Sanitized with apostrophe replaced
    TARGET_CLIENT.replace("'", ""),  # Apostrophe removed
    TARGET_CLIENT.lower(),  # Lowercase
    TARGET_CLIENT.replace(" ", "_"),  # Spaces to underscores
]

print(f"\n" + "=" * 120)
print("CLIENT NAME VARIATIONS TO SEARCH")
print("=" * 120)
for i, variation in enumerate(client_variations, 1):
    print(f"{i}. '{variation}'")

# Define all possible base paths to search
year = TARGET_DATE.strftime('%Y')
month = TARGET_DATE.strftime('%B')

base_paths_to_check = [
    # NEW STRUCTURE (correct)
    os.path.join(settings.MEDIA_ROOT, 'inspection', year, month),

    # OLD STRUCTURE (compliance files)
    os.path.join(settings.MEDIA_ROOT, year, month),

    # Other possible locations
    os.path.join(settings.MEDIA_ROOT, 'inspection_files', year, month),
    os.path.join(settings.MEDIA_ROOT, 'inspection', year),
    os.path.join(settings.MEDIA_ROOT, year),
]

print(f"\n" + "=" * 120)
print("BASE PATHS TO SEARCH")
print("=" * 120)
for i, path in enumerate(base_paths_to_check, 1):
    exists = os.path.exists(path)
    print(f"{i}. {path}")
    print(f"   Exists: {exists}")
    if exists:
        try:
            subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
            print(f"   Subdirectories: {len(subdirs)} - {subdirs[:5]}{'...' if len(subdirs) > 5 else ''}")
        except Exception as e:
            print(f"   Error listing: {e}")

# File types to check
file_types = ['RFI', 'rfi', 'Invoice', 'invoice', 'Lab', 'lab', 'Compliance', 'compliance']

print(f"\n" + "=" * 120)
print("SEARCHING FOR FILES")
print("=" * 120)

found_files = []

# Search all combinations
for base_path in base_paths_to_check:
    if not os.path.exists(base_path):
        continue

    for client_variation in client_variations:
        client_path = os.path.join(base_path, client_variation)

        if os.path.exists(client_path):
            print(f"\n✓ FOUND CLIENT FOLDER: {client_path}")

            # List everything in this folder
            try:
                items = os.listdir(client_path)
                print(f"  Contents ({len(items)} items):")
                for item in items:
                    item_path = os.path.join(client_path, item)
                    if os.path.isdir(item_path):
                        # Check if it's a file type folder
                        if item in file_types:
                            try:
                                files_in_type = os.listdir(item_path)
                                print(f"    📁 {item}/ - {len(files_in_type)} files")
                                for file in files_in_type:
                                    file_path = os.path.join(item_path, file)
                                    if os.path.isfile(file_path):
                                        size = os.path.getsize(file_path)
                                        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                                        print(f"       📄 {file}")
                                        print(f"          Size: {size:,} bytes")
                                        print(f"          Modified: {mtime}")
                                        print(f"          Full path: {file_path}")
                                        found_files.append({
                                            'file': file,
                                            'type': item,
                                            'path': file_path,
                                            'size': size,
                                            'modified': mtime,
                                            'client_folder': client_variation,
                                            'base_path': base_path
                                        })
                            except Exception as e:
                                print(f"    📁 {item}/ - Error: {e}")
                        else:
                            # Could be Inspection-XXX folder (old structure)
                            print(f"    📁 {item}/")
                            # Check if there's a Compliance subfolder
                            compliance_path = os.path.join(item_path, 'Compliance')
                            if os.path.exists(compliance_path):
                                print(f"       📁 Compliance/ found!")
                                try:
                                    for subitem in os.listdir(compliance_path):
                                        subitem_path = os.path.join(compliance_path, subitem)
                                        if os.path.isdir(subitem_path):
                                            files_in_comp = os.listdir(subitem_path)
                                            print(f"          📁 {subitem}/ - {len(files_in_comp)} files")
                                            for file in files_in_comp:
                                                file_path = os.path.join(subitem_path, file)
                                                if os.path.isfile(file_path):
                                                    size = os.path.getsize(file_path)
                                                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                                                    print(f"             📄 {file}")
                                                    print(f"                Size: {size:,} bytes")
                                                    print(f"                Modified: {mtime}")
                                                    print(f"                Full path: {file_path}")
                                                    found_files.append({
                                                        'file': file,
                                                        'type': f"Compliance/{subitem}",
                                                        'path': file_path,
                                                        'size': size,
                                                        'modified': mtime,
                                                        'client_folder': client_variation,
                                                        'base_path': base_path
                                                    })
                                except Exception as e:
                                    print(f"          Error reading Compliance: {e}")
                    else:
                        # File directly in client folder
                        size = os.path.getsize(item_path)
                        print(f"    📄 {item} ({size:,} bytes)")
            except Exception as e:
                print(f"  Error reading folder: {e}")

# Also search for any folder that contains "food" or "lover" or "knysna"
print(f"\n" + "=" * 120)
print("FUZZY SEARCH (folders containing 'food', 'lover', or 'knysna')")
print("=" * 120)

for base_path in base_paths_to_check:
    if not os.path.exists(base_path):
        continue

    try:
        for item in os.listdir(base_path):
            item_lower = item.lower()
            if any(keyword in item_lower for keyword in ['food', 'lover', 'knysna']):
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path):
                    print(f"\n✓ FUZZY MATCH: {item_path}")
                    print(f"  Folder name: '{item}'")
    except Exception as e:
        pass

# Summary
print(f"\n" + "=" * 120)
print("SUMMARY")
print("=" * 120)
print(f"\nTotal files found: {len(found_files)}")

if found_files:
    print(f"\nFILES BY TYPE:")
    types_count = {}
    for f in found_files:
        file_type = f['type']
        types_count[file_type] = types_count.get(file_type, 0) + 1
    for file_type, count in sorted(types_count.items()):
        print(f"  {file_type}: {count} files")

    print(f"\nFILES BY LOCATION:")
    location_count = {}
    for f in found_files:
        location = f['base_path']
        location_count[location] = location_count.get(location, 0) + 1
    for location, count in sorted(location_count.items()):
        print(f"  {location}: {count} files")

    print(f"\nMOST RECENT FILE:")
    most_recent = max(found_files, key=lambda x: x['modified'])
    print(f"  File: {most_recent['file']}")
    print(f"  Type: {most_recent['type']}")
    print(f"  Modified: {most_recent['modified']}")
    print(f"  Path: {most_recent['path']}")
else:
    print("\n❌ NO FILES FOUND!")
    print("\nPossible reasons:")
    print("  1. Files were uploaded but saved to a different location")
    print("  2. Client name sanitization created a different folder name")
    print("  3. Files are in a different year/month folder")
    print("  4. File upload failed but didn't show error")

print("\n" + "=" * 120)
print("DIAGNOSTIC COMPLETE")
print("=" * 120)
