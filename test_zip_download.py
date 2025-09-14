#!/usr/bin/env python3
"""
Test script for ZIP download functionality
Tests the download_all_inspection_files function to ensure it works correctly
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def test_zip_download():
    """Test the ZIP download functionality"""
    print("🧪 Testing ZIP Download Functionality")
    print("=" * 60)
    
    # Import required modules
    from django.test import RequestFactory
    from django.contrib.auth import get_user_model
    from main.views.core_views import download_all_inspection_files
    import json
    
    # Create test user
    User = get_user_model()
    try:
        test_user = User.objects.get(username='developer')
        print(f"✅ Using existing test user: {test_user.username}")
    except User.DoesNotExist:
        test_user = User.objects.create_user(
            username='test_user',
            password='test_password',
            role='admin'
        )
        print(f"✅ Created test user: {test_user.username}")
    
    # Create request factory
    factory = RequestFactory()
    
    # Test cases
    test_cases = [
        {
            'client_name': 'Roots Butchery - Soshanguve Crossing',
            'inspection_date': '2025-09-04',
            'group_id': 'RootsButcherySoshanguveCrossing_20250904'
        },
        {
            'client_name': 'SUPERSPAR - Southernwood East London', 
            'inspection_date': '2025-09-08',
            'group_id': 'SUPERSPARSouthernwoodEastLondon_20250908'
        },
        {
            'client_name': 'Bayswater Kwikspar',
            'inspection_date': '2025-09-02', 
            'group_id': 'BayswaterKwikspar_20250902'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['client_name']}")
        print("-" * 50)
        
        # Create POST request
        request_data = {
            'client_name': test_case['client_name'],
            'inspection_date': test_case['inspection_date'],
            'group_id': test_case['group_id']
        }
        
        request = factory.post(
            '/inspections/download-all-files/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        request.user = test_user
        
        try:
            # Call the function
            print(f"📞 Calling download_all_inspection_files...")
            response = download_all_inspection_files(request)
            
            # Check response
            if hasattr(response, 'status_code'):
                print(f"📊 Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    if hasattr(response, 'content'):
                        content_length = len(response.content)
                        print(f"📦 ZIP Size: {content_length:,} bytes")
                        
                        if content_length > 1000:  # More than 1KB indicates actual content
                            print(f"✅ SUCCESS: ZIP appears to contain actual files")
                            
                            # Try to extract filename from response
                            content_disposition = response.get('Content-Disposition', '')
                            if 'filename=' in content_disposition:
                                filename = content_disposition.split('filename=')[1].strip('"')
                                print(f"📄 ZIP Filename: {filename}")
                        else:
                            print(f"❌ FAILED: ZIP too small ({content_length} bytes) - likely corrupted")
                    else:
                        print(f"❌ FAILED: Response has no content")
                else:
                    print(f"❌ FAILED: HTTP {response.status_code}")
                    if hasattr(response, 'content'):
                        try:
                            error_data = json.loads(response.content)
                            print(f"   Error: {error_data.get('error', 'Unknown error')}")
                        except:
                            print(f"   Raw response: {response.content[:200]}")
            
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()

def test_file_structure():
    """Test and display the actual file structure"""
    print("\n\n🗂️ Testing File Structure")
    print("=" * 60)
    
    from django.conf import settings
    
    inspection_base = os.path.join(settings.MEDIA_ROOT, 'inspection')
    print(f"📁 Inspection base: {inspection_base}")
    
    if not os.path.exists(inspection_base):
        print("❌ Inspection folder doesn't exist!")
        return
    
    # Check recent months
    import datetime
    current_date = datetime.datetime.now()
    
    for months_back in range(3):  # Check last 3 months
        check_date = current_date - datetime.timedelta(days=months_back * 30)
        year_folder = check_date.strftime('%Y')
        month_folder = check_date.strftime('%B')
        
        year_month_path = os.path.join(inspection_base, year_folder, month_folder)
        
        if os.path.exists(year_month_path):
            print(f"\n📅 Found: {year_folder}/{month_folder}")
            
            # List client folders
            client_folders = [f for f in os.listdir(year_month_path) if os.path.isdir(os.path.join(year_month_path, f))]
            print(f"   👥 Client folders ({len(client_folders)}): {client_folders[:5]}...")  # Show first 5
            
            # Check a sample client folder for structure
            if client_folders:
                sample_client = client_folders[0]
                sample_path = os.path.join(year_month_path, sample_client)
                
                print(f"\n   🔍 Sample client structure: {sample_client}")
                if os.path.exists(sample_path):
                    contents = os.listdir(sample_path)
                    print(f"      📂 Contents: {contents}")
                    
                    # Check for compliance folder
                    compliance_path = os.path.join(sample_path, 'Compliance')
                    if os.path.exists(compliance_path):
                        compliance_contents = os.listdir(compliance_path)
                        print(f"      📋 Compliance: {compliance_contents}")
                        
                        # Check commodity folders
                        for commodity in compliance_contents:
                            commodity_path = os.path.join(compliance_path, commodity)
                            if os.path.isdir(commodity_path):
                                commodity_files = os.listdir(commodity_path)
                                print(f"         🏷️ {commodity}: {len(commodity_files)} files")

if __name__ == "__main__":
    print("🚀 Starting ZIP Download Test Suite")
    print("=" * 60)
    
    try:
        # Test file structure first
        test_file_structure()
        
        # Test ZIP download functionality
        test_zip_download()
        
        print("\n" + "=" * 60)
        print("🏁 Test Suite Completed")
        
    except Exception as e:
        print(f"\n❌ Test Suite Failed: {e}")
        import traceback
        traceback.print_exc()
