#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find "New Processed Meat Retailer" inspections
Search by client name to see what account codes they have
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
print("FIND 'NEW PROCESSED MEAT RETAILER' INSPECTIONS")
print("="*80)

# Search by client name
client_name_search = "New Processed Meat Retailer"

print(f"\nSearching for inspections with client name containing: '{client_name_search}'")

inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains=client_name_search
)

if inspections.exists():
    print(f"\n✅ FOUND {inspections.count()} inspection(s)!")

    # Check account codes
    with_account_code = 0
    without_account_code = 0

    print(f"\n" + "="*80)
    print(f"INSPECTION DETAILS")
    print("="*80)

    for idx, insp in enumerate(inspections[:10], 1):
        has_code = insp.internal_account_code is not None and insp.internal_account_code != ''
        if has_code:
            with_account_code += 1
        else:
            without_account_code += 1

        print(f"\nInspection #{idx}:")
        print(f"   ├─ ID: {insp.id}")
        print(f"   ├─ Remote ID: {insp.remote_id}")
        print(f"   ├─ Client Name: {insp.client_name}")
        print(f"   ├─ Account Code: {insp.internal_account_code or 'NONE/NULL'} {'✅' if has_code else '❌'}")
        print(f"   ├─ Date: {insp.date_of_inspection}")
        print(f"   ├─ Inspector: {insp.inspector_name}")
        print(f"   ├─ Commodity: {insp.commodity}")
        print(f"   └─ Last Synced: {insp.last_synced}")

    if inspections.count() > 10:
        print(f"\n... and {inspections.count() - 10} more inspection(s)")

        # Count all
        for insp in inspections[10:]:
            if insp.internal_account_code is not None and insp.internal_account_code != '':
                with_account_code += 1
            else:
                without_account_code += 1

    print(f"\n" + "="*80)
    print(f"ACCOUNT CODE STATISTICS")
    print("="*80)
    print(f"\n   Total inspections: {inspections.count()}")
    print(f"   ├─ With account code: {with_account_code} ({(with_account_code/inspections.count()*100):.1f}%)")
    print(f"   └─ WITHOUT account code: {without_account_code} ({(without_account_code/inspections.count()*100):.1f}%)")

    if without_account_code > 0:
        print(f"\n   ⚠️  {without_account_code} inspection(s) don't have account codes in database!")
        print(f"   → This is why the search by account code didn't find them")
        print(f"   → The inspection page might show account code from SQL Server directly")
        print(f"   → Need to run SQL Server sync to populate account codes")

else:
    print(f"\n❌ NO inspections found with client name containing '{client_name_search}'")

    # Try other searches
    print(f"\n   Trying partial search...")
    partial_inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains="Retailer"
    )

    if partial_inspections.exists():
        print(f"\n   ✅ Found {partial_inspections.count()} inspections with 'Retailer' in name:")
        for insp in partial_inspections[:5]:
            print(f"      - {insp.client_name}")
    else:
        print(f"\n   ❌ No inspections found even with partial search")

# Also check today's inspections
from datetime import date
today = date.today()

print(f"\n" + "="*80)
print(f"TODAY'S INSPECTIONS ({today})")
print("="*80)

todays_inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection=today
)

if todays_inspections.exists():
    print(f"\n✅ Found {todays_inspections.count()} inspection(s) from today:")

    for idx, insp in enumerate(todays_inspections[:10], 1):
        has_code = insp.internal_account_code is not None and insp.internal_account_code != ''
        code_display = insp.internal_account_code if has_code else 'NONE/NULL'

        print(f"\n   Inspection #{idx}:")
        print(f"   ├─ Client Name: {insp.client_name}")
        print(f"   ├─ Account Code: {code_display} {'✅' if has_code else '❌'}")
        print(f"   ├─ Date: {insp.date_of_inspection}")
        print(f"   └─ Inspector: {insp.inspector_name}")

        # Highlight if it's the one we're looking for
        if "Retailer" in insp.client_name or "RE-IND-RAW-NA-0222" == insp.internal_account_code:
            print(f"   ⭐ THIS MIGHT BE THE ONE YOU'RE LOOKING FOR!")
else:
    print(f"\n❌ No inspections from today")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

if inspections.exists():
    if without_account_code > 0:
        print(f"\n📋 FOUND THE ISSUE!")
        print(f"   ├─ Inspections exist: {inspections.count()}")
        print(f"   ├─ But account codes NOT populated in database: {without_account_code}")
        print(f"   └─ Inspection page shows account code from SQL Server directly")
        print(f"\n   Solution:")
        print(f"   1. Run SQL Server sync to populate account codes in Django database")
        print(f"   2. Then account code matching with Google Sheets will work")
        print(f"   3. Then name changes from Google Sheets will apply")
    else:
        print(f"\n✅ All inspections have account codes populated!")
else:
    print(f"\n❌ No inspections found with this client name")

print("\n" + "="*80 + "\n")
