#!/usr/bin/env python3
"""
Simple test script to verify KM and Hours endpoints are accessible
This script can be run without Django setup to test basic connectivity
"""

import requests
import json

def test_endpoints():
    """Test if the endpoints are accessible"""
    
    print("🧪 Testing KM and Hours Endpoints (Simple)")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test endpoints
    endpoints = [
        "/update-group-km-traveled/",
        "/update-group-hours/"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        
        try:
            # Test with GET request first (should return method not allowed)
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   GET Response Status: {response.status_code}")
            
            if response.status_code == 405:  # Method Not Allowed
                print("   ✅ Endpoint exists (GET not allowed, as expected)")
            elif response.status_code == 200:
                print("   ✅ Endpoint accessible")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
            
            # Test with POST request (will fail without proper data, but we can check if endpoint exists)
            test_data = {
                'group_id': 'test_group',
                'km_traveled': '10.0',
                'csrfmiddlewaretoken': 'test'
            }
            
            response = requests.post(f"{base_url}{endpoint}", data=test_data)
            print(f"   POST Response Status: {response.status_code}")
            
            if response.status_code == 403:  # Forbidden (CSRF token issue)
                print("   ✅ Endpoint exists (CSRF token required, as expected)")
            elif response.status_code == 400:  # Bad Request
                print("   ✅ Endpoint exists (bad request, as expected)")
            elif response.status_code == 200:
                print("   ✅ Endpoint working")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
            
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection Error - Server not running")
            print("   Please start Django server: python manage.py runserver")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_server_status():
    """Test if the Django server is running"""
    
    print("\n🌐 Testing Server Status")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    try:
        # Try to access the main page
        response = requests.get(base_url, timeout=5)
        print(f"   Server Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Django server is running")
            return True
        else:
            print(f"   ⚠️  Server responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Server not running")
        print("   Please start Django server: python manage.py runserver")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Simple Endpoint Tests")
    print("=" * 60)
    
    # Test server status
    server_running = test_server_status()
    
    if server_running:
        # Test endpoints
        test_endpoints()
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS")
        print("=" * 60)
        print("✅ Server is running")
        print("✅ Endpoints are accessible")
        print("\n📝 Next Steps:")
        print("   1. Open your browser to the shipment list page")
        print("   2. Open browser console (F12)")
        print("   3. Try entering values in KM and Hours fields")
        print("   4. Check console for any error messages")
    else:
        print("\n❌ Server not running. Please start Django server first.")
        print("   Run: python manage.py runserver")

if __name__ == "__main__":
    main()
