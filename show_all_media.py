#!/usr/bin/env python3
"""
Show All Media Folder Contents
================================
Shows EVERYTHING in the media folder - complete structure, all files, all folders.
Use this to understand what's actually on the server.
"""

import os
from pathlib import Path
from collections import defaultdict


def show_all_media(media_root='./media'):
    """Show complete media folder structure and statistics."""
    media_root = Path(media_root)

    if not media_root.exists():
        print(f"[ERROR] Media folder does not exist: {media_root}")
        return

    print(f"\n{'='*100}")
    print(f"COMPLETE MEDIA FOLDER SCAN")
    print(f"{'='*100}")
    print(f"Media Root: {media_root.absolute()}")
    print()

    # Statistics
    total_files = 0
    total_folders = 0
    total_inspections = 0
    files_by_extension = defaultdict(int)
    inspections_with_files = []
    all_inspections = []

    # Scan everything
    print(f"[SCANNING] This may take a moment...")
    print()

    inspection_details = []

    for root, dirs, files in os.walk(media_root):
        root_path = Path(root)
        relative_path = root_path.relative_to(media_root)

        # Count folders
        total_folders += len(dirs)

        # Count files
        for file in files:
            total_files += 1
            ext = Path(file).suffix.lower()
            files_by_extension[ext] += 1

        # Check if this is an Inspection folder
        if root_path.name.lower().startswith('inspection-'):
            total_inspections += 1
            all_inspections.append(str(relative_path))

            file_count = len(files)

            # Get all files in this inspection recursively
            inspection_files = []
            for sub_root, sub_dirs, sub_files in os.walk(root_path):
                for f in sub_files:
                    file_path = Path(sub_root) / f
                    rel_to_inspection = file_path.relative_to(root_path)
                    inspection_files.append(str(rel_to_inspection))

            if inspection_files:
                inspections_with_files.append({
                    'path': str(relative_path),
                    'name': root_path.name,
                    'files': inspection_files,
                    'file_count': len(inspection_files)
                })

    # Print statistics
    print(f"{'='*100}")
    print(f"STATISTICS")
    print(f"{'='*100}")
    print(f"Total Folders: {total_folders}")
    print(f"Total Files: {total_files}")
    print(f"Total Inspection Folders: {total_inspections}")
    print(f"Inspections with Files: {len(inspections_with_files)}")
    print()

    print(f"Files by Extension:")
    for ext, count in sorted(files_by_extension.items(), key=lambda x: x[1], reverse=True):
        ext_name = ext if ext else '(no extension)'
        print(f"  {ext_name}: {count} files")
    print()

    # Show all inspections with files
    print(f"{'='*100}")
    print(f"ALL INSPECTIONS WITH FILES ({len(inspections_with_files)} found)")
    print(f"{'='*100}")
    print()

    for i, inspection in enumerate(inspections_with_files, 1):
        print(f"{i}. {inspection['name']}")
        print(f"   Path: {inspection['path']}")
        print(f"   Files: {inspection['file_count']}")

        # Show folder structure with files
        file_structure = defaultdict(list)
        for f in inspection['files']:
            folder = str(Path(f).parent)
            if folder == '.':
                folder = '(root)'
            file_structure[folder].append(Path(f).name)

        print(f"   Structure:")
        for folder, files in sorted(file_structure.items()):
            print(f"     {folder}/")
            for file in sorted(files)[:5]:  # Show first 5 files per folder
                print(f"       - {file}")
            if len(files) > 5:
                print(f"       ... and {len(files) - 5} more files")
        print()

    # Show complete directory tree
    print(f"{'='*100}")
    print(f"COMPLETE DIRECTORY TREE")
    print(f"{'='*100}")
    print()

    def print_tree(path, prefix="", max_files_per_folder=10):
        """Print directory tree with file counts."""
        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

            dirs = [x for x in items if x.is_dir()]
            files = [x for x in items if x.is_file()]

            # Print directories
            for i, item in enumerate(dirs):
                is_last_dir = (i == len(dirs) - 1) and len(files) == 0
                current_prefix = "└── " if is_last_dir else "├── "

                # Count files in this directory recursively
                file_count = sum(1 for _ in item.rglob('*') if _.is_file())

                print(f"{prefix}{current_prefix}{item.name}/ ({file_count} files)")

                extension_prefix = "    " if is_last_dir else "│   "
                print_tree(item, prefix + extension_prefix, max_files_per_folder)

            # Print files (limited)
            files_to_show = files[:max_files_per_folder]
            remaining_files = len(files) - len(files_to_show)

            for i, item in enumerate(files_to_show):
                is_last = (i == len(files_to_show) - 1) and remaining_files == 0
                current_prefix = "└── " if is_last else "├── "
                size_kb = item.stat().st_size / 1024
                print(f"{prefix}{current_prefix}{item.name} ({size_kb:.1f} KB)")

            if remaining_files > 0:
                print(f"{prefix}└── ... and {remaining_files} more files")

        except (OSError, PermissionError):
            print(f"{prefix}[Permission Denied]")

    print(f"{media_root.name}/")
    print_tree(media_root)

    print()
    print(f"{'='*100}")
    print(f"SCAN COMPLETE")
    print(f"{'='*100}")
    print()

    # Summary with actionable info
    if inspections_with_files:
        print(f"[SUMMARY]")
        print(f"  - Found {len(inspections_with_files)} inspections with files")
        print(f"  - Total {total_files} files in media folder")
        print()
        print(f"[FIRST 5 INSPECTIONS TO TEST ON FRONTEND]")
        for i, inspection in enumerate(inspections_with_files[:5], 1):
            # Extract client info from path
            parts = Path(inspection['path']).parts
            print(f"\n  {i}. {inspection['name']}")
            if len(parts) >= 3:
                print(f"     Year/Month: {parts[0]}/{parts[1]}")
                if len(parts) >= 4:
                    # Reconstruct full client name from parts
                    # Everything between month and inspection folder is client name
                    client_parts = []
                    for j in range(2, len(parts)):
                        if parts[j].lower().startswith('inspection-'):
                            break
                        client_parts.append(parts[j])
                    client_name = '/'.join(client_parts) if client_parts else 'Unknown'
                    print(f"     Client: {client_name}")
            print(f"     Files: {inspection['file_count']}")
            print(f"     Full Path: {inspection['path']}")
    else:
        print(f"[WARNING] No inspections with files found!")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Show complete media folder contents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show everything in default media folder
  python show_all_media.py

  # Show everything in custom media folder
  python show_all_media.py --media-root /path/to/media

  # Save output to file
  python show_all_media.py > media_report.txt
        """
    )

    parser.add_argument(
        '--media-root',
        type=str,
        default='./media',
        help='Path to the media folder (default: ./media)'
    )

    args = parser.parse_args()

    show_all_media(media_root=args.media_root)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
