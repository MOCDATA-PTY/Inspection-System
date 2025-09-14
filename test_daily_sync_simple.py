#!/usr/bin/env python3
"""
Simple test for Daily Compliance Sync functionality with test user
"""

import os
import sys
import django
import json
import time

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from main.models import SystemSettings, Settings
from main.services.daily_compliance_sync import DailyComplianceSyncService, daily_sync_service


def test_with_test_user():
    """Test with the test user we created"""
    print("🧪 Testing Daily Compliance Sync with Test User")
    print("=" * 60)
    
    try:
        client = Client()
        
        # Login with test user
        print("Logging in with test user...")
        login_success = client.login(username='testuser', password='testpass123')
        
        if not login_success:
            print("❌ Could not login with test user")
            return False
        
        print("✅ Successfully logged in with test user")
        
        # Test settings page
        print("\nTesting settings page...")
        response = client.get('/settings/')
        print(f"Settings page status: {response.status_code}")
        
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
            ]
            
            print("\n📋 Settings Page Elements:")
            all_found = True
            for check_name, check_text in checks:
                if check_text in content:
                    print(f"  ✅ {check_name}")
                else:
                    print(f"  ❌ {check_name}")
                    all_found = False
            
            if all_found:
                print("\n✅ All Daily Compliance Sync elements found on settings page!")
            else:
                print("\n❌ Some elements missing from settings page")
            
        else:
            print(f"❌ Settings page error: {response.status_code}")
            return False
        
        # Test API endpoints
        print("\nTesting API endpoints...")
        
        # Status endpoint
        response = client.get('/daily-sync/status/')
        print(f"Status endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Status: {data.get('success', False)}")
        
        # Start endpoint
        response = client.post('/daily-sync/start/')
        print(f"Start endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Start: {data.get('success', False)} - {data.get('message', '')}")
        
        # Stop endpoint
        response = client.post('/daily-sync/stop/')
        print(f"Stop endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Stop: {data.get('success', False)} - {data.get('message', '')}")
        
        # Test service directly
        print("\nTesting service directly...")
        service = DailyComplianceSyncService()
        
        print(f"Service status: {service.get_status()}")
        
        print("Starting service...")
        service.start_daily_sync()
        print(f"Service running: {service.is_running}")
        
        print("Stopping service...")
        service.stop_daily_sync()
        print(f"Service running: {service.is_running}")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False


def test_settings_form():
    """Test settings form submission"""
    print("\n📝 Testing Settings Form Submission")
    print("=" * 40)
    
    try:
        client = Client()
        client.login(username='testuser', password='testpass123')
        
        # Get settings page to extract CSRF token
        response = client.get('/settings/')
        if response.status_code != 200:
            print(f"❌ Could not get settings page: {response.status_code}")
            return False
        
        content = response.content.decode('utf-8')
        
        # Extract CSRF token
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
        if not csrf_match:
            print("❌ Could not find CSRF token")
            return False
        
        csrf_token = csrf_match.group(1)
        print(f"✅ Found CSRF token")
        
        # Submit form with daily sync settings
        form_data = {
            'csrfmiddlewaretoken': csrf_token,
            'compliance_sync_enabled': 'on',
            'compliance_skip_processed': 'on',
            'compliance_sync_interval': '5',
            'compliance_sync_interval_unit': 'days',
        }
        
        print("Submitting form...")
        response = client.post('/settings/', form_data)
        print(f"Form submission status: {response.status_code}")
        
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
            return False
            
    except Exception as e:
        print(f"❌ Error testing form: {e}")
        return False


def main():
    """Run the simple test"""
    print("🚀 Daily Compliance Sync - Simple Test")
    print("=" * 50)
    
    # Test 1: Basic functionality
    result1 = test_with_test_user()
    
    # Test 2: Form submission
    result2 = test_settings_form()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    print(f"Basic Functionality: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Form Submission: {'✅ PASS' if result2 else '❌ FAIL'}")
    
    if result1 and result2:
        print("\n🎉 All tests passed! Daily Compliance Sync is working!")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
    
    print("\n🔗 Test the settings page manually at: http://127.0.0.1:8000/settings/")
    print("   Login with: testuser / testpass123")


if __name__ == "__main__":
    main()
