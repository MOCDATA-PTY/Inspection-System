#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sync SQL Server and Check "Ethans butchery" Update
Account Code: RE-IND-RAW-NA-0222

This script will:
1. Run SQL Server sync to populate account codes
2. Match account code RE-IND-RAW-NA-0222 with Google Sheets
3. Update inspection names to "Ethans butchery"
4. Verify the change worked
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
print("SYNC AND UPDATE TO 'ETHANS BUTCHERY'")
print("Account Code: RE-IND-RAW-NA-0222")
print("="*80)

# STEP 1: Check Google Sheets name BEFORE sync
print("\n" + "="*80)
print("STEP 1: Checking Google Sheets Client Name (BEFORE SYNC)")
print("="*80)

account_code = "RE-IND-RAW-NA-0222"
google_client = Client.objects.filter(internal_account_code=account_code).first()

if google_client:
    print(f"\n✅ Google Sheets Client found:")
    print(f"   Account Code: {account_code}")
    print(f"   Client Name: {google_client.name}")
    print(f"   → This is the name that will be used for inspections!")
    google_sheets_name = google_client.name
else:
    print(f"\n❌ Google Sheets Client NOT found!")
    print(f"   You may need to sync Google Sheets first")
    google_sheets_name = None

# STEP 2: Check inspections BEFORE sync
print("\n" + "="*80)
print("STEP 2: Checking Inspections (BEFORE SYNC)")
print("="*80)

inspections_before = FoodSafetyAgencyInspection.objects.filter(
    internal_account_code=account_code
)

if inspections_before.exists():
    print(f"\n✅ Found {inspections_before.count()} inspection(s) with account code")
    print(f"\n   Current names:")
    for insp in inspections_before[:5]:
        print(f"   - {insp.client_name}")
else:
    print(f"\n❌ No inspections with account code '{account_code}'")
    print(f"   → Account codes not populated yet")
    print(f"   → SQL Server sync will populate them")

# STEP 3: Run SQL Server Sync
print("\n" + "="*80)
print("STEP 3: Running SQL Server Sync")
print("="*80)
print("\nThis will:")
print("  1. Fetch inspections from SQL Server WITH account codes")
print("  2. Match account code 'RE-IND-RAW-NA-0222' with Google Sheets")
print("  3. Update client names to 'Ethans butchery' (if that's what Google Sheets has)")
print("\n" + "="*80)

input("\nPress Enter to start sync (or Ctrl+C to cancel)...")

try:
    service = ScheduledSyncService()
    success = service.sync_sql_server()

    if not success:
        print("\n❌ SQL Server sync FAILED!")
        print("Check error messages above")
        sys.exit(1)

    print("\n✅ SQL Server sync COMPLETED!")

except Exception as e:
    print(f"\n❌ Error during sync: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# STEP 4: Check inspections AFTER sync
print("\n" + "="*80)
print("STEP 4: Checking Inspections (AFTER SYNC)")
print("="*80)

inspections_after = FoodSafetyAgencyInspection.objects.filter(
    internal_account_code=account_code
)

if inspections_after.exists():
    print(f"\n✅ Found {inspections_after.count()} inspection(s) with account code '{account_code}'")

    # Check names
    unique_names = set()
    for insp in inspections_after:
        unique_names.add(insp.client_name)

    print(f"\n   Client names found:")
    for name in unique_names:
        match_status = "✅ MATCHES Google Sheets" if name == google_sheets_name else "❌ DIFFERENT"
        print(f"   - '{name}' ({match_status})")

    # Show sample inspections
    print(f"\n   Sample inspections:")
    for idx, insp in enumerate(inspections_after[:5], 1):
        print(f"\n   Inspection #{idx}:")
        print(f"   ├─ ID: {insp.id}")
        print(f"   ├─ Client Name: {insp.client_name}")
        print(f"   ├─ Account Code: {insp.internal_account_code}")
        print(f"   ├─ Date: {insp.date_of_inspection}")
        print(f"   └─ Inspector: {insp.inspector_name}")

    if inspections_after.count() > 5:
        print(f"\n   ... and {inspections_after.count() - 5} more")

else:
    print(f"\n❌ No inspections found with account code '{account_code}' after sync")
    print(f"   This is unexpected - check the sync logs above")

# STEP 5: Verification
print("\n" + "="*80)
print("STEP 5: Verification")
print("="*80)

if google_sheets_name and inspections_after.exists():
    all_match = True
    for insp in inspections_after:
        if insp.client_name != google_sheets_name:
            all_match = False
            break

    if all_match:
        print(f"\n✅ SUCCESS! All inspections updated correctly!")
        print(f"\n   Google Sheets Name: '{google_sheets_name}'")
        print(f"   All {inspections_after.count()} inspection(s) now show: '{google_sheets_name}'")
        print(f"\n   ⭐ Your change from 'New Processed Meat Retailer' to 'Ethans butchery' worked!")
    else:
        print(f"\n⚠️  PARTIAL SUCCESS - Some names don't match")
        print(f"\n   Google Sheets Name: '{google_sheets_name}'")
        print(f"   Inspection Names: {list(unique_names)}")
        print(f"\n   Some inspections may need to be resynced")
else:
    print(f"\n⚠️  Could not verify - missing data")

# STEP 6: Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print(f"\n📊 Before Sync:")
print(f"   - Inspections with account code: {inspections_before.count()}")

print(f"\n📊 After Sync:")
print(f"   - Inspections with account code: {inspections_after.count()}")

if google_sheets_name:
    print(f"\n📊 Google Sheets:")
    print(f"   - Account Code: {account_code}")
    print(f"   - Client Name: '{google_sheets_name}'")

if inspections_after.exists():
    matching = sum(1 for insp in inspections_after if insp.client_name == google_sheets_name)
    print(f"\n📊 Match Status:")
    print(f"   - Total inspections: {inspections_after.count()}")
    print(f"   - Matching Google Sheets: {matching} ({(matching/inspections_after.count()*100):.1f}%)")
    print(f"   - Not matching: {inspections_after.count() - matching}")

print("\n" + "="*80)
print("TEST COMPLETED")
print("="*80 + "\n")
