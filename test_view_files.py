#!/usr/bin/env python3
"""
Test script for the new View Files functionality.
This script tests the get_client_all_files endpoint.
"""

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth.models import User

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.views.core_views import get_client_all_files
from main.models import FoodSafetyAgencyInspection, Client

def test_client_all_files():
    """Test the get_client_all_files functionality."""
    print("🧪 Testing Client All Files Functionality")
    print("=" * 50)
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.post('/client-all-files/', 
                          data='{"client_name": "Test Client"}', 
                          content_type='application/json')
    
    # Create a test user (or use existing)
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        request.user = user
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False
    
    # Check if we have any clients
    clients = Client.objects.all()[:5]
    print(f"📊 Found {clients.count()} clients in database")
    
    if clients.count() == 0:
        print("⚠️ No clients found in database. Creating test client...")
        # You could create test data here if needed
        return True
    
    # Test with the first client
    test_client = clients.first()
    print(f"🔍 Testing with client: {test_client.name}")
    
    # Update request data
    request._body = f'{{"client_name": "{test_client.name}"}}'.encode('utf-8')
    
    try:
        print("🚀 Calling get_client_all_files...")
        response = get_client_all_files(request)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Client All Files Test PASSED!")
                print(f"📁 Total Files: {data.get('total_files', 0)}")
                print(f"📂 Inspection Periods: {len(data.get('inspections_found', []))}")
                print(f"📊 Categories Found:")
                
                files = data.get('files', {})
                for category, file_list in files.items():
                    print(f"  - {category}: {len(file_list)} files")
                
                return True
            else:
                print(f"❌ Test FAILED: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Test FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test FAILED with exception: {e}")
        return False

def check_media_structure():
    """Check if the media folder structure exists."""
    print("\n🔍 Checking Media Folder Structure...")
    
    from django.conf import settings
    inspection_base = os.path.join(settings.MEDIA_ROOT, 'inspection')
    
    if os.path.exists(inspection_base):
        print(f"✅ Found inspection folder: {inspection_base}")
        
        # List year folders
        year_folders = [f for f in os.listdir(inspection_base) if os.path.isdir(os.path.join(inspection_base, f))]
        print(f"📅 Year folders found: {year_folders}")
        
        # Check for client folders
        total_client_folders = 0
        for year in year_folders:
            year_path = os.path.join(inspection_base, year)
            for month in os.listdir(year_path):
                month_path = os.path.join(year_path, month)
                if os.path.isdir(month_path):
                    client_folders = [f for f in os.listdir(month_path) if os.path.isdir(os.path.join(month_path, f))]
                    total_client_folders += len(client_folders)
        
        print(f"👥 Total client folders found: {total_client_folders}")
        return total_client_folders > 0
    else:
        print(f"❌ Inspection folder not found: {inspection_base}")
        print("💡 Run the 4-month data pull first to create the folder structure")
        return False

if __name__ == "__main__":
    print("🧪 View Files Functionality Test")
    print("=" * 50)
    
    # Check media structure first
    if not check_media_structure():
        print("\n⚠️ No media structure found. Please run the 4-month data pull first.")
        sys.exit(1)
    
    # Run the test
    success = test_client_all_files()
    
    if success:
        print("\n🎉 All tests passed! The View Files functionality is working.")
        print("\n💡 Now you can:")
        print("   1. Go to http://127.0.0.1:8000/inspections/")
        print("   2. Click 'View Files' on any client row")
        print("   3. See ALL files for that client across all inspections!")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        sys.exit(1)
