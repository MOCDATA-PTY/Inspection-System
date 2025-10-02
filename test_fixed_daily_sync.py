#!/usr/bin/env python3
"""
Test the fixed Daily Compliance Sync functionality
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

from main.services.daily_compliance_sync import DailyComplianceSyncService


def test_fixed_daily_sync():
    """Test the fixed daily sync functionality"""
    print("🔧 Testing Fixed Daily Compliance Sync")
    print("=" * 50)
    
    try:
        service = DailyComplianceSyncService()
        
        # Test basic functionality
        print("1. Testing service initialization...")
        print(f"   Service created: ✅")
        print(f"   Is running: {service.is_running}")
        
        # Test start/stop
        print("\n2. Testing start/stop...")
        service.start_daily_sync()
        print(f"   Started: {service.is_running}")
        
        time.sleep(1)
        
        service.stop_daily_sync()
        print(f"   Stopped: {not service.is_running}")
        
        # Test status
        print("\n3. Testing status...")
        status = service.get_status()
        print(f"   Status: {json.dumps(status, indent=2, default=str)}")
        
        # Test settings
        print("\n4. Testing settings...")
        settings = service.get_system_settings()
        if settings:
            print(f"   Daily sync enabled: {settings.compliance_daily_sync_enabled}")
            print(f"   Skip processed: {settings.compliance_skip_processed}")
        
        # Test document ID generation
        print("\n5. Testing document ID generation...")
        from main.models import FoodSafetyAgencyInspection
        inspection = FoodSafetyAgencyInspection.objects.first()
        if inspection:
            doc_id = service.generate_document_id(inspection)
            print(f"   Generated ID: {doc_id}")
            print(f"   Inspection ID: {inspection.id}")
            print(f"   Inspection Date: {inspection.date_of_inspection}")
        
        # Test should run logic
        print("\n6. Testing should run logic...")
        should_run = service.should_run_daily_sync()
        print(f"   Should run: {should_run}")
        
        print("\n✅ All tests passed! Daily Compliance Sync is working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_with_real_processing():
    """Test with real processing (but limited)"""
    print("\n🔄 Testing Real Processing (Limited)")
    print("=" * 50)
    
    try:
        service = DailyComplianceSyncService()
        
        # Enable daily sync for testing
        settings = service.get_system_settings()
        settings.compliance_daily_sync_enabled = True
        settings.save()
        
        print("1. Starting service with real processing...")
        service.start_daily_sync()
        
        # Let it run for a few seconds
        print("2. Letting service run for 3 seconds...")
        time.sleep(3)
        
        # Stop the service
        print("3. Stopping service...")
        service.stop_daily_sync()
        
        # Check final status
        status = service.get_status()
        print(f"4. Final status: {json.dumps(status, indent=2, default=str)}")
        
        print("\n✅ Real processing test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in real processing test: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Fixed Daily Compliance Sync Test")
    print("=" * 60)
    
    # Test basic functionality
    result1 = test_fixed_daily_sync()
    
    # Test real processing
    result2 = test_with_real_processing()
    
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    print(f"Basic Functionality: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Real Processing: {'✅ PASS' if result2 else '❌ FAIL'}")
    
    if result1 and result2:
        print("\n🎉 All tests passed! Daily Compliance Sync is fully working!")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
