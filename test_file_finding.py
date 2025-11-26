#!/usr/bin/env python3
"""
Test File Finding Logic
========================
Tests if the file finding logic can locate files for specific inspections.
Use this to debug file visibility issues on the frontend.
"""

import os
import sys
from pathlib import Path


def test_inspection_files(media_root, client_name, year, month):
    """
    Test if files can be found for a specific inspection.

    Args:
        media_root: Path to media folder
        client_name: Client name to search for
        year: Year (e.g., '2025')
        month: Month (e.g., 'October')
    """
    media_root = Path(media_root)

    print(f"\n{'='*80}")
    print(f"TESTING FILE FINDING FOR:")
    print(f"{'='*80}")
    print(f"Client: {client_name}")
    print(f"Year: {year}")
    print(f"Month: {month}")
    print(f"Media Root: {media_root}")
    print()

    # Check if base path exists
    base_paths_to_check = [
        media_root / year / month,
        media_root / 'inspection' / year / month
    ]

    print(f"[STEP 1] Checking base paths...")
    print(f"{'-'*80}")

    found_base_path = None
    for base_path in base_paths_to_check:
        exists = base_path.exists()
        print(f"  {base_path}: {'EXISTS' if exists else 'NOT FOUND'}")
        if exists and not found_base_path:
            found_base_path = base_path

    if not found_base_path:
        print(f"\n[ERROR] No valid base path found!")
        return

    print(f"\n[STEP 2] Looking for client folder...")
    print(f"{'-'*80}")

    # List all items in the month folder
    try:
        items = list(found_base_path.iterdir())
        print(f"  Found {len(items)} items in {found_base_path.relative_to(media_root)}")

        # Try to find client folder (case insensitive)
        client_folder = None
        for item in items:
            if item.is_dir():
                # Check if client name matches (partial match)
                if client_name.lower() in item.name.lower() or item.name.lower() in client_name.lower():
                    print(f"  FOUND CLIENT FOLDER: {item.name}")
                    client_folder = item
                    break

        if not client_folder:
            print(f"\n  Client folder not found. Available folders:")
            for item in sorted(items):
                if item.is_dir():
                    print(f"    - {item.name}")
            return

        print(f"\n[STEP 3] Scanning client folder structure...")
        print(f"{'-'*80}")
        print(f"  Client folder: {client_folder.relative_to(media_root)}")

        # Show folder structure
        def print_tree(path, prefix="", max_depth=4, current_depth=0):
            """Print directory tree structure."""
            if current_depth >= max_depth:
                return

            try:
                items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    print(f"{prefix}{current_prefix}{item.name}")

                    if item.is_dir():
                        extension_prefix = "    " if is_last else "│   "
                        print_tree(item, prefix + extension_prefix, max_depth, current_depth + 1)
            except (OSError, PermissionError) as e:
                print(f"{prefix}    [Permission Denied]")

        print()
        print_tree(client_folder)

        print(f"\n[STEP 4] Looking for Inspection folders...")
        print(f"{'-'*80}")

        inspection_folders = []

        # Check direct children for Inspection folders
        for item in client_folder.iterdir():
            if item.is_dir():
                if item.name.lower().startswith('inspection-'):
                    inspection_folders.append(item)
                    print(f"  FOUND (direct): {item.name}")
                else:
                    # Check subdirectories (DATE folders)
                    try:
                        for subitem in item.iterdir():
                            if subitem.is_dir() and subitem.name.lower().startswith('inspection-'):
                                inspection_folders.append(subitem)
                                print(f"  FOUND (in {item.name}): {subitem.name}")
                    except (OSError, PermissionError):
                        pass

        if not inspection_folders:
            print(f"  No Inspection folders found!")
            return

        print(f"\n[STEP 5] Counting files in each Inspection folder...")
        print(f"{'-'*80}")

        for inspection_folder in inspection_folders:
            print(f"\n  Inspection: {inspection_folder.name}")
            print(f"  Path: {inspection_folder.relative_to(media_root)}")

            # Count files recursively
            total_files = 0
            file_types = {}

            for root, dirs, files in os.walk(inspection_folder):
                if files:
                    folder_name = Path(root).name
                    file_count = len(files)
                    total_files += file_count

                    if folder_name not in file_types:
                        file_types[folder_name] = 0
                    file_types[folder_name] += file_count

                    print(f"    {Path(root).relative_to(inspection_folder)}: {file_count} file(s)")
                    for f in files[:3]:  # Show first 3 files
                        print(f"      - {f}")
                    if len(files) > 3:
                        print(f"      ... and {len(files) - 3} more")

            print(f"\n  TOTAL FILES: {total_files}")
            print(f"  File types breakdown:")
            for folder, count in file_types.items():
                print(f"    - {folder}: {count} file(s)")

        print(f"\n{'='*80}")
        print(f"TEST COMPLETE")
        print(f"{'='*80}")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Test file finding logic for specific inspections',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test Marang inspection (October 2025)
  python test_file_finding.py --client "Marang" --year 2025 --month October

  # Test with custom media root
  python test_file_finding.py --media-root /path/to/media --client "Marang" --year 2025 --month October
        """
    )

    parser.add_argument(
        '--media-root',
        type=str,
        default='./media',
        help='Path to the media folder (default: ./media)'
    )

    parser.add_argument(
        '--client',
        type=str,
        required=True,
        help='Client name (or partial match)'
    )

    parser.add_argument(
        '--year',
        type=str,
        required=True,
        help='Year (e.g., 2025)'
    )

    parser.add_argument(
        '--month',
        type=str,
        required=True,
        help='Month (e.g., October)'
    )

    args = parser.parse_args()

    test_inspection_files(
        media_root=args.media_root,
        client_name=args.client,
        year=args.year,
        month=args.month
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())
