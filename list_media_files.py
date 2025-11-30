#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List all files in the media folder
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def format_size(bytes):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def list_media_files():
    """List all files in media folder"""
    print("=" * 80)
    print("MEDIA FOLDER FILE LISTING")
    print("=" * 80)

    # Get the project root directory
    project_root = Path(__file__).parent
    media_path = project_root / 'media'

    print(f"\nSearching in: {media_path}")
    print(f"Absolute path: {media_path.absolute()}")

    if not media_path.exists():
        print(f"\n❌ Media folder does not exist at: {media_path}")
        return

    if not media_path.is_dir():
        print(f"\n❌ Media path exists but is not a directory: {media_path}")
        return

    print("\n" + "=" * 80)
    print("FILES FOUND")
    print("=" * 80)

    # Walk through all directories and files
    all_files = []
    total_size = 0

    for root, dirs, files in os.walk(media_path):
        for filename in files:
            filepath = Path(root) / filename
            try:
                stat = filepath.stat()
                size = stat.st_size
                mtime = datetime.fromtimestamp(stat.st_mtime)

                # Get relative path from media folder
                rel_path = filepath.relative_to(media_path)

                all_files.append({
                    'path': str(rel_path),
                    'size': size,
                    'modified': mtime,
                    'full_path': str(filepath)
                })
                total_size += size
            except Exception as e:
                print(f"⚠️  Error reading {filepath}: {e}")

    # Sort by path
    all_files.sort(key=lambda x: x['path'])

    if not all_files:
        print("\n📁 Media folder is empty - no files found")
    else:
        print(f"\nFound {len(all_files)} files")
        print(f"Total size: {format_size(total_size)}\n")

        # Group by folder
        folders = {}
        for file_info in all_files:
            folder = str(Path(file_info['path']).parent)
            if folder == '.':
                folder = 'Root'
            if folder not in folders:
                folders[folder] = []
            folders[folder].append(file_info)

        # Print files grouped by folder
        for folder in sorted(folders.keys()):
            print(f"\n📂 {folder}/")
            print("-" * 80)

            folder_size = sum(f['size'] for f in folders[folder])
            print(f"   Files: {len(folders[folder])} | Size: {format_size(folder_size)}")
            print()

            for file_info in folders[folder]:
                filename = Path(file_info['path']).name
                size_str = format_size(file_info['size'])
                date_str = file_info['modified'].strftime('%Y-%m-%d %H:%M')

                print(f"   • {filename}")
                print(f"     Size: {size_str} | Modified: {date_str}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files: {len(all_files)}")
    print(f"Total size: {format_size(total_size)}")
    print(f"Folders: {len(folders)}")
    print("=" * 80)

if __name__ == "__main__":
    try:
        list_media_files()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
