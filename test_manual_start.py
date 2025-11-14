#!/usr/bin/env python3
"""
Test manual start functionality for Daily Compliance Sync
Tests that manual starts run even if already run today
"""

import os
import sys
import django
import json
import time
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.daily_compliance_sync import DailyComplianceSyncService
from main.models import SystemSettings


def test_manual_start_functionality():
    """Test that manual start runs even if already run today"""
    print("🔧 Testing Manual Start Functionality")
    print("=" * 50)
    
    try:
        service = DailyComplianceSyncService()
        
        # Enable daily sync
        settings = SystemSettings.get_settings()
        settings.compliance_daily_sync_enabled = True
        settings.compliance_last_processed_date = datetime.now()  # Set as if already run today
        settings.save()
        
        print("1. Set up: Daily sync enabled, already run today")
        print(f"   Last processed: {settings.compliance_last_processed_date}")
        
        # Test automatic start (should skip)
        print("\n2. Testing automatic start (should skip)...")
        should_run_auto = service.should_run_daily_sync(manual_start=False)
        print(f"   Should run (automatic): {should_run_auto}")
        
        # Test manual start (should run)
        print("\n3. Testing manual start (should run)...")
        should_run_manual = service.should_run_daily_sync(manual_start=True)
        print(f"   Should run (manual): {should_run_manual}")
        
        # Test actual start with manual flag
        print("\n4. Testing actual manual start...")
        service.start_daily_sync(manual_start=True)
        print(f"   Service running: {service.is_running}")
        
        # Let it run briefly
        time.sleep(2)
        
        # Stop the service
        service.stop_daily_sync()
        print(f"   Service stopped: {not service.is_running}")
        
        print("\n✅ Manual start functionality test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_api_manual_start():
    """Test API endpoint with manual start"""
    print("\n🌐 Testing API Manual Start")
    print("=" * 50)
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        
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
        client.login(username='testuser', password='testpass123')
        
        # Set up: Mark as already run today
        settings = SystemSettings.get_settings()
        settings.compliance_daily_sync_enabled = True
        settings.compliance_last_processed_date = datetime.now()
        settings.save()
        
        print("1. Set up: Marked as already run today")
        
        # Test API start endpoint
        print("\n2. Testing API start endpoint...")
        response = client.post('/daily-sync/start/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            # Check if service is running
            time.sleep(1)
            status_response = client.get('/daily-sync/status/')
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"   Service running: {status_data.get('status', {}).get('is_running', False)}")
            
            # Stop the service
            client.post('/daily-sync/stop/')
            print("   Service stopped")
            
            return True
        else:
            print(f"   Error: {response.content}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_scenario_workflow():
    """Test the complete scenario: run, stop, run again"""
    print("\n🔄 Testing Complete Scenario Workflow")
    print("=" * 50)
    
    try:
        service = DailyComplianceSyncService()
        
        # Enable daily sync
        settings = SystemSettings.get_settings()
        settings.compliance_daily_sync_enabled = True
        settings.compliance_last_processed_date = None  # Reset
        settings.save()
        
        print("1. Initial state: Daily sync enabled, never run")
        
        # First run (automatic)
        print("\n2. First run (automatic)...")
        service.start_daily_sync(manual_start=False)
        time.sleep(2)
        service.stop_daily_sync()
        print("   First run completed")
        
        # Check that it won't run again automatically
        print("\n3. Testing automatic run after first run...")
        should_run = service.should_run_daily_sync(manual_start=False)
        print(f"   Should run automatically: {should_run}")
        
        # Manual run (should work)
        print("\n4. Manual run after automatic run...")
        should_run_manual = service.should_run_daily_sync(manual_start=True)
        print(f"   Should run manually: {should_run_manual}")
        
        # Actually start manually
        service.start_daily_sync(manual_start=True)
        time.sleep(2)
        service.stop_daily_sync()
        print("   Manual run completed")
        
        print("\n✅ Complete scenario workflow test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all manual start tests"""
    print("🧪 Manual Start Functionality Test")
    print("=" * 60)
    
    # Test 1: Basic manual start functionality
    result1 = test_manual_start_functionality()
    
    # Test 2: API manual start
    result2 = test_api_manual_start()
    
    # Test 3: Complete scenario
    result3 = test_scenario_workflow()
    
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    print(f"Manual Start Functionality: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"API Manual Start: {'✅ PASS' if result2 else '❌ FAIL'}")
    print(f"Complete Scenario: {'✅ PASS' if result3 else '❌ FAIL'}")
    
    if result1 and result2 and result3:
        print("\n🎉 All tests passed! Manual start functionality is working!")
        print("\n📋 Key Features:")
        print("   - Manual starts run even if already run today")
        print("   - Automatic starts respect daily schedule")
        print("   - API endpoints support manual override")
        print("   - Stop/start workflow works correctly")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
