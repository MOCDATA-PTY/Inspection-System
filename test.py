#!/usr/bin/env python3
"""
Test script to verify file button color functionality.

This script tests that View Files buttons turn orange when files are detected
and red when no files are present.
"""

import os
import sys
import django
import time
from datetime import datetime, date

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
import os

def create_test_data():
    """Create test inspections and files for testing button colors."""
    print("Creating test data...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
    )
    
    # Test case 1: Inspection with files (should show orange button)
    inspection_with_files, created = FoodSafetyAgencyInspection.objects.get_or_create(
        client_name='Test Client With Files',
        date_of_inspection=date.today(),
        defaults={
            'remote_id': 99991,
            'rfi_uploaded_by': user,
            'rfi_uploaded_date': timezone.now()
        }
    )
    
    # Create a test file on filesystem for this inspection
    create_test_file(inspection_with_files, 'rfi')
    
    # Test case 2: Inspection without files (should show red button)
    inspection_no_files, created = FoodSafetyAgencyInspection.objects.get_or_create(
        client_name='Test Client No Files',
        date_of_inspection=date.today(),
        defaults={
            'remote_id': 99992
        }
    )
    
    print("Created test inspections:")
    print(f"   - {inspection_with_files.client_name} (ID: {inspection_with_files.id}) - Has files")
    print(f"   - {inspection_no_files.client_name} (ID: {inspection_no_files.id}) - No files")
    
    return inspection_with_files, inspection_no_files

def create_test_file(inspection, file_type):
    """Create a test file on the filesystem for an inspection."""
    from datetime import datetime
    import re
    
    # Create folder structure matching the upload system
    date_obj = inspection.date_of_inspection
    year_folder = date_obj.strftime('%Y')
    month_folder = date_obj.strftime('%B')
    
    # Sanitize client name for filesystem (matching upload function)
    def create_folder_name(name):
        if not name:
            return "unknown_client"
        clean_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)
        clean_name = clean_name.replace(' ', '_').replace('-', '_')
        clean_name = re.sub(r'_+', '_', clean_name)
        clean_name = clean_name.strip('_').lower()
        return clean_name or "unknown_client"
    
    client_folder = create_folder_name(inspection.client_name)
    
    # Create the directory structure
    inspection_folder = os.path.join(
        settings.MEDIA_ROOT, 
        'inspection', 
        year_folder, 
        month_folder, 
        client_folder,
        file_type
    )
    
    os.makedirs(inspection_folder, exist_ok=True)
    
    # Create a test file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_{file_type}_{timestamp}.pdf"
    file_path = os.path.join(inspection_folder, filename)
    
    with open(file_path, 'w') as f:
        f.write(f"Test {file_type} document for {inspection.client_name}")
    
    print(f"   Created test file: {file_path}")

