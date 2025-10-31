"""
Download ALL compliance documents from Google Drive
"""

import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.google_drive_service import GoogleDriveService
from main.views.core_views import load_drive_files_real
from django.http import HttpRequest
from django.conf import settings

def download_all():
    print("=" * 80)
    print("DOWNLOADING ALL COMPLIANCE DOCUMENTS")
    print("=" * 80)
    print()
    
    request = HttpRequest()
    
    # Load file lookup
    print("Loading Google Drive files...")
    file_lookup = load_drive_files_real(request, use_cache=True)
    print(f"Found {len(file_lookup)} files")
    print()
    
    # Authenticate Google Drive
    drive_service = GoogleDriveService()
    drive_service.authenticate(request)
    
    # Create download directory
    download_dir = os.path.join(settings.MEDIA_ROOT, 'compliance_downloads')
    os.makedirs(download_dir, exist_ok=True)
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    print(f"Downloading all {len(file_lookup)} files...")
    print("This will take a while...")
    print()
    
    start_time = time.time()
    
    for i, (key, info) in enumerate(file_lookup.items()):
        file_id = info.get('file_id')
        filename = info.get('name')
        file_path = os.path.join(download_dir, filename)
        
        # Progress every 50 files
        if (i + 1) % 50 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            remaining = (len(file_lookup) - i - 1) / rate if rate > 0 else 0
            print(f"Progress: {i + 1}/{len(file_lookup)} | Downloaded: {downloaded} | Failed: {failed} | Time: {elapsed/60:.1f}m")
        
        if not file_id:
            failed += 1
            continue
        
        if os.path.exists(file_path):
            skipped += 1
            continue
        
        try:
            success = drive_service.download_file(file_id, file_path, request=request)
            if success:
                downloaded += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            failed += 1
    
    total_time = time.time() - start_time
    
    print()
    print("=" * 80)
    print(f"Downloaded: {downloaded}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Location: {download_dir}")
    print("=" * 80)

if __name__ == "__main__":
    download_all()

