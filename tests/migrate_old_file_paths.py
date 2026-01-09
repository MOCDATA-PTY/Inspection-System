#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migrate files from old path structure to new inspection-based structure
OLD: inspection/2025/November/client_name/rfi/file.pdf
NEW: inspection/2025/November/client_name/Inspection-XXXX/rfi/file.pdf
"""

import os
import sys
import shutil
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
from main.models import FoodSafetyAgencyInspection


def find_inspection_for_files(client_name, inspection_date, year, month):
    """Find the inspection record for a given client and date"""

    # Clean client name for matching
    clean_client = client_name.replace('_', ' ').replace('mobile ', '').strip()

    print(f"    Looking for inspection: {clean_client} on {inspection_date}")

    # Try to find exact match
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__iexact=clean_client,
        date_of_inspection=inspection_date
    )

    if inspections.exists():
        inspection = inspections.first()
        print(f"    ✅ Found inspection: {inspection.remote_id} - {inspection.client_name}")
        return inspection

    # Try to find by client name only (in case date doesn't match exactly)
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains=clean_client
    ).order_by('-date_of_inspection')

    if inspections.exists():
        inspection = inspections.first()
        print(f"    ⚠️  Found similar inspection: {inspection.remote_id} - {inspection.client_name} on {inspection.date_of_inspection}")
        return inspection

    print(f"    ❌ No inspection found for {clean_client}")
    return None


def migrate_files(dry_run=True):
    """Migrate files from old structure to new structure"""

    media_root = settings.MEDIA_ROOT
    inspection_root = os.path.join(media_root, 'inspection')

    print(f"\n{'='*100}")
    print(f"MIGRATING FILES FROM OLD STRUCTURE TO NEW STRUCTURE")
    print(f"{'='*100}")
    print(f"Media Root: {media_root}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will move files)'}")
    print(f"{'='*100}\n")

    if not os.path.exists(inspection_root):
        print(f"❌ Inspection directory not found: {inspection_root}")
        return

    moved_count = 0
    error_count = 0
    skip_count = 0

    # Walk through year directories (2025, etc.)
    for year in os.listdir(inspection_root):
        year_path = os.path.join(inspection_root, year)
        if not os.path.isdir(year_path):
            continue

        print(f"\n📅 Processing year: {year}")

        # Walk through month directories (January, February, etc.)
        for month in os.listdir(year_path):
            month_path = os.path.join(inspection_root, year, month)
            if not os.path.isdir(month_path):
                continue

            print(f"  📅 Processing month: {month}")

            # Walk through client directories
            for client_dir in os.listdir(month_path):
                client_path = os.path.join(month_path, client_dir)
                if not os.path.isdir(client_path):
                    continue

                # Check if this is OLD structure (has rfi, invoice, etc. folders directly)
                old_structure_folders = ['rfi', 'invoice', 'lab', 'lab_form', 'retest',
                                        'occurrence', 'composition', 'compliance', 'lab results']

                has_old_structure = False
                for folder in old_structure_folders:
                    folder_path = os.path.join(client_path, folder)
                    if os.path.exists(folder_path) and os.path.isdir(folder_path):
                        has_old_structure = True
                        break

                if not has_old_structure:
                    continue

                print(f"\n    🔍 Found OLD structure: {client_dir}")

                # Extract date from folder name if possible (format: YYYYMMDD or YYYY-MM-DD)
                # For mobile uploads, try to extract date from first file
                inspection_date = None

                # Try to find any file to extract date
                for folder in old_structure_folders:
                    folder_path = os.path.join(client_path, folder)
                    if os.path.exists(folder_path):
                        files = os.listdir(folder_path)
                        if files:
                            # Try to extract date from filename
                            # Format: FSA-RFI-XX-YYMMDD.pdf
                            for filename in files:
                                if filename.endswith('.pdf'):
                                    parts = filename.split('-')
                                    if len(parts) >= 3:
                                        date_part = parts[-1].replace('.pdf', '')
                                        # Try YYMMDD format
                                        if len(date_part) == 6 and date_part.isdigit():
                                            year_2digit = date_part[:2]
                                            month_2digit = date_part[2:4]
                                            day_2digit = date_part[4:6]
                                            try:
                                                inspection_date = f"20{year_2digit}-{month_2digit}-{day_2digit}"
                                                print(f"    📅 Extracted date from filename: {inspection_date}")
                                                break
                                            except:
                                                pass
                                    break
                            if inspection_date:
                                break

                if not inspection_date:
                    print(f"    ⚠️  Could not extract date, skipping")
                    skip_count += 1
                    continue

                # Find inspection record
                inspection = find_inspection_for_files(client_dir, inspection_date, year, month)

                if not inspection:
                    print(f"    ⚠️  No inspection found, skipping")
                    skip_count += 1
                    continue

                # Create new path: inspection/2025/November/client_name/Inspection-XXXX/
                new_base_path = os.path.join(
                    inspection_root,
                    year,
                    month,
                    client_dir,
                    f"Inspection-{inspection.remote_id}"
                )

                print(f"    📂 New base path: Inspection-{inspection.remote_id}/")

                # Move files from each old folder to new structure
                for old_folder in old_structure_folders:
                    old_folder_path = os.path.join(client_path, old_folder)
                    if not os.path.exists(old_folder_path):
                        continue

                    files = os.listdir(old_folder_path)
                    if not files:
                        continue

                    print(f"      📁 Moving {len(files)} files from {old_folder}/")

                    # Map old folder names to new structure
                    new_folder_name = old_folder
                    if old_folder == 'lab results':
                        new_folder_name = 'lab'

                    new_folder_path = os.path.join(new_base_path, new_folder_name)

                    for filename in files:
                        old_file_path = os.path.join(old_folder_path, filename)
                        new_file_path = os.path.join(new_folder_path, filename)

                        if not dry_run:
                            try:
                                # Create new directory if needed
                                os.makedirs(new_folder_path, exist_ok=True)

                                # Move file
                                shutil.move(old_file_path, new_file_path)
                                print(f"        ✅ Moved: {filename}")
                                moved_count += 1
                            except Exception as e:
                                print(f"        ❌ Error moving {filename}: {str(e)}")
                                error_count += 1
                        else:
                            print(f"        [DRY RUN] Would move: {filename}")
                            moved_count += 1

                # Remove empty old folders
                if not dry_run:
                    for old_folder in old_structure_folders:
                        old_folder_path = os.path.join(client_path, old_folder)
                        if os.path.exists(old_folder_path) and not os.listdir(old_folder_path):
                            try:
                                os.rmdir(old_folder_path)
                                print(f"      🗑️  Removed empty folder: {old_folder}/")
                            except Exception as e:
                                print(f"      ⚠️  Could not remove {old_folder}/: {str(e)}")

    # Print summary
    print(f"\n{'='*100}")
    print(f"MIGRATION SUMMARY")
    print(f"{'='*100}")
    print(f"Files {'would be moved' if dry_run else 'moved'}: {moved_count}")
    print(f"Files skipped: {skip_count}")
    print(f"Errors: {error_count}")
    print(f"{'='*100}\n")

    if dry_run:
        print("⚠️  This was a DRY RUN - no files were actually moved")
        print("⚠️  Run with --live flag to perform actual migration")
    else:
        print("✅ Migration complete!")


if __name__ == "__main__":
    print("\n" + "="*100)
    print("FILE PATH MIGRATION TOOL")
    print("="*100)

    # Check for --live flag
    dry_run = '--live' not in sys.argv

    if dry_run:
        print("\n⚠️  RUNNING IN DRY RUN MODE (no changes will be made)")
        print("⚠️  Add --live flag to perform actual migration\n")
    else:
        print("\n🚨 RUNNING IN LIVE MODE - FILES WILL BE MOVED")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration cancelled")
            sys.exit(0)
        print()

    try:
        migrate_files(dry_run=dry_run)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
