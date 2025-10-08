#!/usr/bin/env python3
"""
Debug the template rendering to see what's actually being generated
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

def debug_template():
    print("🔍 Debugging Template Rendering")
    print("=" * 50)
    
    # Find inspection 9080
    inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=9080).first()
    
    if not inspection:
        print("❌ Inspection 9080 not found")
        return
    
    print(f"✅ Found inspection: {inspection.remote_id}")
    print(f"   Commodity: '{inspection.commodity}'")
    print(f"   Product Class: '{inspection.product_class}'")
    
    # Create test user and client
    test_user = User.objects.filter(is_staff=True).first()
    if not test_user:
        print("❌ No staff user found")
        return
    
    client = Client()
    client.force_login(test_user)
    
    # Get the page
    response = client.get('/inspections/')
    
    if response.status_code != 200:
        print(f"❌ Page failed to load: {response.status_code}")
        return
    
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
        return
    
    print("✅ Found product class select element")
    print(f"   data-commodity: '{test_select.get('data-commodity')}'")
    print(f"   data-inspection-id: '{test_select.get('data-inspection-id')}'")
    
    # Check all options
    options = test_select.find_all('option')
    print(f"\n📋 All options in dropdown ({len(options)} total):")
    
    for i, opt in enumerate(options):
        value = opt.get('value', '')
        text = opt.text.strip()
        selected = 'selected' in opt.attrs
        print(f"   {i+1}. Value: '{value}' | Text: '{text}' | Selected: {selected}")
    
    # Check if the database value is in the options
    db_value = inspection.product_class
    matching_options = [opt for opt in options if opt.get('value') == db_value or opt.text.strip() == db_value]
    
    if matching_options:
        print(f"\n✅ Found matching option for database value: '{db_value}'")
        for opt in matching_options:
            print(f"   - Value: '{opt.get('value')}' | Text: '{opt.text.strip()}' | Selected: {'selected' in opt.attrs}")
    else:
        print(f"\n❌ No matching option found for database value: '{db_value}'")
        print("   This explains why the dropdown shows no selection!")

if __name__ == '__main__':
    debug_template()