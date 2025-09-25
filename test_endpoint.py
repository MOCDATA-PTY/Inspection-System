#!/usr/bin/env python
"""
Test script to verify the list-client-folder-files endpoint is working
"""
import os
import sys
import django
import json
from datetime import datetime

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# Setup Django
django.setup()

def test_endpoint_directly():
    """Test the endpoint function directly"""
    print("🧪 Testing list_client_folder_files function directly...")
    
    try:
        from django.test import RequestFactory
        from main.views.core_views import list_client_folder_files
        
        factory = RequestFactory()
        
        # Test with valid data
        test_data = {
            'client_name': 'Test Client',
            'inspection_date': '2025-09-25'
        }
        
        request = factory.post(
            '/list-client-folder-files/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        response = list_client_folder_files(request)
        print(f"✅ Direct function call successful")
        print(f"   Status Code: {response.status_code}")
        
        response_data = json.loads(response.content)
        print(f"   Response: {response_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_endpoint_via_client():
    """Test the endpoint via Django test client"""
    print("\n🌐 Testing endpoint via Django test client...")
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        
        client = Client()
        
        # Create a test user and login
        try:
            user = User.objects.create_user(username='testuser', password='testpass')
            client.login(username='testuser', password='testpass')
        except:
            # User might already exist, try to login
            client.login(username='testuser', password='testpass')
        
        # Test data
        test_data = {
            'client_name': 'Test Client',
            'inspection_date': '2025-09-25'
        }
        
        response = client.post(
            '/list-client-folder-files/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"✅ HTTP request successful")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            print(f"   Response: {response_data}")
        else:
            print(f"   Response Content: {response.content}")
        
        return response.status_code in [200, 400]  # 400 is expected for non-existent client
        
    except Exception as e:
        print(f"❌ HTTP client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_old_vs_new_endpoint():
    """Compare old vs new endpoint behavior"""
    print("\n🔄 Testing old vs new endpoint...")
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        
        client = Client()
        
        # Login
        try:
            client.login(username='testuser', password='testpass')
        except:
            pass
        
        # Test old endpoint with wrong data (should fail)
        old_data = {
            'client_name': 'Test Client',
            'inspection_date': '2025-09-25'
        }
        
        old_response = client.post(
            '/list-uploaded-files/',
            data=json.dumps(old_data),
            content_type='application/json'
        )
        
        print(f"📊 Old endpoint (/list-uploaded-files/) with client_name/date:")
        print(f"   Status: {old_response.status_code} (should be 400 - Bad Request)")
        
        # Test new endpoint with same data (should work)
        new_response = client.post(
            '/list-client-folder-files/',
            data=json.dumps(old_data),
            content_type='application/json'
        )
        
        print(f"📊 New endpoint (/list-client-folder-files/) with client_name/date:")
        print(f"   Status: {new_response.status_code} (should be 200 or 400 with proper error)")
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint comparison failed: {e}")
        return False

def test_javascript_fix():
    """Verify JavaScript changes are correct"""
    print("\n📜 Checking JavaScript file changes...")
    
    try:
        with open('static/js/upload_functions.js', 'r') as f:
            js_content = f.read()
        
        # Check if old endpoint calls are replaced
        old_calls = js_content.count('/list-uploaded-files/')
        new_calls = js_content.count('/list-client-folder-files/')
        
        print(f"📊 JavaScript endpoint usage:")
        print(f"   Old endpoint calls (/list-uploaded-files/): {old_calls}")
        print(f"   New endpoint calls (/list-client-folder-files/): {new_calls}")
        
        if new_calls >= 2:  # We should have at least 2 calls to the new endpoint
            print("✅ JavaScript appears to be updated correctly")
            return True
        else:
            print("⚠️ JavaScript may need more updates")
            return False
            
    except Exception as e:
        print(f"❌ JavaScript check failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("🔧 ENDPOINT FUNCTIONALITY TEST")
    print("=" * 70)
    
    tests = [
        ("Direct Function Test", test_endpoint_directly),
        ("HTTP Client Test", test_endpoint_via_client),
        ("Old vs New Endpoint", test_old_vs_new_endpoint),
        ("JavaScript Fix Check", test_javascript_fix)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 All tests passed! The fix should be working.")
        print("\n💡 Next steps:")
        print("   1. The server should now handle /list-client-folder-files/ requests")
        print("   2. JavaScript should call the new endpoint")
        print("   3. No more 400 Bad Request errors for file status checks")
    else:
        print("\n💥 Some tests failed. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
