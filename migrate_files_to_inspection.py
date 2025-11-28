#!/usr/bin/env python
"""
Migrate all media files to unified inspection/ folder structure

OLD STRUCTURE: media/2025/November/CLIENT/Inspection-XXX/Compliance/TYPE/file.pdf
NEW STRUCTURE: media/inspection/2025/November/CLIENT/Compliance/file.pdf

This script will:
1. Find all files in the old structure
2. Move them to the new inspection/ structure
3. Clean up empty old directories
4. Provide dry-run option to preview changes
"""
import os
import django
import shutil
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

# Configuration
DRY_RUN = True  # Set to False to actually move files
REMOVE_EMPTY_DIRS = True  # Remove empty directories after migration

print("=" * 100)
print("FILE MIGRATION TO UNIFIED INSPECTION STRUCTURE")
print("=" * 100)
print(f"\nMode: {'DRY RUN (no files will be moved)' if DRY_RUN else 'LIVE (files will be moved)'}")
print(f"Remove empty dirs: {REMOVE_EMPTY_DIRS}")
print("\n" + "=" * 100)

media_root = settings.MEDIA_ROOT
old_base = media_root
new_base = os.path.join(media_root, 'inspection')

print(f"\nMEDIA_ROOT: {media_root}")
print(f"Old structure base: {old_base}")
print(f"New structure base: {new_base}")

# Statistics
stats = {
    'files_found': 0,
    'files_moved': 0,
    'files_skipped': 0,
    'errors': 0,
    'dirs_removed': 0
}

migrations = []

print("\n" + "=" * 100)
print("SCANNING FOR FILES TO MIGRATE")
print("=" * 100)

def scan_for_old_files(path, depth=0, max_depth=10):
    """Scan for files in old structure"""
    if depth > max_depth or not os.path.exists(path):
        return

    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)

            if item == 'inspection':
                continue

            if os.path.isfile(item_path):
                rel_path = os.path.relpath(item_path, media_root)
                parts = rel_path.split(os.sep)

                # Old structure: 2025/November/CLIENT/Inspection-XXX/Compliance/TYPE/file.pdf
                if len(parts) >= 6:
                    year = parts[0]
                    month = parts[1]
                    client = parts[2]
                    inspection_folder = parts[3]
                    compliance_folder = parts[4]
                    file_type = parts[5]

                    if (year.isdigit() and len(year) == 4 and
                        inspection_folder.startswith('Inspection-') and
                        compliance_folder == 'Compliance'):

                        stats['files_found'] += 1

                        # New path: inspection/YEAR/MONTH/CLIENT/Compliance/file.pdf
                        new_rel_path = os.path.join('inspection', year, month, client, 'Compliance', item)
                        new_path = os.path.join(media_root, new_rel_path)

                        migrations.append({
                            'old_path': item_path,
                            'new_path': new_path,
                            'old_rel': rel_path,
                            'new_rel': new_rel_path,
                            'size': os.path.getsize(item_path),
                            'client': client,
                            'year': year,
                            'month': month,
                            'type': file_type
                        })

            elif os.path.isdir(item_path):
                scan_for_old_files(item_path, depth + 1, max_depth)

    except PermissionError:
        pass
    except Exception as e:
        print(f"Error scanning {path}: {e}")
        stats['errors'] += 1

print("Scanning old file structure...")
scan_for_old_files(media_root)

print(f"\nFound {stats['files_found']} files to migrate")

if migrations:
    print("\n" + "=" * 100)
    print("SAMPLE MIGRATIONS (first 10)")
    print("=" * 100)
    for i, migration in enumerate(migrations[:10]):
        print(f"\n{i+1}. {migration['client']} - {migration['type']}")
        print(f"   FROM: {migration['old_rel']}")
        print(f"   TO:   {migration['new_rel']}")
        print(f"   Size: {migration['size']:,} bytes")

    if len(migrations) > 10:
        print(f"\n... and {len(migrations) - 10} more files")

if not DRY_RUN and migrations:
    print("\n" + "=" * 100)
    print("WARNING: This will move files!")
    print("=" * 100)
    response = input(f"\nMove {len(migrations)} files? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        exit(0)

if migrations:
    print("\n" + "=" * 100)
    print("PERFORMING MIGRATION")
    print("=" * 100)

    for i, migration in enumerate(migrations):
        try:
            old_path = migration['old_path']
            new_path = migration['new_path']
            new_dir = os.path.dirname(new_path)

            if not DRY_RUN:
                os.makedirs(new_dir, exist_ok=True)

            if os.path.exists(new_path):
                print(f"SKIP [{i+1}/{len(migrations)}]: File exists - {migration['new_rel']}")
                stats['files_skipped'] += 1
                continue

            if DRY_RUN:
                print(f"[{i+1}/{len(migrations)}] WOULD MOVE: {migration['old_rel']} -> {migration['new_rel']}")
                stats['files_moved'] += 1
            else:
                shutil.move(old_path, new_path)
                print(f"[{i+1}/{len(migrations)}] MOVED: {migration['new_rel']}")
                stats['files_moved'] += 1

        except Exception as e:
            print(f"ERROR [{i+1}/{len(migrations)}]: {migration['old_rel']} - {e}")
            stats['errors'] += 1

if REMOVE_EMPTY_DIRS and not DRY_RUN and stats['files_moved'] > 0:
    print("\n" + "=" * 100)
    print("CLEANING UP EMPTY DIRECTORIES")
    print("=" * 100)

    def remove_empty_dirs(path, depth=0, max_depth=10):
        if depth > max_depth or not os.path.exists(path):
            return

        if 'inspection' in path:
            return

        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    remove_empty_dirs(item_path, depth + 1, max_depth)

            if not os.listdir(path):
                if path != media_root and not (depth == 1 and os.path.basename(path).isdigit()):
                    print(f"Removing empty: {os.path.relpath(path, media_root)}")
                    os.rmdir(path)
                    stats['dirs_removed'] += 1

        except Exception as e:
            print(f"Error cleaning {path}: {e}")

    remove_empty_dirs(media_root)

print("\n" + "=" * 100)
print("MIGRATION COMPLETE")
print("=" * 100)
print(f"\nStatistics:")
print(f"  Files found:     {stats['files_found']}")
print(f"  Files moved:     {stats['files_moved']}")
print(f"  Files skipped:   {stats['files_skipped']}")
print(f"  Errors:          {stats['errors']}")
if REMOVE_EMPTY_DIRS and not DRY_RUN:
    print(f"  Dirs removed:    {stats['dirs_removed']}")

if DRY_RUN:
    print("\nThis was a DRY RUN - no files were moved.")
    print("To perform migration, set DRY_RUN = False in the script.")
else:
    print("\nMigration completed!")
    print("\nNext steps:")
    print("1. Run find_media_files.py to verify")
    print("2. Test file uploads and downloads")

print("\n" + "=" * 100)
