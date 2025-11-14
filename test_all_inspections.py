"""
Test pulling compliance documents for ALL inspections
"""

import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, Client
from main.services.google_drive_service import GoogleDriveService
from main.views.core_views import load_drive_files_real, find_document_link_apps_script_replica, download_compliance_document
from django.http import HttpRequest
from datetime import date

def test_all_inspections():
    print("=" * 80)
    print("PULLING COMPLIANCE DOCUMENTS FOR ALL INSPECTIONS")
    print("=" * 80)
    print()
    
    request = HttpRequest()
    
    # Load Google Drive files
    print("Loading Google Drive files...")
    file_lookup = load_drive_files_real(request, use_cache=True)
    print(f"Loaded {len(file_lookup)} files from Google Drive")
    print()
    
    # Get all inspections
    start_date = date(2025, 10, 1)
    end_date = date(2026, 4, 1)
    
    inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=start_date,
        date_of_inspection__lt=end_date
    ).order_by('-date_of_inspection')
    
    print(f"Found {inspections.count()} inspections to process")
    print()
    
    # Build client mapping
    client_map = {}
    for client in Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code=''):
        client_map[client.name] = client.internal_account_code
    
    print(f"Loaded {len(client_map)} client mappings")
    print()
    print("Starting download of compliance documents...")
    print()
    
    downloaded = 0
    skipped = 0
    not_found = 0
    
    for i, inspection in enumerate(inspections):
        # Show progress every 100 inspections
        if (i + 1) % 100 == 0:
            print(f"Progress: {i + 1}/{inspections.count()} inspections processed | Downloaded: {downloaded} | Skipped: {skipped} | Not Found: {not_found}")
        
        # Get account code
        account_code = client_map.get(inspection.client_name)
        
        if not account_code:
            not_found += 1
            continue
        
        # Find document
        document_link = find_document_link_apps_script_replica(
            account_code,
            inspection.commodity,
            inspection.date_of_inspection,
            file_lookup
        )
        
        if not document_link or document_link == "Document Not Found":
            not_found += 1
            continue
        
        # Find file info and download
        found_file = False
        for file_key, file_info in file_lookup.items():
            if (file_info.get('commodity', '').lower() == str(inspection.commodity).lower().strip() and
                file_info.get('accountCode') == account_code):
                
                # Download the file
                downloaded_path = download_compliance_document(
                    file_info['file_id'],
                    account_code,
                    inspection.commodity,
                    inspection.date_of_inspection,
                    file_info['name'],
                    inspection.client_name,
                    None
                )
                
                if downloaded_path:
                    downloaded += 1
                else:
                    skipped += 1
                found_file = True
                break
        
        if not found_file:
            not_found += 1
    
    print()
    print("=" * 80)
    print("DOWNLOAD COMPLETE")
    print("=" * 80)
    print(f"Total inspections: {inspections.count()}")
    print(f"Downloaded: {downloaded}")
    print(f"Skipped (already exist): {skipped}")
    print(f"Not found: {not_found}")
    print("=" * 80)

if __name__ == "__main__":
    test_all_inspections()

