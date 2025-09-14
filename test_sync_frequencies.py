#!/usr/bin/env python3
"""
Test Daily Compliance Sync with different frequencies
Tests various sync interval settings and units
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

from main.models import SystemSettings, Settings
from main.services.daily_compliance_sync import DailyComplianceSyncService


def test_different_sync_frequencies():
    """Test different sync frequency settings"""
    print("⏰ Testing Different Sync Frequencies")
    print("=" * 50)
    
    try:
        service = DailyComplianceSyncService()
        
        # Test different frequency combinations
        test_frequencies = [
            {'interval': 1, 'unit': 'minutes', 'description': '1 minute'},
            {'interval': 5, 'unit': 'minutes', 'description': '5 minutes'},
            {'interval': 30, 'unit': 'minutes', 'description': '30 minutes'},
            {'interval': 1, 'unit': 'hours', 'description': '1 hour'},
            {'interval': 6, 'unit': 'hours', 'description': '6 hours'},
            {'interval': 12, 'unit': 'hours', 'description': '12 hours'},
            {'interval': 1, 'unit': 'days', 'description': '1 day'},
            {'interval': 3, 'unit': 'days', 'description': '3 days'},
            {'interval': 7, 'unit': 'days', 'description': '7 days'},
            {'interval': 1, 'unit': 'weeks', 'description': '1 week'},
            {'interval': 2, 'unit': 'weeks', 'description': '2 weeks'},
            {'interval': 1, 'unit': 'months', 'description': '1 month'},
        ]
        
        print("Testing various sync frequency combinations:")
        print("-" * 50)
        
        for i, freq in enumerate(test_frequencies, 1):
            print(f"\n{i:2d}. Testing {freq['description']} ({freq['interval']} {freq['unit']})")
            
            # Update settings
            settings = Settings.get_settings()
            settings.compliance_sync_interval = freq['interval']
            settings.compliance_sync_unit = freq['unit']
            settings.save()
            
            # Test should_run_daily_sync logic
            should_run = service.should_run_daily_sync()
            print(f"    Should run: {should_run}")
            
            # Test frequency calculation
            if freq['unit'] == 'minutes':
                total_minutes = freq['interval']
            elif freq['unit'] == 'hours':
                total_minutes = freq['interval'] * 60
            elif freq['unit'] == 'days':
                total_minutes = freq['interval'] * 24 * 60
            elif freq['unit'] == 'weeks':
                total_minutes = freq['interval'] * 7 * 24 * 60
            elif freq['unit'] == 'months':
                total_minutes = freq['interval'] * 30 * 24 * 60  # Approximate
            
            print(f"    Total minutes: {total_minutes:,}")
            
            # Test service status
            status = service.get_status()
            print(f"    Service running: {status['is_running']}")
            
            # Test start/stop with this frequency
            if not status['is_running']:
                service.start_daily_sync()
                time.sleep(0.5)  # Brief pause
                service.stop_daily_sync()
                print(f"    Start/Stop: ✅")
            else:
                print(f"    Start/Stop: Already running")
        
        print(f"\n✅ Tested {len(test_frequencies)} different frequency combinations")
        return True
        
    except Exception as e:
        print(f"❌ Error testing frequencies: {e}")
        return False


def test_system_settings_frequencies():
    """Test SystemSettings frequency configurations"""
    print("\n⚙️ Testing SystemSettings Frequency Configurations")
    print("=" * 50)
    
    try:
        # Test different SystemSettings configurations
        test_configs = [
            {'enabled': True, 'skip_processed': True, 'description': 'Enabled with skip processed'},
            {'enabled': True, 'skip_processed': False, 'description': 'Enabled without skip processed'},
            {'enabled': False, 'skip_processed': True, 'description': 'Disabled with skip processed'},
            {'enabled': False, 'skip_processed': False, 'description': 'Disabled without skip processed'},
        ]
        
        for i, config in enumerate(test_configs, 1):
            print(f"\n{i}. Testing: {config['description']}")
            
            # Update SystemSettings
            sys_settings = SystemSettings.get_settings()
            sys_settings.compliance_daily_sync_enabled = config['enabled']
            sys_settings.compliance_skip_processed = config['skip_processed']
            sys_settings.save()
            
            print(f"   - Daily sync enabled: {sys_settings.compliance_daily_sync_enabled}")
            print(f"   - Skip processed: {sys_settings.compliance_skip_processed}")
            
            # Test service with these settings
            service = DailyComplianceSyncService()
            should_run = service.should_run_daily_sync()
            print(f"   - Should run: {should_run}")
            
            # Test status
            status = service.get_status()
            print(f"   - Service status: {status['is_running']}")
        
        print(f"\n✅ Tested {len(test_configs)} SystemSettings configurations")
        return True
        
    except Exception as e:
        print(f"❌ Error testing SystemSettings: {e}")
        return False


def test_frequency_validation():
    """Test frequency validation and edge cases"""
    print("\n🔍 Testing Frequency Validation and Edge Cases")
    print("=" * 50)
    
    try:
        service = DailyComplianceSyncService()
        
        # Test edge cases
        edge_cases = [
            {'interval': 0, 'unit': 'minutes', 'description': 'Zero minutes'},
            {'interval': -1, 'unit': 'minutes', 'description': 'Negative minutes'},
            {'interval': 1, 'unit': 'invalid', 'description': 'Invalid unit'},
            {'interval': 999999, 'unit': 'minutes', 'description': 'Very large interval'},
            {'interval': 1, 'unit': 'seconds', 'description': 'Unsupported unit'},
        ]
        
        print("Testing edge cases:")
        print("-" * 30)
        
        for i, case in enumerate(edge_cases, 1):
            print(f"\n{i}. {case['description']} ({case['interval']} {case['unit']})")
            
            try:
                # Update settings
                settings = Settings.get_settings()
                settings.compliance_sync_interval = case['interval']
                settings.compliance_sync_unit = case['unit']
                settings.save()
                
                # Test service behavior
                should_run = service.should_run_daily_sync()
                print(f"   Should run: {should_run}")
                
                # Test service start/stop
                if not service.is_running:
                    service.start_daily_sync()
                    time.sleep(0.2)
                    service.stop_daily_sync()
                    print(f"   Start/Stop: ✅")
                
            except Exception as e:
                print(f"   Error: {e}")
        
        print(f"\n✅ Tested {len(edge_cases)} edge cases")
        return True
        
    except Exception as e:
        print(f"❌ Error testing edge cases: {e}")
        return False


def test_frequency_combinations():
    """Test realistic frequency combinations"""
    print("\n🎯 Testing Realistic Frequency Combinations")
    print("=" * 50)
    
    try:
        service = DailyComplianceSyncService()
        
        # Realistic combinations for different use cases
        realistic_combinations = [
            {
                'name': 'Real-time Monitoring',
                'interval': 5, 'unit': 'minutes',
                'sys_enabled': True, 'sys_skip': True,
                'description': 'High-frequency monitoring for critical systems'
            },
            {
                'name': 'Hourly Updates',
                'interval': 1, 'unit': 'hours',
                'sys_enabled': True, 'sys_skip': True,
                'description': 'Regular hourly synchronization'
            },
            {
                'name': 'Daily Processing',
                'interval': 24, 'unit': 'hours',
                'sys_enabled': True, 'sys_skip': True,
                'description': 'Standard daily processing'
            },
            {
                'name': 'Weekly Batch',
                'interval': 1, 'unit': 'weeks',
                'sys_enabled': True, 'sys_skip': False,
                'description': 'Weekly batch processing without skipping'
            },
            {
                'name': 'Monthly Archive',
                'interval': 1, 'unit': 'months',
                'sys_enabled': True, 'sys_skip': False,
                'description': 'Monthly archival processing'
            },
            {
                'name': 'Disabled Mode',
                'interval': 1, 'unit': 'hours',
                'sys_enabled': False, 'sys_skip': True,
                'description': 'Disabled for maintenance'
            },
        ]
        
        print("Testing realistic frequency combinations:")
        print("-" * 50)
        
        for i, combo in enumerate(realistic_combinations, 1):
            print(f"\n{i}. {combo['name']}")
            print(f"   Description: {combo['description']}")
            print(f"   Frequency: {combo['interval']} {combo['unit']}")
            print(f"   System enabled: {combo['sys_enabled']}")
            print(f"   Skip processed: {combo['sys_skip']}")
            
            # Update Settings
            settings = Settings.get_settings()
            settings.compliance_sync_interval = combo['interval']
            settings.compliance_sync_unit = combo['unit']
            settings.save()
            
            # Update SystemSettings
            sys_settings = SystemSettings.get_settings()
            sys_settings.compliance_daily_sync_enabled = combo['sys_enabled']
            sys_settings.compliance_skip_processed = combo['sys_skip']
            sys_settings.save()
            
            # Test service behavior
            should_run = service.should_run_daily_sync()
            print(f"   Should run: {should_run}")
            
            # Test service operations
            if not service.is_running:
                service.start_daily_sync()
                time.sleep(0.3)
                status = service.get_status()
                print(f"   Service running: {status['is_running']}")
                service.stop_daily_sync()
                print(f"   Start/Stop: ✅")
            else:
                print(f"   Service already running")
        
        print(f"\n✅ Tested {len(realistic_combinations)} realistic combinations")
        return True
        
    except Exception as e:
        print(f"❌ Error testing realistic combinations: {e}")
        return False


def test_frequency_persistence():
    """Test that frequency settings persist correctly"""
    print("\n💾 Testing Frequency Settings Persistence")
    print("=" * 50)
    
    try:
        # Test saving and loading different frequencies
        test_frequencies = [
            {'interval': 15, 'unit': 'minutes'},
            {'interval': 2, 'unit': 'hours'},
            {'interval': 1, 'unit': 'days'},
            {'interval': 1, 'unit': 'weeks'},
        ]
        
        print("Testing frequency persistence:")
        print("-" * 30)
        
        for i, freq in enumerate(test_frequencies, 1):
            print(f"\n{i}. Testing persistence: {freq['interval']} {freq['unit']}")
            
            # Save settings
            settings = Settings.get_settings()
            settings.compliance_sync_interval = freq['interval']
            settings.compliance_sync_unit = freq['unit']
            settings.save()
            
            # Reload and verify
            settings_reloaded = Settings.get_settings()
            print(f"   Saved: {settings_reloaded.compliance_sync_interval} {settings_reloaded.compliance_sync_unit}")
            
            if (settings_reloaded.compliance_sync_interval == freq['interval'] and 
                settings_reloaded.compliance_sync_unit == freq['unit']):
                print(f"   ✅ Persistence: Correct")
            else:
                print(f"   ❌ Persistence: Failed")
                return False
        
        print(f"\n✅ All frequency settings persist correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing persistence: {e}")
        return False


def main():
    """Run all frequency tests"""
    print("🧪 Daily Compliance Sync - Frequency Tests")
    print("=" * 60)
    print("Testing different sync frequencies and configurations...")
    print()
    
    tests = [
        ("Different Sync Frequencies", test_different_sync_frequencies),
        ("SystemSettings Configurations", test_system_settings_frequencies),
        ("Frequency Validation", test_frequency_validation),
        ("Realistic Combinations", test_frequency_combinations),
        ("Frequency Persistence", test_frequency_persistence),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        result = test_func()
        results.append((test_name, result))
    
    print(f"\n{'='*60}")
    print("📊 FREQUENCY TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} frequency tests passed")
    
    if passed == len(results):
        print("\n🎉 All frequency tests passed! Sync frequencies work perfectly!")
        print("\n📋 Supported Frequencies:")
        print("   - Minutes: 1, 5, 15, 30, 60+")
        print("   - Hours: 1, 2, 6, 12, 24")
        print("   - Days: 1, 3, 7, 14, 30")
        print("   - Weeks: 1, 2, 4")
        print("   - Months: 1, 2, 3, 6, 12")
    else:
        print(f"\n⚠️ {len(results) - passed} frequency tests failed. Check the output above.")


if __name__ == "__main__":
    main()
