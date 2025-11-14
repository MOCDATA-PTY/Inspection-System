"""
Simple test script to download a few compliance documents
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, Client
from main.views.core_views import find_document_link_apps_script_replica, download_compliance_document
from main.services.google_drive_service import GoogleDriveService
from datetime import date, datetime
import re

def test_download():
    print("=" * 80)
    print("TEST: Download Compliance Documents from October 2025")
    print("=" * 80)
    print()

    # Load Drive files focusing on October 2025
    print("[Loading] Fetching Google Drive files for October 2025...")
    drive_service = GoogleDriveService()
    folder_id = "18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4"

    print("[Drive] Fetching files...")
    all_files = drive_service.list_files_in_folder(folder_id, request=None, max_items=5000)
    print(f"[Drive] Retrieved {len(all_files)} files total")

    # Filter for October 2025 files only
    october_files = []
    for file in all_files:
        file_name = file.get('name', '')
        if '2025-10-' in file_name:  # October 2025 files
            october_files.append(file)

    print(f"[Filter] Found {len(october_files)} files from October 2025")

    # Build file lookup for October files
    file_lookup = {}
    for file in october_files:
        file_name = file.get('name', '')
        file_id = file.get('id', '')
        web_view_link = file.get('webViewLink', '')

        full_pattern = re.match(r'^([A-Za-z]+)-([A-Z]{2}-[A-Z]{3}-[A-Z]{3}-[A-Z]{2,3}-\d+)-(\d{4}-\d{2}-\d{2})', file_name)

        if full_pattern and file_id:
            commodity_prefix = full_pattern.group(1)
            account_code = full_pattern.group(2)
            zip_date_str = full_pattern.group(3)

            try:
                zip_date = datetime.strptime(zip_date_str, '%Y-%m-%d')
            except:
                continue

            compound_key = f"{commodity_prefix.lower()}|{account_code}|{zip_date_str}"

            file_lookup[compound_key] = {
                'url': web_view_link or f"https://drive.google.com/file/d/{file_id}/view",
                'name': file_name,
                'commodity': commodity_prefix,
                'accountCode': account_code,
                'zipDate': zip_date,
                'zipDateStr': zip_date_str,
                'file_id': file_id
            }

    print(f"[OK] Built lookup with {len(file_lookup)} October files")

    if len(file_lookup) == 0:
        print("[ERROR] No October 2025 files found in Drive")
        return

    # Show sample
    print("\n[Sample] First 5 October files:")
    for i, (key, info) in enumerate(list(file_lookup.items())[:5]):
        print(f"  {i+1}. {info['name']}")
        print(f"      Account: {info['accountCode']} | Date: {info['zipDateStr']}")
    print()

    # Get account codes from October files
    account_codes = list(set([info['accountCode'] for info in file_lookup.values()]))
    print(f"[Matching] Looking for inspections with {len(account_codes)} account codes...")

    # Find clients with these account codes
    clients = Client.objects.filter(internal_account_code__in=account_codes)
    print(f"[Found] {len(clients)} clients")

    # Get inspections from October 2025 for these clients
    start_date = date(2025, 10, 1)
    end_date = date(2025, 11, 1)

    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__in=[c.name for c in clients],
        date_of_inspection__gte=start_date,
        date_of_inspection__lt=end_date
    ).order_by('-date_of_inspection')[:5]

    print(f"[Testing] {inspections.count()} inspections from October 2025")
    print()

    downloaded_count = 0
    not_found_count = 0

    for inspection in inspections:
        print(f"\n{'='*60}")
        print(f"ID: {inspection.id} | Client: {inspection.client_name}")
        print(f"Commodity: {inspection.commodity} | Date: {inspection.date_of_inspection}")
        print(f"{'='*60}")

        # Get account code
        client = Client.objects.filter(name=inspection.client_name).first()
        if not client or not client.internal_account_code:
            print(f"[SKIP] No account code for client")
            continue

        account_code = client.internal_account_code
        print(f"Account: {account_code}")

        # Find document
        commodity_prefix = str(inspection.commodity).lower().strip()
        if commodity_prefix == 'eggs':
            commodity_prefix = 'egg'

        best_match = None
        best_days_diff = 999

        for file_key, file_info in file_lookup.items():
            if (file_info.get('commodity', '').lower() == commodity_prefix and
                file_info.get('accountCode') == account_code):

                days_diff = abs((file_info['zipDate'].date() - inspection.date_of_inspection).days)

                if days_diff <= 15 and days_diff < best_days_diff:
                    best_match = file_info
                    best_days_diff = days_diff

        if best_match:
            print(f"[FOUND] {best_match['name']} (within {best_days_diff} days)")
            print(f"[Download] Starting download...")

            # Download
            downloaded_path = download_compliance_document(
                best_match['file_id'],
                account_code,
                inspection.commodity,
                inspection.date_of_inspection,
                best_match['name'],
                inspection.client_name,
                None
            )

            if downloaded_path:
                print(f"[SUCCESS] Downloaded to:")
                print(f"  {downloaded_path}")
                downloaded_count += 1
            else:
                print(f"[ERROR] Download failed")
        else:
            print(f"[NOT FOUND] No matching file")
            not_found_count += 1

    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print(f"Downloaded: {downloaded_count} | Not found: {not_found_count}")
    print()
    print("Check folder structure at: media/inspection/2025/October/ClientName/")
    print("  - Inspection-XXX/Compliance/COMMODITY/ (individual docs)")
    print("  - Compliance/COMMODITY/ (general docs)")
    print("=" * 80)

if __name__ == "__main__":
    test_download()
