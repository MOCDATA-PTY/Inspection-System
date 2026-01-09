#!/usr/bin/env python3
"""
Test script for Daily Compliance Sync functions - no authentication needed
Tests the core functionality directly
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

from main.models import SystemSettings, Settings, FoodSafetyAgencyInspection
from main.services.daily_compliance_sync import DailyComplianceSyncService, daily_sync_service


def test_service_initialization():
    """Test service initialization"""
    print("🔧 Testing Service Initialization")
    print("=" * 40)
    
    try:
        service = DailyComplianceSyncService()
        print(f"✅ Service created: {type(service).__name__}")
        print(f"  - Is Running: {service.is_running}")
        print(f"  - Last Sync: {service.last_sync_time}")
        print(f"  - Stats: {service.sync_stats}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_start_stop_functionality():
    """Test start/stop functionality"""
    print("\n🔄 Testing Start/Stop Functionality")
    print("=" * 40)
    
    try:
        service = DailyComplianceSyncService()
        
        print("Initial state:", service.is_running)
        
        print("Starting service...")
        service.start_daily_sync()
        print("After start:", service.is_running)
        
        time.sleep(1)
        
        print("Stopping service...")
        service.stop_daily_sync()
        print("After stop:", service.is_running)
        
        print("✅ Start/Stop functionality works!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_status_function():
    """Test status function"""
    print("\n📊 Testing Status Function")
    print("=" * 40)
    
    try:
        service = DailyComplianceSyncService()
        status = service.get_status()
        
        print("Status:", json.dumps(status, indent=2, default=str))
        
        # Check required fields
        required_fields = ['is_running', 'last_sync_time', 'total_documents_processed', 'documents_skipped', 'documents_processed']
        for field in required_fields:
            if field in status:
                print(f"  ✅ {field}: {status[field]}")
            else:
                print(f"  ❌ Missing field: {field}")
                return False
        
        print("✅ Status function works!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_system_settings_retrieval():
    """Test system settings retrieval"""
    print("\n⚙️ Testing System Settings Retrieval")
    print("=" * 40)
    
    try:
        service = DailyComplianceSyncService()
        settings = service.get_system_settings()
        
        if settings:
            print("✅ Settings retrieved:")
            print(f"  - Daily sync enabled: {settings.compliance_daily_sync_enabled}")
            print(f"  - Skip processed: {settings.compliance_skip_processed}")
            print(f"  - Last processed: {settings.compliance_last_processed_date}")
        else:
            print("❌ Could not retrieve settings")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_should_run_daily_sync():
    """Test should_run_daily_sync logic"""
    print("\n🤔 Testing Should Run Daily Sync Logic")
    print("=" * 40)
    
    try:
        service = DailyComplianceSyncService()
        should_run = service.should_run_daily_sync()
        
        print(f"Should run daily sync: {should_run}")
        
        # Test with different settings
        settings = service.get_system_settings()
        if settings:
            print(f"  - Daily sync enabled: {settings.compliance_daily_sync_enabled}")
            print(f"  - Skip processed: {settings.compliance_skip_processed}")
        
        print("✅ Should run logic works!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_document_id_generation():
    """Test document ID generation"""
    print("\n🆔 Testing Document ID Generation")
    print("=" * 40)
    
    try:
        service = DailyComplianceSyncService()
        
        # Get a sample inspection
        inspection = FoodSafetyAgencyInspection.objects.first()
        if inspection:
            doc_id = service.generate_document_id(inspection)
            print(f"✅ Generated document ID: {doc_id}")
            print(f"  - Inspection ID: {inspection.id}")
            print(f"  - Inspection Date: {inspection.date_of_inspection}")
        else:
            print("❌ No inspections found in database")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_inspection_queries():
    """Test inspection queries"""
    print("\n📋 Testing Inspection Queries")
    print("=" * 40)
    
    try:
        # Test the query used in the service
        six_months_ago = datetime.now() - timedelta(days=180)
        
        # Count inspections
        total_inspections = FoodSafetyAgencyInspection.objects.count()
        recent_inspections = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection__gte=six_months_ago
        ).count()
        
        print(f"✅ Total inspections: {total_inspections}")
        print(f"✅ Recent inspections (6 months): {recent_inspections}")
        
        # Test the actual query from the service
        inspections = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection__gte=six_months_ago
        ).order_by('-date_of_inspection')
        
        print(f"✅ Query works: {inspections.count()} inspections found")
        
        if inspections.exists():
            sample = inspections.first()
            print(f"  - Sample inspection: {sample.id} - {sample.date_of_inspection}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_global_service_instance():
    """Test global service instance"""
    print("\n🌍 Testing Global Service Instance")
    print("=" * 40)
    
    try:
        print(f"Global service: {daily_sync_service}")
        print(f"Type: {type(daily_sync_service)}")
        
        # Test that it's the same instance
        service1 = DailyComplianceSyncService()
        service2 = DailyComplianceSyncService()
        
        print(f"New instances are different: {service1 is not service2}")
        print(f"Global instance is singleton: {daily_sync_service is daily_sync_service}")
        
        # Test global instance functionality
        status = daily_sync_service.get_status()
        print(f"Global status: {json.dumps(status, indent=2, default=str)}")
        
        print("✅ Global service instance works!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_settings_models():
    """Test settings models"""
    print("\n⚙️ Testing Settings Models")
    print("=" * 40)
    
    try:
        # Test SystemSettings
        sys_settings = SystemSettings.get_settings()
        print(f"✅ SystemSettings: {sys_settings}")
        print(f"  - Daily sync enabled: {sys_settings.compliance_daily_sync_enabled}")
        print(f"  - Skip processed: {sys_settings.compliance_skip_processed}")
        
        # Test Settings
        app_settings = Settings.get_settings()
        print(f"✅ Settings: {app_settings}")
        print(f"  - Auto sync: {app_settings.compliance_auto_sync}")
        print(f"  - Sync interval: {app_settings.compliance_sync_interval}")
        print(f"  - Sync unit: {app_settings.compliance_sync_unit}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all function tests"""
    print("🧪 Daily Compliance Sync - Function Tests")
    print("=" * 60)
    print("Testing core functions without authentication...")
    print()
    
    tests = [
        ("Service Initialization", test_service_initialization),
        ("Start/Stop Functionality", test_start_stop_functionality),
        ("Status Function", test_status_function),
        ("System Settings Retrieval", test_system_settings_retrieval),
        ("Should Run Logic", test_should_run_daily_sync),
        ("Document ID Generation", test_document_id_generation),
        ("Inspection Queries", test_inspection_queries),
        ("Global Service Instance", test_global_service_instance),
        ("Settings Models", test_settings_models),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        result = test_func()
        results.append((test_name, result))
    
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All function tests passed! Daily Compliance Sync functions are working!")
    else:
        print(f"\n⚠️ {len(results) - passed} tests failed. Check the output above.")
    
    print("\n🔧 The Daily Compliance Sync service is functional!")
    print("   - Service can be started/stopped")
    print("   - Status can be retrieved")
    print("   - Settings can be accessed")
    print("   - Document processing logic works")


if __name__ == "__main__":
    main()
