#!/usr/bin/env python3
"""
Test the template fix by checking if the JavaScript preserves the database value
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
from bs4 import BeautifulSoup

def test_template_fix():
    print("🧪 Testing Template Fix")
    print("=" * 30)
    
    # Find inspection 9080
    inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=9080).first()
    
    if not inspection:
        print("❌ Inspection 9080 not found")
        return False
    
    print(f"✅ Testing inspection: {inspection.remote_id}")
    print(f"   Product Class: '{inspection.product_class}'")
    
    # Create test user and client
    test_user = User.objects.filter(is_staff=True).first()
    if not test_user:
        print("❌ No staff user found")
        return False
    
    client = Client()
    client.force_login(test_user)
    
    # Get just the first page to minimize load time
    response = client.get('/inspections/?page=1&per_page=3')
    
    if response.status_code != 200:
        print(f"❌ Page failed to load: {response.status_code}")
        return False
    
    print("✅ Page loaded successfully")
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the product class select for inspection 9080
    select_elements = soup.find_all('select', class_='product-class-select')
    
    test_select = None
    for select in select_elements:
        if select.get('data-inspection-id') == '9080':
            test_select = select
            break
    
    if not test_select:
        print("❌ Could not find select for inspection 9080")
        return False
    
    print("✅ Found product class select element")
    
    # Check if the template has the selected option
    selected_option = test_select.find('option', selected=True)
    if selected_option:
        selected_value = selected_option.get('value')
        expected_value = inspection.product_class
        
        if selected_value == expected_value:
            print(f"✅ Template correctly shows selected option: '{selected_value}'")
            return True
        else:
            print(f"❌ Template shows wrong option: '{selected_value}' (expected: '{expected_value}')")
            return False
    else:
        print("❌ Template shows no selected option")
        # Show what options are available
        options = test_select.find_all('option')
        print(f"   Available options ({len(options)}):")
        for opt in options[:5]:  # Show first 5
            print(f"     - '{opt.get('value')}' | '{opt.text.strip()}'")
        return False

if __name__ == '__main__':
    try:
        success = test_template_fix()
        
        print("\n" + "=" * 30)
        if success:
            print("🎉 TEMPLATE FIX WORKS!")
        else:
            print("❌ Template fix needs more work")
                
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n🏁 Test completed!")