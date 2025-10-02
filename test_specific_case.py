#!/usr/bin/env python3
"""
Test script for the specific case: Boxer Superstore - Kwamashu 2
"""

import requests
import json
import re

def test_specific_group():
    """Test the specific group that's not working"""
    
    print("🧪 Testing Specific Case: Boxer Superstore - Kwamashu 2")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    # First, get the main page to establish session and get CSRF token
    print("1. Getting CSRF token...")
    try:
        response = session.get(f"{base_url}/")
        csrf_token = None
        
        # Extract CSRF token from the page
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"   CSRF token found: {csrf_token[:20]}...")
        else:
            print("   ❌ CSRF token not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error getting CSRF token: {e}")
        return False
    
    # Test different group ID formats for "Boxer Superstore - Kwamashu 2"
    print("\n2. Testing different group ID formats...")
    
    # The client name is "Boxer Superstore - Kwamashu 2"
    # Date is 09/26/25 which should be 20250926
    client_name_variations = [
        "Boxer_Superstore_-_Kwamashu_2",
        "Boxer_Superstore___Kwamashu_2", 
        "Boxer_Superstore_Kwamashu_2",
        "Boxer_Superstore_Kwamashu_2"
    ]
    
    date_str = "20250926"  # 09/26/25 = 2025-09-26
    
    for client_name in client_name_variations:
        test_group_id = f"{client_name}_{date_str}"
        print(f"\n   Testing Group ID: {test_group_id}")
        
        # Test KM update
        km_data = {
            'group_id': test_group_id,
            'km_traveled': '40.0',
            'csrfmiddlewaretoken': csrf_token
        }
        
        try:
            response = session.post(f"{base_url}/update-group-km-traveled/", data=km_data)
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    print(f"   Response: {response_data}")
                    if response_data.get('success'):
                        print(f"   ✅ SUCCESS with Group ID: {test_group_id}")
                        return True
                    else:
                        print(f"   ❌ Failed: {response_data.get('error')}")
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response")
            else:
                print(f"   ❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return False

def check_javascript_issues():
    """Check for potential JavaScript issues"""
    
    print("\n🔍 POTENTIAL JAVASCRIPT ISSUES")
    print("=" * 40)
    
    print("\n1. Check if the input field has the correct attributes:")
    print("   - data-group-id should be set")
    print("   - onchange and onblur events should be attached")
    print("   - The input should have class 'group-km-input'")
    
    print("\n2. Check browser console for errors:")
    print("   - Open F12 → Console tab")
    print("   - Look for any red error messages")
    print("   - Check if 'updateGroupKmTraveled' function is defined")
    
    print("\n3. Check if the event is firing:")
    print("   - Enter a value in the KM field")
    print("   - Click away from the field")
    print("   - Look for console log: 'Updating Group KM - Group ID: ...'")
    print("   - If no log appears, the event isn't firing")
    
    print("\n4. Check the Group ID format:")
    print("   - The Group ID should be: 'ClientName_Date'")
    print("   - For 'Boxer Superstore - Kwamashu 2' on 09/26/25")
    print("   - It should be: 'Boxer_Superstore_-_Kwamashu_2_20250926'")
    print("   - Or: 'Boxer_Superstore___Kwamashu_2_20250926'")

def provide_debugging_steps():
    """Provide specific debugging steps"""
    
    print("\n🛠️  SPECIFIC DEBUGGING STEPS")
    print("=" * 40)
    
    print("\n1. Open browser console (F12)")
    print("2. Go to the shipment list page")
    print("3. Find the KM input field for 'Boxer Superstore - Kwamashu 2'")
    print("4. Right-click on the input field and select 'Inspect Element'")
    print("5. Check the HTML attributes:")
    print("   - Look for: data-group-id='...'")
    print("   - Look for: onchange='updateGroupKmTraveled(this)'")
    print("   - Look for: onblur='updateGroupKmTraveled(this)'")
    
    print("\n6. In the console, type:")
    print("   document.querySelector('.group-km-input').getAttribute('data-group-id')")
    print("   This should show the group ID")
    
    print("\n7. Test the function manually:")
    print("   const input = document.querySelector('.group-km-input');")
    print("   updateGroupKmTraveled(input);")
    print("   This should trigger the update function")
    
    print("\n8. Check if CSRF token is available:")
    print("   getCSRFToken()")
    print("   This should return a token string")

def main():
    """Main function"""
    
    print("🚀 Specific Case Testing")
    print("=" * 60)
    
    # Test the specific group
    success = test_specific_group()
    
    # Provide debugging information
    check_javascript_issues()
    provide_debugging_steps()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Found working Group ID format!")
    else:
        print("❌ Need to check JavaScript and HTML attributes")
    
    print("\n📋 NEXT STEPS:")
    print("1. Follow the debugging steps above")
    print("2. Check the browser console for errors")
    print("3. Verify the input field attributes")
    print("4. Test the JavaScript function manually")
    print("=" * 60)

if __name__ == "__main__":
    main()
