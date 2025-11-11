#!/usr/bin/env python3
"""
Find all mobile_* folders in the inspection directory to identify
inspections that need to be migrated.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def get_folder_size(folder_path):
    """Calculate total size of all files in a folder"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception as e:
        pass
    return total_size

def format_size(size_bytes):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def main():
    print("\n" + "=" * 80)
    print("SCAN FOR ALL MOBILE_* FOLDERS")
    print("=" * 80)

    inspection_root = os.path.join(settings.MEDIA_ROOT, 'inspection')

    if not os.path.exists(inspection_root):
        print(f"❌ Inspection root doesn't exist: {inspection_root}")
        return

    mobile_folders = []
    total_files = 0
    total_size = 0

    # Walk through all years and months
    for year_folder in os.listdir(inspection_root):
        year_path = os.path.join(inspection_root, year_folder)
        if not os.path.isdir(year_path):
            continue

        for month_folder in os.listdir(year_path):
            month_path = os.path.join(year_path, month_folder)
            if not os.path.isdir(month_path):
                continue

            # Look for folders starting with "mobile_"
            for client_folder in os.listdir(month_path):
                if client_folder.startswith('mobile_'):
                    folder_path = os.path.join(month_path, client_folder)

                    # Get folder details
                    folder_info = {
                        'year': year_folder,
                        'month': month_folder,
                        'folder_name': client_folder,
                        'full_path': folder_path,
                        'files': {}
                    }

                    # Check each document type
                    folder_size = 0
                    folder_file_count = 0

                    for doc_type in ['rfi', 'invoice', 'lab', 'occurrence', 'compliance', 'composition']:
                        doc_path = os.path.join(folder_path, doc_type)
                        if os.path.exists(doc_path):
                            files = [f for f in os.listdir(doc_path) if f.endswith('.pdf')]
                            if files:
                                folder_info['files'][doc_type] = files
                                folder_file_count += len(files)
                                # Calculate size
                                for f in files:
                                    file_path = os.path.join(doc_path, f)
                                    if os.path.exists(file_path):
                                        file_size = os.path.getsize(file_path)
                                        folder_size += file_size

                    folder_info['file_count'] = folder_file_count
                    folder_info['size'] = folder_size

                    if folder_file_count > 0:
                        mobile_folders.append(folder_info)
                        total_files += folder_file_count
                        total_size += folder_size

    # Display results
    if not mobile_folders:
        print("\n✅ No mobile_* folders found with files!")
        print("All inspections are in the correct folder structure.")
    else:
        print(f"\n⚠️  Found {len(mobile_folders)} mobile_* folder(s) with files:\n")

        for idx, folder in enumerate(mobile_folders, 1):
            print(f"{idx}. {folder['year']}/{folder['month']}/{folder['folder_name']}")
            print(f"   📊 {folder['file_count']} file(s) | {format_size(folder['size'])}")
            print(f"   📁 Path: {folder['full_path']}")

            # List files by type
            for doc_type, files in folder['files'].items():
                print(f"   📄 {doc_type.upper()}: {len(files)} file(s)")
                for file in files:
                    file_path = os.path.join(folder['full_path'], doc_type, file)
                    size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    print(f"      - {file} ({format_size(size)})")

            # Try to extract client name and date
            folder_name = folder['folder_name'].replace('mobile_', '')
            print(f"   🎯 Target folder: {folder_name}")
            print()

        print("=" * 80)
        print(f"SUMMARY")
        print("=" * 80)
        print(f"Total mobile folders: {len(mobile_folders)}")
        print(f"Total files to migrate: {total_files}")
        print(f"Total size: {format_size(total_size)}")
        print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
