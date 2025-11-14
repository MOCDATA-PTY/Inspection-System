#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run SQL Server Sync NOW
This will populate account codes and match with Google Sheets
"""
import os
import sys
import django

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.scheduled_sync_service import ScheduledSyncService
from main.models import FoodSafetyAgencyInspection, Client

print("\n" + "="*80)
print("RUN SQL SERVER SYNC - POPULATE ACCOUNT CODES & MATCH WITH GOOGLE SHEETS")
print("="*80)

# Check Google Sheets first
print("\n📊 Checking Google Sheets for 'Ethans butchery'...")
ethans_client = Client.objects.filter(internal_account_code="RE-IND-RAW-NA-0222").first()

if ethans_client:
    print(f"✅ Found in Google Sheets:")
    print(f"   Account Code: {ethans_client.internal_account_code}")
    print(f"   Client Name: {ethans_client.name}")
    print(f"\n   → This name will be used for all matching inspections!")
else:
    print(f"❌ Not found in Google Sheets!")
    print(f"   You may need to:")
    print(f"   1. Update Google Sheets to 'Ethans butchery'")
    print(f"   2. Sync Google Sheets first")

# Check inspections before
print(f"\n📋 Checking inspections BEFORE sync...")
before_inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains="New Processed Meat Retailer"
)
before_with_code = before_inspections.filter(
    internal_account_code__isnull=False
).exclude(internal_account_code='').count()

print(f"   Total inspections: {before_inspections.count()}")
print(f"   With account code: {before_with_code}")
print(f"   WITHOUT account code: {before_inspections.count() - before_with_code}")

print("\n" + "="*80)
print("STARTING SYNC")
print("="*80)
print("\nThis will:")
print("  1. Fetch all inspections from SQL Server WITH account codes")
print("  2. Populate internal_account_code field in Django database")
print("  3. Match account codes with Google Sheets")
print("  4. Update client names to Google Sheets names (e.g., 'Ethans butchery')")
print("\n" + "="*80)

input("\nPress Enter to start (or Ctrl+C to cancel)...")

try:
    service = ScheduledSyncService()
    success = service.sync_sql_server()

    if success:
        print("\n" + "="*80)
        print("CHECKING RESULTS")
        print("="*80)

        # Check inspections after
        after_inspections = FoodSafetyAgencyInspection.objects.filter(
            internal_account_code="RE-IND-RAW-NA-0222"
        )

        if after_inspections.exists():
            print(f"\n✅ Found {after_inspections.count()} inspections with account code RE-IND-RAW-NA-0222")

            # Check names
            unique_names = set(insp.client_name for insp in after_inspections)
            print(f"\n   Client names:")
            for name in unique_names:
                count = after_inspections.filter(client_name=name).count()
                print(f"   - '{name}' ({count} inspections)")

            # Sample
            print(f"\n   Sample inspection:")
            sample = after_inspections.first()
            print(f"   ├─ Client Name: {sample.client_name}")
            print(f"   ├─ Account Code: {sample.internal_account_code}")
            print(f"   └─ Date: {sample.date_of_inspection}")

            if ethans_client and sample.client_name == ethans_client.name:
                print(f"\n   ✅ SUCCESS! Name updated to '{ethans_client.name}'!")
            elif ethans_client:
                print(f"\n   ⚠️  Name is '{sample.client_name}', expected '{ethans_client.name}'")
            else:
                print(f"\n   ℹ️  Using SQL Server name (Google Sheets not updated yet)")
        else:
            print(f"\n⚠️  No inspections found with account code after sync")
            print(f"   Check sync logs above for issues")

    else:
        print("\n❌ Sync failed - check error messages above")

except KeyboardInterrupt:
    print("\n\n❌ Cancelled by user")
    sys.exit(1)
except Exception as e:
    print(f"\n\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
