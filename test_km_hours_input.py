#!/usr/bin/env python3
"""
Test script to simulate KM and Hours input button interactions
"""

import os
import sys
import django
from django.conf import settings
import requests
from bs4 import BeautifulSoup
import re

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

def test_km_hours_input_simulation():
    """Test KM and Hours input functionality by simulating button interactions"""
    print("🧪 Testing KM and Hours Input Button Simulation")
    print("=" * 60)
    
    # Create a test client
    client = Client()
    
    # Use the developer user
    username = 'developer'
    password = 'XHnj1C#QkFs9'
    
    print(f"🔐 Attempting to login as: {username}")
    
    # Login the user
    login_success = client.login(username=username, password=password)
    print(f"🔐 Login successful: {login_success}")
    
    if not login_success:
        print("❌ Failed to login test user")
        return False
    
    # Get the inspections page
    print("\n📄 Loading inspections page...")
    response = client.get('/inspections/')
    print(f"📥 Page response status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Failed to load inspections page")
        return False
    
    # Parse the HTML to find KM and Hours input fields
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find KM input fields
    km_inputs = soup.find_all('input', {'class': 'group-km-input'})
    print(f"🔍 Found {len(km_inputs)} KM input fields")
    
    # Find Hours input fields
    hours_inputs = soup.find_all('input', {'class': 'group-hours-input'})
    print(f"🔍 Found {len(hours_inputs)} Hours input fields")
    
    if not km_inputs and not hours_inputs:
        print("❌ No KM or Hours input fields found")
        return False
    
    # Test KM input fields
    if km_inputs:
        print("\n🚗 Testing KM Input Fields")
        print("-" * 30)
        
        for i, km_input in enumerate(km_inputs[:3]):  # Test first 3
            group_id = km_input.get('data-group-id')
            current_value = km_input.get('value', '')
            
            print(f"📋 KM Input {i+1}:")
            print(f"   Group ID: {group_id}")
            print(f"   Current Value: {current_value}")
            
            if group_id:
                # Test updating KM value
                new_km_value = "45.5"
                print(f"   Testing update to: {new_km_value}")
                
                # Get CSRF token from the page
                csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
                csrf_value = csrf_token.get('value') if csrf_token else ''
                
                km_data = {
                    'group_id': group_id,
                    'km_traveled': new_km_value,
                    'csrfmiddlewaretoken': csrf_value
                }
                
                try:
                    response = client.post('/update-group-km-traveled/', data=km_data)
                    print(f"   📥 KM Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = json.loads(response.content)
                            print(f"   ✅ KM Response: {data}")
                            if data.get('success'):
                                print(f"   🎉 KM update successful!")
                            else:
                                print(f"   ❌ KM update failed: {data.get('error')}")
                        except json.JSONDecodeError:
                            print(f"   ❌ KM response is not valid JSON")
                    else:
                        print(f"   ❌ KM endpoint returned status {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ KM endpoint error: {e}")
            else:
                print(f"   ⚠️ No group ID found for KM input {i+1}")
    
    # Test Hours input fields
    if hours_inputs:
        print("\n⏰ Testing Hours Input Fields")
        print("-" * 30)
        
        for i, hours_input in enumerate(hours_inputs[:3]):  # Test first 3
            group_id = hours_input.get('data-group-id')
            current_value = hours_input.get('value', '')
            
            print(f"📋 Hours Input {i+1}:")
            print(f"   Group ID: {group_id}")
            print(f"   Current Value: {current_value}")
            
            if group_id:
                # Test updating Hours value
                new_hours_value = "8.5"
                print(f"   Testing update to: {new_hours_value}")
                
                # Get CSRF token from the page
                csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
                csrf_value = csrf_token.get('value') if csrf_token else ''
                
                hours_data = {
                    'group_id': group_id,
                    'hours': new_hours_value,
                    'csrfmiddlewaretoken': csrf_value
                }
                
                try:
                    response = client.post('/update-group-hours/', data=hours_data)
                    print(f"   📥 Hours Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = json.loads(response.content)
                            print(f"   ✅ Hours Response: {data}")
                            if data.get('success'):
                                print(f"   🎉 Hours update successful!")
                            else:
                                print(f"   ❌ Hours update failed: {data.get('error')}")
                        except json.JSONDecodeError:
                            print(f"   ❌ Hours response is not valid JSON")
                    else:
                        print(f"   ❌ Hours endpoint returned status {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Hours endpoint error: {e}")
            else:
                print(f"   ⚠️ No group ID found for Hours input {i+1}")
    
    return True

def test_javascript_functions_in_html():
    """Test if JavaScript functions are properly defined in the HTML"""
    print("\n🔧 Testing JavaScript Functions in HTML")
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
    global_assignments_found = 'window.updateGroupKmTraveled = updateGroupKmTraveled' in content
    
    print(f"🔍 updateGroupKmTraveled function found: {km_function_found}")
    print(f"🔍 updateGroupHours function found: {hours_function_found}")
    print(f"🔍 Global assignments found: {global_assignments_found}")
    
    if km_function_found and hours_function_found and global_assignments_found:
        print("✅ All JavaScript functions are properly defined")
        
        # Check for syntax errors
        if 'window.updateGroupKmTraveled = updateGroupKmTraveled;' in content:
            print("✅ Global assignments have proper semicolons")
        else:
            print("⚠️ Global assignments may have syntax issues")
            
        return True
    else:
        print("❌ JavaScript functions are missing or incomplete")
        return False

def test_input_field_attributes():
    """Test if input fields have the correct attributes"""
    print("\n🔍 Testing Input Field Attributes")
    print("=" * 40)
    
    # Read the HTML file
    html_file = 'main/templates/main/shipment_list_clean.html'
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for KM input fields
    km_inputs = re.findall(r'<input[^>]*class="[^"]*group-km-input[^"]*"[^>]*>', content)
    print(f"🔍 Found {len(km_inputs)} KM input fields in HTML")
    
    # Check for Hours input fields
    hours_inputs = re.findall(r'<input[^>]*class="[^"]*group-hours-input[^"]*"[^>]*>', content)
    print(f"🔍 Found {len(hours_inputs)} Hours input fields in HTML")
    
    # Check for event handlers
    onchange_handlers = content.count('onchange="updateGroupKmTraveled(this)"')
    onblur_handlers = content.count('onblur="updateGroupKmTraveled(this)"')
    
    print(f"🔍 KM onchange handlers: {onchange_handlers}")
    print(f"🔍 KM onblur handlers: {onblur_handlers}")
    
    if km_inputs and hours_inputs and onchange_handlers and onblur_handlers:
        print("✅ Input fields have correct attributes and event handlers")
        return True
    else:
        print("❌ Input fields may be missing attributes or event handlers")
        return False

def main():
    """Main test function"""
    print("🧪 KM and Hours Input Button Test")
    print("=" * 60)
    
    # Test JavaScript functions
    js_ok = test_javascript_functions_in_html()
    
    # Test input field attributes
    attributes_ok = test_input_field_attributes()
    
    # Test actual input simulation
    simulation_ok = test_km_hours_input_simulation()
    
    print("\n📋 Test Summary")
    print("=" * 30)
    print(f"🔧 JavaScript Functions: {'✅ PASS' if js_ok else '❌ FAIL'}")
    print(f"🔍 Input Attributes: {'✅ PASS' if attributes_ok else '❌ FAIL'}")
    print(f"🎯 Input Simulation: {'✅ PASS' if simulation_ok else '❌ FAIL'}")
    
    if js_ok and attributes_ok and simulation_ok:
        print("\n🎉 All tests passed! KM and Hours input functionality should work.")
        print("\n📝 Manual Testing Instructions:")
        print("1. Open the inspections page in your browser")
        print("2. Look for KM and Hours input fields")
        print("3. Change a value (e.g., from 30 to 40)")
        print("4. Click away from the field or press Tab")
        print("5. Check browser console for update logs")
        print("6. Refresh page to verify value persists")
    else:
        print("\n⚠️ Some tests failed. Check the issues above.")
    
    return js_ok and attributes_ok and simulation_ok

if __name__ == '__main__':
    main()
