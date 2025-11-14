#!/usr/bin/env python3
"""
Test RFI file visibility fix
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
import json

def test_rfi_file_visibility():
    """Test that RFI files are visible in View Files popup"""
    print("=" * 60)
    print("TESTING RFI FILE VISIBILITY FIX")
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
    
    # Test the View Files popup for Meat Mania (where we uploaded RFI)
    print("\n1. Testing View Files popup for Meat Mania (RFI uploaded):")
    
    request_data = {
        'group_id': 'Meat_Mania_20250926',
        'client_name': 'Meat Mania',
        'inspection_date': '2025-09-26',
        '_force_refresh': True
    }
    
    try:
        response = client.post('/inspections/files/', 
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Response success: {data.get('success', False)}")
                
                if data.get('success'):
                    files = data.get('files', {})
                    rfi_files = files.get('rfi', [])
                    print(f"   RFI files found: {len(rfi_files)}")
                    
                    if rfi_files:
                        print("   [OK] SUCCESS: RFI files are visible!")
                        for file_info in rfi_files:
                            print(f"      - {file_info.get('filename', 'Unknown')}")
                    else:
                        print("   [X] ISSUE: No RFI files found in response")
                        print(f"   Available file categories: {list(files.keys())}")
                        for category, file_list in files.items():
                            print(f"      {category}: {len(file_list)} files")
                else:
                    print(f"   [X] ERROR: {data.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"   [X] ERROR parsing response: {str(e)}")
                print(f"   Response content: {response.content.decode()[:500]}...")
        else:
            print(f"   [X] ERROR: HTTP {response.status_code}")
            print(f"   Response content: {response.content.decode()[:500]}...")
            
    except Exception as e:
        print(f"   [X] ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("RFI FILE VISIBILITY TEST COMPLETED")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_rfi_file_visibility()
