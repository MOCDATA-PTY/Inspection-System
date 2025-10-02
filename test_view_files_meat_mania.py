#!/usr/bin/env python3
"""
Test View Files functionality for Meat Mania inspection
"""

import os
import sys
import django
import requests
from io import BytesIO

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from main.models import FoodSafetyAgencyInspection

def test_view_files_meat_mania():
    """Test View Files functionality for Meat Mania inspection"""
    
    print("=== Testing View Files for Meat Mania ===")
    
    # Create test client
    client = Client()
    
    # Login as developer
    login_success = client.login(username='developer', password='XHnj1C#QkFs9')
    if not login_success:
        print("FAILED: Failed to login as developer")
        return False
    
    print("SUCCESS: Logged in as developer")
    
    # Test data for Meat Mania
    client_name = "Meat Mania"
    inspection_date = "2025-09-26"
    group_id = "Meat_Mania_20250926"
    
    print(f"Testing View Files for: {client_name} on {inspection_date}")
    
    # Test View Files endpoint
    view_files_data = {
        'client_name': client_name,
        'inspection_date': inspection_date,
        'group_id': group_id
    }
    
    print("Sending View Files request...")
    response = client.post('/inspections/files/', 
                          data=view_files_data,
                          content_type='application/json')
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("SUCCESS: View Files response received")
            print(f"Files found: {len(data.get('files', {}))}")
            
            if data.get('files'):
                print("File categories:")
                for category, files in data['files'].items():
                    print(f"  {category}: {len(files)} files")
                    for file_info in files:
                        print(f"    - {file_info.get('filename', 'Unknown')}")
            else:
                print("No files found for this inspection")
                
        except Exception as e:
            print(f"ERROR: Error parsing JSON response: {e}")
            print(f"Raw response: {response.content}")
    else:
        print(f"ERROR: View Files request failed: {response.status_code}")
        print(f"Response: {response.content}")
    
    return response.status_code == 200

def test_upload_rfi_meat_mania():
    """Test uploading RFI file for Meat Mania and then viewing files"""
    
    print("\n=== Testing RFI Upload for Meat Mania ===")
    
    # Create test client
    client = Client()
    
    # Login as developer
    login_success = client.login(username='developer', password='XHnj1C#QkFs9')
    if not login_success:
        print("FAILED: Failed to login as developer")
        return False
    
    print("SUCCESS: Logged in as developer")
    
    # Test data for Meat Mania
    client_name = "Meat Mania"
    inspection_date = "2025-09-26"
    group_id = "Meat_Mania_20250926"
    
    print(f"Testing RFI upload for: {client_name} on {inspection_date}")
    
    # Create a test PDF file
    test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF"
    
    # Test RFI upload
    upload_data = {
        'client_name': client_name,
        'inspection_date': inspection_date,
        'group_id': group_id,
        'document_type': 'rfi'
    }
    
    print("Sending RFI upload request...")
    
    # Create a proper file object for Django test client
    from django.core.files.uploadedfile import SimpleUploadedFile
    test_file = SimpleUploadedFile(
        "test_rfi_meat_mania.pdf",
        test_pdf_content,
        content_type="application/pdf"
    )
    
    print(f"Test file created: {test_file.name}, size: {test_file.size}, content_type: {test_file.content_type}")
    
    response = client.post('/upload-document/', 
                          data=upload_data,
                          files={'file': test_file})
    
    print(f"Response content: {response.content}")
    
    print(f"Upload response status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("SUCCESS: RFI upload successful")
            print(f"Full response: {data}")
            print(f"File saved: {data.get('filename', 'Unknown')}")
            print(f"File path: {data.get('file_path', 'Unknown')}")
            
            # Wait a moment for file system operations
            import time
            time.sleep(1)
            
            # Now test View Files to see if the RFI appears
            print("\nTesting View Files after RFI upload...")
            view_files_data = {
                'client_name': client_name,
                'inspection_date': inspection_date,
                'group_id': group_id
            }
            
            response = client.post('/inspections/files/', 
                                  data=view_files_data,
                                  content_type='application/json')
            
            print(f"View Files response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("SUCCESS: View Files response received after upload")
                    print(f"Files found: {len(data.get('files', {}))}")
                    
                    if data.get('files'):
                        print("File categories:")
                        for category, files in data['files'].items():
                            print(f"  {category}: {len(files)} files")
                            for file_info in files:
                                print(f"    - {file_info.get('filename', 'Unknown')}")
                    else:
                        print("No files found after upload")
                        
                except Exception as e:
                    print(f"ERROR: Error parsing View Files JSON response: {e}")
                    print(f"Raw response: {response.content}")
            else:
                print(f"ERROR: View Files request failed after upload: {response.status_code}")
                print(f"Response: {response.content}")
                
        except Exception as e:
            print(f"ERROR: Error parsing upload JSON response: {e}")
            print(f"Raw response: {response.content}")
    else:
        print(f"ERROR: RFI upload failed: {response.status_code}")
        print(f"Response: {response.content}")
    
    return response.status_code == 200

def main():
    """Main test function"""
    print("Testing View Files functionality for Meat Mania inspection")
    print("=" * 60)
    
    # Test 1: View Files before upload
    print("\n1. Testing View Files before upload...")
    view_success = test_view_files_meat_mania()
    
    # Test 2: Upload RFI and then View Files
    print("\n2. Testing RFI upload and then View Files...")
    upload_success = test_upload_rfi_meat_mania()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print(f"  View Files (before upload): {'PASS' if view_success else 'FAIL'}")
    print(f"  RFI Upload + View Files: {'PASS' if upload_success else 'FAIL'}")
    
    if view_success and upload_success:
        print("\nSUCCESS: All tests passed! View Files functionality is working correctly.")
    else:
        print("\nWARNING: Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
