"""
Media Folder Audit Script
Scans the entire media folder, shows all files, and helps identify misplaced files
"""

import os
import django
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection


def get_file_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def scan_media_folder():
    """Scan the entire media folder and categorize files"""
    media_root = settings.MEDIA_ROOT

    print("\n" + "="*120)
    print("MEDIA FOLDER AUDIT")
    print("="*120)
    print(f"\nMedia Root: {media_root}")
    print(f"Scanning...\n")

    if not os.path.exists(media_root):
        print("ERROR: Media folder does not exist!")
        return

    # Data structures to organize findings
    all_files = []
    files_by_type = defaultdict(list)
    files_by_directory = defaultdict(list)
    total_size = 0

    # Scan all files
    for root, dirs, files in os.walk(media_root):
        for filename in files:
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, media_root)

            try:
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                file_modified = datetime.fromtimestamp(file_stat.st_mtime)
                file_ext = os.path.splitext(filename)[1].lower()

                file_info = {
                    'filename': filename,
                    'full_path': file_path,
                    'relative_path': relative_path,
                    'directory': os.path.dirname(relative_path),
                    'size': file_size,
                    'size_formatted': get_file_size(file_size),
                    'modified': file_modified,
                    'extension': file_ext
                }

                all_files.append(file_info)
                files_by_type[file_ext].append(file_info)
                files_by_directory[os.path.dirname(relative_path)].append(file_info)
                total_size += file_size

            except Exception as e:
                print(f"Error reading file {relative_path}: {e}")

    # Print summary
    print("="*120)
    print("SUMMARY")
    print("="*120)
    print(f"\nTotal Files: {len(all_files)}")
    print(f"Total Size: {get_file_size(total_size)}")
    print(f"\nFile Types Found:")
    for ext, files in sorted(files_by_type.items(), key=lambda x: len(x[1]), reverse=True):
        ext_name = ext if ext else "No Extension"
        print(f"  {ext_name}: {len(files)} files")

    # Print directory structure
    print(f"\n{'='*120}")
    print("DIRECTORY STRUCTURE")
    print("="*120)
    for directory, files in sorted(files_by_directory.items()):
        dir_size = sum(f['size'] for f in files)
        print(f"\n{directory if directory else '[Root]'}")
        print(f"  Files: {len(files)} | Total Size: {get_file_size(dir_size)}")

    # Detailed file listing
    print(f"\n{'='*120}")
    print("DETAILED FILE LISTING")
    print("="*120)
    print(f"\n{'-'*120}")
    print(f"{'#':<5} {'File Name':<50} {'Directory':<35} {'Size':<15} {'Modified':<20}")
    print("-"*120)

    for idx, file_info in enumerate(sorted(all_files, key=lambda x: x['relative_path']), start=1):
        filename = file_info['filename'][:48]
        directory = file_info['directory'][:33]
        size = file_info['size_formatted']
        modified = file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')

        print(f"{idx:<5} {filename:<50} {directory:<35} {size:<15} {modified:<20}")

    print("-"*120)

    # Identify potential issues
    print(f"\n{'='*120}")
    print("POTENTIAL ISSUES / MISPLACED FILES")
    print("="*120)

    # Look for files in unexpected locations
    issues_found = False

    # Check for files in root media folder (should be in subdirectories)
    root_files = [f for f in all_files if not f['directory'] or f['directory'] == '.']
    if root_files:
        issues_found = True
        print(f"\n[WARNING] FILES IN ROOT MEDIA FOLDER (should be in subdirectories): {len(root_files)}")
        for f in root_files[:10]:
            print(f"  - {f['filename']}")
        if len(root_files) > 10:
            print(f"  ... and {len(root_files) - 10} more")

    # Check for duplicate filenames in different locations
    filename_locations = defaultdict(list)
    for f in all_files:
        filename_locations[f['filename']].append(f['relative_path'])

    duplicates = {k: v for k, v in filename_locations.items() if len(v) > 1}
    if duplicates:
        issues_found = True
        print(f"\n[WARNING] DUPLICATE FILENAMES IN DIFFERENT LOCATIONS: {len(duplicates)}")
        for filename, locations in list(duplicates.items())[:5]:
            print(f"\n  {filename}:")
            for loc in locations:
                print(f"    - {loc}")
        if len(duplicates) > 5:
            print(f"  ... and {len(duplicates) - 5} more duplicate sets")

    # Check for files with unusual extensions
    expected_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.xlsx', '.xls', '.doc', '.docx', '.zip'}
    unusual_files = [f for f in all_files if f['extension'] and f['extension'] not in expected_extensions]
    if unusual_files:
        issues_found = True
        print(f"\n[WARNING] FILES WITH UNUSUAL EXTENSIONS: {len(unusual_files)}")
        unusual_by_type = defaultdict(list)
        for f in unusual_files:
            unusual_by_type[f['extension']].append(f['filename'])
        for ext, files in unusual_by_type.items():
            print(f"  {ext}: {len(files)} files")
            for filename in files[:3]:
                print(f"    - {filename}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")

    # Check for very old files (might be outdated)
    one_year_ago = datetime.now().timestamp() - (365 * 24 * 60 * 60)
    old_files = [f for f in all_files if f['modified'].timestamp() < one_year_ago]
    if old_files:
        issues_found = True
        print(f"\n[WARNING] FILES OLDER THAN 1 YEAR: {len(old_files)}")
        oldest_size = sum(f['size'] for f in old_files)
        print(f"  Total size: {get_file_size(oldest_size)}")

    # Check for very large files
    large_files = [f for f in all_files if f['size'] > 50 * 1024 * 1024]  # > 50MB
    if large_files:
        issues_found = True
        print(f"\n[WARNING] FILES LARGER THAN 50MB: {len(large_files)}")
        for f in sorted(large_files, key=lambda x: x['size'], reverse=True)[:5]:
            print(f"  - {f['filename']}: {f['size_formatted']} in {f['directory']}")

    if not issues_found:
        print("\n[OK] No obvious issues found!")

    # Interactive deletion option
    print(f"\n{'='*120}")
    print("CLEANUP OPTIONS")
    print("="*120)
    print("\nWould you like to:")
    print("1. Delete all files in root media folder")
    print("2. Delete files older than 1 year")
    print("3. Delete files with specific extension")
    print("4. Delete files in a specific directory")
    print("5. Export full file list to CSV")
    print("6. Exit (no changes)")

    choice = input("\nEnter your choice (1-6): ").strip()

    if choice == '1' and root_files:
        confirm = input(f"Delete {len(root_files)} files from root folder? (yes/no): ").strip().lower()
        if confirm == 'yes':
            deleted = 0
            for f in root_files:
                try:
                    os.remove(f['full_path'])
                    deleted += 1
                    print(f"  Deleted: {f['filename']}")
                except Exception as e:
                    print(f"  Error deleting {f['filename']}: {e}")
            print(f"\n✓ Deleted {deleted} files")

    elif choice == '2' and old_files:
        confirm = input(f"Delete {len(old_files)} files older than 1 year? (yes/no): ").strip().lower()
        if confirm == 'yes':
            deleted = 0
            for f in old_files:
                try:
                    os.remove(f['full_path'])
                    deleted += 1
                    print(f"  Deleted: {f['filename']}")
                except Exception as e:
                    print(f"  Error deleting {f['filename']}: {e}")
            print(f"\n✓ Deleted {deleted} files")

    elif choice == '3':
        ext = input("Enter file extension to delete (e.g., .tmp): ").strip().lower()
        files_to_delete = [f for f in all_files if f['extension'] == ext]
        if files_to_delete:
            confirm = input(f"Delete {len(files_to_delete)} {ext} files? (yes/no): ").strip().lower()
            if confirm == 'yes':
                deleted = 0
                for f in files_to_delete:
                    try:
                        os.remove(f['full_path'])
                        deleted += 1
                        print(f"  Deleted: {f['filename']}")
                    except Exception as e:
                        print(f"  Error deleting {f['filename']}: {e}")
                print(f"\n[OK] Deleted {deleted} files")
        else:
            print(f"No {ext} files found")

    elif choice == '4':
        directory = input("Enter directory path (relative to media root): ").strip()
        files_to_delete = files_by_directory.get(directory, [])
        if files_to_delete:
            confirm = input(f"Delete {len(files_to_delete)} files from '{directory}'? (yes/no): ").strip().lower()
            if confirm == 'yes':
                deleted = 0
                for f in files_to_delete:
                    try:
                        os.remove(f['full_path'])
                        deleted += 1
                        print(f"  Deleted: {f['filename']}")
                    except Exception as e:
                        print(f"  Error deleting {f['filename']}: {e}")
                print(f"\n[OK] Deleted {deleted} files")
        else:
            print(f"No files found in directory: {directory}")

    elif choice == '5':
        csv_path = 'media_folder_audit.csv'
        try:
            import csv
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Filename', 'Directory', 'Size (Bytes)', 'Size (Formatted)', 'Modified', 'Extension', 'Full Path'])
                for f in sorted(all_files, key=lambda x: x['relative_path']):
                    writer.writerow([
                        f['filename'],
                        f['directory'],
                        f['size'],
                        f['size_formatted'],
                        f['modified'].strftime('%Y-%m-%d %H:%M:%S'),
                        f['extension'],
                        f['full_path']
                    ])
            print(f"\n[OK] File list exported to: {csv_path}")
        except Exception as e:
            print(f"Error creating CSV: {e}")

    print(f"\n{'='*120}")
    print("AUDIT COMPLETE")
    print("="*120 + "\n")


if __name__ == "__main__":
    try:
        scan_media_folder()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
