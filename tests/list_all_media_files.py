#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List ALL media files in the inspection system
Shows complete file inventory with paths, sizes, and dates
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()

from django.conf import settings


def format_size(bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"


def list_all_media_files():
    """List ALL files in the media directory"""

    media_root = settings.MEDIA_ROOT
    print(f"\n{'='*100}")
    print(f"📁 COMPLETE MEDIA FILES INVENTORY")
    print(f"{'='*100}")
    print(f"Media Root: {media_root}")
    print(f"Scan Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*100}\n")

    if not os.path.exists(media_root):
        print(f"❌ ERROR: Media directory does not exist: {media_root}")
        return

    # Statistics
    total_files = 0
    total_size = 0
    files_by_type = {}
    files_by_year = {}
    files_by_month = {}
    all_files_list = []

    # Walk through all directories
    print("🔍 Scanning all directories...\n")

    for root, dirs, files in os.walk(media_root):
        for filename in files:
            filepath = os.path.join(root, filename)

            try:
                # Get file stats
                stat = os.stat(filepath)
                size = stat.st_size
                modified = datetime.fromtimestamp(stat.st_mtime)

                # Get relative path
                rel_path = os.path.relpath(filepath, media_root)

                # Get file extension
                ext = os.path.splitext(filename)[1].lower()
                if not ext:
                    ext = 'no_extension'

                # Extract year/month from path
                path_parts = rel_path.split(os.sep)
                year = path_parts[1] if len(path_parts) > 1 else 'unknown'
                month = path_parts[2] if len(path_parts) > 2 else 'unknown'

                # Collect stats
                total_files += 1
                total_size += size

                files_by_type[ext] = files_by_type.get(ext, 0) + 1
                files_by_year[year] = files_by_year.get(year, 0) + 1
                files_by_month[f"{year}/{month}"] = files_by_month.get(f"{year}/{month}", 0) + 1

                all_files_list.append({
                    'path': rel_path,
                    'size': size,
                    'modified': modified,
                    'ext': ext,
                    'year': year,
                    'month': month
                })

            except Exception as e:
                print(f"⚠️  Error reading file: {filepath}")
                print(f"   Error: {str(e)}\n")

    # Sort files by path
    all_files_list.sort(key=lambda x: x['path'])

    # Print all files
    print(f"\n{'='*100}")
    print(f"📄 COMPLETE FILE LIST ({total_files:,} files)")
    print(f"{'='*100}\n")

    for idx, file_info in enumerate(all_files_list, 1):
        print(f"{idx:5d}. {file_info['path']}")
        print(f"       Size: {format_size(file_info['size']):<15} Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    # Print summary statistics
    print(f"\n{'='*100}")
    print(f"📊 SUMMARY STATISTICS")
    print(f"{'='*100}\n")

    print(f"Total Files: {total_files:,}")
    print(f"Total Size:  {format_size(total_size)}")
    print(f"\n")

    # Files by type
    print(f"{'─'*100}")
    print(f"📁 FILES BY TYPE")
    print(f"{'─'*100}")
    for ext, count in sorted(files_by_type.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_files * 100) if total_files > 0 else 0
        print(f"  {ext:20s}: {count:6,} files ({percentage:5.1f}%)")

    # Files by year
    print(f"\n{'─'*100}")
    print(f"📅 FILES BY YEAR")
    print(f"{'─'*100}")
    for year, count in sorted(files_by_year.items()):
        percentage = (count / total_files * 100) if total_files > 0 else 0
        print(f"  {year:20s}: {count:6,} files ({percentage:5.1f}%)")

    # Files by month
    print(f"\n{'─'*100}")
    print(f"📅 FILES BY MONTH")
    print(f"{'─'*100}")
    for month, count in sorted(files_by_month.items()):
        percentage = (count / total_files * 100) if total_files > 0 else 0
        print(f"  {month:20s}: {count:6,} files ({percentage:5.1f}%)")

    print(f"\n{'='*100}")
    print(f"✅ Scan completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*100}\n")

    # Export to file
    output_file = BASE_DIR / f"media_files_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    print(f"💾 Saving detailed inventory to: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"MEDIA FILES INVENTORY\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Media Root: {media_root}\n")
        f.write(f"{'='*100}\n\n")

        f.write(f"COMPLETE FILE LIST ({total_files:,} files)\n")
        f.write(f"{'='*100}\n\n")

        for idx, file_info in enumerate(all_files_list, 1):
            f.write(f"{idx:5d}. {file_info['path']}\n")
            f.write(f"       Size: {format_size(file_info['size']):<15} Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\n")

        f.write(f"\n{'='*100}\n")
        f.write(f"SUMMARY STATISTICS\n")
        f.write(f"{'='*100}\n\n")
        f.write(f"Total Files: {total_files:,}\n")
        f.write(f"Total Size:  {format_size(total_size)}\n\n")

        f.write(f"FILES BY TYPE\n")
        f.write(f"{'─'*100}\n")
        for ext, count in sorted(files_by_type.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files * 100) if total_files > 0 else 0
            f.write(f"  {ext:20s}: {count:6,} files ({percentage:5.1f}%)\n")

        f.write(f"\nFILES BY YEAR\n")
        f.write(f"{'─'*100}\n")
        for year, count in sorted(files_by_year.items()):
            percentage = (count / total_files * 100) if total_files > 0 else 0
            f.write(f"  {year:20s}: {count:6,} files ({percentage:5.1f}%)\n")

        f.write(f"\nFILES BY MONTH\n")
        f.write(f"{'─'*100}\n")
        for month, count in sorted(files_by_month.items()):
            percentage = (count / total_files * 100) if total_files > 0 else 0
            f.write(f"  {month:20s}: {count:6,} files ({percentage:5.1f}%)\n")

    print(f"✅ Inventory saved successfully!\n")


if __name__ == "__main__":
    print("\n" + "="*100)
    print("🔍 MEDIA FILES INVENTORY SCANNER")
    print("="*100)

    try:
        list_all_media_files()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
