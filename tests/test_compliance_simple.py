#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Daily Compliance Sync Test
Non-interactive test to verify daily compliance sync pulls data correctly
"""

import os
import sys
import django
import time
from datetime import datetime

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

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def main():
    print_header("DAILY COMPLIANCE SYNC TEST - SIMPLE VERSION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Test 1: Check System Settings
    print_header("1. System Settings")
    try:
        settings = SystemSettings.get_settings()
        print(f"[OK] Daily Sync Enabled: {settings.compliance_daily_sync_enabled}")
        print(f"[OK] Skip Processed: {settings.compliance_skip_processed}")
        print(f"[OK] Sync Interval: {settings.compliance_sync_interval_hours} hours")
        print(f"[OK] Last Processed: {settings.compliance_last_processed_date or 'Never'}")

        if not settings.compliance_daily_sync_enabled:
            print("\n[WARNING] Daily sync is DISABLED - enabling it now...")
            settings.compliance_daily_sync_enabled = True
            settings.save()
            print("[OK] Enabled!")
    except Exception as e:
        print(f"[ERROR] Failed to load settings: {e}")
        return False

    # Test 2: Check Inspections
    print_header("2. Available Inspections")
    try:
        from datetime import date
        start_date = date(2025, 10, 1)
        end_date = date(2026, 4, 1)

        inspections = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection__gte=start_date,
            date_of_inspection__lt=end_date
        ).order_by('-date_of_inspection')

        count = inspections.count()
        print(f"[OK] Found {count} inspections between {start_date} and {end_date}")

        if count > 0:
            print("\nSample inspections:")
            for i, insp in enumerate(inspections[:3], 1):
                print(f"   {i}. ID={insp.id}, Client={insp.client_name}, Date={insp.date_of_inspection}")
    except Exception as e:
        print(f"[ERROR] Failed to check inspections: {e}")

    # Test 3: Check Cache
    print_header("3. Processed Documents Cache")
    try:
        processed = daily_sync_service.get_processed_documents_cache()
        print(f"[OK] Cache has {len(processed)} processed documents")

        # Clear cache for fresh test
        cache.delete('processed_compliance_documents')
        print("[OK] Cache cleared for fresh test")
    except Exception as e:
        print(f"[ERROR] Failed to check cache: {e}")

    # Test 4: Check Service Status
    print_header("4. Service Status (Before)")
    try:
        status = daily_sync_service.get_status()
        print(f"[OK] Is Running: {status['is_running']}")
        print(f"[OK] Last Sync: {status['last_sync_time'] or 'Never'}")
        print(f"[OK] Total Processed: {status['total_documents_processed']}")

        if status['is_running']:
            print("\n[WARNING] Service already running - stopping it...")
            daily_sync_service.stop_daily_sync()
            time.sleep(2)
            print("[OK] Stopped")
    except Exception as e:
        print(f"[ERROR] Failed to check status: {e}")

    # Test 5: Test Google Drive Connection
    print_header("5. Google Drive Connection Test")
    try:
        print("[...] Loading Google Drive files (this may take a moment)...")
        file_lookup = daily_sync_service.load_drive_files_standalone()

        if file_lookup:
            print(f"[OK] Successfully loaded {len(file_lookup)} files from Google Drive")

            # Show sample files
            sample_count = 0
            for key, info in file_lookup.items():
                if sample_count < 3:
                    print(f"   - {info.get('name', 'Unknown')}")
                    sample_count += 1
                else:
                    break
        else:
            print("[ERROR] Failed to load files from Google Drive")
            return False
    except Exception as e:
        print(f"[ERROR] Google Drive connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 6: Start Sync Service
    print_header("6. Starting Daily Compliance Sync")
    try:
        print("[...] Starting sync service with manual flag...")
        daily_sync_service.start_daily_sync(manual_start=True)
        print("[OK] Service started!")

        print("\n[...] Monitoring progress for 30 seconds...")
        print("      (The service runs in background)\n")

        # Monitor for 30 seconds
        last_processed = 0
        for i in range(6):  # 6 x 5 seconds = 30 seconds
            time.sleep(5)
            status = daily_sync_service.get_status()
            current_processed = status['total_documents_processed']

            if current_processed != last_processed:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Processed: {current_processed}, Skipped: {status['documents_skipped']}")
                last_processed = current_processed
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No new documents processed yet...")

        print("\n[...] Final check after 30 seconds:")

    except Exception as e:
        print(f"[ERROR] Failed to start service: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 7: Final Status
    print_header("7. Service Status (After)")
    try:
        status = daily_sync_service.get_status()
        print(f"[OK] Is Running: {status['is_running']}")
        print(f"[OK] Last Sync: {status['last_sync_time']}")
        print(f"[OK] Total Processed: {status['total_documents_processed']}")
        print(f"[OK] Documents Skipped: {status['documents_skipped']}")
    except Exception as e:
        print(f"[ERROR] Failed to get final status: {e}")

    # Test 8: Check Downloaded Files
    print_header("8. Downloaded Files Check")
    try:
        import django.conf
        media_path = os.path.join(django.conf.settings.MEDIA_ROOT, 'inspection')

        if os.path.exists(media_path):
            file_count = sum(len(files) for _, _, files in os.walk(media_path))
            print(f"[OK] Found {file_count} files in {media_path}")

            # Show sample files
            if file_count > 0:
                print("\nSample files:")
                count = 0
                for root, dirs, files in os.walk(media_path):
                    for file in files[:3]:
                        count += 1
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        print(f"   {count}. {file} ({size / 1024:.1f} KB)")
                        if count >= 3:
                            break
                    if count >= 3:
                        break
        else:
            print(f"[INFO] Directory {media_path} does not exist yet")
    except Exception as e:
        print(f"[ERROR] Failed to check files: {e}")

    # Cleanup
    print_header("9. Cleanup")
    print("[...] Stopping the service...")
    try:
        daily_sync_service.stop_daily_sync()
        print("[OK] Service stopped")
    except Exception as e:
        print(f"[ERROR] Failed to stop service: {e}")

    print_header("TEST COMPLETED")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n[SUMMARY]")
    print("The test has completed. Check the output above for:")
    print("  - Google Drive connection status")
    print("  - Number of files loaded from Drive")
    print("  - Documents processed during sync")
    print("  - Downloaded files in media/inspection folder")

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Test stopped by user")
        daily_sync_service.stop_daily_sync()
        sys.exit(130)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
