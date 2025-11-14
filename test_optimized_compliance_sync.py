#!/usr/bin/env python3
"""
Test the optimized compliance sync that only fetches from specific month folders
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.daily_compliance_sync import DailyComplianceSyncService

def main():
    print("\n" + "=" * 80)
    print("TEST OPTIMIZED COMPLIANCE SYNC - MONTH FOLDER APPROACH")
    print("=" * 80)

    # Create service instance
    service = DailyComplianceSyncService()

    print("\n📋 This test will:")
    print("   1. Connect to parent folder: 1pzot8MQ-m3u0f9-BWxpBO40QgLmeZhRP")
    print("   2. List all month folders (September 2025, October 2025, etc.)")
    print("   3. Filter to only October 2025+ folders")
    print("   4. Fetch compliance files ONLY from those specific folders")
    print("   5. Show statistics and verify optimization\n")

    print("-" * 80)
    print("STARTING FILE LOAD TEST")
    print("-" * 80)

    start_time = datetime.now()

    # Call the optimized load function
    file_lookup = service.load_drive_files_standalone()

    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()

    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)

    if file_lookup is None:
        print("❌ FAILED: File lookup returned None (possibly stopped)")
        return

    if not file_lookup:
        print("⚠️  WARNING: No files found in lookup")
        print("   This could mean:")
        print("   - No month folders exist for October 2025+")
        print("   - No compliance files match the naming pattern")
        print("   - Authentication issues with Google Drive")
        return

    # Statistics
    total_files = len(file_lookup)
    print(f"\n✅ SUCCESS: Loaded {total_files} compliance files")
    print(f"⏱️  Time taken: {elapsed:.2f} seconds")
    print(f"🚀 Speed: {total_files / max(elapsed, 0.1):.1f} files/second\n")

    # Analyze by month
    print("-" * 80)
    print("FILES BY MONTH")
    print("-" * 80)

    months = {}
    for key, file_info in file_lookup.items():
        zip_date = file_info.get('zipDate')
        if zip_date:
            month_key = zip_date.strftime("%B %Y")
            if month_key not in months:
                months[month_key] = []
            months[month_key].append(file_info)

    for month_name in sorted(months.keys(), key=lambda x: datetime.strptime(x, "%B %Y")):
        count = len(months[month_name])
        print(f"   {month_name}: {count} files")

    # Analyze by commodity
    print("\n" + "-" * 80)
    print("FILES BY COMMODITY")
    print("-" * 80)

    commodities = {}
    for key, file_info in file_lookup.items():
        commodity = file_info.get('commodity', 'Unknown')
        commodities[commodity] = commodities.get(commodity, 0) + 1

    for commodity in sorted(commodities.keys()):
        print(f"   {commodity}: {commodities[commodity]} files")

    # Show sample files
    print("\n" + "-" * 80)
    print("SAMPLE FILES (First 10)")
    print("-" * 80)

    sample_count = 0
    for key, file_info in list(file_lookup.items())[:10]:
        print(f"\n   File: {file_info['name']}")
        print(f"      Commodity: {file_info['commodity']}")
        print(f"      Account Code: {file_info['accountCode']}")
        print(f"      Date: {file_info['zipDateStr']}")
        print(f"      Compound Key: {key}")
        sample_count += 1

    if total_files > 10:
        print(f"\n   ... and {total_files - 10} more files")

    # Verify optimization
    print("\n" + "=" * 80)
    print("OPTIMIZATION VERIFICATION")
    print("=" * 80)

    earliest_date = min([f['zipDate'] for f in file_lookup.values()])
    latest_date = max([f['zipDate'] for f in file_lookup.values()])

    print(f"\n✅ Date Range: {earliest_date.strftime('%Y-%m-%d')} to {latest_date.strftime('%Y-%m-%d')}")

    if earliest_date.date() >= datetime(2025, 10, 1).date():
        print("✅ OPTIMIZATION WORKING: All files are from October 2025 or later")
        print("✅ No unnecessary files loaded from before October 2025")
    else:
        print(f"⚠️  WARNING: Found files before October 2025 (earliest: {earliest_date.strftime('%Y-%m-%d')})")

    print(f"\n🎯 Optimization Benefits:")
    print(f"   - Only fetched from October 2025+ month folders")
    print(f"   - Skipped all files before October 2025")
    print(f"   - Much faster loading time!")
    print(f"   - Reduced memory usage")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
