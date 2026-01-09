#!/usr/bin/env python3
"""
Debug script to test the actual endpoint behavior
"""

import requests
import json

def test_endpoint_with_session():
    """Test endpoint with a proper session"""
    
    print("🧪 Testing KM and Hours Endpoints with Session")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # First, try to get the main page to establish a session
    print("1. Establishing session...")
    try:
        response = session.get(f"{base_url}/")
        print(f"   Main page status: {response.status_code}")
        
        # Look for CSRF token in the response
        csrf_token = None
        if 'csrfmiddlewaretoken' in response.text:
            # Extract CSRF token from the page
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"   Found CSRF token: {csrf_token[:20]}...")
            else:
                print("   ❌ CSRF token not found in page")
        else:
            print("   ❌ No CSRF token field found")
            
    except Exception as e:
        print(f"   ❌ Error establishing session: {e}")
        return False
    
    # Test with a real group ID from your data
    test_group_id = "Boxer_Superstore___Kwamashu_2_20250926"  # From the test results
    
    # Test KM update
    print(f"\n2. Testing KM update with group ID: {test_group_id}")
    
    km_data = {
        'group_id': test_group_id,
        'km_traveled': '40.0'
    }
    
    if csrf_token:
        km_data['csrfmiddlewaretoken'] = csrf_token
    
    try:
        response = session.post(f"{base_url}/update-group-km-traveled/", data=km_data)
        print(f"   Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"   Response JSON: {response_data}")
                if response_data.get('success'):
                    print("   ✅ KM update successful")
                else:
                    print(f"   ❌ KM update failed: {response_data.get('error')}")
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON response: {response.text}")
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            print(f"   Response text: {response.text[:500]}...")
            
    except Exception as e:
        print(f"   ❌ Error testing KM update: {e}")
    
    # Test Hours update
    print(f"\n3. Testing Hours update with group ID: {test_group_id}")
    
    hours_data = {
        'group_id': test_group_id,
        'hours': '5.0'
    }
    
    if csrf_token:
        hours_data['csrfmiddlewaretoken'] = csrf_token
    
    try:
        response = session.post(f"{base_url}/update-group-hours/", data=hours_data)
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"   Response JSON: {response_data}")
                if response_data.get('success'):
                    print("   ✅ Hours update successful")
                else:
                    print(f"   ❌ Hours update failed: {response_data.get('error')}")
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON response: {response.text}")
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            print(f"   Response text: {response.text[:500]}...")
            
    except Exception as e:
        print(f"   ❌ Error testing Hours update: {e}")
    
    return True

def check_browser_console_instructions():
    """Provide instructions for checking browser console"""
    
    print("\n🔍 BROWSER CONSOLE DEBUGGING INSTRUCTIONS")
    print("=" * 60)
    
    print("\n1. Open your browser to the shipment list page")
    print("2. Press F12 to open Developer Tools")
    print("3. Go to the Console tab")
    print("4. Clear the console (click the clear button or press Ctrl+L)")
    print("5. Find a KM or Hours input field")
    print("6. Enter a value (e.g., 40)")
    print("7. Click away from the field")
    print("8. Look for these console messages:")
    print("   - 'Updating Group KM - Group ID: ... Value: ...'")
    print("   - 'CSRF Token: ...'")
    print("   - 'KM Response status: ...'")
    print("   - 'KM Response data: ...'")
    
    print("\n9. If you see errors, check the Network tab:")
    print("   - Go to Network tab in Developer Tools")
    print("   - Clear the network log")
    print("   - Enter a value and click away")
    print("   - Look for requests to '/update-group-km-traveled/' or '/update-group-hours/'")
    print("   - Click on the request to see details")
    print("   - Check the Request Headers and Response")
    
    print("\n10. Common issues to look for:")
    print("    - 403 Forbidden: CSRF token issue")
    print("    - 404 Not Found: Endpoint not found")
    print("    - 500 Internal Server Error: Backend error")
    print("    - No request at all: JavaScript error")

def main():
    """Main function"""
    
    print("🚀 Endpoint Debug Tests")
    print("=" * 60)
    
    # Test endpoint with session
    test_endpoint_with_session()
    
    # Provide browser debugging instructions
    check_browser_console_instructions()
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("1. Follow the browser console debugging instructions above")
    print("2. Check if the JavaScript functions are being called")
    print("3. Verify the network requests are being made")
    print("4. Check the server logs for any backend errors")
    print("=" * 60)

if __name__ == "__main__":
    main()
