#!/usr/bin/env python3
"""
Test script to verify that compliance documents create folders with original client names
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def test_compliance_folder_creation():
    """Test that compliance documents create folders with original client names"""
    print("🧪 Testing Compliance Document Folder Creation")
    print("=" * 60)
    
    from django.conf import settings
    from main.models import FoodSafetyAgencyInspection
    
    # Get a sample inspection with a client name that has spaces/special characters
    sample_inspection = FoodSafetyAgencyInspection.objects.filter(
        client_name__isnull=False,
        date_of_inspection__isnull=False
    ).first()
    
    if not sample_inspection:
        print("❌ No sample inspection found for testing")
        return False
    
    client_name = sample_inspection.client_name
    inspection_date = sample_inspection.date_of_inspection
    
    print(f"📋 Testing with client: {client_name}")
    print(f"📅 Testing with date: {inspection_date}")
    
    # Test the compliance document folder creation functions
    from main.views.core_views import download_compliance_document
    
    # Create a test compliance document folder
    test_file_id = "test_file_123"
    test_account_code = "TEST001"
    test_commodity = "POULTRY"
    test_filename = "test_compliance_document.pdf"
    
    print(f"\n📄 Testing compliance document folder creation...")
    print(f"   🏢 Client: {client_name}")
    print(f"   📅 Date: {inspection_date}")
    print(f"   🥩 Commodity: {test_commodity}")
    
    try:
        # This should create a folder with the original client name
        result_path = download_compliance_document(
            file_id=test_file_id,
            account_code=test_account_code,
            commodity=test_commodity,
            inspection_date=inspection_date,
            filename=test_filename,
            client_name=client_name,
            request=None
        )
        
        if result_path:
            print(f"   ✅ Compliance document function returned: {result_path}")
            
            # Check if the folder was created with the original client name
            expected_path_parts = [
                'media', 'inspection',
                inspection_date.strftime('%Y'),
                inspection_date.strftime('%B'),
                client_name,  # Should be original name with spaces
                'Compliance',
                test_commodity
            ]
            
            expected_path = os.path.join(*expected_path_parts)
            full_expected_path = os.path.join(Path(__file__).parent, expected_path)
            
            print(f"   📁 Expected path: {expected_path}")
            print(f"   📁 Full expected path: {full_expected_path}")
            
            if os.path.exists(full_expected_path):
                print(f"   ✅ Compliance folder created with original client name!")
                
                # List files in the directory
                files = os.listdir(full_expected_path)
                print(f"   📄 Files in directory: {files}")
                
                return True
            else:
                print(f"   ❌ Compliance folder not found at expected path")
                
                # Check what folders actually exist
                parent_dir = os.path.dirname(full_expected_path)
                if os.path.exists(parent_dir):
                    folders = os.listdir(parent_dir)
                    print(f"   📁 Available folders: {folders}")
                    
                    # Check if there's a sanitized version
                    sanitized_name = client_name.replace(' ', '').replace('-', '').replace("'", '')
                    if sanitized_name in folders:
                        print(f"   ⚠️  Found sanitized folder: {sanitized_name}")
                        print(f"   ⚠️  This suggests the function is still using old logic")
                        return False
                else:
                    print(f"   ❌ Parent directory not found: {parent_dir}")
                return False
        else:
            print(f"   ❌ Compliance document function returned None")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing compliance document creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_existing_compliance_folders():
    """Check what compliance folders currently exist"""
    print("\n📁 Checking existing compliance folder structure...")
    
    from django.conf import settings
    
    inspection_base = os.path.join(settings.MEDIA_ROOT, 'inspection')
    
    if not os.path.exists(inspection_base):
        print("❌ No inspection folder found")
        return
    
    # Check current year/month
    current_year = datetime.now().year
    current_month = datetime.now().strftime('%B')
    
    year_path = os.path.join(inspection_base, str(current_year))
    month_path = os.path.join(year_path, current_month)
    
    if os.path.exists(month_path):
        print(f"📁 Checking compliance folders in {current_year}/{current_month}:")
        folders = os.listdir(month_path)
        compliance_folders = []
        
        for folder in folders:
            folder_path = os.path.join(month_path, folder)
            if os.path.isdir(folder_path):
                # Check if it has a Compliance subfolder
                compliance_path = os.path.join(folder_path, 'Compliance')
                if os.path.exists(compliance_path):
                    compliance_folders.append(folder)
        
        if compliance_folders:
            print(f"   📁 Compliance folders found:")
            for folder in compliance_folders[:10]:  # Show first 10
                print(f"      📁 {folder}")
        else:
            print(f"   ❌ No compliance folders found")
    else:
        print(f"❌ Month folder not found: {month_path}")

if __name__ == "__main__":
    try:
        # Check existing folders first
        check_existing_compliance_folders()
        
        # Test compliance folder creation
        success = test_compliance_folder_creation()
        
        if success:
            print("\n🎉 Compliance folder creation test PASSED!")
            print("✅ Compliance documents now create folders with original client names")
        else:
            print("\n❌ Compliance folder creation test FAILED!")
            print("⚠️  Check the error messages above")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
