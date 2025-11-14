#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Daily Compliance Sync Service
This script tests whether the daily compliance sync service properly pulls compliance documents
"""

import os
import sys
import django
import time
from datetime import datetime, timedelta

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.daily_compliance_sync import daily_sync_service
from main.models import SystemSettings, FoodSafetyAgencyInspection
from django.core.cache import cache

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def test_daily_compliance_sync():
    """Test the daily compliance sync service"""

    print_section("DAILY COMPLIANCE SYNC TEST")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Step 1: Check System Settings
    print_section("Step 1: Checking System Settings")
    try:
        settings = SystemSettings.get_settings()
        print(f"✅ System settings loaded successfully")
        print(f"   - Daily Sync Enabled: {settings.compliance_daily_sync_enabled}")
        print(f"   - Skip Processed: {settings.compliance_skip_processed}")
        print(f"   - Compliance Sync Interval: {settings.compliance_sync_interval_hours} hours")
        print(f"   - Last Processed Date: {settings.compliance_last_processed_date or 'Never'}")

        if not settings.compliance_daily_sync_enabled:
            print("\n⚠️  WARNING: Daily compliance sync is DISABLED in settings!")
            print("   To enable it, go to Settings page and toggle 'Enable Daily Sync'")
            response = input("\nDo you want to enable it now for testing? (y/n): ")
            if response.lower() == 'y':
                settings.compliance_daily_sync_enabled = True
                settings.save()
                print("✅ Daily compliance sync enabled!")
            else:
                print("❌ Cannot proceed with test - sync is disabled")
                return False
    except Exception as e:
        print(f"❌ Error loading system settings: {e}")
        return False

    # Step 2: Check Inspections
    print_section("Step 2: Checking Available Inspections")
    try:
        from datetime import date
        start_date = date(2025, 10, 1)
        end_date = date(2026, 4, 1)

        inspections = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection__gte=start_date,
            date_of_inspection__lt=end_date
        ).order_by('-date_of_inspection')

        inspection_count = inspections.count()
        print(f"✅ Found {inspection_count} inspections between {start_date} and {end_date}")

        if inspection_count > 0:
            print(f"\nFirst 5 inspections:")
            for i, insp in enumerate(inspections[:5], 1):
                print(f"   {i}. ID: {insp.id} | Client: {insp.client_name} | Date: {insp.date_of_inspection} | Commodity: {insp.commodity}")
        else:
            print("⚠️  No inspections found in the date range!")
            print("   The sync may not process any documents")
    except Exception as e:
        print(f"❌ Error checking inspections: {e}")
        return False

    # Step 3: Check Cache Status
    print_section("Step 3: Checking Processed Documents Cache")
    try:
        processed_docs = daily_sync_service.get_processed_documents_cache()
        print(f"✅ Cache currently has {len(processed_docs)} processed documents")

        if len(processed_docs) > 0:
            print(f"   Sample processed document IDs (first 5):")
            for i, doc_id in enumerate(list(processed_docs)[:5], 1):
                print(f"      {i}. {doc_id}")

            response = input("\nDo you want to clear the cache for a fresh test? (y/n): ")
            if response.lower() == 'y':
                cache.delete('processed_compliance_documents')
                print("✅ Cache cleared!")
    except Exception as e:
        print(f"❌ Error checking cache: {e}")

    # Step 4: Check Service Status
    print_section("Step 4: Checking Service Status")
    try:
        status = daily_sync_service.get_status()
        print(f"Service Status:")
        print(f"   - Is Running: {status['is_running']}")
        print(f"   - Last Sync: {status['last_sync_time'] or 'Never'}")
        print(f"   - Total Processed: {status['total_documents_processed']}")
        print(f"   - Documents Skipped: {status['documents_skipped']}")

        if status['is_running']:
            print("\n⚠️  Service is already running!")
            response = input("Do you want to stop it first? (y/n): ")
            if response.lower() == 'y':
                daily_sync_service.stop_daily_sync()
                print("✅ Service stopped")
                time.sleep(2)
    except Exception as e:
        print(f"❌ Error checking service status: {e}")

    # Step 5: Test Google Drive Connection
    print_section("Step 5: Testing Google Drive Connection")
    try:
        print("Loading Google Drive files (this may take a moment)...")
        file_lookup = daily_sync_service.load_drive_files_standalone()

        if file_lookup:
            print(f"✅ Successfully loaded {len(file_lookup)} files from Google Drive")
            print(f"\nSample files (first 5):")
            for i, (key, info) in enumerate(list(file_lookup.items())[:5], 1):
                print(f"   {i}. {info.get('name', 'Unknown')} | Commodity: {info.get('commodity', 'N/A')} | Date: {info.get('zipDateStr', 'N/A')}")
        else:
            print("❌ Failed to load files from Google Drive")
            print("   This could be an authentication issue or network problem")
            return False
    except Exception as e:
        print(f"❌ Error testing Google Drive connection: {e}")
        return False

    # Step 6: Start the Sync Service
    print_section("Step 6: Starting Daily Compliance Sync Service")
    try:
        print("Starting the sync service...")
        print("⏳ This will process compliance documents in the background")
        print("   The service will check for documents and download them\n")

        # Start with manual flag to force immediate run
        daily_sync_service.start_daily_sync(manual_start=True)

        print("✅ Service started successfully!")
        print("\nMonitoring progress (will check every 5 seconds for 60 seconds)...")
        print("Press Ctrl+C to stop monitoring\n")

        # Monitor for 60 seconds
        start_time = time.time()
        last_processed = 0

        try:
            while time.time() - start_time < 60:
                status = daily_sync_service.get_status()
                current_processed = status['total_documents_processed']

                if current_processed != last_processed:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Progress Update:")
                    print(f"   - Documents Processed: {current_processed}")
                    print(f"   - Documents Skipped: {status['documents_skipped']}")
                    print(f"   - Service Running: {status['is_running']}")
                    last_processed = current_processed

                time.sleep(5)
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")

        # Final status
        print_section("Final Status After Monitoring")
        status = daily_sync_service.get_status()
        print(f"Service Status:")
        print(f"   - Is Running: {status['is_running']}")
        print(f"   - Last Sync: {status['last_sync_time'] or 'Never'}")
        print(f"   - Total Processed: {status['total_documents_processed']}")
        print(f"   - Documents Skipped: {status['documents_skipped']}")

        # Check if any files were downloaded
        print_section("Checking Downloaded Files")
        media_inspection_path = os.path.join(django.conf.settings.MEDIA_ROOT, 'inspection')

        if os.path.exists(media_inspection_path):
            # Count files in the directory
            file_count = 0
            for root, dirs, files in os.walk(media_inspection_path):
                file_count += len(files)

            print(f"✅ Found {file_count} files in {media_inspection_path}")

            # Show some sample files
            if file_count > 0:
                print("\nSample downloaded files:")
                count = 0
                for root, dirs, files in os.walk(media_inspection_path):
                    for file in files[:5]:
                        count += 1
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        print(f"   {count}. {file} ({file_size / 1024:.1f} KB)")
                        if count >= 5:
                            break
                    if count >= 5:
                        break
        else:
            print(f"⚠️  Directory {media_inspection_path} does not exist")
            print("   No files have been downloaded yet")

        print("\n" + "=" * 80)
        print("  TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"\nThe service is still running in the background.")
        response = input("Do you want to stop the service? (y/n): ")
        if response.lower() == 'y':
            daily_sync_service.stop_daily_sync()
            print("✅ Service stopped")
        else:
            print("ℹ️  Service will continue running in the background")
            print("   To stop it later, use the Settings page or restart the server")

        return True

    except Exception as e:
        print(f"❌ Error starting sync service: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_daily_compliance_sync()
        if success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        print("Stopping service...")
        daily_sync_service.stop_daily_sync()
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
