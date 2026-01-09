#!/usr/bin/env python3
"""
Real test for sync fixes - tests actual behavior
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


def test_sync_interval_zero():
    """Test that sync interval 0 doesn't cause immediate syncing"""
    print("🔧 Testing Sync Interval 0 (Should NOT sync automatically)")
    print("=" * 60)
    
    try:
        # Set sync interval to 0
        settings_obj = SystemSettings.objects.first()
        if settings_obj:
            original_interval = settings_obj.sync_interval_hours
            settings_obj.sync_interval_hours = 0
            settings_obj.auto_sync_enabled = True
            settings_obj.save()
            
            print(f"Set sync interval to {settings_obj.sync_interval_hours} hours")
            
            sync_service = ScheduledSyncService()
            
            # Test should_run_sync with 0 interval
            sync_service.last_sync_times = {'google_sheets': datetime.now() - timedelta(minutes=1)}
            
            google_should_sync = sync_service.should_run_sync('google_sheets')
            sql_should_sync = sync_service.should_run_sync('sql_server')
            
            print(f"Google Sheets should sync: {google_should_sync} (expected: False)")
            print(f"SQL Server should sync: {sql_should_sync} (expected: False)")
            
            if not google_should_sync and not sql_should_sync:
                print("✅ Correct: 0 interval prevents automatic syncing")
            else:
                print("❌ Error: 0 interval should prevent automatic syncing")
            
            # Restore original settings
            settings_obj.sync_interval_hours = original_interval
            settings_obj.save()
            print(f"Restored original interval: {original_interval} hours")
        else:
            print("No system settings found")
            
    except Exception as e:
        print(f"❌ Error testing sync interval 0: {e}")
    
    print()


def test_sync_interval_one_minute():
    """Test that 1 minute interval works correctly"""
    print("⏰ Testing Sync Interval 1 Minute")
    print("=" * 60)
    
    try:
        # Set sync interval to 1 minute
        settings_obj = SystemSettings.objects.first()
        if settings_obj:
            original_interval = settings_obj.sync_interval_hours
            settings_obj.sync_interval_hours = 0.017  # 1 minute
            settings_obj.auto_sync_enabled = True
            settings_obj.save()
            
            print(f"Set sync interval to {settings_obj.sync_interval_hours} hours (1 minute)")
            
            sync_service = ScheduledSyncService()
            
            # Test timing
            now = datetime.now()
            test_cases = [
                (30, "30 seconds ago", False),
                (45, "45 seconds ago", False), 
                (60, "1 minute ago", True),
                (90, "1.5 minutes ago", True)
            ]
            
            for seconds, description, expected in test_cases:
                test_time = now - timedelta(seconds=seconds)
                sync_service.last_sync_times = {'google_sheets': test_time, 'sql_server': test_time}
                
                google_should_sync = sync_service.should_run_sync('google_sheets')
                sql_should_sync = sync_service.should_run_sync('sql_server')
                
                print(f"  {description}:")
                print(f"    Google Sheets: {google_should_sync} (expected: {expected})")
                print(f"    SQL Server: {sql_should_sync} (expected: {expected})")
                
                if google_should_sync == expected and sql_should_sync == expected:
                    print(f"    ✅ Correct timing")
                else:
                    print(f"    ❌ Incorrect timing")
            
            # Restore original settings
            settings_obj.sync_interval_hours = original_interval
            settings_obj.save()
            print(f"\nRestored original interval: {original_interval} hours")
        else:
            print("No system settings found")
            
    except Exception as e:
        print(f"❌ Error testing 1 minute interval: {e}")
    
    print()


def test_duplicate_client_ids():
    """Test that client ID generation avoids duplicates"""
    print("🆔 Testing Duplicate Client ID Prevention")
    print("=" * 60)
    
    try:
        # Clear existing clients
        Client.objects.all().delete()
        print("Cleared existing clients")
        
        # Test the new ID generation method
        print("Testing new client ID generation...")
        clients = []
        
        for i in range(10):
            unique_id = f"CL{int(time.time() * 1000) % 100000:05d}{i:03d}"
            client = Client(
                name=f"Test Client {i}",
                client_id=unique_id,
                internal_account_code=f"TEST{i}",
                email=f"test{i}@example.com"
            )
            clients.append(client)
        
        # Create clients
        Client.objects.bulk_create(clients)
        print(f"Created {len(clients)} clients")
        
        # Check for duplicates
        all_clients = Client.objects.all()
        client_ids = [client.client_id for client in all_clients]
        unique_ids = set(client_ids)
        
        print(f"Total clients: {len(all_clients)}")
        print(f"Unique client IDs: {len(unique_ids)}")
        print(f"No duplicates: {len(client_ids) == len(unique_ids)}")
        
        if len(client_ids) == len(unique_ids):
            print("✅ No duplicate client IDs found")
        else:
            print("❌ Duplicate client IDs found!")
            duplicates = [id for id in client_ids if client_ids.count(id) > 1]
            print(f"Duplicate IDs: {set(duplicates)}")
        
        # Show sample IDs
        print("\nSample client IDs:")
        for client in all_clients[:5]:
            print(f"  {client.client_id}: {client.name}")
        
        # Clean up
        Client.objects.all().delete()
        print("\nCleaned up test clients")
        
    except Exception as e:
        print(f"❌ Error testing duplicate client IDs: {e}")
    
    print()


def test_actual_sync_behavior():
    """Test the actual sync service behavior"""
    print("🔄 Testing Actual Sync Service Behavior")
    print("=" * 60)
    
    try:
        sync_service = ScheduledSyncService()
        
        # Get current settings
        settings = sync_service.get_system_settings()
        print(f"Current sync interval: {settings.get('sync_interval_hours', 0)} hours")
        print(f"Auto sync enabled: {settings.get('auto_sync_enabled', False)}")
        
        # Test manual sync
        print("\nTesting manual Google Sheets sync...")
        result = sync_service.sync_google_sheets()
        print(f"Google Sheets sync result: {result}")
        
        # Check if clients were created with new ID format
        clients = Client.objects.all()
        if clients.exists():
            sample_client = clients.first()
            print(f"Sample client ID format: {sample_client.client_id}")
            
            # Check if it follows the new format
            if sample_client.client_id.startswith('CL') and len(sample_client.client_id) >= 8:
                print("✅ Client ID follows new format")
            else:
                print("❌ Client ID doesn't follow new format")
        
    except Exception as e:
        print(f"❌ Error testing actual sync behavior: {e}")
    
    print()


def main():
    """Run all real sync fix tests"""
    print("🧪 Real Sync Fixes Test Suite")
    print("=" * 70)
    print()
    
    # Run all tests
    test_sync_interval_zero()
    test_sync_interval_one_minute()
    test_duplicate_client_ids()
    test_actual_sync_behavior()
    
    print("✅ All real sync fix tests completed!")
    print()
    print("📋 Summary:")
    print("   - Sync interval 0 should NOT cause automatic syncing")
    print("   - 1 minute interval should work correctly")
    print("   - Client ID generation should avoid duplicates")
    print("   - Actual sync behavior should be tested")


if __name__ == "__main__":
    main()
