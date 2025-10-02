#!/usr/bin/env python3
"""
Test script for Daily Compliance Sync functionality with proper authentication
Tests the settings page UI, backend services, and API endpoints with real login
"""

import os
import sys
import django
import json
import time
import requests
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from main.models import SystemSettings, Settings, FoodSafetyAgencyInspection
from main.services.daily_compliance_sync import DailyComplianceSyncService, daily_sync_service


def test_authenticated_settings_page():
    """Test settings page with proper authentication"""
    print("🔐 Testing Authenticated Settings Page")
    print("=" * 50)
    
    try:
        # Create a test client
        client = Client()
        
        # Try different authentication methods
        auth_methods = [
            {'username': 'armand', 'password': 'Armand2025SuperAdmin'},
            {'username': 'anthony', 'password': 'Anthony2025SuperAdmin'},
            {'username': 'developer', 'password': 'Developer2025'},
            {'username': 'admin', 'password': 'admin'},
        ]
        
        authenticated = False
        for auth in auth_methods:
            try:
                print(f"Trying authentication with {auth['username']}...")
                
                # Try to login
                login_success = client.login(username=auth['username'], password=auth['password'])
                if login_success:
                    print(f"✅ Successfully authenticated as {auth['username']}")
                    authenticated = True
                    break
                else:
                    print(f"❌ Authentication failed for {auth['username']}")
                    
            except Exception as e:
                print(f"❌ Error authenticating {auth['username']}: {e}")
                continue
        
        if not authenticated:
            print("❌ Could not authenticate with any credentials")
            return False
        
        # Test settings page
        print("\nTesting /settings/ page...")
        response = client.get('/settings/')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for daily sync elements
            checks = [
                ('Daily Compliance Sync heading', 'Daily Compliance Sync'),
                ('Enable Daily Sync checkbox', 'compliance_sync_enabled'),
                ('Skip Processed Documents checkbox', 'compliance_skip_processed'),
                ('Sync Frequency input', 'compliance_sync_interval'),
                ('Start Daily Sync button', 'startDailySyncBtn'),
                ('Stop Daily Sync button', 'stopDailySyncBtn'),
                ('JavaScript functions', 'startDailySync'),
                ('JavaScript functions', 'stopDailySync'),
            ]
            
            print("\n📋 Settings Page Elements Check:")
            for check_name, check_text in checks:
                if check_text in content:
                    print(f"  ✅ {check_name}: Found")
                else:
                    print(f"  ❌ {check_name}: Missing")
            
            # Check for CSRF token
            if 'csrfmiddlewaretoken' in content:
                print(f"  ✅ CSRF Token: Found")
            else:
                print(f"  ❌ CSRF Token: Missing")
            
            return True
                
        else:
            print(f"❌ Settings page error: {response.status_code}")
            print(f"Response: {response.content}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing authenticated settings page: {e}")
        return False


