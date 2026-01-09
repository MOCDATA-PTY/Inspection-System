#!/usr/bin/env python3
"""
Test with the correct group ID format based on sanitize_group_id filter
"""

import requests
import json
import re

def test_correct_group_id():
    """Test with the correct group ID format"""
    
    print("🧪 Testing with Correct Group ID Format")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    # Get CSRF token
    print("1. Getting CSRF token...")
    try:
        response = session.get(f"{base_url}/")
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"   CSRF token: {csrf_token[:20]}...")
        else:
            print("   ❌ CSRF token not found")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test the correct group ID format
    # "Boxer Superstore - Kwamashu 2" becomes "Boxer_Superstore_Kwamashu_2"
    # Date: 09/26/25 = 20250926
    correct_group_id = "Boxer_Superstore_Kwamashu_2_20250926"
    
    print(f"\n2. Testing with correct Group ID: {correct_group_id}")
    
    # Test KM update
    km_data = {
        'group_id': correct_group_id,
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
                    print(f"   ✅ SUCCESS! KM updated to 40.0")
                    return True
                else:
                    print(f"   ❌ Failed: {response_data.get('error')}")
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON response")
                print(f"   Response text: {response.text[:200]}...")
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            print(f"   Response text: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

def show_debugging_instructions():
    """Show specific debugging instructions"""
    
    print("\n🔍 SPECIFIC DEBUGGING INSTRUCTIONS")
    print("=" * 50)
    
    print("\n1. Open browser console (F12)")
    print("2. Go to the shipment list page")
    print("3. Find the KM input field for 'Boxer Superstore - Kwamashu 2'")
    print("4. Right-click on the input field and select 'Inspect Element'")
    print("5. Look for the data-group-id attribute")
    print("6. It should be: 'Boxer_Superstore_Kwamashu_2_20250926'")
    
    print("\n7. In the console, run:")
    print("   const input = document.querySelector('.group-km-input');")
    print("   console.log('Group ID:', input.getAttribute('data-group-id'));")
    print("   console.log('Current value:', input.value);")
    
    print("\n8. Test the function:")
    print("   input.value = '40';")
    print("   updateGroupKmTraveled(input);")
    
    print("\n9. Check the console for logs:")
    print("   - 'Updating Group KM - Group ID: Boxer_Superstore_Kwamashu_2_20250926 Value: 40'")
    print("   - 'CSRF Token: [token]'")
    print("   - 'KM Response status: 200'")
    print("   - 'KM Response data: {success: true}'")
    
    print("\n10. If you see errors, check:")
    print("    - Is the input field found?")
    print("    - Is the group ID correct?")
    print("    - Is the function defined?")
    print("    - Is the CSRF token valid?")

def main():
    """Main function"""
    
    print("🚀 Correct Group ID Test")
    print("=" * 50)
    
    # Test with correct group ID
    success = test_correct_group_id()
    
    # Show debugging instructions
    show_debugging_instructions()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Backend is working! The issue is likely in the frontend.")
    else:
        print("❌ Backend issue detected.")
    
    print("\n📋 NEXT STEPS:")
    print("1. Follow the debugging instructions above")
    print("2. Check the browser console for errors")
    print("3. Verify the input field attributes")
    print("4. Test the JavaScript function manually")
    print("=" * 50)

if __name__ == "__main__":
    main()
