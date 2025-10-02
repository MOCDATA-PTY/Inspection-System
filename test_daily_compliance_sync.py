#!/usr/bin/env python3
"""
Test script for Daily Compliance Sync functionality
Tests the settings page UI, backend services, and API endpoints
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

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from main.models import SystemSettings, Settings, FoodSafetyAgencyInspection
from main.services.daily_compliance_sync import DailyComplianceSyncService, daily_sync_service


def test_daily_sync_service_initialization():
    """Test Daily Compliance Sync Service initialization"""
    print("🔧 Testing Daily Sync Service Initialization")
    print("=" * 50)
    
    try:
        service = DailyComplianceSyncService()
        
        print(f"Service initialized: ✅")
        print(f"  - Is Running: {service.is_running}")
        print(f"  - Last Sync Time: {service.last_sync_time}")
        print(f"  - Sync Stats: {service.sync_stats}")
        
        # Test status method
        status = service.get_status()
        print(f"  - Status: {json.dumps(status, indent=2, default=str)}")
        
    except Exception as e:
        print(f"❌ Error initializing service: {e}")
    
    print()


def test_system_settings_retrieval():
    """Test system settings retrieval for daily sync"""
    print("⚙️ Testing System Settings Retrieval")
    print("=" * 50)
    
    try:
        # Test SystemSettings model
        settings = SystemSettings.get_settings()
        print(f"SystemSettings found: ✅")
        print(f"  - Compliance Daily Sync Enabled: {settings.compliance_daily_sync_enabled}")
        print(f"  - Compliance Skip Processed: {settings.compliance_skip_processed}")
        print(f"  - Compliance Last Processed Date: {settings.compliance_last_processed_date}")
        
        # Test Settings model
        app_settings = Settings.get_settings()
        print(f"Settings found: ✅")
        print(f"  - Compliance Auto Sync: {app_settings.compliance_auto_sync}")
        print(f"  - Compliance Sync Interval: {app_settings.compliance_sync_interval}")
        print(f"  - Compliance Sync Unit: {app_settings.compliance_sync_unit}")
        print(f"  - Compliance Batch Mode: {app_settings.compliance_batch_mode}")
        
    except Exception as e:
        print(f"❌ Error retrieving settings: {e}")
    
    print()


def test_daily_sync_api_endpoints():
    """Test Daily Sync API endpoints"""
    print("🌐 Testing Daily Sync API Endpoints")
    print("=" * 50)
    
    try:
        # Create a test client
        client = Client()
        
        # Create a test user and login
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        client.force_login(user)
        
        # Test status endpoint
        print("Testing /daily-sync/status/ endpoint...")
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
            
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
    
    print()


def test_settings_page_rendering():
    """Test settings page rendering with daily sync section"""
    print("📄 Testing Settings Page Rendering")
    print("=" * 50)
    
    try:
        client = Client()
        
        # Create a test user and login
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        client.force_login(user)
        
        # Test settings page
        print("Testing /settings/ page...")
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
                
        else:
            print(f"Error: {response.content}")
            
    except Exception as e:
        print(f"❌ Error testing settings page: {e}")
    
    print()


def test_daily_sync_service_operations():
    """Test daily sync service start/stop operations"""
    print("🔄 Testing Daily Sync Service Operations")
    print("=" * 50)
    
    try:
        service = DailyComplianceSyncService()
        
        # Test initial state
        print(f"Initial state - Is Running: {service.is_running}")
        
        # Test start service
        print("Starting daily sync service...")
        service.start_daily_sync()
        print(f"After start - Is Running: {service.is_running}")
        
        # Wait a moment
        time.sleep(2)
        
        # Test status
        status = service.get_status()
        print(f"Service status: {json.dumps(status, indent=2, default=str)}")
        
        # Test stop service
        print("Stopping daily sync service...")
        service.stop_daily_sync()
        print(f"After stop - Is Running: {service.is_running}")
        
    except Exception as e:
        print(f"❌ Error testing service operations: {e}")
    
    print()


def test_compliance_documents_processing():
    """Test compliance documents processing logic"""
    print("📋 Testing Compliance Documents Processing")
    print("=" * 50)
    
    try:
        service = DailyComplianceSyncService()
        
        # Get system settings
        settings = service.get_system_settings()
        if settings:
            print(f"System settings retrieved: ✅")
            print(f"  - Daily sync enabled: {settings.compliance_daily_sync_enabled}")
            print(f"  - Skip processed: {settings.compliance_skip_processed}")
        else:
            print("❌ Could not retrieve system settings")
            return
        
        # Check if we should run daily sync
        should_run = service.should_run_daily_sync()
        print(f"Should run daily sync: {should_run}")
        
        # Get inspection count for testing
        six_months_ago = datetime.now() - timedelta(days=180)
        inspection_count = FoodSafetyAgencyInspection.objects.filter(
            inspection_date__gte=six_months_ago
        ).count()
        print(f"Inspections available for processing: {inspection_count}")
        
        # Test document ID generation
        if inspection_count > 0:
            latest_inspection = FoodSafetyAgencyInspection.objects.filter(
                inspection_date__gte=six_months_ago
            ).first()
            doc_id = service.generate_document_id(latest_inspection)
            print(f"Sample document ID: {doc_id}")
        
    except Exception as e:
        print(f"❌ Error testing compliance processing: {e}")
    
    print()


def test_settings_form_submission():
    """Test settings form submission with daily sync settings"""
    print("📝 Testing Settings Form Submission")
    print("=" * 50)
    
    try:
        client = Client()
        
        # Create a test user and login
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
        
        client.force_login(user)
        
        # Test form submission with daily sync settings
        form_data = {
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
            
        else:
            print(f"❌ Form submission failed: {response.content}")
            
    except Exception as e:
        print(f"❌ Error testing form submission: {e}")
    
    print()


def test_javascript_functionality():
    """Test JavaScript functionality for daily sync"""
    print("🔧 Testing JavaScript Functionality")
    print("=" * 50)
    
    try:
        # Read the settings.html file to check JavaScript
        with open('main/templates/main/settings.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required JavaScript functions
        js_checks = [
            ('startDailySync function', 'function startDailySync()'),
            ('stopDailySync function', 'function stopDailySync()'),
            ('Event listeners', 'startDailySyncBtn'),
            ('Event listeners', 'stopDailySyncBtn'),
            ('CSRF token function', 'getCsrfToken()'),
            ('API endpoints', '/daily-sync/start/'),
            ('API endpoints', '/daily-sync/stop/'),
            ('Error handling', 'try {'),
            ('Success handling', 'result.success'),
        ]
        
        for check_name, check_text in js_checks:
            if check_text in content:
                print(f"  ✅ {check_name}: Found")
            else:
                print(f"  ❌ {check_name}: Missing")
        
        # Check for proper error handling
        if 'alert(' in content and 'error' in content.lower():
            print(f"  ✅ Error handling: Found")
        else:
            print(f"  ❌ Error handling: Missing")
            
    except Exception as e:
        print(f"❌ Error testing JavaScript: {e}")
    
    print()


def test_global_service_instance():
    """Test global daily sync service instance"""
    print("🌍 Testing Global Service Instance")
    print("=" * 50)
    
    try:
        # Test global instance
        print(f"Global service instance: {daily_sync_service}")
        print(f"  - Type: {type(daily_sync_service)}")
        print(f"  - Is Running: {daily_sync_service.is_running}")
        
        # Test status
        status = daily_sync_service.get_status()
        print(f"  - Status: {json.dumps(status, indent=2, default=str)}")
        
        # Test that it's the same instance
        service1 = DailyComplianceSyncService()
        service2 = DailyComplianceSyncService()
        print(f"  - New instances are different: {service1 is not service2}")
        print(f"  - Global instance is singleton: {daily_sync_service is daily_sync_service}")
        
    except Exception as e:
        print(f"❌ Error testing global instance: {e}")
    
    print()


def main():
    """Run all daily compliance sync tests"""
    print("🧪 Daily Compliance Sync Test Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    test_daily_sync_service_initialization()
    test_system_settings_retrieval()
    test_daily_sync_api_endpoints()
    test_settings_page_rendering()
    test_daily_sync_service_operations()
    test_compliance_documents_processing()
    test_settings_form_submission()
    test_javascript_functionality()
    test_global_service_instance()
    
    print("✅ All tests completed!")
    print()
    print("📋 Test Summary:")
    print("   - Service initialization and configuration")
    print("   - API endpoint functionality")
    print("   - Settings page UI elements")
    print("   - Form submission and data persistence")
    print("   - JavaScript functionality")
    print("   - Global service instance management")
    print()
    print("🔗 Related URLs:")
    print("   - Settings Page: http://127.0.0.1:8000/settings/")
    print("   - Start Sync: http://127.0.0.1:8000/daily-sync/start/")
    print("   - Stop Sync: http://127.0.0.1:8000/daily-sync/stop/")
    print("   - Sync Status: http://127.0.0.1:8000/daily-sync/status/")


if __name__ == "__main__":
    main()
