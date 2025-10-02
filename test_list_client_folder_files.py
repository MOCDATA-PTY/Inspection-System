#!/usr/bin/env python3
"""
Test the list_client_folder_files endpoint for Meat Mania inspection
"""

import os
import sys
import django
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from main.models import FoodSafetyAgencyInspection

def test_list_client_folder_files():
    """Test the list_client_folder_files endpoint for Meat Mania inspection"""
    
    print("=== Testing list_client_folder_files for Meat Mania ===")
    
    # Create test client
    client = Client()
    
    # Login as developer
    login_success = client.login(username='developer', password='XHnj1C#QkFs9')
    if not login_success:
        print("FAILED: Failed to login as developer")
        return False
    
    print("SUCCESS: Logged in as developer")
    
    # Test data for Meat Mania
    client_name = "Meat Mania"
    inspection_date = "2025-09-26"
    
    print(f"Testing list_client_folder_files for: {client_name} on {inspection_date}")
    
    # Test list_client_folder_files endpoint
    request_data = {
        'client_name': client_name,
        'inspection_date': inspection_date
    }
    
    print("Sending list_client_folder_files request...")
    response = client.post('/list-client-folder-files/', 
                          data=json.dumps(request_data),
                          content_type='application/json')
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("SUCCESS: list_client_folder_files response received")
            print(f"Response data: {data}")
            
            if data.get('success'):
                files = data.get('files', {})
                print(f"Files found: {len(files)}")
                
                if files:
                    print("File categories:")
                    for category, file_list in files.items():
                        print(f"  {category}: {len(file_list)} files")
                        for file_info in file_list:
                            print(f"    - {file_info.get('name', 'Unknown')}")
                else:
                    print("No files found for this inspection")
            else:
                print(f"ERROR: {data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"ERROR: Error parsing JSON response: {e}")
            print(f"Raw response: {response.content}")
    else:
        print(f"ERROR: list_client_folder_files request failed: {response.status_code}")
        print(f"Response: {response.content}")
    
    return response.status_code == 200

def main():
    """Main test function"""
    print("Testing list_client_folder_files endpoint for Meat Mania inspection")
    print("=" * 70)
    
    success = test_list_client_folder_files()
    
    print("\n" + "=" * 70)
    if success:
        print("SUCCESS: list_client_folder_files endpoint is working!")
    else:
        print("FAILED: Some issues found. Check the output above for details.")

if __name__ == "__main__":
    main()
