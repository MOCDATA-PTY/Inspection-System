#!/usr/bin/env python3
"""
Simple test to check if product class is being saved and can be retrieved
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.test import Client
from django.contrib.auth.models import User

def test_save_and_retrieve():
    print("🧪 Testing Product Class Save & Retrieve")
    print("=" * 40)
    
    # Find inspection 9080
    inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=9080).first()
    
    if not inspection:
        print("❌ Inspection 9080 not found")
        return False
    
    print(f"✅ Found inspection: {inspection.remote_id}")
    print(f"   Current product_class: '{inspection.product_class}'")
    
    # Test 1: Check if we can update the product class
    test_class = "Test Class for Persistence"
    original_class = inspection.product_class
    
    print(f"\n🧪 Testing database update...")
    inspection.product_class = test_class
    inspection.save()
    
    # Verify it was saved
    updated = FoodSafetyAgencyInspection.objects.get(remote_id=9080)
    if updated.product_class == test_class:
        print("✅ Database update successful")
    else:
        print(f"❌ Database update failed: got '{updated.product_class}'")
        return False
    
    # Test 2: Test API endpoint
    print(f"\n🧪 Testing API endpoint...")
    test_user = User.objects.filter(is_staff=True).first()
    if not test_user:
        print("❌ No staff user found")
        return False
    
    client = Client()
    client.force_login(test_user)
    
    api_test_class = "API Test Class"
    response = client.post('/update-product-class/', {
        'inspection_id': 9080,
        'product_class': api_test_class
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            # Check database
            updated = FoodSafetyAgencyInspection.objects.get(remote_id=9080)
            if updated.product_class == api_test_class:
                print("✅ API update successful")
            else:
                print(f"❌ API update failed: got '{updated.product_class}'")
                return False
        else:
            print(f"❌ API returned error: {data.get('error')}")
            return False
    else:
        print(f"❌ API call failed: {response.status_code}")
        return False
    
    # Restore original value
    inspection.product_class = original_class
    inspection.save()
    print("✅ Restored original value")
    
    return True

if __name__ == '__main__':
    try:
        success = test_save_and_retrieve()
        
        print("\n" + "=" * 40)
        if success:
            print("✅ SAVE/RETRIEVE WORKS - The issue is in template rendering")
        else:
            print("❌ SAVE/RETRIEVE FAILED - The issue is in database/API")
                
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n🏁 Test completed!")