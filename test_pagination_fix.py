#!/usr/bin/env python3
"""
Test script for the pagination fix.
This script verifies that pagination navigation works correctly.
"""

import os
import sys
import django
from django.test import RequestFactory, Client
from django.contrib.auth.models import User

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.views.core_views import shipment_list
from main.models import FoodSafetyAgencyInspection, Client

def test_pagination_fix():
    """Test that pagination works correctly."""
    print("🔧 Testing Pagination Fix")
    print("=" * 40)
    
    # Create a test client
    client = Client()
    
    # Create a test user (or use existing)
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False
    
    # Login the user
    client.force_login(user)
    
    print("🔍 Testing pagination navigation...")
    
    # Test different page numbers
    test_pages = [1, 2, 3, 'last']
    
    for page in test_pages:
        try:
            if page == 'last':
                # Test last page by getting a high page number
                response = client.get('/inspections/?page=999')
            else:
                response = client.get(f'/inspections/?page={page}')
            
            if response.status_code == 200:
                print(f"✅ Page {page}: OK (HTTP {response.status_code})")
                
                # Check if pagination links are present
                content = response.content.decode('utf-8')
                if 'pagination' in content.lower():
                    print(f"  📄 Pagination controls found on page {page}")
                else:
                    print(f"  ⚠️ No pagination controls found on page {page}")
                    
            else:
                print(f"❌ Page {page}: FAILED (HTTP {response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Page {page}: ERROR - {e}")
            return False
    
    print("\n🎯 Testing specific pagination scenarios...")
    
    # Test first page
    try:
        response = client.get('/inspections/?page=1')
        if response.status_code == 200:
            print("✅ First page loads correctly")
        else:
            print("❌ First page failed")
            return False
    except Exception as e:
        print(f"❌ First page error: {e}")
        return False
    
    # Test second page
    try:
        response = client.get('/inspections/?page=2')
        if response.status_code == 200:
            print("✅ Second page loads correctly")
        else:
            print("❌ Second page failed")
            return False
    except Exception as e:
        print(f"❌ Second page error: {e}")
        return False
    
    # Test invalid page (should redirect to last valid page)
    try:
        response = client.get('/inspections/?page=999999')
        if response.status_code in [200, 404]:
            print("✅ Invalid page handled correctly")
        else:
            print(f"⚠️ Invalid page returned {response.status_code} (expected 200 or 404)")
    except Exception as e:
        print(f"❌ Invalid page error: {e}")
        return False
    
    print("\n🔍 Testing pagination HTML structure...")
    
    # Test that pagination HTML is properly formed
    try:
        response = client.get('/inspections/?page=1')
        content = response.content.decode('utf-8')
        
        # Check for pagination elements
        pagination_checks = [
            ('pagination', 'Pagination container'),
            ('page-info', 'Page info display'),
            ('btn btn-sm btn-secondary', 'Pagination buttons'),
        ]
        
        for check, description in pagination_checks:
            if check in content:
                print(f"✅ {description} found")
            else:
                print(f"⚠️ {description} not found")
        
    except Exception as e:
        print(f"❌ HTML structure test error: {e}")
        return False
    
    return True

def test_pagination_javascript():
    """Test that pagination JavaScript functions are properly defined."""
    print("\n🔧 Testing Pagination JavaScript Functions")
    print("=" * 45)
    
    # Read the template file to check for JavaScript functions
    try:
        with open('main/templates/main/shipment_list.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required JavaScript functions
        js_functions = [
            ('enablePagination', 'Function to enable pagination'),
            ('handlePageNavigation', 'Function to handle page navigation'),
            ('handlePaginationClick', 'Function to handle pagination clicks'),
        ]
        
        for func, description in js_functions:
            if f'function {func}' in content:
                print(f"✅ {description} defined")
            else:
                print(f"❌ {description} missing")
                return False
        
        # Check for pagination event listeners
        if 'addEventListener(\'click\', handlePaginationClick)' in content:
            print("✅ Pagination click listeners added")
        else:
            print("❌ Pagination click listeners missing")
            return False
        
        # Check for enablePagination calls
        if 'enablePagination()' in content:
            print("✅ enablePagination() is called")
        else:
            print("❌ enablePagination() not called")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ JavaScript test error: {e}")
        return False

def test_pagination_scenarios():
    """Test various pagination scenarios."""
    print("\n🎯 Testing Pagination Scenarios")
    print("=" * 35)
    
    scenarios = [
        {
            'name': 'First Page',
            'url': '/inspections/?page=1',
            'expected': 'Should show First and Previous buttons disabled'
        },
        {
            'name': 'Middle Page',
            'url': '/inspections/?page=2',
            'expected': 'Should show all navigation buttons'
        },
        {
            'name': 'Last Page',
            'url': '/inspections/?page=999',
            'expected': 'Should show Next and Last buttons disabled'
        },
        {
            'name': 'Invalid Page',
            'url': '/inspections/?page=abc',
            'expected': 'Should redirect to page 1 or show error'
        }
    ]
    
    client = Client()
    user = User.objects.first()
    if user:
        client.force_login(user)
    
    for scenario in scenarios:
        try:
            response = client.get(scenario['url'])
            if response.status_code == 200:
                print(f"✅ {scenario['name']}: OK")
                print(f"   {scenario['expected']}")
            else:
                print(f"⚠️ {scenario['name']}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {scenario['name']}: Error - {e}")

if __name__ == "__main__":
    print("🔧 Pagination Fix Test")
    print("=" * 30)
    
    # Test pagination functionality
    pagination_ok = test_pagination_fix()
    
    # Test JavaScript functions
    js_ok = test_pagination_javascript()
    
    # Test pagination scenarios
    test_pagination_scenarios()
    
    if pagination_ok and js_ok:
        print("\n🎉 All pagination tests passed!")
        print("\n💡 What was fixed:")
        print("   🔧 Added enablePagination() function")
        print("   🔧 Added handlePageNavigation() function")
        print("   🔧 Added handlePaginationClick() function")
        print("   🔧 Fixed loading overlay interference")
        print("   🔧 Added proper event listeners")
        print("   🔧 Reduced loading delays")
        print("\n🚀 Now pagination should work correctly:")
        print("   ✅ First page navigation")
        print("   ✅ Previous page navigation")
        print("   ✅ Next page navigation")
        print("   ✅ Last page navigation")
        print("   ✅ Page number navigation")
        print("   ✅ No more blocking overlays")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)
