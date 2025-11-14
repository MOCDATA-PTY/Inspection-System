"""
Simple test to verify compliance document downloading works
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, Client
from main.services.google_drive_service import GoogleDriveService
from main.views.core_views import load_drive_files_real, find_document_link_apps_script_replica, download_compliance_document
from django.http import HttpRequest

def test_simple_download():
    print("Testing compliance document download...")
    
    # Get one inspection
    inspection = FoodSafetyAgencyInspection.objects.first()
    if not inspection:
        print("No inspections found")
        return
    
    print(f"Testing with inspection: {inspection.id}")
    print(f"Client: {inspection.client_name}")
    print(f"Date: {inspection.date_of_inspection}")
    
    # Get account code
    client = Client.objects.filter(name=inspection.client_name).first()
    account_code = client.internal_account_code if client else None
    
    if not account_code:
        print("No account code found")
        return
    
    print(f"Account code: {account_code}")
    
    # Load Google Drive files
    request = HttpRequest()
    print("Loading Google Drive files...")
    file_lookup = load_drive_files_real(request, use_cache=True)
    print(f"Loaded {len(file_lookup)} files")
    
    # Find document
    document_link = find_document_link_apps_script_replica(
        account_code,
        inspection.commodity,
        inspection.date_of_inspection,
        file_lookup
    )
    
    if not document_link or document_link == "Document Not Found":
        print("No document found")
        return
    
    print(f"Found document link: {document_link[:80]}...")
    
    # Find file info for download
    for file_key, file_info in file_lookup.items():
        if (file_info.get('commodity', '').lower() == str(inspection.commodity).lower().strip() and
            file_info.get('accountCode') == account_code):
            
            print(f"Downloading: {file_info['name']}")
            
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
                print(f"SUCCESS: Downloaded to {downloaded_path}")
            else:
                print("FAILED: Download failed")
            return
    
    print("Could not find file to download")

if __name__ == "__main__":
    test_simple_download()

