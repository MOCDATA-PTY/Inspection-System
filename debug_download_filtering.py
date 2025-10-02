#!/usr/bin/env python3
"""
Debug script to see what files are being found and filtered in download all functionality
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime
import re

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def debug_file_filtering():
    """Debug the file filtering logic"""
    print("🔍 Debugging Download All File Filtering")
    print("=" * 60)
    
    from django.conf import settings
    
    # Test parameters
    client_name = "Test Compliance Client"
    inspection_date = "2025-09-14"
    
    print(f"📋 Client: {client_name}")
    print(f"📅 Inspection Date: {inspection_date}")
    
    # Parse date
    date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
    year_folder = date_obj.strftime('%Y')
    month_folder = date_obj.strftime('%B')
    
    print(f"📁 Looking in: {year_folder}/{month_folder}")
    
    # Base inspection path
    inspection_base = os.path.join(settings.MEDIA_ROOT, 'inspection')
    year_path = os.path.join(inspection_base, year_folder)
    month_path = os.path.join(year_path, month_folder)
    
    print(f"📁 Full path: {month_path}")
    
    if not os.path.exists(month_path):
        print("❌ Month folder does not exist")
        return
    
    # List all folders in the month
    print(f"\n📂 Folders in {month_folder}:")
    for item in os.listdir(month_path):
        item_path = os.path.join(month_path, item)
        if os.path.isdir(item_path):
            print(f"   📁 {item}")
    
    # Find client folder
    client_folder_pattern = re.sub(r'[^a-zA-Z0-9_]', '_', client_name)
    client_folder_pattern = re.sub(r'_+', '_', client_folder_pattern).strip('_')
    
    print(f"\n🔍 Looking for client folder pattern: {client_folder_pattern}")
    
    matching_folders = []
    for item in os.listdir(month_path):
        item_path = os.path.join(month_path, item)
        if os.path.isdir(item_path):
            if client_folder_pattern.lower() in item.lower():
                matching_folders.append(item)
                print(f"   ✅ Match found: {item}")
            else:
                print(f"   ❌ No match: {item}")
    
    if not matching_folders:
        print("❌ No matching client folders found")
        return
    
    # Process the first matching folder
    client_folder = matching_folders[0]
    client_folder_path = os.path.join(month_path, client_folder)
    
    print(f"\n📁 Processing folder: {client_folder}")
    print(f"📁 Full path: {client_folder_path}")
    
    # List all files in the folder
    print(f"\n📄 Files in folder:")
    for root, dirs, files in os.walk(client_folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, client_folder_path)
            file_size = os.path.getsize(file_path)
            print(f"   📄 {relative_path} ({file_size} bytes)")
    
    # Test the date filtering function
    print(f"\n🧪 Testing date filtering function:")
    
    def is_file_for_inspection_date(filename, target_date):
        """Check if a file belongs to the specific inspection date"""
        try:
            target_date_obj = datetime.strptime(target_date, '%Y-%m-%d') if isinstance(target_date, str) else target_date
            target_date_str = target_date_obj.strftime('%Y-%m-%d')
            target_date_compact = target_date_obj.strftime('%Y%m%d')
            
            print(f"   🔍 Checking file: {filename}")
            print(f"   📅 Target date string: {target_date_str}")
            print(f"   📅 Target date compact: {target_date_compact}")
            
            # Check for YYYY-MM-DD format (compliance files) - must be exact match
            date_pattern_str = r'(?:^|[^0-9])' + re.escape(target_date_str) + r'(?:[^0-9]|$)'
            if re.search(date_pattern_str, filename):
                print(f"   ✅ Matched YYYY-MM-DD pattern")
                return True
            
            # Check for YYYYMMDD format (uploaded files) - must be exact match
            date_pattern_compact = r'(?:^|[^0-9])' + re.escape(target_date_compact) + r'(?:[^0-9]|$)'
            if re.search(date_pattern_compact, filename):
                print(f"   ✅ Matched YYYYMMDD pattern")
                return True
            
            print(f"   ❌ No date pattern found - EXCLUDED")
            return False
            
        except Exception as e:
            print(f"   ⚠️ Error checking file date: {e}")
            return True
    
    # Test with actual files
    for root, dirs, files in os.walk(client_folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, client_folder_path)
            file_size = os.path.getsize(file_path)
            
            print(f"\n   📄 Testing: {file}")
            is_included = is_file_for_inspection_date(file, inspection_date)
            print(f"   📊 Result: {'INCLUDED' if is_included else 'EXCLUDED'}")
            print(f"   📊 Size: {file_size} bytes")

if __name__ == "__main__":
    try:
        debug_file_filtering()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
