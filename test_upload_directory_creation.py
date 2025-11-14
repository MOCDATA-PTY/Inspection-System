#!/usr/bin/env python3
"""
Test script to verify that uploads go to the correct directory with original client names
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

def test_upload_directory_creation():
    """Test that uploads create directories with original client names"""
    print("🧪 Testing Upload Directory Creation with Original Client Names")
    print("=" * 70)
    
    from django.test import Client
    from django.contrib.auth import get_user_model
    from main.models import FoodSafetyAgencyInspection
    from django.core.files.uploadedfile import SimpleUploadedFile
    import json
    
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
    
    # Get a sample inspection for testing
    sample_inspection = FoodSafetyAgencyInspection.objects.filter(
        client_name__isnull=False,
        date_of_inspection__isnull=False
    ).first()
    
    if not sample_inspection:
        print("❌ No sample inspection found for testing")
        return False
    
    client_name = sample_inspection.client_name
    inspection_date = sample_inspection.date_of_inspection
    inspection_id = sample_inspection.id
    
    print(f"📋 Testing with client: {client_name}")
    print(f"📅 Testing with date: {inspection_date}")
    print(f"🆔 Testing with inspection ID: {inspection_id}")
    
    # Test different document types
    document_types = ['rfi', 'invoice', 'lab', 'retest']
    
    for doc_type in document_types:
        print(f"\n📄 Testing {doc_type.upper()} upload...")
        
        # Create a test file
        test_content = f"Test {doc_type} content for {client_name}"
        test_file = SimpleUploadedFile(
            f"test_{doc_type}.pdf",
            test_content.encode(),
            content_type="application/pdf"
        )
        
        # Test upload
        try:
            response = client.post('/upload_document/', {
                'file': test_file,
                'document_type': doc_type,
                'inspection_id': inspection_id,
                'group_id': f"{client_name}_{inspection_date.strftime('%Y-%m-%d')}"
            })
            
            print(f"   📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if response_data.get('success'):
                        print(f"   ✅ {doc_type.upper()} upload successful")
                        
                        # Check if the file was created in the correct directory
                        expected_path = os.path.join(
                            'media', 'inspection',
                            inspection_date.strftime('%Y'),
                            inspection_date.strftime('%B'),
                            client_name,  # Should use original client name
                            doc_type
                        )
                        
                        full_path = os.path.join(Path(__file__).parent, expected_path)
                        print(f"   📁 Expected path: {expected_path}")
                        print(f"   📁 Full path: {full_path}")
                        
                        if os.path.exists(full_path):
                            print(f"   ✅ Directory exists: {expected_path}")
                            
                            # List files in the directory
                            files = os.listdir(full_path)
                            print(f"   📄 Files in directory: {files}")
                            
                            # Check if our test file is there
                            test_filename = f"test_{doc_type}.pdf"
                            if test_filename in files:
                                print(f"   ✅ Test file found: {test_filename}")
                            else:
                                print(f"   ❌ Test file not found: {test_filename}")
                                return False
                        else:
                            print(f"   ❌ Directory does not exist: {expected_path}")
                            return False
                    else:
                        print(f"   ❌ Upload failed: {response_data.get('error', 'Unknown error')}")
                        return False
                except Exception as e:
                    print(f"   ❌ Error parsing response: {e}")
                    return False
            else:
                print(f"   ❌ Upload failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   ❌ Error details: {error_data}")
                except:
                    print(f"   ❌ Error response: {response.content.decode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception during upload: {e}")
            return False
    
    print(f"\n🎉 All upload tests passed!")
    print(f"✅ Uploads now go to directories with original client names: '{client_name}'")
    return True

def check_existing_folders():
    """Check what folders currently exist to see the naming pattern"""
    print("\n📁 Checking existing folder structure...")
    
    from django.conf import settings
    
    inspection_base = os.path.join(settings.MEDIA_ROOT, 'inspection')
    
    if not os.path.exists(inspection_base):
        print("❌ No inspection folder found")
        return
    
    # Check current year/month
    current_year = datetime.now().year
    current_month = datetime.now().month
    month_name = datetime.now().strftime('%B')
    
    year_path = os.path.join(inspection_base, str(current_year))
    month_path = os.path.join(year_path, month_name)
    
    if os.path.exists(month_path):
        print(f"📁 Checking folders in {current_year}/{month_name}:")
        folders = os.listdir(month_path)
        for folder in folders[:10]:  # Show first 10 folders
            folder_path = os.path.join(month_path, folder)
            if os.path.isdir(folder_path):
                print(f"   📁 {folder}")
    else:
        print(f"❌ Month folder not found: {month_path}")

if __name__ == "__main__":
    try:
        # Check existing folders first
        check_existing_folders()
        
        # Test upload directory creation
        success = test_upload_directory_creation()
        
        if success:
            print("\n🎉 Upload directory test PASSED!")
            print("✅ Uploads now create directories with original client names")
        else:
            print("\n❌ Upload directory test FAILED!")
            print("⚠️  Check the error messages above")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
