#!/usr/bin/env python3
"""
Test script to debug file listing and create test files for Canonbury Eggs
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.models import FoodSafetyAgencyInspection

def create_test_files():
    """Create test files for Canonbury Eggs to demonstrate the system working"""
    
    # Define the path structure
    media_root = settings.MEDIA_ROOT
    year_folder = "2025"
    month_folder = "September"
    client_folder = "CanonburyEggs"  # This matches the folder naming convention
    
    base_path = os.path.join(media_root, 'inspection', year_folder, month_folder, client_folder)
    
    print(f"🔧 Creating test files in: {base_path}")
    
    # Create directories
    folders = ['rfi', 'invoice', 'lab', 'lab_form', 'retest']
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f"✅ Created directory: {folder_path}")
    
    # Create test PDF content (simple text files for testing)
    test_files = {
        'rfi': [
            'Canonbury_Eggs_20250912_rfi_20250914_142552.pdf',
            'Canonbury_Eggs_20250912_rfi_response_20250914_143000.pdf'
        ],
        'invoice': [
            'Canonbury_Eggs_20250912_invoice_20250914_142600.pdf'
        ],
        'lab': [
            'Canonbury_Eggs_20250912_lab_report_20250914_150000.pdf'
        ],
        'lab_form': [
            'Canonbury_Eggs_20250912_lab_form_20250914_150500.pdf'
        ],
        'retest': []  # No retest files for this example
    }
    
    # Create the actual files
    for folder, files in test_files.items():
        for filename in files:
            file_path = os.path.join(base_path, folder, filename)
            with open(file_path, 'w') as f:
                f.write(f"""TEST PDF CONTENT FOR {filename}
                
This is a test file created to demonstrate the file listing system.
File: {filename}
Created: {datetime.now()}
Path: {file_path}

This would normally be a PDF file with inspection data.
""")
            print(f"✅ Created test file: {file_path}")
    
    # Also create compliance files
    compliance_path = os.path.join(base_path, 'Compliance', 'Eggs')
    os.makedirs(compliance_path, exist_ok=True)
    
    compliance_files = [
        'Canonbury_Eggs_compliance_certificate_20250912.pdf',
        'Canonbury_Eggs_compliance_audit_20250912.pdf'
    ]
    
    for filename in compliance_files:
        file_path = os.path.join(compliance_path, filename)
        with open(file_path, 'w') as f:
            f.write(f"""COMPLIANCE DOCUMENT: {filename}
            
This is a test compliance document.
Created: {datetime.now()}
Client: Canonbury Eggs
""")
        print(f"✅ Created compliance file: {file_path}")
    
    return base_path

def test_file_listing():
    """Test the file listing function directly"""
    
    print("\n🧪 Testing file listing function...")
    
    # Import the function
    from main.views.core_views import list_uploaded_files
    from django.http import HttpRequest
    
    # Create a mock request
    request = HttpRequest()
    request.method = 'GET'
    request.GET = {'group_id': 'Canonbury_Eggs_20250912'}
    
    try:
        response = list_uploaded_files(request)
        print(f"✅ Function executed successfully")
        print(f"📄 Response status: {response.status_code}")
        print(f"📄 Response content: {response.content.decode()[:500]}...")
        
        # Parse JSON response
        import json
        data = json.loads(response.content.decode())
        print(f"📊 Response data keys: {list(data.keys())}")
        
        if 'files' in data:
            files = data['files']
            print(f"📁 Files found: {list(files.keys())}")
            for category, file_list in files.items():
                print(f"  - {category}: {len(file_list)} files")
        
        return data
        
    except Exception as e:
        print(f"❌ Error testing file listing: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_existing_files():
    """Check what files already exist"""
    
    print("\n🔍 Checking existing files...")
    
    media_root = settings.MEDIA_ROOT
    inspection_path = os.path.join(media_root, 'inspection')
    
    if not os.path.exists(inspection_path):
        print(f"❌ Inspection path doesn't exist: {inspection_path}")
        return
    
    print(f"📁 Inspection base path: {inspection_path}")
    
    # Check 2025/September structure
    september_path = os.path.join(inspection_path, '2025', 'September')
    if os.path.exists(september_path):
        print(f"📁 September path exists: {september_path}")
        
        # List all client folders
        try:
            clients = [d for d in os.listdir(september_path) if os.path.isdir(os.path.join(september_path, d))]
            print(f"👥 Client folders found: {clients}")
            
            # Check Canonbury variations
            canonbury_variations = [
                'CanonburyEggs',
                'Canonbury_Eggs',
                'canonburyeggs',
                'Canonbury Eggs'
            ]
            
            for variation in canonbury_variations:
                path = os.path.join(september_path, variation)
                if os.path.exists(path):
                    print(f"✅ Found Canonbury folder: {path}")
                    
                    # List contents
                    contents = os.listdir(path)
                    print(f"   Contents: {contents}")
                    
                    # Check for document folders
                    for doc_type in ['rfi', 'invoice', 'lab', 'lab_form', 'retest']:
                        doc_path = os.path.join(path, doc_type)
                        if os.path.exists(doc_path):
                            files = [f for f in os.listdir(doc_path) if os.path.isfile(os.path.join(doc_path, f))]
                            print(f"   📄 {doc_type}: {len(files)} files - {files}")
                else:
                    print(f"❌ Not found: {path}")
        
        except Exception as e:
            print(f"❌ Error listing client folders: {e}")
    else:
        print(f"❌ September path doesn't exist: {september_path}")

def main():
    """Main test function"""
    
    print("🚀 Starting file system test and setup...")
    print("=" * 60)
    
    # Check existing files first
    check_existing_files()
    
    # Create test files
    print("\n" + "=" * 60)
    base_path = create_test_files()
    
    # Test the file listing function
    print("\n" + "=" * 60)
    result = test_file_listing()
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print(f"✅ Test files created in: {base_path}")
    
    if result:
        if result.get('success'):
            print("✅ File listing function works correctly")
            files = result.get('files', {})
            total_files = sum(len(file_list) for file_list in files.values())
            print(f"📊 Total files found: {total_files}")
        else:
            print(f"❌ File listing returned error: {result.get('error', 'Unknown error')}")
    else:
        print("❌ File listing function failed")
    
    print("\n🧪 Now test in browser:")
    print("1. Refresh the page")
    print("2. Click 'View Files' on Canonbury Eggs")
    print("3. Should see real files instead of test data")
    print("4. Button should be BLUE (partial files)")

if __name__ == '__main__':
    main()