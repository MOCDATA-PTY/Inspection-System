#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Internal Account Code for New Processed Meat Retailer
Account Code: RE-IND-RAW-NA-0222

This test checks:
1. What inspections have this account code
2. What client name is in the Google Sheets (Django Client table)
3. What client name is shown in the inspections
4. Whether they match or not
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

from main.models import FoodSafetyAgencyInspection, Client

print("\n" + "="*80)
print("CHECK INTERNAL ACCOUNT CODE: RE-IND-RAW-NA-0222")
print("Client: New Processed Meat Retailer")
print("="*80)

account_code = "RE-IND-RAW-NA-0222"

# STEP 1: Check Google Sheets (Django Client table)
print("\n" + "="*80)
print("STEP 1: Checking Google Sheets Client Table")
print("="*80)

print(f"\nSearching for account code: {account_code}")

google_client = Client.objects.filter(internal_account_code=account_code).first()

if google_client:
    print(f"\n✅ FOUND in Google Sheets Client table!")
    print(f"\n   Client Details:")
    print(f"   ├─ Client ID: {google_client.client_id}")
    print(f"   ├─ Client Name: {google_client.name}")
    print(f"   ├─ Account Code: {google_client.internal_account_code}")
    print(f"   ├─ Email: {google_client.email or 'None'}")
    print(f"   ├─ Created: {google_client.created_at}")
    print(f"   └─ Updated: {google_client.updated_at}")

    google_sheets_name = google_client.name
else:
    print(f"\n❌ NOT FOUND in Google Sheets Client table!")
    print(f"   This account code is not in the Django Client table.")
    print(f"   → You may need to sync Google Sheets first")
    google_sheets_name = None

# STEP 2: Check Inspections with this Account Code
print("\n" + "="*80)
print("STEP 2: Checking Inspections with Account Code")
print("="*80)

print(f"\nSearching for inspections with account code: {account_code}")

inspections = FoodSafetyAgencyInspection.objects.filter(
    internal_account_code=account_code
)

if inspections.exists():
    print(f"\n✅ FOUND {inspections.count()} inspection(s) with this account code!")

    for idx, insp in enumerate(inspections[:10], 1):
        print(f"\n   Inspection #{idx}:")
        print(f"   ├─ ID: {insp.id}")
        print(f"   ├─ Remote ID: {insp.remote_id}")
        print(f"   ├─ Client Name (in inspection): {insp.client_name}")
        print(f"   ├─ Account Code: {insp.internal_account_code}")
        print(f"   ├─ Date: {insp.date_of_inspection}")
        print(f"   ├─ Inspector: {insp.inspector_name}")
        print(f"   ├─ Commodity: {insp.commodity}")
        print(f"   └─ Last Synced: {insp.last_synced}")

    if inspections.count() > 10:
        print(f"\n   ... and {inspections.count() - 10} more inspection(s)")
else:
    print(f"\n❌ NO inspections found with this account code!")
    print(f"   This means the inspections don't have account codes populated yet.")
    print(f"   → You need to sync SQL Server to populate account codes")

# STEP 3: Comparison
print("\n" + "="*80)
print("STEP 3: Comparison - Google Sheets vs Inspections")
print("="*80)

if google_sheets_name and inspections.exists():
    print(f"\n📊 Comparing names:")
    print(f"   Google Sheets Name: {google_sheets_name}")

    # Check all inspections
    inspection_names = set()
    matches = 0
    mismatches = 0

    for insp in inspections:
        inspection_names.add(insp.client_name)
        if insp.client_name == google_sheets_name:
            matches += 1
        else:
            mismatches += 1

    print(f"\n   Inspection Names Found:")
    for idx, name in enumerate(inspection_names, 1):
        match_status = "✅ MATCH" if name == google_sheets_name else "❌ DIFFERENT"
        print(f"   {idx}. {name} ({match_status})")

    print(f"\n   Statistics:")
    print(f"   ├─ Total inspections: {inspections.count()}")
    print(f"   ├─ Matching Google Sheets: {matches} ({(matches/inspections.count()*100):.1f}%)")
    print(f"   └─ Different from Google Sheets: {mismatches} ({(mismatches/inspections.count()*100):.1f}%)")

    if mismatches > 0:
        print(f"\n   ⚠️  MISMATCH DETECTED!")
        print(f"   → Google Sheets has: '{google_sheets_name}'")
        print(f"   → Inspections have: {list(inspection_names)}")
        print(f"\n   To fix:")
        print(f"   1. Sync SQL Server to update inspection names")
        print(f"   2. The sync will match account code '{account_code}'")
        print(f"   3. And update inspection names to '{google_sheets_name}'")
    else:
        print(f"\n   ✅ ALL INSPECTIONS MATCH GOOGLE SHEETS!")
        print(f"   → Everything is synced correctly")

