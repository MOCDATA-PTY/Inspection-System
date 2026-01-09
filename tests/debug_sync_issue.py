#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Sync Issue - Check what's happening with client name updates
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
print("DEBUG: CHECKING SYNC ISSUE")
print("="*80)

account_code = "RE-IND-RAW-NA-0222"

# STEP 1: Check Client table (Google Sheets data)
print("\n" + "="*80)
print("STEP 1: Client Table (Google Sheets Data)")
print("="*80)

client = Client.objects.filter(internal_account_code=account_code).first()

if client:
    print(f"\n✅ Found in Client table:")
    print(f"   Client ID: {client.client_id}")
    print(f"   Client Name: '{client.name}'")
    print(f"   Account Code: {client.internal_account_code}")
    print(f"   Email: {client.email or 'None'}")
    print(f"   Created: {client.created_at}")
    print(f"   Updated: {client.updated_at}")
    print(f"\n   👉 This is what Google Sheets sync loaded")
    print(f"   👉 This is what should be used for inspections")

    expected_name = client.name
else:
    print(f"\n❌ NOT found in Client table!")
    print(f"   Account code '{account_code}' is not in the Client table")
    print(f"   This means Google Sheets doesn't have this account code")
    expected_name = None

# STEP 2: Check all clients with "Ethan" in name
print("\n" + "="*80)
print("STEP 2: All Clients with 'Ethan' in Name")
print("="*80)

ethan_clients = Client.objects.filter(name__icontains="Ethan")
print(f"\nFound {ethan_clients.count()} client(s) with 'Ethan' in name:")
for c in ethan_clients:
    print(f"\n   Client:")
    print(f"   ├─ Name: '{c.name}'")
    print(f"   ├─ Account Code: {c.internal_account_code}")
    print(f"   └─ Updated: {c.updated_at}")

# STEP 3: Check inspections
print("\n" + "="*80)
print("STEP 3: Inspections with Account Code " + account_code)
print("="*80)

inspections = FoodSafetyAgencyInspection.objects.filter(
    internal_account_code=account_code
)

if inspections.exists():
    print(f"\n✅ Found {inspections.count()} inspection(s)")

    # Get unique client names
    unique_names = set(insp.client_name for insp in inspections)

    print(f"\n   Client names in inspections:")
    for name in unique_names:
        count = inspections.filter(client_name=name).count()

        if expected_name:
            if name == expected_name:
                status = "✅ MATCHES Client table"
            else:
                status = f"❌ DIFFERENT! Expected: '{expected_name}'"
        else:
            status = "⚠️ No Client table entry to compare"

        print(f"   - '{name}' ({count} inspections) {status}")

    # Show 3 sample inspections
    print(f"\n   Sample inspections:")
    for idx, insp in enumerate(inspections[:3], 1):
        print(f"\n   {idx}. Inspection #{insp.id}")
        print(f"      ├─ Client Name: '{insp.client_name}'")
        print(f"      ├─ Account Code: {insp.internal_account_code}")
        print(f"      ├─ Date: {insp.date_of_inspection}")
        print(f"      └─ Inspector: {insp.inspector_name}")

else:
    print(f"\n❌ No inspections found with account code '{account_code}'")
    print(f"   This means:")
    print(f"   1. Either no inspections exist for this account code in SQL Server")
    print(f"   2. Or the inspections haven't been synced yet")

# STEP 4: Check recent sync
print("\n" + "="*80)
print("STEP 4: Check If Syncs Ran Recently")
print("="*80)

# Check if any inspections were synced recently (last 10 minutes)
from datetime import datetime, timedelta

# Can't check last_synced because that field doesn't exist
# Instead check by updated_at
recent_time = datetime.now() - timedelta(minutes=10)

# Check Client table updates
recent_clients = Client.objects.filter(updated_at__gte=recent_time).count()
print(f"\n   Clients updated in last 10 minutes: {recent_clients}")

if client and client.updated_at:
    time_since_update = datetime.now().astimezone() - client.updated_at
    print(f"   Account '{account_code}' last updated: {time_since_update.total_seconds()/60:.1f} minutes ago")

# STEP 5: Diagnosis
print("\n" + "="*80)
print("STEP 5: DIAGNOSIS")
print("="*80)

if not client:
    print(f"\n❌ PROBLEM: Client table doesn't have account code '{account_code}'")
    print(f"\n   Possible causes:")
    print(f"   1. Google Sheets doesn't have this account code in Column H")
    print(f"   2. Google Sheets sync failed")
    print(f"   3. Account code in Google Sheets is spelled differently")
    print(f"\n   Solution:")
    print(f"   1. Check Google Sheets - find '{account_code}' in Column H")
    print(f"   2. Make sure Column J has the client name you want")
    print(f"   3. Click 'Sync Clients' button")

elif not inspections.exists():
    print(f"\n❌ PROBLEM: No inspections with account code '{account_code}'")
    print(f"\n   Possible causes:")
    print(f"   1. Inspections haven't been synced from SQL Server yet")
    print(f"   2. SQL Server doesn't have inspections for this account code")
    print(f"\n   Solution:")
    print(f"   1. Click 'Sync Inspections' button")
    print(f"   2. Wait for sync to complete (5-10 minutes)")

elif expected_name and all(insp.client_name == expected_name for insp in inspections):
    print(f"\n✅ NO PROBLEM - Everything is synced correctly!")
    print(f"\n   Client table has: '{expected_name}'")
    print(f"   All {inspections.count()} inspections show: '{expected_name}'")
    print(f"\n   If you're seeing a different name, try:")
    print(f"   1. Hard refresh your browser (Ctrl+F5)")
    print(f"   2. Clear browser cache")

elif expected_name:
    print(f"\n❌ PROBLEM: Inspection names don't match Client table!")
    print(f"\n   Client table has: '{expected_name}'")
    print(f"   But inspections show: {unique_names}")
    print(f"\n   This means:")
    print(f"   1. You synced Clients (updated Client table)")
    print(f"   2. But didn't sync Inspections (didn't update inspection records)")
    print(f"\n   Solution:")
    print(f"   1. Click 'Sync Inspections' button on home page")
    print(f"   2. Wait for it to complete (5-10 minutes)")
    print(f"   3. The sync will match account code '{account_code}' with Client table")
    print(f"   4. And update all inspection names to '{expected_name}'")

# STEP 6: Check what you should see
print("\n" + "="*80)
print("STEP 6: WHAT YOU SHOULD SEE")
print("="*80)

if expected_name:
    print(f"\n   After syncing BOTH Clients and Inspections:")
    print(f"   ✅ Client table: '{expected_name}'")
    print(f"   ✅ Inspection page: '{expected_name}'")
    print(f"   ✅ All {inspections.count() if inspections.exists() else '???'} inspections: '{expected_name}'")

    print(f"\n   If you're seeing something different:")
    print(f"   1. Check what Google Sheets Column J shows for account '{account_code}'")
    print(f"   2. That's what should be syncing through")

print("\n" + "="*80 + "\n")
