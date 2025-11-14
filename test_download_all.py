#!/usr/bin/env python3
"""
Simple test script to verify the Download All button functionality
Tests both frontend JavaScript issues and backend endpoint
"""

import os
import sys
import django
import json

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from main.models import FoodSafetyAgencyInspection, Client as ClientModel

def test_javascript_syntax_errors():
    """Test for JavaScript syntax errors in the HTML template"""
    print("\n[TEST] Checking JavaScript syntax errors...")
    
    template_path = 'main/templates/main/shipment_list_clean.html'
    
    if not os.path.exists(template_path):
        print(f"[ERROR] Template file not found: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the specific syntax errors that were fixed
    errors = []
    
    # Check for semicolon in variable names (should be fixed now)
    if 'window.currentFilesClien;t;' in content:
        errors.append("Syntax error in 'window.currentFilesClient' - extra semicolon")
    
    if 'window.currentFilesDat;e;' in content:
        errors.append("Syntax error in 'window.currentFilesDate' - extra semicolon")
    
    if 'window.currentFilesGroupI;d;' in content:
        errors.append("Syntax error in 'window.currentFilesGroupId' - extra semicolon")
    
    if 'downloadBtn.innerHTM;L;' in content:
        errors.append("Syntax error in 'downloadBtn.innerHTML' - extra semicolon")
    
    # Check for missing quote in filename (should be fixed now)
    if "clientName + '_' + inspectionDate + '_all_files.zip;" in content:
        errors.append("Missing closing quote in filename string")
    
    if errors:
        print("[ERROR] JavaScript syntax errors found:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("[OK] No JavaScript syntax errors found")
        return True

def test_backend_endpoint():
    """Test if the backend endpoint exists and is accessible"""
    print("\n[TEST] Testing backend endpoint...")
    
    try:
        client = Client()
        
        # Try to get a user for authentication
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
            
            if user:
                client.force_login(user)
                print(f"[OK] Logged in as: {user.username}")
            else:
                print("[WARNING] No users found - creating test without authentication")
        except Exception as e:
            print(f"[WARNING] Authentication setup failed: {e}")
        
        # Test with POST request (as required by the endpoint)
        response = client.post(
            '/inspections/download-all-files/',
            data=json.dumps({
                'client_name': 'Test Client',
                'inspection_date': '2024-01-01',
                'group_id': 'test_group'
            }),
            content_type='application/json'
        )
        
        print(f"[INFO] Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("[OK] Backend endpoint is accessible and working")
            return True
        elif response.status_code == 404:
            print("[ERROR] Backend endpoint not found (404)")
            return False
        elif response.status_code == 403:
            print("[ERROR] Access forbidden (403) - check authentication")
            return False
        elif response.status_code == 405:
            print("[ERROR] Method not allowed (405)")
            return False
        else:
            print(f"[WARNING] Unexpected response: {response.status_code}")
            if hasattr(response, 'content'):
                content = response.content.decode()[:200]
                print(f"[INFO] Response content: {content}...")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error testing backend endpoint: {e}")
        return False

def test_url_mapping():
    """Test if URL mapping is correct"""
    print("\n[TEST] Testing URL mapping...")
    
    try:
        from django.urls import reverse
        url = reverse('download_all_inspection_files')
        print(f"[OK] URL mapping found: {url}")
        return True
    except Exception as e:
        print(f"[ERROR] URL mapping error: {e}")
        return False

def test_sample_data():
    """Check if there's sample data to test with"""
    print("\n[TEST] Checking for sample data...")
    
    try:
        # Check for inspections
        inspection_count = FoodSafetyAgencyInspection.objects.count()
        print(f"[INFO] Found {inspection_count} inspections in database")
        
        # Check for clients
        client_count = ClientModel.objects.count()
        print(f"[INFO] Found {client_count} clients in database")
        
        if inspection_count > 0 and client_count > 0:
            print("[OK] Sample data available for testing")
            
            # Show a sample inspection
            sample_inspection = FoodSafetyAgencyInspection.objects.first()
            print(f"[INFO] Sample inspection: {sample_inspection.client_name} on {sample_inspection.date_of_inspection}")
            return True
        else:
            print("[WARNING] No sample data found - create some test data for full testing")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error checking sample data: {e}")
        return False

def test_file_system_access():
    """Test if the system can access files for download"""
    print("\n[TEST] Testing file system access...")
    
    try:
        from django.conf import settings
        
        # Check media directory
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and os.path.exists(media_root):
            print(f"[OK] Media directory accessible: {media_root}")
            
            # Check for uploaded files
            uploaded_files = []
            for root, dirs, files in os.walk(media_root):
                uploaded_files.extend(files)
                if len(uploaded_files) >= 5:  # Just check first few
                    break
            
            print(f"[INFO] Found {len(uploaded_files)} files in media directory")
            if uploaded_files:
                print(f"[INFO] Sample files: {uploaded_files[:3]}")
                return True
            else:
                print("[WARNING] No files found in media directory")
                return False
        else:
            print(f"[ERROR] Media directory not accessible: {media_root}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error testing file system: {e}")
        return False

def generate_fix_recommendations():
    """Generate recommendations to fix the issues"""
    print("\n[RECOMMENDATIONS] Fix Recommendations:")
    print("=" * 50)
    
    print("1. JavaScript Syntax Errors:")
    print("   - Fix semicolons in variable names (should be fixed now)")
    print("   - Add missing quote in filename string (should be fixed now)")
    print("   - These prevent the download function from executing")
    
    print("\n2. Backend Endpoint:")
    print("   - Endpoint exists at '/inspections/download-all-files/'")
    print("   - Requires POST method with JSON data")
    print("   - Needs client_name, inspection_date, and group_id parameters")
    
    print("\n3. Authentication:")
    print("   - Requires user login (@login_required decorator)")
    print("   - Make sure user has proper permissions")
    
    print("\n4. File System:")
    print("   - Ensure MEDIA_ROOT is properly configured")
    print("   - Check file permissions for reading uploaded documents")
    
    print("\n5. Frontend Integration:")
    print("   - Verify CSRF token is properly included")
    print("   - Check that modal variables are set correctly")
    print("   - Ensure button visibility logic works")

def main():
    """Main function to run the test"""
    print("Download All Button Test Script")
    print("Testing the functionality at http://127.0.0.1:8000/inspections/?page=2")
    print("=" * 60)
    
    # Run all tests
    results = {
        'javascript_syntax': test_javascript_syntax_errors(),
        'backend_endpoint': test_backend_endpoint(),
        'url_mapping': test_url_mapping(),
        'sample_data': test_sample_data(),
        'file_system': test_file_system_access()
    }
    
    print("\n[SUMMARY] Test Results:")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed < total:
        generate_fix_recommendations()
    else:
        print("\n[SUCCESS] All tests passed! The Download All button should work properly.")
    
    # Return exit code based on results
    if all(results.values()):
        return 0  # Success
    else:
        return 1  # Some tests failed

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