elif google_sheets_name and not inspections.exists():
    print(f"\n⚠️  ISSUE: Google Sheets has the client, but NO inspections found!")
    print(f"   Google Sheets Name: {google_sheets_name}")
    print(f"   Inspections: NONE")
    print(f"\n   Possible causes:")
    print(f"   1. Inspections haven't been synced from SQL Server yet")
    print(f"   2. Account codes aren't populated in inspections")
    print(f"\n   To fix:")
    print(f"   → Run SQL Server sync to fetch and populate inspections")

elif not google_sheets_name and inspections.exists():
    print(f"\n⚠️  ISSUE: Inspections exist, but Google Sheets has NO match!")
    print(f"   Inspections: {inspections.count()}")
    print(f"   Google Sheets: NO MATCH")
    print(f"\n   Inspection names:")
    for insp in inspections[:5]:
        print(f"   - {insp.client_name}")
    print(f"\n   To fix:")
    print(f"   → Sync Google Sheets to populate Client table with account code")

else:
    print(f"\n❌ NEITHER Google Sheets nor Inspections have this account code!")
    print(f"   Google Sheets: NOT FOUND")
    print(f"   Inspections: NOT FOUND")
    print(f"\n   To fix:")
    print(f"   1. Sync Google Sheets first (to populate Client table)")
    print(f"   2. Sync SQL Server second (to fetch inspections with account codes)")

# STEP 4: Recommendations
print("\n" + "="*80)
print("STEP 4: Recommendations")
print("="*80)

if google_sheets_name and inspections.exists():
    # Check if any mismatch
    needs_sync = False
    for insp in inspections:
        if insp.client_name != google_sheets_name:
            needs_sync = True
            break

    if needs_sync:
        print(f"\n📋 ACTION REQUIRED:")
        print(f"   1. Google Sheets has: '{google_sheets_name}'")
        print(f"   2. Some inspections have different names")
        print(f"   3. Run SQL Server sync to update inspection names")
        print(f"\n   Command:")
        print(f"   → Go to Settings → Click 'Sync SQL Server Inspections'")
        print(f"   → Or run: python test_sync_with_logging.py")
    else:
        print(f"\n✅ NO ACTION REQUIRED!")
        print(f"   Everything is already synced correctly")
        print(f"   Google Sheets name matches all inspections")

elif google_sheets_name and not inspections.exists():
    print(f"\n📋 ACTION REQUIRED:")
    print(f"   1. Google Sheets has client: '{google_sheets_name}'")
    print(f"   2. But no inspections found with this account code")
    print(f"   3. Run SQL Server sync to fetch inspections")
    print(f"\n   Command:")
    print(f"   → Go to Settings → Click 'Sync SQL Server Inspections'")

elif not google_sheets_name and inspections.exists():
    print(f"\n📋 ACTION REQUIRED:")
    print(f"   1. Inspections exist with account code '{account_code}'")
    print(f"   2. But Google Sheets doesn't have this account code")
    print(f"   3. Sync Google Sheets first to populate Client table")
    print(f"\n   Command:")
    print(f"   → Go to Settings → Click 'Sync Google Sheets'")

else:
    print(f"\n📋 ACTION REQUIRED:")
    print(f"   1. Sync Google Sheets FIRST")
    print(f"   2. Sync SQL Server SECOND")
    print(f"   3. This will populate both tables with account code data")

print("\n" + "="*80)
print("TEST COMPLETED")
print("="*80 + "\n")