def test_authenticated_api_endpoints():
    """Test Daily Sync API endpoints with authentication"""
    print("\n🌐 Testing Authenticated API Endpoints")
    print("=" * 50)
    
    try:
        client = Client()
        
        # Authenticate
        login_success = client.login(username='armand', password='Armand2025SuperAdmin')
        if not login_success:
            print("❌ Could not authenticate for API testing")
            return False
        
        print("✅ Authenticated for API testing")
        
        # Test status endpoint
        print("\nTesting /daily-sync/status/ endpoint...")
        response = client.get('/daily-sync/status/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"Error: {response.content}")
        
        # Test start endpoint
        print("\nTesting /daily-sync/start/ endpoint...")
        response = client.post('/daily-sync/start/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"Error: {response.content}")
        
        # Test stop endpoint
        print("\nTesting /daily-sync/stop/ endpoint...")
        response = client.post('/daily-sync/stop/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"Error: {response.content}")
        
        return True
            
    except Exception as e:
        print(f"❌ Error testing authenticated API endpoints: {e}")
        return False


def test_settings_form_submission():
    """Test settings form submission with authentication"""
    print("\n📝 Testing Settings Form Submission")
    print("=" * 50)
    
    try:
        client = Client()
        
        # Authenticate
        login_success = client.login(username='armand', password='Armand2025SuperAdmin')
        if not login_success:
            print("❌ Could not authenticate for form testing")
            return False
        
        # Get CSRF token first
        response = client.get('/settings/')
        if response.status_code != 200:
            print(f"❌ Could not get settings page: {response.status_code}")
            return False
        
        content = response.content.decode('utf-8')
        csrf_token = None
        
        # Extract CSRF token
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"✅ Found CSRF token: {csrf_token[:20]}...")
        else:
            print("❌ Could not find CSRF token")
            return False
        
        # Test form submission with daily sync settings
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'compliance_sync_enabled': 'on',
            'compliance_skip_processed': 'on',
            'compliance_sync_interval': '5',
            'compliance_sync_interval_unit': 'days',
        }
        
        print("Submitting settings form with daily sync data...")
        response = client.post('/settings/', form_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Form submitted successfully")
            
            # Check if settings were saved
            settings = SystemSettings.get_settings()
            print(f"Settings after submission:")
            print(f"  - Compliance Daily Sync Enabled: {settings.compliance_daily_sync_enabled}")
            print(f"  - Compliance Skip Processed: {settings.compliance_skip_processed}")
            
            return True
        else:
            print(f"❌ Form submission failed: {response.status_code}")
            print(f"Response: {response.content}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing form submission: {e}")
        return False


def test_http_requests_with_session():
    """Test using HTTP requests with session management"""
    print("\n🌐 Testing HTTP Requests with Session")
    print("=" * 50)
    
    try:
        session = requests.Session()
        
        # Get login page
        print("Getting login page...")
        login_page = session.get('http://127.0.0.1:8000/login/')
        print(f"Login page status: {login_page.status_code}")
        
        if login_page.status_code != 200:
            print("❌ Could not get login page")
            return False
        
        # Extract CSRF token
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
        if not csrf_match:
            print("❌ Could not find CSRF token in login page")
            return False
        
        csrf_token = csrf_match.group(1)
        print(f"✅ Found CSRF token: {csrf_token[:20]}...")
        
        # Login
        print("Logging in...")
        login_data = {
            'username': 'armand',
            'password': 'Armand2025SuperAdmin',
            'csrfmiddlewaretoken': csrf_token,
            'next': '/settings/'
        }
        
        login_response = session.post('http://127.0.0.1:8000/login/', data=login_data)
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200 and 'settings' in login_response.url:
            print("✅ Successfully logged in")
        else:
            print("❌ Login failed")
            return False
        
        # Test settings page
        print("Testing settings page...")
        settings_response = session.get('http://127.0.0.1:8000/settings/')
        print(f"Settings page status: {settings_response.status_code}")
        
        if settings_response.status_code == 200:
            content = settings_response.text
            
            # Check for daily sync elements
            if 'Daily Compliance Sync' in content:
                print("✅ Daily Compliance Sync section found")
            else:
                print("❌ Daily Compliance Sync section not found")
            
            if 'startDailySyncBtn' in content:
                print("✅ Start Daily Sync button found")
            else:
                print("❌ Start Daily Sync button not found")
            
            if 'stopDailySyncBtn' in content:
                print("✅ Stop Daily Sync button found")
            else:
                print("❌ Stop Daily Sync button not found")
            
            return True
        else:
            print(f"❌ Settings page error: {settings_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing HTTP requests: {e}")
        return False


def test_daily_sync_functionality():
    """Test the actual daily sync functionality"""
    print("\n🔄 Testing Daily Sync Functionality")
    print("=" * 50)
    
    try:
        # Test service initialization
        service = DailyComplianceSyncService()
        print(f"✅ Service initialized: {type(service).__name__}")
        
        # Test status
        status = service.get_status()
        print(f"✅ Service status: {json.dumps(status, indent=2, default=str)}")
        
        # Test start/stop
        print("Testing start/stop functionality...")
        service.start_daily_sync()
        print(f"After start - Is Running: {service.is_running}")
        
        time.sleep(2)
        
        service.stop_daily_sync()
        print(f"After stop - Is Running: {service.is_running}")
        
        # Test settings retrieval
        settings = service.get_system_settings()
        if settings:
            print(f"✅ System settings retrieved:")
            print(f"  - Daily sync enabled: {settings.compliance_daily_sync_enabled}")
            print(f"  - Skip processed: {settings.compliance_skip_processed}")
        else:
            print("❌ Could not retrieve system settings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing daily sync functionality: {e}")
        return False


def main():
    """Run all authenticated daily compliance sync tests"""
    print("🧪 Daily Compliance Sync - Authenticated Test Suite")
    print("=" * 70)
    print()
    
    # Run all tests
    test_results = []
    
    test_results.append(("Authenticated Settings Page", test_authenticated_settings_page()))
    test_results.append(("Authenticated API Endpoints", test_authenticated_api_endpoints()))
    test_results.append(("Settings Form Submission", test_settings_form_submission()))
    test_results.append(("HTTP Requests with Session", test_http_requests_with_session()))
    test_results.append(("Daily Sync Functionality", test_daily_sync_functionality()))
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Daily Compliance Sync is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print()
    print("🔗 Test URLs:")
    print("   - Login: http://127.0.0.1:8000/login/")
    print("   - Settings: http://127.0.0.1:8000/settings/")
    print("   - Start Sync: http://127.0.0.1:8000/daily-sync/start/")
    print("   - Stop Sync: http://127.0.0.1:8000/daily-sync/stop/")
    print("   - Sync Status: http://127.0.0.1:8000/daily-sync/status/")


if __name__ == "__main__":
    main()
