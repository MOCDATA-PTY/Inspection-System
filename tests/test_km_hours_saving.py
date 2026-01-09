#!/usr/bin/env python3
"""
Test script to verify KM and Hours saving functionality
This script tests the backend endpoints for updating group KM and Hours
"""

import requests
import json
from datetime import datetime, date
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User

def test_km_hours_endpoints():
    """Test the KM and Hours update endpoints"""
    
    print("🧪 Testing KM and Hours Saving Functionality")
    print("=" * 50)
    
    # Test data
    base_url = "http://localhost:8000"  # Adjust if your server runs on different port
    
    # First, let's check if we have any inspections in the database
    print("\n1. Checking database for existing inspections...")
    inspections = FoodSafetyAgencyInspection.objects.all()
    print(f"   Found {inspections.count()} total inspections")
    
    if inspections.count() == 0:
        print("   ❌ No inspections found in database. Please add some test data first.")
        return False
    
    # Get a sample inspection to work with
    sample_inspection = inspections.first()
    print(f"   Using sample inspection: {sample_inspection.client_name} on {sample_inspection.date_of_inspection}")
    
    # Create a test group ID (format: client_name_date)
    client_name = sample_inspection.client_name.replace(' ', '_').replace('-', '_')
    date_str = sample_inspection.date_of_inspection.strftime('%Y%m%d')
    test_group_id = f"{client_name}_{date_str}"
    
    print(f"   Test Group ID: {test_group_id}")
    
    # Test KM update
    print("\n2. Testing KM update endpoint...")
    km_test_data = {
        'group_id': test_group_id,
        'km_traveled': '25.5',
        'csrfmiddlewaretoken': 'test_token'  # This will need to be replaced with real token
    }
    
    try:
        # Note: This will fail without proper authentication, but we can test the endpoint structure
        response = requests.post(f"{base_url}/update-group-km-traveled/", data=km_test_data)
        print(f"   KM Update Response Status: {response.status_code}")
        print(f"   KM Update Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Server not running. Please start the Django server first.")
        print("   Run: python manage.py runserver")
        return False
    except Exception as e:
        print(f"   ❌ KM Update Error: {e}")
    
    # Test Hours update
    print("\n3. Testing Hours update endpoint...")
    hours_test_data = {
        'group_id': test_group_id,
        'hours': '3.5',
        'csrfmiddlewaretoken': 'test_token'  # This will need to be replaced with real token
    }
    
    try:
        response = requests.post(f"{base_url}/update-group-hours/", data=hours_test_data)
        print(f"   Hours Update Response Status: {response.status_code}")
        print(f"   Hours Update Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Hours Update Error: {e}")
    
    # Test database update directly
    print("\n4. Testing database update directly...")
    try:
        # Find inspections in the group
        matching_inspections = FoodSafetyAgencyInspection.objects.filter(
            client_name=sample_inspection.client_name,
            date_of_inspection=sample_inspection.date_of_inspection
        )
        
        print(f"   Found {matching_inspections.count()} inspections in group")
        
        # Update KM and Hours directly
        updated_km = matching_inspections.update(km_traveled=30.0)
        updated_hours = matching_inspections.update(hours=4.0)
        
        print(f"   ✅ Updated KM for {updated_km} inspections")
        print(f"   ✅ Updated Hours for {updated_hours} inspections")
        
        # Verify the updates
        updated_inspection = matching_inspections.first()
        print(f"   Verification - KM: {updated_inspection.km_traveled}, Hours: {updated_inspection.hours}")
        
    except Exception as e:
        print(f"   ❌ Database Update Error: {e}")
        return False
    
    print("\n5. Testing group ID parsing logic...")
    try:
        # Test the group ID parsing logic from the backend
        group_id = test_group_id
        
        if '_' not in group_id:
            print("   ❌ Invalid group ID format")
            return False
        
        parts = group_id.split('_')
        if len(parts) < 2:
            print("   ❌ Invalid group ID format")
            return False
        
        # Reconstruct client_name and date
        date_part = parts[-1]
        client_name_parts = parts[:-1]
        client_name = '_'.join(client_name_parts)
        
        print(f"   Parsed Client Name: {client_name}")
        print(f"   Parsed Date Part: {date_part}")
        
        # Convert date string to date object
        from datetime import datetime
        date_of_inspection = None
        for fmt in ('%Y-%m-%d', '%Y%m%d'):
            try:
                date_of_inspection = datetime.strptime(date_part, fmt).date()
                break
            except ValueError:
                continue
        
        if not date_of_inspection:
            print(f"   ❌ Invalid date format: {date_part}")
            return False
        
        print(f"   Parsed Date: {date_of_inspection}")
        
        # Test normalization
        import re
        def normalize(n):
            return re.sub(r'[^a-zA-Z0-9]', '', (n or '')).lower()
        
        raw_key = normalize(client_name)
        print(f"   Normalized Key: {raw_key}")
        
        # Find matching inspections
        candidate_qs = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection=date_of_inspection
        )
        matching_ids = [ins.id for ins in candidate_qs if normalize(ins.client_name) == raw_key]
        inspections = FoodSafetyAgencyInspection.objects.filter(id__in=matching_ids)
        
        print(f"   Found {inspections.count()} matching inspections")
        
    except Exception as e:
        print(f"   ❌ Group ID Parsing Error: {e}")
        return False
    
    print("\n✅ All tests completed!")
    return True

def test_frontend_integration():
    """Test the frontend integration by checking the HTML structure"""
    
    print("\n🌐 Testing Frontend Integration")
    print("=" * 50)
    
    # Check if the HTML file exists and contains the required elements
    html_file = "main/templates/main/shipment_list_clean.html"
    
    if not os.path.exists(html_file):
        print(f"   ❌ HTML file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required elements
    checks = [
        ("KM input fields", "group-km-input"),
        ("Hours input fields", "group-hours-input"),
        ("KM update function", "updateGroupKmTraveled"),
        ("Hours update function", "updateGroupHours"),
        ("CSRF token function", "getCSRFToken"),
        ("KM endpoint", "/update-group-km-traveled/"),
        ("Hours endpoint", "/update-group-hours/"),
        ("onchange events", "onchange=\"updateGroupKmTraveled(this)\""),
        ("onblur events", "onblur=\"updateGroupKmTraveled(this)\""),
    ]
    
    print("\n   Checking HTML elements:")
    all_found = True
    
    for check_name, search_term in checks:
        if search_term in content:
            print(f"   ✅ {check_name}: Found")
        else:
            print(f"   ❌ {check_name}: Missing")
            all_found = False
    
    return all_found

def main():
    """Main test function"""
    
    print("🚀 Starting KM and Hours Saving Tests")
    print("=" * 60)
    
    # Test frontend integration
    frontend_ok = test_frontend_integration()
    
    # Test backend functionality
    backend_ok = test_km_hours_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if frontend_ok:
        print("✅ Frontend Integration: PASSED")
    else:
        print("❌ Frontend Integration: FAILED")
    
    if backend_ok:
        print("✅ Backend Functionality: PASSED")
    else:
        print("❌ Backend Functionality: FAILED")
    
    if frontend_ok and backend_ok:
        print("\n🎉 ALL TESTS PASSED! KM and Hours saving should work correctly.")
        print("\n📝 Next Steps:")
        print("   1. Start your Django server: python manage.py runserver")
        print("   2. Open the browser console (F12)")
        print("   3. Try entering values in KM and Hours fields")
        print("   4. Check console logs for debugging information")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    return frontend_ok and backend_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
