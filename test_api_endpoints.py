#!/usr/bin/env python3
"""
Test API endpoints for Daily Compliance Sync
"""

import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User


def test_api_endpoints():
    """Test all API endpoints"""
    print("🌐 Testing API Endpoints")
    print("=" * 40)
    
    try:
        client = Client()
        
        # Create or get test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        # Login
        login_success = client.login(username='testuser', password='testpass123')
        if not login_success:
            print("❌ Could not login")
            return False
        
        print("✅ Logged in successfully")
        
        # Test status endpoint
        print("\nTesting /daily-sync/status/...")
        response = client.get('/daily-sync/status/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status response: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"❌ Status error: {response.content}")
            return False
        
        # Test start endpoint
        print("\nTesting /daily-sync/start/...")
        response = client.post('/daily-sync/start/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Start response: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"❌ Start error: {response.content}")
            return False
        
        # Test stop endpoint
        print("\nTesting /daily-sync/stop/...")
        response = client.post('/daily-sync/stop/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stop response: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"❌ Stop error: {response.content}")
            return False
        
        print("\n✅ All API endpoints working!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False


def test_settings_page_access():
    """Test settings page access"""
    print("\n📄 Testing Settings Page Access")
    print("=" * 40)
    
    try:
        client = Client()
        client.login(username='testuser', password='testpass123')
        
        # Test settings page
        response = client.get('/settings/')
        print(f"Settings page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for key elements
            checks = [
                ('Daily Compliance Sync', 'Daily Compliance Sync'),
                ('Start Daily Sync Button', 'startDailySyncBtn'),
                ('Stop Daily Sync Button', 'stopDailySyncBtn'),
                ('JavaScript Functions', 'startDailySync'),
            ]
            
            print("Checking page elements:")
            for name, text in checks:
                if text in content:
                    print(f"  ✅ {name}")
                else:
                    print(f"  ❌ {name}")
            
            return True
        else:
            print(f"❌ Settings page error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing settings page: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 API Endpoints Test Suite")
    print("=" * 50)
    
    # Test API endpoints
    api_result = test_api_endpoints()
    
    # Test settings page
    page_result = test_settings_page_access()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    print(f"API Endpoints: {'✅ PASS' if api_result else '❌ FAIL'}")
    print(f"Settings Page: {'✅ PASS' if page_result else '❌ FAIL'}")
    
    if api_result and page_result:
        print("\n🎉 Everything is working perfectly!")
    else:
        print("\n⚠️ Some issues found. Check the output above.")


if __name__ == "__main__":
    main()
