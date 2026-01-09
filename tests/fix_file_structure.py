#!/usr/bin/env python3
"""
File Structure Fixer
====================
Automatically reorganizes files to the correct folder structure based on the scanner report.

This script:
1. Reads the misplaced files report
2. Determines correct destinations for all files
3. Creates proper folder structures
4. Moves files to correct locations
5. Logs all operations

IMPORTANT: Run in dry-run mode first to preview changes!
"""

import os
import json
import shutil
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class FileStructureFixer:
    """Fix file structure issues by moving files to correct locations."""

    def __init__(self, media_root, report_file, dry_run=True):
        """
        Initialize the fixer.

        Args:
            media_root: Path to the media folder
            report_file: Path to the JSON report from scanner
            dry_run: If True, only show what would be done without making changes
        """
        self.media_root = Path(media_root)
        self.report_file = Path(report_file)
        self.dry_run = dry_run
        self.operations = []
        self.stats = {
            'files_moved': 0,
            'folders_created': 0,
            'errors': 0
        }

    def load_report(self):
        """Load the scanner report."""
        print(f"\n{'='*80}")
        print(f"Loading report: {self.report_file}")
        print(f"{'='*80}\n")

        with open(self.report_file, 'r', encoding='utf-8') as f:
            self.report = json.load(f)

        print(f"Report loaded:")
        print(f"  - Scan date: {self.report['scan_date']}")
        print(f"  - Total files scanned: {self.report['statistics']['total_files_scanned']:,}")
        print(f"  - Issues found: {self.report['statistics']['misplaced_files_found']:,}")
        print()

    def fix_root_structure(self):
        """Fix the root structure - remove 'inspection' folder."""
        print("\n[STEP 1] Fixing root structure...")
        print("-" * 80)

        inspection_folder = self.media_root / 'inspection'

        if not inspection_folder.exists():
            print("  No 'inspection' root folder found - structure is correct")
            return

        print(f"  Found incorrect root: {inspection_folder}")
        print(f"  Will move contents up one level")

        # Get all items in inspection folder
        try:
            items = list(inspection_folder.iterdir())
            print(f"  Found {len(items)} items to move")

            for item in items:
                dest = self.media_root / item.name

                if self.dry_run:
                    print(f"  [DRY RUN] Would move: {item.name} -> {dest}")
                else:
                    print(f"  Moving: {item.name} -> {dest}")
                    if dest.exists():
                        # Merge directories
                        if item.is_dir():
                            self._merge_directories(item, dest)
                        else:
                            print(f"    WARNING: {dest} already exists, skipping")
                    else:
                        shutil.move(str(item), str(dest))

                self.stats['files_moved'] += 1

            # Remove empty inspection folder
            if not self.dry_run and not list(inspection_folder.iterdir()):
                inspection_folder.rmdir()
                print(f"  Removed empty folder: {inspection_folder}")

        except Exception as e:
            print(f"  ERROR: {e}")
            self.stats['errors'] += 1

    def _merge_directories(self, src, dest):
        """Recursively merge source directory into destination."""
        for item in src.iterdir():
            dest_item = dest / item.name
            if item.is_dir():
                if dest_item.exists():
                    self._merge_directories(item, dest_item)
                else:
                    shutil.move(str(item), str(dest_item))
            else:
                if not dest_item.exists():
                    shutil.move(str(item), str(dest_item))
                else:
                    print(f"    WARNING: {dest_item} already exists, skipping")

    def fix_date_folders(self):
        """Create missing date folders based on file names."""
        print("\n[STEP 2] Creating missing date folders...")
        print("-" * 80)

        # Pattern to extract dates from filenames: YYYY-MM-DD or YYMMDD
        date_patterns = [
            re.compile(r'(\d{4})-(\d{2})-(\d{2})'),  # 2025-11-07
            re.compile(r'(\d{2})(\d{2})(\d{2})'),    # 251107
        ]

        # Get all files that are too shallow
        shallow_files = self.report['issues'].get('files_too_shallow', [])

        print(f"  Processing {len(shallow_files)} files...")

        for issue in shallow_files:
            file_path = self.media_root / issue['file']

            if not file_path.exists():
                continue

            # Extract date from filename
            filename = file_path.name
            date_str = None

            for pattern in date_patterns:
                match = pattern.search(filename)
                if match:
                    groups = match.groups()
                    if len(groups) == 3:
                        if len(groups[0]) == 4:  # YYYY-MM-DD format
                            date_str = f"{groups[0]}-{groups[1]}-{groups[2]}"
                        else:  # YYMMDD format
                            year = f"20{groups[0]}"
                            date_str = f"{year}-{groups[1]}-{groups[2]}"
                        break

            if not date_str:
                print(f"  WARNING: Could not extract date from: {filename}")
                continue

            # Determine new path structure
            parts = file_path.relative_to(self.media_root).parts

            # Expected structure: YEAR/MONTH/CLIENT/DATE/Inspection-XXX/DOC_TYPE/file
            if len(parts) >= 4:
                year = parts[0]
                month = parts[1]
                client = parts[2]

                # Find or create Inspection folder
                client_folder = self.media_root / year / month / client
                date_folder = client_folder / date_str

                # Determine inspection number from filename or use 001
                inspection_match = re.search(r'Inspection[_-]?(\d+)', str(file_path), re.IGNORECASE)
                if inspection_match:
                    inspection_num = inspection_match.group(1).zfill(3)
                else:
                    inspection_num = '001'

                inspection_folder = date_folder / f'Inspection-{inspection_num}'

                # Determine document type from current folder or filename
                doc_type = self._determine_doc_type(file_path)
                doc_type_folder = inspection_folder / doc_type

                # New file path
                new_file_path = doc_type_folder / filename

                if self.dry_run:
                    print(f"  [DRY RUN] Would move:")
                    print(f"    From: {file_path.relative_to(self.media_root)}")
                    print(f"    To:   {new_file_path.relative_to(self.media_root)}")
                else:
                    # Create folders
                    doc_type_folder.mkdir(parents=True, exist_ok=True)
                    self.stats['folders_created'] += 1

                    # Move file
                    if new_file_path.exists():
                        print(f"  WARNING: {new_file_path} already exists, skipping")
                    else:
                        shutil.move(str(file_path), str(new_file_path))
                        print(f"  Moved: {filename} -> {new_file_path.relative_to(self.media_root)}")
                        self.stats['files_moved'] += 1

    def _determine_doc_type(self, file_path):
        """Determine document type from path or filename."""
        filename_lower = file_path.name.lower()
        parent = file_path.parent.name.lower()

        # Check parent folder first
        doc_type_map = {
            'rfi': 'Request For Invoice',
            'request for invoice': 'Request For Invoice',
            'invoice': 'invoice',
            'lab': 'lab results',
            'lab results': 'lab results',
            'retest': 'retest',
            'compliance': 'Compliance',
            'occurrence': 'occurrence',
            'composition': 'composition'
        }

        for key, value in doc_type_map.items():
            if key in parent:
                return value

        # Check filename
        if 'rfi' in filename_lower:
            return 'Request For Invoice'
        elif 'invoice' in filename_lower:
            return 'invoice'
        elif 'lab' in filename_lower:
            return 'lab results'
        elif 'retest' in filename_lower:
            return 'retest'
        elif 'compliance' in filename_lower or 'comp' in filename_lower:
            return 'Compliance'
        elif 'occurrence' in filename_lower:
            return 'occurrence'
        elif 'composition' in filename_lower:
            return 'composition'

        return 'invoice'  # Default fallback

    def fix_folder_names(self):
        """Rename folders to match expected names."""
        print("\n[STEP 3] Fixing folder names...")
        print("-" * 80)

        # Folder name corrections
        corrections = {
            'RFI': 'Request For Invoice',
            'rfi': 'Request For Invoice',
            'Invoice': 'invoice',
            'Lab': 'lab results',
            'lab': 'lab results',
            'Retest': 'retest',
            'compliance': 'Compliance',
            'Occurrence': 'occurrence',
            'Composition': 'composition',
            'Form': 'Request For Invoice',  # Forms are typically RFIs
        }

        # Walk through all directories
        for root, dirs, files in os.walk(self.media_root):
            for dir_name in dirs:
                if dir_name in corrections:
                    old_path = Path(root) / dir_name
                    new_name = corrections[dir_name]
                    new_path = Path(root) / new_name

                    if self.dry_run:
                        print(f"  [DRY RUN] Would rename: {dir_name} -> {new_name}")
                    else:
                        if not new_path.exists():
                            old_path.rename(new_path)
                            print(f"  Renamed: {dir_name} -> {new_name}")
                        else:
                            # Merge directories
                            print(f"  Merging: {dir_name} -> {new_name}")
                            self._merge_directories(old_path, new_path)
                            if not list(old_path.iterdir()):
                                old_path.rmdir()

    def cleanup_empty_folders(self):
        """Remove empty folders after reorganization."""
        print("\n[STEP 4] Cleaning up empty folders...")
        print("-" * 80)

        removed_count = 0

        # Walk bottom-up to remove empty folders
        for root, dirs, files in os.walk(self.media_root, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not list(dir_path.iterdir()):
                        if self.dry_run:
                            print(f"  [DRY RUN] Would remove empty: {dir_path.relative_to(self.media_root)}")
                        else:
                            dir_path.rmdir()
                            removed_count += 1
                except:
                    pass

        if not self.dry_run:
            print(f"  Removed {removed_count} empty folders")

    def create_backup(self):
        """Create a backup before making changes."""
        if self.dry_run:
            print("\n[DRY RUN MODE] Skipping backup creation")
            return

        print("\n[BACKUP] Creating backup...")
        print("-" * 80)

        backup_name = f"media_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.media_root.parent / backup_name

        print(f"  Creating backup: {backup_path}")
        print(f"  This may take a while...")

        try:
            shutil.copytree(self.media_root, backup_path)
            print(f"  Backup created successfully!")
            print(f"  Location: {backup_path}")
        except Exception as e:
            print(f"  ERROR creating backup: {e}")
            print(f"  Aborting to prevent data loss!")
            raise

    def run(self):
        """Run the fixer."""
        print(f"\n{'='*80}")
        print(f"FILE STRUCTURE FIXER")
        print(f"{'='*80}")
        print(f"Mode: {'DRY RUN (no changes will be made)' if self.dry_run else 'LIVE (files will be moved!)'}")
        print(f"Media root: {self.media_root}")
        print(f"{'='*80}\n")

        # Load report
        self.load_report()

        # Create backup (only in live mode)
        if not self.dry_run:
            self.create_backup()

        # Run fixes in order
        self.fix_root_structure()
        self.fix_date_folders()
        self.fix_folder_names()
        self.cleanup_empty_folders()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print summary of operations."""
        print(f"\n{'='*80}")
        print(f"SUMMARY")
        print(f"{'='*80}\n")

        mode_text = "DRY RUN - No changes were made" if self.dry_run else "LIVE MODE - Changes applied"
        print(f"Mode: {mode_text}\n")

        print(f"Statistics:")
        print(f"  - Folders created: {self.stats['folders_created']}")
        print(f"  - Files moved: {self.stats['files_moved']}")
        print(f"  - Errors: {self.stats['errors']}")
        print()

        if self.dry_run:
            print("To apply these changes, run with --no-dry-run flag")
        else:
            print("File reorganization complete!")
            print("Run the scanner again to verify all issues are fixed:")
            print(f"  python find_misplaced_files.py --media-root {self.media_root}")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Fix file structure issues by moving files to correct locations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes (dry run)
  python fix_file_structure.py --report server_report.json

  # Apply changes
  python fix_file_structure.py --report server_report.json --no-dry-run

  # Specify custom media folder
  python fix_file_structure.py --media-root /path/to/media --report report.json
        """
    )

    parser.add_argument(
        '--media-root',
        type=str,
        default='./media',
        help='Path to the media folder (default: ./media)'
    )

    parser.add_argument(
        '--report',
        type=str,
        required=True,
        help='Path to the JSON report from scanner (required)'
    )

    parser.add_argument(
        '--no-dry-run',
        action='store_true',
        help='Actually perform changes (default is dry-run mode)'
    )

    args = parser.parse_args()

    # Confirmation for live mode
    if args.no_dry_run:
        print("\n" + "="*80)
        print("WARNING: You are about to make changes to your file structure!")
        print("="*80)
        print(f"Media folder: {args.media_root}")
        print(f"Report file: {args.report}")
        print()
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return 1

    # Initialize and run fixer
    fixer = FileStructureFixer(
        media_root=args.media_root,
        report_file=args.report,
        dry_run=not args.no_dry_run
    )

    fixer.run()
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
