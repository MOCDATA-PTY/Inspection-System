#!/usr/bin/env python
"""Find all media files and identify ones in unexpected locations"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

print("=" * 100)
print("MEDIA FILES LOCATION SCANNER")
print("=" * 100)

# Get base paths
media_root = settings.MEDIA_ROOT
expected_inspection_path = os.path.join(media_root, 'inspection')

print(f"\nMEDIA_ROOT: {media_root}")
print(f"Expected inspection path: {expected_inspection_path}")
print(f"\nScanning for all files...\n")

# Track file locations
files_by_location = {
    'correct_location': [],      # Files in MEDIA_ROOT/inspection/YEAR/MONTH/CLIENT/TYPE/
    'wrong_location': [],         # Files in unexpected locations
    'inspection_files_folder': [], # Files in old 'inspection_files' folder
    'other_media': []             # Other media files (profile pics, etc)
}

# Scan the entire MEDIA_ROOT
def scan_directory(path, depth=0, max_depth=10):
    """Recursively scan directory and categorize files"""
    if depth > max_depth or not os.path.exists(path):
        return

    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)

            if os.path.isfile(item_path):
                # Get file info
                rel_path = os.path.relpath(item_path, media_root)
                size = os.path.getsize(item_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(item_path))

                file_info = {
                    'path': item_path,
                    'rel_path': rel_path,
                    'size': size,
                    'modified': mtime,
                    'name': item
                }

                # Categorize the file
                if item_path.startswith(expected_inspection_path):
                    # Check if it follows correct structure: inspection/YEAR/MONTH/CLIENT/TYPE/
                    parts = rel_path.split(os.sep)
                    if len(parts) >= 5 and parts[0] == 'inspection':
                        # parts[1] should be year (e.g., "2025")
                        # parts[2] should be month (e.g., "November")
                        # parts[3] should be client name
                        # parts[4] should be file type (RFI, Invoice, etc)
                        if parts[1].isdigit() and len(parts[1]) == 4:
                            files_by_location['correct_location'].append(file_info)
                        else:
                            files_by_location['wrong_location'].append(file_info)
                    else:
                        files_by_location['wrong_location'].append(file_info)
                elif 'inspection_files' in item_path.lower():
                    files_by_location['inspection_files_folder'].append(file_info)
                else:
                    files_by_location['other_media'].append(file_info)

            elif os.path.isdir(item_path):
                scan_directory(item_path, depth + 1, max_depth)

    except PermissionError:
        pass
    except Exception as e:
        print(f"Error scanning {path}: {e}")

# Start scanning
print("Scanning MEDIA_ROOT...")
scan_directory(media_root)

# Print results
print("\n" + "=" * 100)
print("SCAN RESULTS")
print("=" * 100)

# 1. Files in correct location
print(f"\n1. ✅ FILES IN CORRECT LOCATION (inspection/YEAR/MONTH/CLIENT/TYPE/)")
print(f"   Count: {len(files_by_location['correct_location'])}")
print("-" * 100)
if files_by_location['correct_location']:
    # Show last 20 files
    for file_info in files_by_location['correct_location'][-20:]:
        print(f"   {file_info['rel_path']}")
        print(f"      Size: {file_info['size']:,} bytes | Modified: {file_info['modified']}")
    if len(files_by_location['correct_location']) > 20:
        print(f"   ... and {len(files_by_location['correct_location']) - 20} more files")

# 2. Files in wrong location (within inspection folder but wrong structure)
print(f"\n2. ⚠️  FILES IN WRONG LOCATION (inspection/* but not following structure)")
print(f"   Count: {len(files_by_location['wrong_location'])}")
print("-" * 100)
if files_by_location['wrong_location']:
    for file_info in files_by_location['wrong_location']:
        print(f"   {file_info['rel_path']}")
        print(f"      Size: {file_info['size']:,} bytes | Modified: {file_info['modified']}")
else:
    print("   None found")

# 3. Files in old inspection_files folder
print(f"\n3. ❌ FILES IN OLD 'inspection_files' FOLDER (WRONG!)")
print(f"   Count: {len(files_by_location['inspection_files_folder'])}")
print("-" * 100)
if files_by_location['inspection_files_folder']:
    for file_info in files_by_location['inspection_files_folder']:
        print(f"   {file_info['rel_path']}")
        print(f"      Size: {file_info['size']:,} bytes | Modified: {file_info['modified']}")
else:
    print("   None found")

# 4. Other media files
print(f"\n4. ℹ️  OTHER MEDIA FILES (profile pics, etc.)")
print(f"   Count: {len(files_by_location['other_media'])}")
print("-" * 100)
if files_by_location['other_media']:
    # Just show first 10
    for file_info in files_by_location['other_media'][:10]:
        print(f"   {file_info['rel_path']}")
    if len(files_by_location['other_media']) > 10:
        print(f"   ... and {len(files_by_location['other_media']) - 10} more files")

# Summary
print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"✅ Correct location:          {len(files_by_location['correct_location'])} files")
print(f"⚠️  Wrong location (inspect):  {len(files_by_location['wrong_location'])} files")
print(f"❌ Old inspection_files:       {len(files_by_location['inspection_files_folder'])} files")
print(f"ℹ️  Other media:               {len(files_by_location['other_media'])} files")
print(f"\nTotal files scanned:         {sum(len(v) for v in files_by_location.values())} files")

# Check if expected path exists
print("\n" + "=" * 100)
print("PATH CHECKS")
print("=" * 100)
print(f"MEDIA_ROOT exists:           {os.path.exists(media_root)}")
print(f"inspection/ folder exists:   {os.path.exists(expected_inspection_path)}")

# List immediate subdirectories of MEDIA_ROOT
if os.path.exists(media_root):
    print(f"\nFolders in MEDIA_ROOT:")
    try:
        for item in sorted(os.listdir(media_root)):
            item_path = os.path.join(media_root, item)
            if os.path.isdir(item_path):
                file_count = sum(1 for _, _, files in os.walk(item_path) for _ in files)
                print(f"   - {item}/ ({file_count} files)")
    except Exception as e:
        print(f"   Error listing: {e}")

# List year folders in inspection/
if os.path.exists(expected_inspection_path):
    print(f"\nYear folders in inspection/:")
    try:
        for item in sorted(os.listdir(expected_inspection_path)):
            item_path = os.path.join(expected_inspection_path, item)
            if os.path.isdir(item_path):
                file_count = sum(1 for _, _, files in os.walk(item_path) for _ in files)
                print(f"   - {item}/ ({file_count} files)")
    except Exception as e:
        print(f"   Error listing: {e}")

print("\n" + "=" * 100)
print("SCAN COMPLETE")
print("=" * 100)
