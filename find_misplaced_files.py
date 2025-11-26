#!/usr/bin/env python3
"""
Find Misplaced Files Script
============================
This script scans the media folder structure and identifies files that are in the wrong places.

Expected folder structure:
    media/
    └── YEAR (e.g., 2025)/
        └── MONTH (e.g., January)/
            └── CLIENT_NAME/
                └── INSPECTION_DATE (e.g., 2025-01-15)/
                    └── Inspection-XXX/
                        ├── Request For Invoice/
                        ├── invoice/
                        ├── lab results/
                        ├── retest/
                        ├── Compliance/
                        ├── occurrence/
                        └── composition/

The script will identify:
1. Files in wrong folder levels
2. Files outside expected Inspection-XXX folders
3. Files in unexpected document type folders
4. Incorrectly named folders
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Configuration
EXPECTED_MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

EXPECTED_DOC_TYPES = [
    'Request For Invoice',
    'invoice',
    'lab results',
    'retest',
    'Compliance',
    'compliance',  # Case variation
    'occurrence',
    'composition'
]

# Patterns
YEAR_PATTERN = re.compile(r'^20\d{2}$')  # Matches 2000-2099
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')  # Matches YYYY-MM-DD
INSPECTION_PATTERN = re.compile(r'^inspection-\d+$', re.IGNORECASE)  # Matches Inspection-XXX


class MisplacedFilesFinder:
    """Find files that are in the wrong places in the media folder."""

    def __init__(self, media_root, dry_run=True):
        """
        Initialize the finder.

        Args:
            media_root: Path to the media folder
            dry_run: If True, only report issues without making changes
        """
        self.media_root = Path(media_root)
        self.dry_run = dry_run
        self.misplaced_files = defaultdict(list)
        self.stats = {
            'total_files_scanned': 0,
            'misplaced_files_found': 0,
            'folders_scanned': 0,
            'issues_by_type': defaultdict(int)
        }

    def scan(self):
        """Scan the media folder and identify misplaced files."""
        print(f"\n{'='*80}")
        print(f"Scanning media folder: {self.media_root}")
        print(f"{'='*80}\n")

        if not self.media_root.exists():
            print(f"[ERROR] Media folder does not exist: {self.media_root}")
            return

        # Start scanning from media root
        self._scan_directory(self.media_root, level=0)

        # Print summary
        self._print_summary()

        return self.misplaced_files

    def _scan_directory(self, path, level=0):
        """Recursively scan directory and check structure."""
        self.stats['folders_scanned'] += 1

        try:
            items = list(path.iterdir())
        except PermissionError:
            print(f"[WARNING] Permission denied: {path}")
            return

        for item in items:
            if item.is_file():
                self.stats['total_files_scanned'] += 1
                self._check_file(item, level)
            elif item.is_dir():
                self._check_folder(item, level)
                self._scan_directory(item, level + 1)

    def _check_file(self, file_path, level):
        """Check if a file is in the correct location."""
        relative_path = file_path.relative_to(self.media_root)
        parts = relative_path.parts

        # Expected structure depth:
        # Level 0: media (root)
        # Level 1: YEAR
        # Level 2: MONTH
        # Level 3: CLIENT_NAME
        # Level 4: DATE
        # Level 5: Inspection-XXX
        # Level 6: DOC_TYPE
        # Level 7+: Actual files (or subfolders in doc type)

        # Files should be at least 7 levels deep
        if len(parts) < 7:
            issue = {
                'type': 'file_too_shallow',
                'file': str(relative_path),
                'level': len(parts),
                'expected_min_level': 7,
                'message': f"File is at level {len(parts)}, expected at least level 7"
            }
            self.misplaced_files['files_too_shallow'].append(issue)
            self.stats['misplaced_files_found'] += 1
            self.stats['issues_by_type']['file_too_shallow'] += 1
            return

        # Check if file is in expected document type folder
        # parts[5] is the document type folder (0=YEAR, 1=MONTH, 2=CLIENT, 3=DATE, 4=INSPECTION, 5=DOC_TYPE)
        if len(parts) >= 7:
            doc_type_folder = parts[5]  # The 6th level is the document type folder
            if doc_type_folder not in EXPECTED_DOC_TYPES:
                issue = {
                    'type': 'unexpected_doc_type',
                    'file': str(relative_path),
                    'found_doc_type': doc_type_folder,
                    'expected_doc_types': EXPECTED_DOC_TYPES,
                    'message': f"File is in unexpected document type folder: '{doc_type_folder}'"
                }
                self.misplaced_files['unexpected_doc_type'].append(issue)
                self.stats['misplaced_files_found'] += 1
                self.stats['issues_by_type']['unexpected_doc_type'] += 1

    def _check_folder(self, folder_path, level):
        """Check if a folder follows the expected structure."""
        relative_path = folder_path.relative_to(self.media_root)
        parts = relative_path.parts
        folder_name = folder_path.name

        # Level-specific checks
        if len(parts) == 1:  # YEAR level
            if not YEAR_PATTERN.match(folder_name):
                issue = {
                    'type': 'invalid_year_folder',
                    'folder': str(relative_path),
                    'folder_name': folder_name,
                    'message': f"Expected year folder (YYYY), found: '{folder_name}'"
                }
                self.misplaced_files['invalid_year_folders'].append(issue)
                self.stats['issues_by_type']['invalid_year_folder'] += 1

        elif len(parts) == 2:  # MONTH level
            if folder_name not in EXPECTED_MONTHS:
                issue = {
                    'type': 'invalid_month_folder',
                    'folder': str(relative_path),
                    'folder_name': folder_name,
                    'expected': EXPECTED_MONTHS,
                    'message': f"Expected month name, found: '{folder_name}'"
                }
                self.misplaced_files['invalid_month_folders'].append(issue)
                self.stats['issues_by_type']['invalid_month_folder'] += 1

        elif len(parts) == 3:  # CLIENT_NAME level
            # Client names can vary, but check for common issues
            if folder_name.strip() != folder_name or folder_name == '':
                issue = {
                    'type': 'invalid_client_folder',
                    'folder': str(relative_path),
                    'folder_name': repr(folder_name),
                    'message': f"Client folder has leading/trailing spaces or is empty"
                }
                self.misplaced_files['invalid_client_folders'].append(issue)
                self.stats['issues_by_type']['invalid_client_folder'] += 1

        elif len(parts) == 4:  # DATE level
            if not DATE_PATTERN.match(folder_name):
                issue = {
                    'type': 'invalid_date_folder',
                    'folder': str(relative_path),
                    'folder_name': folder_name,
                    'message': f"Expected date folder (YYYY-MM-DD), found: '{folder_name}'"
                }
                self.misplaced_files['invalid_date_folders'].append(issue)
                self.stats['issues_by_type']['invalid_date_folder'] += 1

        elif len(parts) == 5:  # Inspection-XXX level
            if not INSPECTION_PATTERN.match(folder_name):
                issue = {
                    'type': 'invalid_inspection_folder',
                    'folder': str(relative_path),
                    'folder_name': folder_name,
                    'message': f"Expected 'Inspection-XXX' folder, found: '{folder_name}'"
                }
                self.misplaced_files['invalid_inspection_folders'].append(issue)
                self.stats['issues_by_type']['invalid_inspection_folder'] += 1

        elif len(parts) == 6:  # DOC_TYPE level
            if folder_name not in EXPECTED_DOC_TYPES:
                issue = {
                    'type': 'unexpected_doc_type_folder',
                    'folder': str(relative_path),
                    'folder_name': folder_name,
                    'expected': EXPECTED_DOC_TYPES,
                    'message': f"Unexpected document type folder: '{folder_name}'"
                }
                self.misplaced_files['unexpected_doc_type_folders'].append(issue)
                self.stats['issues_by_type']['unexpected_doc_type_folder'] += 1

    def _print_summary(self):
        """Print summary of findings."""
        print(f"\n{'='*80}")
        print(f"SCAN SUMMARY")
        print(f"{'='*80}\n")

        print(f"[STATISTICS]")
        print(f"   - Total files scanned: {self.stats['total_files_scanned']:,}")
        print(f"   - Total folders scanned: {self.stats['folders_scanned']:,}")
        print(f"   - Misplaced files found: {self.stats['misplaced_files_found']:,}")
        print()

        if self.stats['misplaced_files_found'] == 0:
            print("[SUCCESS] No misplaced files found! All files are in the correct structure.")
            return

        print(f"[WARNING] Issues Found by Type:")
        for issue_type, count in sorted(self.stats['issues_by_type'].items()):
            print(f"   - {issue_type}: {count:,}")
        print()

        # Detailed breakdown
        print(f"\n{'='*80}")
        print(f"DETAILED FINDINGS")
        print(f"{'='*80}\n")

        for category, issues in sorted(self.misplaced_files.items()):
            if issues:
                print(f"\n{'-'*80}")
                print(f"[CATEGORY] {category.upper().replace('_', ' ')} ({len(issues)} issues)")
                print(f"{'-'*80}")

                # Show first 10 issues in each category
                for i, issue in enumerate(issues[:10], 1):
                    print(f"\n{i}. {issue['message']}")
                    if 'file' in issue:
                        print(f"   File: {issue['file']}")
                    if 'folder' in issue:
                        print(f"   Folder: {issue['folder']}")

                if len(issues) > 10:
                    print(f"\n   ... and {len(issues) - 10} more issues in this category")

    def export_report(self, output_file='misplaced_files_report.json'):
        """Export detailed report to JSON file."""
        report = {
            'scan_date': datetime.now().isoformat(),
            'media_root': str(self.media_root),
            'statistics': dict(self.stats),
            'issues': dict(self.misplaced_files)
        }

        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n[REPORT] Detailed report exported to: {output_path.absolute()}")
        return output_path


def main():
    """Main function to run the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Find misplaced files in the inspection system media folder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan the default media folder (dry run)
  python find_misplaced_files.py

  # Scan a specific folder
  python find_misplaced_files.py --media-root /path/to/media

  # Export detailed JSON report
  python find_misplaced_files.py --export-report misplaced_files.json
        """
    )

    parser.add_argument(
        '--media-root',
        type=str,
        default='./media',
        help='Path to the media folder (default: ./media)'
    )

    parser.add_argument(
        '--export-report',
        type=str,
        default=None,
        help='Export detailed report to JSON file'
    )

    parser.add_argument(
        '--no-dry-run',
        action='store_true',
        help='Actually perform changes (default is dry-run mode)'
    )

    args = parser.parse_args()

    # Initialize finder
    finder = MisplacedFilesFinder(
        media_root=args.media_root,
        dry_run=not args.no_dry_run
    )

    # Run scan
    finder.scan()

    # Export report if requested
    if args.export_report:
        finder.export_report(args.export_report)

    # Return exit code based on findings
    if finder.stats['misplaced_files_found'] > 0:
        print(f"\n[WARNING] Found {finder.stats['misplaced_files_found']} misplaced files. Please review the report.")
        return 1
    else:
        print(f"\n[SUCCESS] All files are in the correct structure!")
        return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
