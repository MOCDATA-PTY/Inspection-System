#!/usr/bin/env python3
"""
Test Django File Finding Function
==================================
Tests the actual Django file finding function with real parameters.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inspection_system.settings')
django.setup()

from main.views.core_views import get_inspection_files_local


def test_file_finding(client_name, inspection_date):
    """Test file finding with real Django function."""

    print(f"\n{'='*80}")
    print(f"TESTING DJANGO FILE FINDING FUNCTION")
    print(f"{'='*80}")
    print(f"Client: {client_name}")
    print(f"Date: {inspection_date}")
    print()

    # Call the actual Django function
    print("[CALLING] get_inspection_files_local()...")
    result = get_inspection_files_local(client_name, inspection_date, force_refresh=True)

    print(f"\n[RESULTS]")
    print(f"{'-'*80}")

    total_files = 0
    for category, files in result.items():
        if files:
            print(f"\n{category.upper()}: {len(files)} files")
            for file in files[:5]:  # Show first 5 files
                print(f"  - {file.get('name', 'unknown')}")
                print(f"    Path: {file.get('path', 'unknown')}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")
            total_files += len(files)

    if total_files == 0:
        print("\n[WARNING] NO FILES FOUND!")
        print("\nPossible issues:")
        print("  1. Client name doesn't match folder name")
        print("  2. Date format is wrong")
        print("  3. Files are in unexpected folder structure")
        print("  4. Folder paths don't exist")
    else:
        print(f"\n[SUCCESS] Found {total_files} total files")

    print(f"\n{'='*80}")

    return result


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Test Django file finding function',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test Marang inspection (October 2025)
  python test_django_file_finding.py --client "Marang Layers Farming Enterprises t/a Maranga Eggs" --date "2025-10-01"

  # Test Superspar Bluewater (November 2025)
  python test_django_file_finding.py --client "Superspar Bluewater" --date "2025-11-01"

  # Test with different date formats
  python test_django_file_finding.py --client "Superspar Bluewater" --date "01/11/2025"
        """
    )

    parser.add_argument(
        '--client',
        type=str,
        required=True,
        help='Client name (as stored in database)'
    )

    parser.add_argument(
        '--date',
        type=str,
        required=True,
        help='Inspection date (YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY)'
    )

    args = parser.parse_args()

    result = test_file_finding(args.client, args.date)

    return 0


if __name__ == '__main__':
    sys.exit(main())
