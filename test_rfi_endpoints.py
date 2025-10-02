#!/usr/bin/env python3
"""
Test RFI endpoints using the correct upload-document endpoint
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

def test_rfi_endpoints():
    """Test RFI functionality using correct endpoints"""
    print("=" * 60)
    print("RFI ENDPOINT TEST")
    print("=" * 60)
    
    client = Client()
    username = 'developer'
    password = 'XHnj1C#QkFs9'
    
    print(f"Logging in as: {username}")
    login_success = client.login(username=username, password=password)
    
    if not login_success:
        print("ERROR: Login failed")
        return False
    
    print("SUCCESS: Login successful")
    
    # Test 1: Test upload-document endpoint for RFI
    print("\n1. Testing upload-document endpoint for RFI:")
    
    test_file = SimpleUploadedFile(
        "test_rfi.pdf",
        b"Test RFI content for testing",
        content_type="application/pdf"
    )
    
    upload_data = {
        'group_id': 'test_client_20250101',
        'document_type': 'rfi',
        'file': test_file,
        'csrfmiddlewaretoken': client.cookies.get('csrftoken', '')
    }
    
    try:
        response = client.post('/upload-document/', upload_data, format='multipart')
        print(f"   Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Upload response: {data}")
                print("   [OK] Upload endpoint accessible")
            except:
                print(f"   Response content: {response.content.decode()[:200]}...")
                print("   [WARN] Non-JSON response")
        else:
            print(f"   [WARN] Upload returned status {response.status_code}")
            print(f"   Response content: {response.content.decode()[:200]}...")
    except Exception as e:
        print(f"   [ERROR] Upload test failed: {str(e)}")
    
    # Test 2: Test list-uploaded-files endpoint
    print("\n2. Testing list-uploaded-files endpoint:")
    
    try:
        files_response = client.get('/list-uploaded-files/?group_id=test_client_20250101')
        print(f"   Files response status: {files_response.status_code}")
        
        if files_response.status_code == 200:
            try:
                files_data = files_response.json()
                print(f"   Files response: {files_data}")
                print("   [OK] File listing endpoint accessible")
            except:
                print(f"   Response content: {files_response.content.decode()[:200]}...")
                print("   [WARN] Non-JSON response")
        else:
            print(f"   [WARN] File listing returned status {files_response.status_code}")
            print(f"   Response content: {files_response.content.decode()[:200]}...")
    except Exception as e:
        print(f"   [ERROR] File listing test failed: {str(e)}")
    
    # Test 3: Test with different document types
    print("\n3. Testing different document types:")
    
    document_types = ['rfi', 'invoice', 'lab', 'retest']
    
    for doc_type in document_types:
        test_file = SimpleUploadedFile(
            f"test_{doc_type}.pdf",
            f"Test {doc_type.upper()} content".encode(),
            content_type="application/pdf"
        )
        
        upload_data = {
            'group_id': f'test_client_{doc_type}_20250101',
            'document_type': doc_type,
            'file': test_file,
            'csrfmiddlewaretoken': client.cookies.get('csrftoken', '')
        }
        
        try:
            response = client.post('/upload-document/', upload_data, format='multipart')
            print(f"   {doc_type.upper()}: Status {response.status_code}")
        except Exception as e:
            print(f"   {doc_type.upper()}: Error - {str(e)}")
    
    print("\n" + "=" * 60)
    print("RFI ENDPOINT TEST COMPLETED")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_rfi_endpoints()
