#!/usr/bin/env python3
"""
Test script to verify upload functionality works correctly.
This script tests the upload_document view to ensure the date_str error is fixed.
"""

import os
import sys
import django
from datetime import datetime
import tempfile
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from main.models import FoodSafetyAgencyInspection
from django.core.files.uploadedfile import SimpleUploadedFile

def create_test_inspection():
    """Create a test inspection for testing uploads."""
    try:
        # Check if test inspection already exists
        inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=99999).first()
        if inspection:
            print("✅ Test inspection already exists")
            return inspection
        
        # Create a new test inspection
        inspection = FoodSafetyAgencyInspection.objects.create(
            remote_id=99999,
            client_name="Test Client for Upload",
            commodity="EGGS",
            date_of_inspection=datetime.now().date(),
            inspector_name="Test Inspector",
            is_sent=False
        )
        print("✅ Created test inspection with ID:", inspection.remote_id)
        return inspection
    except Exception as e:
        print(f"❌ Error creating test inspection: {e}")
        return None

def create_test_pdf():
    """Create a test PDF file for upload testing."""
    try:
        # Create a simple PDF content (minimal valid PDF)
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test PDF Document) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
300
%%EOF"""
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(pdf_content)
        temp_file.close()
        
        print("✅ Created test PDF file:", temp_file.name)
        return temp_file.name
    except Exception as e:
        print(f"❌ Error creating test PDF: {e}")
        return None

def test_lab_upload():
    """Test lab upload functionality."""
    print("\n🧪 Testing Lab Upload Functionality...")
    
    # Create test inspection
    inspection = create_test_inspection()
    if not inspection:
        return False
    
    # Create test PDF
    pdf_path = create_test_pdf()
    if not pdf_path:
        return False
    
    try:
        # Create Django test client
        client = Client()
        
        # Create a test user (or use existing) with scientist role
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com', 'is_staff': True, 'role': 'scientist'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print("✅ Created test user")
        else:
            # Update existing user to scientist role
            user.role = 'scientist'
            user.set_password('testpass123')
            user.save()
            print("✅ Updated existing test user to scientist role")
        
        # Login the user
        login_success = client.login(username='testuser', password='testpass123')
        if not login_success:
            print("❌ Failed to login test user")
            return False
        
        # Prepare the upload data
        with open(pdf_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile(
                "test_lab_result.pdf",
                f.read(),
                content_type="application/pdf"
            )
        
        # Test lab upload with inspection_id only (no group_id)
        print("📤 Testing lab upload with inspection_id only...")
        response = client.post('/upload-document/', {
            'file': uploaded_file,
            'inspection_id': str(inspection.remote_id),
            'document_type': 'lab',
            'csrfmiddlewaretoken': 'test-token'  # In real test, this would be proper CSRF
        })
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = json.loads(response.content)
                print(f"📋 Response data: {response_data}")
                
                if response_data.get('success'):
                    print("✅ Lab upload test PASSED - No date_str error!")
                    return True
                else:
                    print(f"❌ Lab upload test FAILED - Error: {response_data.get('error', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ Lab upload test FAILED - Invalid JSON response: {response.content}")
                return False
        else:
            print(f"❌ Lab upload test FAILED - HTTP {response.status_code}: {response.content}")
            return False
            
    except Exception as e:
        print(f"❌ Lab upload test FAILED - Exception: {e}")
        return False
    finally:
        # Clean up test files
        try:
            if pdf_path and os.path.exists(pdf_path):
                os.unlink(pdf_path)
                print("🧹 Cleaned up test PDF file")
        except:
            pass

def test_lab_form_upload():
    """Test lab form upload functionality."""
    print("\n🧪 Testing Lab Form Upload Functionality...")
    
    # Create test inspection
    inspection = create_test_inspection()
    if not inspection:
        return False
    
    # Create test PDF
    pdf_path = create_test_pdf()
    if not pdf_path:
        return False
    
    try:
        # Create Django test client
        client = Client()
        
        # Login the user
        login_success = client.login(username='testuser', password='testpass123')
        if not login_success:
            print("❌ Failed to login test user")
            return False
        
        # Prepare the upload data
        with open(pdf_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile(
                "test_lab_form.pdf",
                f.read(),
                content_type="application/pdf"
            )
        
        # Test lab form upload with inspection_id only (no group_id)
        print("📤 Testing lab form upload with inspection_id only...")
        response = client.post('/upload-document/', {
            'file': uploaded_file,
            'inspection_id': str(inspection.remote_id),
            'document_type': 'lab_form',
            'csrfmiddlewaretoken': 'test-token'
        })
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = json.loads(response.content)
                print(f"📋 Response data: {response_data}")
                
                if response_data.get('success'):
                    print("✅ Lab form upload test PASSED - No date_str error!")
                    return True
                else:
                    print(f"❌ Lab form upload test FAILED - Error: {response_data.get('error', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ Lab form upload test FAILED - Invalid JSON response: {response.content}")
                return False
        else:
            print(f"❌ Lab form upload test FAILED - HTTP {response.status_code}: {response.content}")
            return False
            
    except Exception as e:
        print(f"❌ Lab form upload test FAILED - Exception: {e}")
        return False
    finally:
        # Clean up test files
        try:
            if pdf_path and os.path.exists(pdf_path):
                os.unlink(pdf_path)
                print("🧹 Cleaned up test PDF file")
        except:
            pass

def test_retest_upload():
    """Test retest upload functionality."""
    print("\n🧪 Testing Retest Upload Functionality...")
    
    # Create test inspection
    inspection = create_test_inspection()
    if not inspection:
        return False
    
    # Create test PDF
    pdf_path = create_test_pdf()
    if not pdf_path:
        return False
    
    try:
        # Create Django test client
        client = Client()
        
        # Login the user
        login_success = client.login(username='testuser', password='testpass123')
        if not login_success:
            print("❌ Failed to login test user")
            return False
        
        # Prepare the upload data
        with open(pdf_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile(
                "test_retest.pdf",
                f.read(),
                content_type="application/pdf"
            )
        
        # Test retest upload with inspection_id only (no group_id)
        print("📤 Testing retest upload with inspection_id only...")
        response = client.post('/upload-document/', {
            'file': uploaded_file,
            'inspection_id': str(inspection.remote_id),
            'document_type': 'retest',
            'csrfmiddlewaretoken': 'test-token'
        })
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = json.loads(response.content)
                print(f"📋 Response data: {response_data}")
                
                if response_data.get('success'):
                    print("✅ Retest upload test PASSED - No date_str error!")
                    return True
                else:
                    print(f"❌ Retest upload test FAILED - Error: {response_data.get('error', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ Retest upload test FAILED - Invalid JSON response: {response.content}")
                return False
        else:
            print(f"❌ Retest upload test FAILED - HTTP {response.status_code}: {response.content}")
            return False
            
    except Exception as e:
        print(f"❌ Retest upload test FAILED - Exception: {e}")
        return False
    finally:
        # Clean up test files
        try:
            if pdf_path and os.path.exists(pdf_path):
                os.unlink(pdf_path)
                print("🧹 Cleaned up test PDF file")
        except:
            pass

def cleanup_test_data():
    """Clean up test data."""
    try:
        # Remove test inspection
        FoodSafetyAgencyInspection.objects.filter(remote_id=99999).delete()
        print("🧹 Cleaned up test inspection")
        
        # Remove test user
        User.objects.filter(username='testuser').delete()
        print("🧹 Cleaned up test user")
        
    except Exception as e:
        print(f"⚠️ Error during cleanup: {e}")

def main():
    """Run all upload tests."""
    print("🚀 Starting Upload Functionality Tests...")
    print("=" * 50)
    
    # Track test results
    test_results = []
    
    # Run tests
    test_results.append(("Lab Upload", test_lab_upload()))
    test_results.append(("Lab Form Upload", test_lab_form_upload()))
    test_results.append(("Retest Upload", test_retest_upload()))
    
    # Print results summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Upload functionality is working correctly.")
        print("✅ The date_str error has been successfully fixed!")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    cleanup_test_data()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
