#!/usr/bin/env python3
"""
Test script to verify exact folder matching works with original client names
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

def test_exact_folder_matching():
    """Test that exact folder matching works with original client names"""
    print("🧪 Testing Exact Folder Matching with Original Client Names")
    print("=" * 70)
    
    from django.test import Client
    from django.contrib.auth import get_user_model
    from main.models import FoodSafetyAgencyInspection
    
    User = get_user_model()
    
    # Create test client
    client = Client()
    
    # Use an existing inspector user
    try:
        user = User.objects.filter(role='inspector').first()
        if not user:
            print("❌ No inspector users found")
            return False
            
        # Set a known password for testing
        user.set_password('testpass123')
        user.save()
        
    except Exception as e:
        print(f"❌ Error setting up test user: {e}")
        return False
    
    # Login the user
    login_success = client.login(username=user.username, password='testpass123')
    if not login_success:
        print("❌ Failed to login test user")
        return False
    
    print("✅ Test user logged in successfully")
    
    # Test with a client that has spaces and special characters
    test_client = "Pick 'n Pay - Midway Mems"
    test_date = "2025-09-11"
    
    print(f"📋 Testing with client: {test_client}")
    print(f"📅 Testing with date: {test_date}")
    
    # Test the download all files endpoint
    test_data = {
        'client_name': test_client,
        'inspection_date': test_date,
        'group_id': 'test_group'
    }
    
    try:
        print("\n🔄 Testing download-all-files endpoint...")
        response = client.post(
            '/inspections/download-all-files/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if it's a ZIP file
            content_type = response.get('Content-Type', '')
            if 'application/zip' in content_type:
                print("✅ Download all endpoint returned ZIP file successfully")
                
                # Check content length
                content_length = len(response.content)
                print(f"📦 Content length: {content_length} bytes")
                
                if content_length > 1000:  # Should be more than just a small test file
                    print("✅ ZIP file contains substantial data")
                    return True
                else:
                    print("⚠️  ZIP file is very small - may not have found files")
                    return False
            else:
                print(f"❌ Expected ZIP file, got: {content_type}")
                return False
        else:
            print(f"❌ Download failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Error details: {error_data}")
            except:
                print(f"❌ Error response: {response.content.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during download test: {e}")
        return False

def create_test_folder_with_spaces():
    """Create a test folder with spaces in the name to test exact matching"""
    print("\n📁 Creating test folder with spaces...")
    
    from django.conf import settings
    
    # Create a test folder with spaces
    test_client_name = "Pick 'n Pay - Midway Mems"
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    year_folder = os.path.join(settings.MEDIA_ROOT, 'inspection', str(current_year))
    month_folder = os.path.join(year_folder, f"{current_month:02d}")
    client_folder = os.path.join(month_folder, test_client_name)
    
    # Create directories
    os.makedirs(client_folder, exist_ok=True)
    print(f"✅ Created folder: {client_folder}")
    
    # Create subfolders
    subfolders = ['rfi', 'invoice', 'lab results', 'retest', 'Compliance']
    for subfolder in subfolders:
        subfolder_path = os.path.join(client_folder, subfolder)
        os.makedirs(subfolder_path, exist_ok=True)
        print(f"✅ Created subfolder: {subfolder}")
    
    # Create test files
    test_files = [
        ('rfi', 'test_rfi_document.pdf'),
        ('invoice', 'test_invoice.xlsx'),
        ('lab results', 'test_lab_results.pdf'),
        ('retest', 'test_retest_document.pdf'),
        ('Compliance', 'test_compliance_document.pdf')
    ]
    
    for folder, filename in test_files:
        file_path = os.path.join(client_folder, folder, filename)
        with open(file_path, 'w') as f:
            f.write(f"Test content for {filename}\nCreated on {datetime.now()}")
        print(f"✅ Created test file: {filename}")
    
    return test_client_name

if __name__ == "__main__":
    try:
        import json
        
        # Create test folder with spaces
        test_client = create_test_folder_with_spaces()
        
        # Test exact matching
        success = test_exact_folder_matching()
        
        if success:
            print("\n🎉 Exact folder matching test PASSED!")
            print("✅ Folders with spaces and special characters now work correctly")
        else:
            print("\n❌ Exact folder matching test FAILED!")
            print("⚠️  Check the error messages above")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
