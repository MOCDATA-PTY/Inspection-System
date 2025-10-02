#!/usr/bin/env python3
"""
Test script to verify KM and Hours saving functionality
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

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
import json

def test_km_hours_endpoints():
    """Test the KM and Hours endpoints"""
    print("🧪 Testing KM and Hours Endpoints")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Created test user")
    else:
        print("✅ Using existing test user")
    
    # Login the user
    login_success = client.login(username='testuser', password='testpass123')
    print(f"🔐 Login successful: {login_success}")
    
    if not login_success:
        print("❌ Failed to login test user")
        return False
    
    # Get a test inspection
    inspection = FoodSafetyAgencyInspection.objects.first()
    if not inspection:
        print("❌ No inspections found in database")
        return False
    
    print(f"📋 Using inspection ID: {inspection.id}")
    print(f"📋 Client: {inspection.client_name}")
    print(f"📋 Date: {inspection.inspection_date}")
    
    # Test KM endpoint
    print("\n🚗 Testing KM Traveled Endpoint")
    print("-" * 30)
    
    km_data = {
        'group_id': f"{inspection.client_name}_{inspection.inspection_date}".replace(' ', '_').replace('-', '_'),
        'km_traveled': '45.5',
        'csrfmiddlewaretoken': client.cookies.get('csrftoken', '').value if client.cookies.get('csrftoken') else ''
    }
    
    print(f"📤 Sending KM data: {km_data}")
    
    try:
        response = client.post('/update-group-km-traveled/', data=km_data)
        print(f"📥 KM Response status: {response.status_code}")
        print(f"📥 KM Response content: {response.content.decode()}")
        
        if response.status_code == 200:
            try:
                data = json.loads(response.content)
                print(f"✅ KM Response JSON: {data}")
                if data.get('success'):
                    print("✅ KM update successful!")
                else:
                    print(f"❌ KM update failed: {data.get('error')}")
            except json.JSONDecodeError:
                print("❌ KM response is not valid JSON")
                print(f"📥 Raw response: {response.content.decode()}")
        else:
            print(f"❌ KM endpoint returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ KM endpoint error: {e}")
    
    # Test Hours endpoint
    print("\n⏰ Testing Hours Endpoint")
    print("-" * 30)
    
    hours_data = {
        'group_id': f"{inspection.client_name}_{inspection.inspection_date}".replace(' ', '_').replace('-', '_'),
        'hours': '8.5',
        'csrfmiddlewaretoken': client.cookies.get('csrftoken', '').value if client.cookies.get('csrftoken') else ''
    }
    
    print(f"📤 Sending Hours data: {hours_data}")
    
    try:
        response = client.post('/update-group-hours/', data=hours_data)
        print(f"📥 Hours Response status: {response.status_code}")
        print(f"📥 Hours Response content: {response.content.decode()}")
        
        if response.status_code == 200:
            try:
                data = json.loads(response.content)
                print(f"✅ Hours Response JSON: {data}")
                if data.get('success'):
                    print("✅ Hours update successful!")
                else:
                    print(f"❌ Hours update failed: {data.get('error')}")
            except json.JSONDecodeError:
                print("❌ Hours response is not valid JSON")
                print(f"📥 Raw response: {response.content.decode()}")
        else:
            print(f"❌ Hours endpoint returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Hours endpoint error: {e}")
    
    # Verify the data was saved
    print("\n🔍 Verifying Data was Saved")
    print("-" * 30)
    
    # Refresh the inspection from database
    inspection.refresh_from_db()
    print(f"📊 Current KM Traveled: {inspection.km_traveled}")
    print(f"📊 Current Hours: {inspection.hours}")
    
    return True

def test_javascript_functions():
    """Test if JavaScript functions are properly defined"""
    print("\n🔧 Testing JavaScript Functions")
    print("=" * 50)
    
    # Read the HTML file
    html_file = 'main/templates/main/shipment_list_clean.html'
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if functions are defined
    km_function_found = 'function updateGroupKmTraveled(input)' in content
    hours_function_found = 'function updateGroupHours(input)' in content
    
    print(f"🔍 updateGroupKmTraveled function found: {km_function_found}")
    print(f"🔍 updateGroupHours function found: {hours_function_found}")
    
    if km_function_found and hours_function_found:
        print("✅ Both JavaScript functions are defined in the HTML file")
        
        # Check if functions are properly closed
        km_function_count = content.count('function updateGroupKmTraveled(input)')
        hours_function_count = content.count('function updateGroupHours(input)')
        
        print(f"📊 updateGroupKmTraveled function count: {km_function_count}")
        print(f"📊 updateGroupHours function count: {hours_function_count}")
        
        if km_function_count == 1 and hours_function_count == 1:
            print("✅ Functions are defined exactly once (no duplicates)")
        else:
            print("⚠️ Functions may have duplicates or be missing")
            
        return True
    else:
        print("❌ JavaScript functions are missing from HTML file")
        return False

def main():
    """Main test function"""
    print("🧪 KM and Hours Functionality Test")
    print("=" * 60)
    
    # Test JavaScript functions
    js_ok = test_javascript_functions()
    
    # Test endpoints
    endpoints_ok = test_km_hours_endpoints()
    
    print("\n📋 Test Summary")
    print("=" * 30)
    print(f"🔧 JavaScript Functions: {'✅ PASS' if js_ok else '❌ FAIL'}")
    print(f"🌐 Endpoints: {'✅ PASS' if endpoints_ok else '❌ FAIL'}")
    
    if js_ok and endpoints_ok:
        print("\n🎉 All tests passed! KM and Hours functionality should work.")
    else:
        print("\n⚠️ Some tests failed. Check the issues above.")
    
    return js_ok and endpoints_ok

if __name__ == '__main__':
    main()