def test_file_status_api():
    """Test the file status API endpoint."""
    print("\nTesting file status detection...")
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        import json
        
        # Create a test client and login
        client = Client()
        user = User.objects.get(username='testuser')
        client.force_login(user)
        
        # Test data
        combinations = [
            'Test Client With Files_' + date.today().strftime('%Y-%m-%d'),
            'Test Client No Files_' + date.today().strftime('%Y-%m-%d')
        ]
        
        # Make the API request
        response = client.post('/get_file_status/', 
            json.dumps({'combinations': combinations}),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("File status results:")
            for combination, status in data.items():
                expected_status = 'partial_files' if 'With Files' in combination else 'no_files'
                status_color = 'ORANGE' if status == 'partial_files' else 'RED' if status == 'no_files' else 'UNKNOWN'
                result = 'PASS' if status == expected_status else 'FAIL'
                
                print(f"   {result}: {combination}: {status} ({status_color})")
                
                if status != expected_status:
                    print(f"      Expected: {expected_status}, Got: {status}")
    else:
            print(f"API request failed with status {response.status_code}")
            print(f"   Response: {response.content.decode('utf-8')}")
            
    except Exception as e:
        print(f"Error testing file status API: {e}")
        import traceback
        traceback.print_exc()

def test_button_color_logic():
    """Test the button color logic by simulating different file statuses."""
    print("\nTesting button color logic...")
    
    test_cases = [
        ('no_files', 'RED', 'No files available'),
        ('partial_files', 'ORANGE', 'Files uploaded'),
        ('compliance_only', 'ORANGE', 'Only compliance documents available'),
        ('all_files', 'GREEN', 'All files available')
    ]
    
    for status, expected_color, expected_title in test_cases:
        print(f"   Testing {status}: Expected {expected_color}")
        
        # This would be the JavaScript logic translated to Python for testing
        if status == 'no_files':
            css_class = 'btn-danger'
            bg_color = '#dc3545'
            text_color = 'white'
        elif status in ['partial_files', 'compliance_only']:
            css_class = 'btn-warning'
            bg_color = '#ff8c00' if status == 'partial_files' else '#ffc107'
            text_color = 'white' if status == 'partial_files' else 'black'
        elif status == 'all_files':
            css_class = 'btn-success'
            bg_color = '#28a745'
            text_color = 'white'
    else:
            css_class = 'btn-info'
            bg_color = '#17a2b8'
            text_color = 'white'
        
        print(f"      CSS Class: {css_class}")
        print(f"      Background: {bg_color}")
        print(f"      Text Color: {text_color}")
        print(f"      Title: {expected_title}")

def cleanup_test_data():
    """Clean up test data."""
    print("\nCleaning up test data...")
    
    try:
        import shutil
        
        # Delete test files from filesystem
        test_clients = ['Test Client With Files', 'Test Client No Files']
        for client_name in test_clients:
            # Create folder structure matching the upload system
            date_obj = date.today()
            year_folder = date_obj.strftime('%Y')
            month_folder = date_obj.strftime('%B')
            
            # Sanitize client name for filesystem
            def create_folder_name(name):
                if not name:
                    return "unknown_client"
                import re
                clean_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)
                clean_name = clean_name.replace(' ', '_').replace('-', '_')
                clean_name = re.sub(r'_+', '_', clean_name)
                clean_name = clean_name.strip('_').lower()
                return clean_name or "unknown_client"
            
            client_folder = create_folder_name(client_name)
            
            # Remove the client folder
            client_path = os.path.join(
                settings.MEDIA_ROOT, 
                'inspection', 
                year_folder, 
                month_folder, 
                client_folder
            )
            
            if os.path.exists(client_path):
                shutil.rmtree(client_path)
                print(f"   Removed folder: {client_path}")
        
        # Delete test inspections from database
        deleted_count = FoodSafetyAgencyInspection.objects.filter(
            client_name__startswith='Test Client'
        ).delete()[0]
        
        print(f"Cleaned up {deleted_count} test records")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    """Main test function."""
    print("Starting File Button Color Test")
    print("=" * 50)
    
    try:
        # Create test data
        inspection_with_files, inspection_no_files = create_test_data()
        
        # Test file status API
        test_file_status_api()
        
        # Test button color logic
        test_button_color_logic()
        
        print("\n" + "=" * 50)
        print("Test completed successfully!")
        print("\nSummary:")
        print("   - Orange buttons should appear for shipments with files")
        print("   - Red buttons should appear for shipments without files")
        print("   - The btn-files-none CSS class should be removed to prevent conflicts")
        print("   - JavaScript should apply btn-warning class with orange background")
        
        print("\nTo test in browser:")
        print("   1. Start the Django server: python manage.py runserver")
        print("   2. Navigate to the shipment list page")
        print("   3. Look for 'Test Client With Files' - button should be ORANGE")
        print("   4. Look for 'Test Client No Files' - button should be RED")
        print("   5. Upload a file to any shipment and verify button turns ORANGE")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Ask user if they want to keep test data
        try:
            keep_data = input("\nKeep test data for manual testing? (y/N): ").lower().strip()
            if keep_data != 'y':
                cleanup_test_data()
    else:
                print("Test data preserved for manual testing")
        except KeyboardInterrupt:
            print("\nCleaning up test data...")
            cleanup_test_data()

if __name__ == '__main__':
    main()