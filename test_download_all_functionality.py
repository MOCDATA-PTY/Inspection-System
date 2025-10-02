#!/usr/bin/env python3
"""
Test script to verify download all functionality works properly
Tests both the frontend JavaScript and backend API endpoints
"""

import os
import sys
import django
import requests
import json
from pathlib import Path
from datetime import datetime, date

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def test_download_all_backend():
    """Test the backend download all functionality"""
    print("🧪 Testing Download All Backend Functionality")
    print("=" * 60)
    
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
            # Create a test user if no inspectors exist
            user = User.objects.create_user(
                username='testuser',
                password='testpass123',
                role='inspector'
            )
            print(f"✅ Created new test user: {user.username}")
        else:
            print(f"✅ Using existing inspector: {user.username}")
            
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
        print("🔍 Trying to debug login issue...")
        
        # Check if user exists and is active
        try:
            user_check = User.objects.get(username='testuser')
            print(f"   User exists: {user_check.username}")
            print(f"   User active: {user_check.is_active}")
            print(f"   User role: {getattr(user_check, 'role', 'No role')}")
        except User.DoesNotExist:
            print("   User does not exist")
        
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
    inspection_date = sample_inspection.date_of_inspection.strftime('%Y-%m-%d')
    
    print(f"📋 Testing with client: {client_name}")
    print(f"📅 Testing with date: {inspection_date}")
    
    # Test the download all files endpoint
    test_data = {
        'client_name': client_name,
        'inspection_date': inspection_date,
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
        print(f"📊 Response content type: {response.get('Content-Type', 'Not set')}")
        
        if response.status_code == 200:
            # Check if it's a ZIP file
            content_type = response.get('Content-Type', '')
            if 'application/zip' in content_type:
                print("✅ Download all endpoint returned ZIP file successfully")
                
                # Check content disposition header
                content_disposition = response.get('Content-Disposition', '')
                print(f"📄 Content-Disposition: {content_disposition}")
                
                # Check if we got actual content
                content_length = len(response.content)
                print(f"📦 Content length: {content_length} bytes")
                
                if content_length > 0:
                    print("✅ ZIP file contains data")
                    return True
                else:
                    print("⚠️  ZIP file is empty")
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

def test_file_structure():
    """Test if the required file structure exists for downloads"""
    print("\n🧪 Testing File Structure")
    print("=" * 60)
    
    from django.conf import settings
    import os
    
    # Check if media root exists
    media_root = settings.MEDIA_ROOT
    print(f"📁 Media root: {media_root}")
    
    if not os.path.exists(media_root):
        print("❌ Media root directory does not exist")
        return False
    
    print("✅ Media root exists")
    
    # Check if inspection folder exists
    inspection_folder = os.path.join(media_root, 'inspection')
    print(f"📁 Inspection folder: {inspection_folder}")
    
    if not os.path.exists(inspection_folder):
        print("❌ Inspection folder does not exist")
        return False
    
    print("✅ Inspection folder exists")
    
    # Check for year/month subfolders
    year_folders = [d for d in os.listdir(inspection_folder) if os.path.isdir(os.path.join(inspection_folder, d)) and d.isdigit()]
    print(f"📅 Year folders found: {year_folders}")
    
    if not year_folders:
        print("⚠️  No year folders found in inspection directory")
        return False
    
    # Check for month folders in the most recent year
    latest_year = max(year_folders)
    year_path = os.path.join(inspection_folder, latest_year)
    month_folders = [d for d in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, d)) and d.isdigit()]
    print(f"📅 Month folders in {latest_year}: {month_folders}")
    
    if not month_folders:
        print("⚠️  No month folders found in latest year")
        return False
    
    print("✅ File structure looks good")
    return True

def test_inspection_data():
    """Test if there's inspection data available for testing"""
    print("\n🧪 Testing Inspection Data")
    print("=" * 60)
    
    from main.models import FoodSafetyAgencyInspection
    
    # Count total inspections
    total_inspections = FoodSafetyAgencyInspection.objects.count()
    print(f"📊 Total inspections in database: {total_inspections}")
    
    if total_inspections == 0:
        print("❌ No inspection data found")
        return False
    
    # Count inspections with client names
    inspections_with_clients = FoodSafetyAgencyInspection.objects.exclude(
        client_name__isnull=True
    ).exclude(client_name='').count()
    print(f"📊 Inspections with client names: {inspections_with_clients}")
    
    # Count inspections with dates
    inspections_with_dates = FoodSafetyAgencyInspection.objects.exclude(
        date_of_inspection__isnull=True
    ).count()
    print(f"📊 Inspections with dates: {inspections_with_dates}")
    
    # Get sample inspection for testing
    sample_inspection = FoodSafetyAgencyInspection.objects.filter(
        client_name__isnull=False,
        date_of_inspection__isnull=False
    ).first()
    
    if sample_inspection:
        print(f"📋 Sample inspection: {sample_inspection.client_name} on {sample_inspection.date_of_inspection}")
        return True
    else:
        print("❌ No suitable sample inspection found")
        return False

def test_frontend_integration():
    """Test frontend integration points"""
    print("\n🧪 Testing Frontend Integration")
    print("=" * 60)
    
    # Check if the template file exists and contains the download function
    template_path = Path('main/templates/main/shipment_list_clean.html')
    
    if not template_path.exists():
        print("❌ Template file not found")
        return False
    
    print("✅ Template file exists")
    
    # Read template and check for download function
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Check for downloadAllFiles function
    if 'downloadAllFiles' in template_content:
        print("✅ downloadAllFiles function found in template")
    else:
        print("❌ downloadAllFiles function not found in template")
        return False
    
    # Check for download all button
    if 'Download All' in template_content:
        print("✅ Download All button found in template")
    else:
        print("❌ Download All button not found in template")
        return False
    
    # Check for API endpoint call
    if '/inspections/download-all-files/' in template_content:
        print("✅ API endpoint call found in template")
    else:
        print("❌ API endpoint call not found in template")
        return False
    
    print("✅ Frontend integration looks good")
    return True

def test_url_configuration():
    """Test URL configuration for download endpoint"""
    print("\n🧪 Testing URL Configuration")
    print("=" * 60)
    
    from django.urls import reverse
    from django.test import Client
    
    try:
        # Test if the URL can be resolved
        url = reverse('download_all_inspection_files')
        print(f"✅ URL resolved: {url}")
        
        # Test with a client
        client = Client()
        response = client.get(url)
        print(f"📊 GET response status: {response.status_code}")
        
        # Should return 405 Method Not Allowed for GET (expects POST) or 302 (redirect to login)
        if response.status_code in [405, 302]:
            print(f"✅ Correctly handles GET requests (status: {response.status_code})")
            return True
        else:
            print(f"⚠️  Unexpected response for GET: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ URL configuration error: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🚀 Starting Comprehensive Download All Functionality Test")
    print("=" * 80)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Inspection Data", test_inspection_data),
        ("Frontend Integration", test_frontend_integration),
        ("URL Configuration", test_url_configuration),
        ("Backend Functionality", test_download_all_backend)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Download all functionality should work correctly.")
    else:
        print("⚠️  Some tests failed. Check the issues above before using download all functionality.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
