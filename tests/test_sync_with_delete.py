#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the updated SQL Server sync that deletes all data first
"""
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.scheduled_sync_service import scheduled_sync_service
from main.models import FoodSafetyAgencyInspection
from datetime import datetime

print("=" * 80)
print("TESTING UPDATED SQL SERVER SYNC (DELETE ALL + PULL FRESH)")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Check count before sync
count_before = FoodSafetyAgencyInspection.objects.count()
print(f"📊 Inspection count BEFORE sync: {count_before:,}")

# Run the sync
print("\n🔄 Running SQL Server sync with DELETE ALL logic...\n")
try:
    success = scheduled_sync_service.sync_sql_server()

    if success:
        # Check count after sync
        count_after = FoodSafetyAgencyInspection.objects.count()

        print("\n" + "=" * 80)
        print("✅ SYNC COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"\n📊 Results:")
        print(f"   Before sync: {count_before:,} inspections")
        print(f"   After sync: {count_after:,} inspections")

        # Check for duplicates
        from django.db.models import Count
        duplicates = FoodSafetyAgencyInspection.objects.values('remote_id').annotate(
            count=Count('id')
        ).filter(count__gt=1).count()

        if duplicates == 0:
            print(f"\n✅ NO DUPLICATES FOUND! Database is clean.")
        else:
            print(f"\n⚠️  WARNING: Found {duplicates:,} duplicate remote_ids")

        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    else:
        print("\n❌ Sync failed!")

except Exception as e:
    print(f"\n❌ Error during sync: {e}")
    import traceback
    traceback.print_exc()
