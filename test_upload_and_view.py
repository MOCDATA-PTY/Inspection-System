#!/usr/bin/env python3
"""
Complete test that uploads a file and then tries to view it
This simulates the exact user workflow that's failing
"""
import os
import sys
import django
import tempfile
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from main.models import FoodSafetyAgencyInspection

def create_test_file():
    """Create a temporary PDF file for testing"""
    content = b"This is a test PDF file for upload testing"
    return SimpleUploadedFile("test_rfi.pdf", content, content_type="application/pdf")

def test_upload_and_view_workflow():
    """Test the complete upload and view workflow"""
    print("=== UPLOAD AND VIEW WORKFLOW TEST ===")
    print()
    
    # Test data
    client_name = "Great Octave Trading 513 CC T/A Sun African"
    inspection_date = "2025-09-23"
    
    print(f"Testing client: {client_name}")
    print(f"Testing date: {inspection_date}")
    print()
    
    # Create Django test client
    client = Client()
    
    # Create test user
    try:
        user = User.objects.get(username='developer')
        print(f"Using existing user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(username='developer', password='test123')
        print(f"Created test user: {user.username}")
    
    # Login
    login_success = client.login(username='developer', password='XHnj1C#QkFs9')
    if not login_success:
        print("❌ LOGIN FAILED - trying with test password")
        login_success = client.login(username='developer', password='test123')
    
    if not login_success:
        print("❌ LOGIN FAILED - cannot proceed with test")
        return False
    
    print("OK LOGIN SUCCESSFUL")
    print()
    
    # Get inspection record
    try:
        inspection = FoodSafetyAgencyInspection.objects.filter(
            client_name=client_name,
            date_of_inspection=inspection_date
        ).first()
        
        if inspection:
            print(f"Using existing inspection: {inspection.id}")
        else:
            inspection = FoodSafetyAgencyInspection.objects.create(
                client_name=client_name,
                date_of_inspection=inspection_date,
                inspector_name="Test Inspector"
            )
            print(f"Created test inspection: {inspection.id}")
    except Exception as e:
        print(f"Error with inspection: {e}")
        return False
    
    print()
    
    # Step 1: Upload RFI file
    print("STEP 1: UPLOADING RFI FILE")
    print("-" * 30)
    
    test_file = create_test_file()
    
    # Create group_id in the format the frontend uses
    # Format: clientname_YYYYMMDD
    date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
    date_str = date_obj.strftime('%Y%m%d')
    
    # Sanitize client name for group_id (same as frontend)
    import re
    sanitized_client = re.sub(r'[^a-zA-Z0-9_]', '_', client_name)
    sanitized_client = re.sub(r'_+', '_', sanitized_client).strip('_')
    group_id = f"{sanitized_client}_{date_str}"
    
    print(f"Generated group_id: {group_id}")
    
    upload_data = {
        'group_id': group_id,
        'document_type': 'rfi',
        'file': test_file
    }
    
    upload_response = client.post('/upload-document/', upload_data)
    
    print(f"Upload response status: {upload_response.status_code}")
    
    if upload_response.status_code == 200:
        try:
            upload_result = json.loads(upload_response.content)
            print(f"Upload result: {upload_result}")
            
            if upload_result.get('success'):
                print("OK UPLOAD SUCCESSFUL")
                uploaded_file_path = upload_result.get('file_path', '')
                print(f"File saved to: {uploaded_file_path}")
            else:
                print(f"❌ UPLOAD FAILED: {upload_result.get('message', 'Unknown error')}")
                return False
        except json.JSONDecodeError:
            print(f"❌ UPLOAD FAILED: Invalid JSON response")
            print(f"Response content: {upload_response.content}")
            return False
    else:
        print(f"❌ UPLOAD FAILED: HTTP {upload_response.status_code}")
        print(f"Response content: {upload_response.content}")
        return False
    
    print()
    
    # Step 2: Try to view the uploaded file
    print("STEP 2: VIEWING UPLOADED FILE")
    print("-" * 30)
    
    view_data = {
        'client_name': client_name,
        'inspection_date': inspection_date,
        'inspection_id': inspection.id,
        '_force_refresh': True
    }
    
    view_response = client.post('/list-client-folder-files/', 
                               json.dumps(view_data),
                               content_type='application/json')
    
    print(f"View response status: {view_response.status_code}")
    
    if view_response.status_code == 200:
        try:
            view_result = json.loads(view_response.content)
            print(f"View result keys: {list(view_result.keys())}")
            
            if view_result.get('success'):
                files = view_result.get('files', {})
                print(f"Files found: {files}")
                
                rfi_files = files.get('rfi', [])
                print(f"RFI files count: {len(rfi_files)}")
                
                if rfi_files:
                    print("OK FILE DETECTION SUCCESSFUL")
                    for i, file_info in enumerate(rfi_files):
                        print(f"  File {i+1}: {file_info.get('name', 'Unknown')}")
                        print(f"    Size: {file_info.get('size', 'Unknown')} bytes")
                        print(f"    Path: {file_info.get('path', 'Unknown')}")
                    return True
                else:
                    print("X FILE DETECTION FAILED: No RFI files found")
                    print("This is the exact problem the user is experiencing!")
                    return False
            else:
                print(f"❌ FILE DETECTION FAILED: {view_result.get('error', 'Unknown error')}")
                return False
        except json.JSONDecodeError:
            print(f"❌ FILE DETECTION FAILED: Invalid JSON response")
            print(f"Response content: {view_response.content}")
            return False
    else:
        print(f"❌ FILE DETECTION FAILED: HTTP {view_response.status_code}")
        print(f"Response content: {view_response.content}")
        return False

def test_folder_structure():
    """Test the actual folder structure that gets created"""
    print("\n=== FOLDER STRUCTURE TEST ===")
    print()
    
    client_name = "Great Octave Trading 513 CC T/A Sun African"
    
    # Test folder name creation (upload logic)
    def create_folder_name(name):
        if not name:
            return "Unknown Client"
        return name.replace('/', ' ').strip()
    
    # Test folder name detection (view logic)
    import re
    def sanitize_client_name(client_name):
        sanitized_client_name = re.sub(r'[^a-zA-Z0-9_]', '_', client_name)
        sanitized_client_name = re.sub(r'_+', '_', sanitized_client_name).strip('_')
        return sanitized_client_name
    
    upload_folder = create_folder_name(client_name)
    detection_sanitized = sanitize_client_name(client_name)
    detection_spaces = client_name.replace('/', ' ')
    
    print(f"Original name: '{client_name}'")
    print(f"Upload creates: '{upload_folder}'")
    print(f"Detection method 1 (sanitized): '{detection_sanitized}'")
    print(f"Detection method 2 (spaces): '{detection_spaces}'")
    print()
    
    if upload_folder == detection_spaces:
        print("OK FOLDER NAMES MATCH (spaces method)")
        return True
    elif upload_folder == detection_sanitized:
        print("OK FOLDER NAMES MATCH (sanitized method)")
        return True
    else:
        print("X FOLDER NAMES DON'T MATCH")
        print("This explains why files aren't found!")
        return False

if __name__ == "__main__":
    print("Starting comprehensive upload and view test...")
    print("=" * 50)
    
    # Test folder structure logic first
    folder_test_passed = test_folder_structure()
    
    # Test actual upload and view workflow
    workflow_test_passed = test_upload_and_view_workflow()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"Folder structure test: {'OK PASSED' if folder_test_passed else 'X FAILED'}")
    print(f"Upload/view workflow test: {'OK PASSED' if workflow_test_passed else 'X FAILED'}")
    
    if folder_test_passed and workflow_test_passed:
        print("\nALL TESTS PASSED - Upload and view should work!")
    else:
        print("\nTESTS FAILED - This explains why the upload/view is broken!")
        
        if not folder_test_passed:
            print("   → Folder naming mismatch between upload and detection")
        if not workflow_test_passed:
            print("   → Actual upload/view workflow is broken")
