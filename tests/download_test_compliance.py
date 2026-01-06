#!/usr/bin/env python
"""Download ALL compliance files for Test1 and Test2 inspections"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from main.services.daily_compliance_sync import DailyComplianceSyncService
from main.views.core_views import download_compliance_document

print("=" * 60)
print("DOWNLOADING ALL COMPLIANCE FILES FOR TEST INSPECTIONS")
print("=" * 60)

# Load files from Google Drive
sync = DailyComplianceSyncService()
sync.is_running = True
print("\nLoading Google Drive files...")
file_lookup = sync.load_drive_files_standalone()

if not file_lookup:
    print("ERROR: Could not load files from Google Drive")
    sys.exit(1)

print(f"Loaded {len(file_lookup)} files\n")

# Find and download for Test1 and Test2
for name in ['Test1', 'Test2']:
    print("-" * 40)
    insp = FoodSafetyAgencyInspection.objects.filter(client_name__icontains=name).first()

    if not insp:
        print(f"{name}: Inspection not found in database")
        continue

    print(f"{name}:")
    print(f"  Account Code: {insp.internal_account_code}")
    print(f"  Commodity: {insp.commodity}")
    print(f"  Date: {insp.date_of_inspection}")

    account_code = insp.internal_account_code
    if not account_code:
        print(f"  ERROR: No account code")
        continue

    # Find ALL matching files by account code (within 15 days)
    matching_files = []

    for file_key, file_info in file_lookup.items():
        if file_info['accountCode'] == account_code:
            # Check date within 15 days
            file_date = file_info['zipDate']
            if hasattr(file_date, 'date'):
                file_date = file_date.date()

            insp_date = insp.date_of_inspection
            if hasattr(insp_date, 'date'):
                insp_date = insp_date.date()

            days_diff = abs((file_date - insp_date).days)
            if days_diff <= 15:
                matching_files.append({
                    'file_info': file_info,
                    'days_diff': days_diff
                })

    if matching_files:
        print(f"\n  FOUND {len(matching_files)} FILES:")

        for match in matching_files:
            file_info = match['file_info']
            days_diff = match['days_diff']

            print(f"\n  - {file_info['name']}")
            print(f"    Commodity: {file_info['commodity']}")
            print(f"    Days diff: {days_diff}")
            print(f"    Downloading...")

            # Download the file - use file's commodity for folder organization
            try:
                downloaded_path = download_compliance_document(
                    file_info['file_id'],
                    account_code,
                    file_info['commodity'],  # Use file's commodity, not inspection's
                    insp.date_of_inspection,
                    file_info['name'],
                    insp.client_name,
                    None
                )

                if downloaded_path:
                    print(f"    SUCCESS: {downloaded_path}")
                else:
                    print(f"    FAILED: Download returned None")
            except Exception as e:
                print(f"    ERROR: {e}")
    else:
        print(f"  NOT FOUND: No files in Google Drive for account code {account_code}")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
