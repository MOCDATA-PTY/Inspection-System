#!/usr/bin/env python3
"""
List Inspections With Files
============================
This script scans the media folder and lists all inspections that contain files.
Useful for debugging and finding inspections to test on the frontend.

Expected folder structure:
    media/YEAR/MONTH/CLIENT/DATE/Inspection-XXX/DOC_TYPE/files
"""

import os
from pathlib import Path
from collections import defaultdict
import json


def find_inspections_with_files(media_root='./media'):
    """Find all inspections that contain files."""
    media_root = Path(media_root)

    if not media_root.exists():
        print(f"[ERROR] Media folder does not exist: {media_root}")
        return []

    inspections = []

    print(f"\n{'='*80}")
    print(f"SCANNING FOR INSPECTIONS WITH FILES")
    print(f"{'='*80}\n")
    print(f"Media root: {media_root.absolute()}\n")

    # Walk through the directory structure
    for root, dirs, files in os.walk(media_root):
        root_path = Path(root)
        relative_path = root_path.relative_to(media_root)
        parts = relative_path.parts

        # Check if this is an Inspection-XXX folder (should be at level 4)
        # Structure: YEAR/MONTH/CLIENT/DATE/Inspection-XXX
        if len(parts) >= 5 and parts[4].lower().startswith('inspection-'):
            inspection_folder = root_path

            # Count files in this inspection (recursively)
            file_count = 0
            file_types = defaultdict(int)

            for sub_root, sub_dirs, sub_files in os.walk(inspection_folder):
                for file in sub_files:
                    file_count += 1
                    # Get the document type folder (immediate parent of file)
                    file_path = Path(sub_root) / file
                    doc_type = file_path.parent.name
                    file_types[doc_type] += 1

            if file_count > 0:
                inspection_info = {
                    'inspection_name': parts[4],
                    'client': parts[2],
                    'date': parts[3],
                    'year': parts[0],
                    'month': parts[1],
                    'path': str(relative_path),
                    'full_path': str(inspection_folder),
                    'file_count': file_count,
                    'file_types': dict(file_types)
                }
                inspections.append(inspection_info)

    return inspections


def print_inspections(inspections):
    """Print the list of inspections with files."""
    if not inspections:
        print("[WARNING] No inspections with files found!")
        return

    print(f"\n{'='*80}")
    print(f"FOUND {len(inspections)} INSPECTIONS WITH FILES")
    print(f"{'='*80}\n")

    # Sort by year, month, client, date
    inspections.sort(key=lambda x: (x['year'], x['month'], x['client'], x['date']))

    for i, inspection in enumerate(inspections, 1):
        print(f"\n{i}. {inspection['inspection_name']}")
        print(f"   Client: {inspection['client']}")
        print(f"   Date: {inspection['date']}")
        print(f"   Location: {inspection['year']}/{inspection['month']}")
        print(f"   Total Files: {inspection['file_count']}")
        print(f"   Document Types:")
        for doc_type, count in inspection['file_types'].items():
            print(f"      - {doc_type}: {count} file(s)")
        print(f"   Path: {inspection['path']}")


def export_to_json(inspections, output_file='inspections_with_files.json'):
    """Export the results to a JSON file."""
    output_path = Path(output_file)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(inspections, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"EXPORT COMPLETE")
    print(f"{'='*80}\n")
    print(f"Exported to: {output_path.absolute()}")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Find all inspections that contain files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan default media folder
  python list_inspections_with_files.py

  # Scan specific folder
  python list_inspections_with_files.py --media-root /path/to/media

  # Export to JSON
  python list_inspections_with_files.py --export inspections.json
        """
    )

    parser.add_argument(
        '--media-root',
        type=str,
        default='./media',
        help='Path to the media folder (default: ./media)'
    )

    parser.add_argument(
        '--export',
        type=str,
        default=None,
        help='Export results to JSON file'
    )

    args = parser.parse_args()

    # Find inspections with files
    inspections = find_inspections_with_files(args.media_root)

    # Print results
    print_inspections(inspections)

    # Export if requested
    if args.export:
        export_to_json(inspections, args.export)

    # Print summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}\n")
    print(f"Total inspections with files: {len(inspections)}")

    if inspections:
        total_files = sum(insp['file_count'] for insp in inspections)
        print(f"Total files across all inspections: {total_files}")
        print(f"\nFirst inspection to test:")
        first = inspections[0]
        print(f"  Name: {first['inspection_name']}")
        print(f"  Client: {first['client']}")
        print(f"  Date: {first['date']}")
        print(f"  Path: {first['path']}")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
