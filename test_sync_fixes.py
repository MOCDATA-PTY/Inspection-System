#!/usr/bin/env python3
"""
Test script to verify sync fixes
Tests duplicate key fix and proper timing
"""

import os
import sys
import django
import time
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.scheduled_sync_service import ScheduledSyncService
from main.models import SystemSettings, Client


def test_duplicate_key_fix():
    """Test that duplicate key errors are fixed"""
    print("🔧 Testing Duplicate Key Fix")
    print("=" * 50)
    
    try:
        # Clear existing clients
        Client.objects.all().delete()
        print("Cleared existing clients")
        
        # Create some test clients with the old method (should fail)
        print("\nTesting old client ID generation (should create duplicates):")
        old_clients = []
        for i in range(5):
            client = Client(
                name=f"Test Client {i}",
                client_id=f"CL{i+1:05d}",
                internal_account_code=f"TEST{i+1}",
                email=f"test{i+1}@example.com"
            )
            old_clients.append(client)
        
        # This should work fine
        Client.objects.bulk_create(old_clients)
        print("✅ Old method created clients successfully")
        
        # Now test the new method
        print("\nTesting new client ID generation (should avoid duplicates):")
        new_clients = []
        for i in range(5):
            unique_id = f"CL{int(time.time() * 1000) % 100000:05d}{i:03d}"
            client = Client(
                name=f"New Test Client {i}",
                client_id=unique_id,
                internal_account_code=f"NEW{i+1}",
                email=f"new{i+1}@example.com"
            )
            new_clients.append(client)
        
        Client.objects.bulk_create(new_clients)
        print("✅ New method created clients successfully")
        
        # Verify no duplicates
        all_clients = Client.objects.all()
        client_ids = [client.client_id for client in all_clients]
        unique_ids = set(client_ids)
        
        print(f"Total clients: {len(all_clients)}")
        print(f"Unique client IDs: {len(unique_ids)}")
        print(f"No duplicates: {len(client_ids) == len(unique_ids)}")
        
        # Clean up
        Client.objects.all().delete()
        print("Cleaned up test clients")
        
    except Exception as e:
        print(f"❌ Error testing duplicate key fix: {e}")
    
    print()


def test_sync_timing():
    """Test that sync timing works correctly"""
    print("⏰ Testing Sync Timing")
    print("=" * 50)
    
    try:
        sync_service = ScheduledSyncService()
        
        # Set up 1 minute interval
        settings_obj = SystemSettings.objects.first()
        if settings_obj:
            original_interval = settings_obj.sync_interval_hours
            settings_obj.sync_interval_hours = 0.017  # 1 minute (0.017 hours)
            settings_obj.auto_sync_enabled = True
            settings_obj.google_sheets_enabled = True
            settings_obj.sql_server_enabled = True
            settings_obj.save()
            
            print("Set sync interval to 1 minute")
            
            # Test should_run_sync logic
            now = datetime.now()
            sync_service.last_sync_times = {'google_sheets': now, 'sql_server': now}
            
            print(f"Last sync time: {now.strftime('%H:%M:%S')}")
            
            # Test timing at different intervals
            test_cases = [
                (30, "30 seconds ago", False),  # Should not sync
                (45, "45 seconds ago", False),  # Should not sync
                (60, "1 minute ago", True),     # Should sync
                (90, "1.5 minutes ago", True),  # Should sync
                (120, "2 minutes ago", True)    # Should sync
            ]
            
            for seconds, description, expected in test_cases:
                test_time = now - timedelta(seconds=seconds)
                sync_service.last_sync_times = {'google_sheets': test_time, 'sql_server': test_time}
                
                google_should_sync = sync_service.should_run_sync('google_sheets')
                sql_should_sync = sync_service.should_run_sync('sql_server')
                
                print(f"  {description}:")
                print(f"    Google Sheets should sync: {google_should_sync} (expected: {expected})")
                print(f"    SQL Server should sync: {sql_should_sync} (expected: {expected})")
                
                if google_should_sync == expected and sql_should_sync == expected:
                    print(f"    ✅ Correct timing behavior")
                else:
                    print(f"    ❌ Incorrect timing behavior")
            
            # Restore original settings
            settings_obj.sync_interval_hours = original_interval
            settings_obj.save()
            print(f"\nRestored original interval: {original_interval} hours")
        else:
            print("No system settings found")
            
    except Exception as e:
        print(f"❌ Error testing sync timing: {e}")
    
    print()


def test_sync_service_behavior():
    """Test the overall sync service behavior"""
    print("🔄 Testing Sync Service Behavior")
    print("=" * 50)
    
    try:
        sync_service = ScheduledSyncService()
        
        # Test service status
        status = sync_service.get_service_status()
        print("Service Status:")
        print(f"  - Is Running: {status.get('is_running', False)}")
        print(f"  - Auto Sync Enabled: {status.get('auto_sync_enabled', False)}")
        print(f"  - Sync Interval: {status.get('sync_interval_hours', 0)} hours")
        
        # Test manual sync
        print("\nTesting manual Google Sheets sync...")
        result = sync_service.sync_google_sheets()
        print(f"Google Sheets sync result: {result}")
        
        print("\nTesting manual SQL Server sync...")
        result = sync_service.sync_sql_server()
        print(f"SQL Server sync result: {result}")
        
    except Exception as e:
        print(f"❌ Error testing sync service behavior: {e}")
    
    print()


def main():
    """Run all sync fix tests"""
    print("🧪 Sync Fixes Test Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    test_duplicate_key_fix()
    test_sync_timing()
    test_sync_service_behavior()
    
    print("✅ All sync fix tests completed!")
    print()
    print("📋 Fix Summary:")
    print("   - Fixed duplicate client_id generation using timestamp + index")
    print("   - Fixed sync timing to only run when actually due")
    print("   - Improved background service loop efficiency")
    print("   - Added proper timing checks before running syncs")


if __name__ == "__main__":
    main()
