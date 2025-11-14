#!/usr/bin/env python3
"""
Test manual file upload and View Files functionality for Meat Mania inspection
"""

import os
import sys
import django
from io import BytesIO

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from main.models import FoodSafetyAgencyInspection
from django.conf import settings

def test_manual_file_upload():
    """Test manually creating a file and then viewing it"""
    
    print("=== Testing Manual File Upload for Meat Mania ===")
    
    # Test data for Meat Mania
    client_name = "Meat Mania"
    inspection_date = "2025-09-26"
    group_id = "Meat_Mania_20250926"
    
    print(f"Testing manual file upload for: {client_name} on {inspection_date}")
    
    # Create the folder structure manually
    base_dir = os.path.join(settings.MEDIA_ROOT, 'inspection')
    year_dir = os.path.join(base_dir, '2025')
    month_dir = os.path.join(year_dir, 'September')
    client_dir = os.path.join(month_dir, client_name)
    rfi_dir = os.path.join(client_dir, 'rfi')
    
    print(f"Creating folder structure: {rfi_dir}")
    os.makedirs(rfi_dir, exist_ok=True)
    
    # Create a test PDF file
    test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF"
    
    # Save the file
    filename = f"{group_id}_rfi_20250926_120000.pdf"
    file_path = os.path.join(rfi_dir, filename)
    
    with open(file_path, 'wb') as f:
        f.write(test_pdf_content)
    
    print(f"Created test file: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    print(f"File size: {os.path.getsize(file_path)} bytes")
    
    # Now test View Files functionality
    print("\n=== Testing View Files after manual upload ===")
    
    # Create test client
    client = Client()
    
    # Login as developer
    login_success = client.login(username='developer', password='XHnj1C#QkFs9')
    if not login_success:
        print("FAILED: Failed to login as developer")
        return False
    
    print("SUCCESS: Logged in as developer")
    
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

def main():
    """Main test function"""
    print("Testing manual file upload and View Files functionality")
    print("=" * 60)
    
    success = test_manual_file_upload()
    
    print("\n" + "=" * 60)
    if success:
        print("SUCCESS: Manual file upload and View Files functionality is working!")
    else:
        print("FAILED: Some issues found. Check the output above for details.")

if __name__ == "__main__":
    main()
