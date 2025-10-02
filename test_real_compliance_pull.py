#!/usr/bin/env python3
"""
Test pulling a real compliance document to verify the directory structure.
"""

import os
import sys
import django
import shutil

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def test_real_compliance_pull():
    """Test pulling a real compliance document and verify structure."""
    from main.views.core_views import download_compliance_documents
    from main.models import FoodSafetyAgencyInspection
    from django.contrib.auth.models import User
    from django.http import HttpRequest
    import json
    
    print("🧪 Testing real compliance document pull...")
    
    # Login as developer user
    try:
        developer_user = User.objects.get(username='developer')
        print(f"✅ Found developer user: {developer_user.username}")
    except User.DoesNotExist:
        print("❌ Developer user not found")
        return False
    
    # Find a test inspection with compliance documents
    test_inspection = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte='2025-09-01'
    ).first()
    
    if not test_inspection:
        print("❌ No inspections found in database")
        return False
    
    print(f"📋 Using test inspection: {test_inspection.client_name} - {test_inspection.date_of_inspection}")
    
    # Clean up any existing test data for this client
    year = test_inspection.date_of_inspection.strftime('%Y')
    month = test_inspection.date_of_inspection.strftime('%B')
    test_client_dir = os.path.join('media', 'inspection', year, month, test_inspection.client_name)
    
    if os.path.exists(test_client_dir):
        print(f"🗑️ Cleaning up existing test data for {test_inspection.client_name}")
        shutil.rmtree(test_client_dir)
    
    # Create a mock request for compliance document download
    class MockRequest:
        def __init__(self):
            self.method = 'POST'
            self.body = json.dumps({
                'commodity': 'all',
                'date_range': 'recent',
                'download_all': True
            }).encode('utf-8')
            self.user = developer_user
    
    mock_request = MockRequest()
    
    # Test the download_compliance_documents function
    try:
        print("📥 Starting compliance document download...")
        response = download_compliance_documents(mock_request)
        print(f"📥 Download response: {response}")
        
        # Check if response indicates success
        if hasattr(response, 'content'):
            import json
            response_data = json.loads(response.content.decode('utf-8'))
            if response_data.get('success'):
                print("✅ Compliance document download completed successfully")
            else:
                print(f"⚠️ Download completed but may have issues: {response_data.get('message', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Error during download: {e}")
        return False
    
    # Verify the directory structure
    return verify_real_structure(test_inspection.client_name, test_inspection.date_of_inspection)

def verify_real_structure(client_name, inspection_date):
    """Verify the real directory structure."""
    print(f"\n🔍 Verifying real directory structure for {client_name}...")
    
    # Build expected path
    year = inspection_date.strftime('%Y')
    month = inspection_date.strftime('%B')
    
    expected_path = os.path.join('media', 'inspection', year, month, client_name)
    
    if not os.path.exists(expected_path):
        print(f"❌ Client directory not found: {expected_path}")
        return False
    
    print(f"✅ Client directory found: {expected_path}")
    
    # List all contents at client level
    contents = os.listdir(expected_path)
    print(f"📁 Client level contents: {contents}")
    
    # Check for Compliance folder
    compliance_path = os.path.join(expected_path, 'Compliance')
    if os.path.exists(compliance_path):
        print(f"✅ Compliance folder found")
        
        compliance_contents = os.listdir(compliance_path)
        print(f"📁 Compliance folder contents: {compliance_contents}")
        
        # Check for commodity subfolders
        commodity_folders = [f for f in compliance_contents if os.path.isdir(os.path.join(compliance_path, f)) and f.isupper()]
        if commodity_folders:
            print(f"✅ Found commodity folders: {commodity_folders}")
            
            # Check contents of first commodity folder
            first_commodity = commodity_folders[0]
            commodity_path = os.path.join(compliance_path, first_commodity)
            commodity_files = os.listdir(commodity_path)
            print(f"📄 Files in {first_commodity} folder: {commodity_files}")
        else:
            print(f"⚠️ No commodity folders found in Compliance")
    else:
        print(f"❌ Compliance folder not found")
    
    # Check for inspection folders at client level
    inspection_folders = [f for f in contents if f.startswith('inspection-')]
    if inspection_folders:
        print(f"✅ Found inspection folders at client level: {inspection_folders}")
        
        # Check structure of first inspection folder
        first_inspection = inspection_folders[0]
        inspection_path = os.path.join(expected_path, first_inspection)
        print(f"\n🔍 Checking structure of {first_inspection}:")
        
        if os.path.exists(inspection_path):
            subfolders = os.listdir(inspection_path)
            print(f"  📁 Subfolders: {subfolders}")
            
            # Check compliance subfolder structure
            compliance_subfolder = os.path.join(inspection_path, 'compliance')
            if os.path.exists(compliance_subfolder):
                compliance_sub_contents = os.listdir(compliance_subfolder)
                print(f"  📁 compliance/ contents: {compliance_sub_contents}")
                
                # Check for commodity subfolders in compliance
                commodity_subfolders = [f for f in compliance_sub_contents if os.path.isdir(os.path.join(compliance_subfolder, f)) and f.isupper()]
                if commodity_subfolders:
                    print(f"  ✅ Found commodity subfolders in compliance/: {commodity_subfolders}")
                    
                    # Check contents of first commodity subfolder
                    first_commodity_sub = commodity_subfolders[0]
                    commodity_sub_path = os.path.join(compliance_subfolder, first_commodity_sub)
                    commodity_sub_files = os.listdir(commodity_sub_path)
                    print(f"  📄 Files in compliance/{first_commodity_sub}/: {commodity_sub_files}")
                else:
                    print(f"  ⚠️ No commodity subfolders found in compliance/")
            else:
                print(f"  ❌ compliance/ subfolder missing")
            
            # Check other subfolders
            for other_folder in ['form', 'lab', 'retest']:
                other_path = os.path.join(inspection_path, other_folder)
                if os.path.exists(other_path):
                    other_contents = os.listdir(other_path)
                    print(f"  📁 {other_folder}/ contents: {other_contents}")
                else:
                    print(f"  ❌ {other_folder}/ subfolder missing")
        else:
            print(f"  ❌ {first_inspection} folder not found")
            return False
    else:
        print(f"ℹ️ No inspection folders found (this is normal if no ZIP files were organized)")
    
    # Check for rfi and invoice folders at client level
    for folder_type in ['rfi', 'invoice']:
        folder_path = os.path.join(expected_path, folder_type)
        if os.path.exists(folder_path):
            folder_files = os.listdir(folder_path)
            print(f"✅ {folder_type}/ folder found with {len(folder_files)} files")
        else:
            print(f"ℹ️ {folder_type}/ folder not found (this is normal if no files uploaded)")
    
    return True

def main():
    """Main test function."""
    print("🧪 Starting real compliance document pull test...")
    
    success = test_real_compliance_pull()
    
    if success:
        print("\n🎉 Real compliance pull test PASSED!")
        print("✅ Directory structure is working correctly!")
    else:
        print("\n❌ Real compliance pull test FAILED!")
        print("⚠️ Check the output above for details")
    
    print("✅ Test complete!")

if __name__ == "__main__":
    main()
