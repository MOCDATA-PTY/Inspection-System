#!/usr/bin/env python3
"""
Test script for backup functionality
Tests both manual and scheduled backup services
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from main.services.backup_service import BackupService
from main.services.scheduled_backup_service import ScheduledBackupService
from main.models import SystemSettings


def test_backup_location():
    """Test where backups are saved"""
    print("🔍 Testing Backup Location")
    print("=" * 50)
    
    # Get the backup directory
    backup_service = BackupService()
    backup_dir = backup_service.backup_dir
    
    print(f"Backup Directory: {backup_dir}")
    print(f"Absolute Path: {os.path.abspath(backup_dir)}")
    print(f"Directory Exists: {os.path.exists(backup_dir)}")
    
    # List existing backup files
    if os.path.exists(backup_dir):
        backup_files = os.listdir(backup_dir)
        print(f"Number of backup files: {len(backup_files)}")
        
        if backup_files:
            print("\nExisting backup files:")
            for file in sorted(backup_files)[-5:]:  # Show last 5 files
                file_path = os.path.join(backup_dir, file)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"  - {file} ({file_size:,} bytes, {file_time.strftime('%Y-%m-%d %H:%M:%S')})")
        else:
            print("No backup files found")
    else:
        print("Backup directory does not exist - will be created on first backup")
    
    print()


def test_manual_backup():
    """Test manual backup creation"""
    print("💾 Testing Manual Backup")
    print("=" * 50)
    
    try:
        backup_service = BackupService()
        print("Creating manual backup...")
        
        success = backup_service.create_backup(backup_type='test_manual')
        
        if success:
            print("✅ Manual backup created successfully!")
            
            # Check what files were created
            backup_dir = backup_service.backup_dir
            if os.path.exists(backup_dir):
                backup_files = [f for f in os.listdir(backup_dir) if 'test_manual' in f]
                print(f"Created files: {backup_files}")
                
                # Show file sizes
                for file in backup_files:
                    file_path = os.path.join(backup_dir, file)
                    file_size = os.path.getsize(file_path)
                    print(f"  - {file}: {file_size:,} bytes")
        else:
            print("❌ Manual backup failed")
            
    except Exception as e:
        print(f"❌ Error creating manual backup: {e}")
    
    print()


def test_scheduled_backup_service():
    """Test scheduled backup service"""
    print("⏰ Testing Scheduled Backup Service")
    print("=" * 50)
    
    try:
        # Get current settings
        settings_obj = SystemSettings.objects.first()
        if settings_obj:
            print(f"Current settings:")
            print(f"  - Auto Sync Enabled: {settings_obj.auto_sync_enabled}")
            print(f"  - Backup Frequency: {settings_obj.backup_frequency_days} days")
        else:
            print("No system settings found")
        
        # Test service status
        scheduled_service = ScheduledBackupService()
        status = scheduled_service.get_service_status()
        
        print(f"\nService Status:")
        print(f"  - Is Running: {status.get('is_running', False)}")
        print(f"  - Auto Sync Enabled: {status.get('auto_sync_enabled', False)}")
        print(f"  - Backup Frequency: {status.get('backup_frequency_days', 7)} days")
        print(f"  - Last Backup: {status.get('last_backup_time', 'Never')}")
        print(f"  - Next Backup: {status.get('next_backup_time', 'Not scheduled')}")
        
        # Test manual backup through service
        print(f"\nTesting manual backup through service...")
        success, message = scheduled_service.run_manual_backup()
        print(f"Manual backup result: {success} - {message}")
        
    except Exception as e:
        print(f"❌ Error testing scheduled backup service: {e}")
    
    print()


def test_backup_service_endpoints():
    """Test backup service API endpoints"""
    print("🌐 Testing Backup Service Endpoints")
    print("=" * 50)
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        
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
        print("Testing /scheduled-backup/status/ endpoint...")
        response = client.get('/scheduled-backup/status/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"Error: {response.content}")
        
        # Test start endpoint
        print("\nTesting /scheduled-backup/start/ endpoint...")
        response = client.post('/scheduled-backup/start/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"Error: {response.content}")
        
        # Test stop endpoint
        print("\nTesting /scheduled-backup/stop/ endpoint...")
        response = client.post('/scheduled-backup/stop/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"Error: {response.content}")
        
        # Test manual backup endpoint
        print("\nTesting /scheduled-backup/manual/ endpoint...")
        response = client.post('/scheduled-backup/manual/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"Error: {response.content}")
            
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
    
    print()


def test_backup_data_integrity():
    """Test backup data integrity"""
    print("🔍 Testing Backup Data Integrity")
    print("=" * 50)
    
    try:
        backup_service = BackupService()
        backup_dir = backup_service.backup_dir
        
        # Find the most recent backup file
        if os.path.exists(backup_dir):
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
            if backup_files:
                latest_file = max(backup_files, key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)))
                file_path = os.path.join(backup_dir, latest_file)
                
                print(f"Testing latest backup file: {latest_file}")
                
                # Load and validate JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                print(f"Backup data structure:")
                print(f"  - Timestamp: {backup_data.get('timestamp')}")
                print(f"  - Backup Type: {backup_data.get('backup_type')}")
                print(f"  - Created At: {backup_data.get('created_at')}")
                print(f"  - Data Keys: {list(backup_data.get('data', {}).keys())}")
                
                # Check if data contains expected tables
                data = backup_data.get('data', {})
                expected_tables = ['clients', 'shipments', 'compliance_documents']
                
                for table in expected_tables:
                    if table in data:
                        count = len(data[table]) if isinstance(data[table], list) else 0
                        print(f"  - {table}: {count} records")
                    else:
                        print(f"  - {table}: Not found")
                
                print("✅ Backup data integrity check completed")
            else:
                print("No backup files found to test")
        else:
            print("Backup directory does not exist")
            
    except Exception as e:
        print(f"❌ Error testing backup data integrity: {e}")
    
    print()


def main():
    """Run all backup tests"""
    print("🧪 Backup Functionality Test Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    test_backup_location()
    test_manual_backup()
    test_scheduled_backup_service()
    test_backup_service_endpoints()
    test_backup_data_integrity()
    
    print("✅ All tests completed!")
    print()
    print("📁 Backup Location Summary:")
    print(f"   Backups are saved to: {os.path.join(settings.BASE_DIR, 'backups', 'exports')}")
    print(f"   Full path: {os.path.abspath(os.path.join(settings.BASE_DIR, 'backups', 'exports'))}")


if __name__ == "__main__":
    main()
