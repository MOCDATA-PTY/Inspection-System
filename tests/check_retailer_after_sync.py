#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check if RE-IND-RAW-NA-0222 inspections updated to show Ethans butchery
Run this AFTER the sync completes
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
print("CHECKING RE-IND-RAW-NA-0222 INSPECTIONS")
print("="*80)

account_code = "RE-IND-RAW-NA-0222"

# Check Google Sheets
print(f"\n📊 Google Sheets:")
google_client = Client.objects.filter(internal_account_code=account_code).first()
if google_client:
    print(f"   Account Code: {account_code}")
    print(f"   Client Name: {google_client.name}")
else:
    print(f"   ❌ Not found in Google Sheets")

# Check inspections
print(f"\n📋 Inspections with account code {account_code}:")
inspections = FoodSafetyAgencyInspection.objects.filter(
    internal_account_code=account_code
)

if inspections.exists():
    print(f"   ✅ Found {inspections.count()} inspection(s)")

    # Show unique client names
    unique_names = set(insp.client_name for insp in inspections)
    print(f"\n   Client names in database:")
    for name in unique_names:
        count = inspections.filter(client_name=name).count()
        print(f"   - '{name}' ({count} inspections)")

    # Check if it matches Google Sheets
    if google_client:
        all_match = all(insp.client_name == google_client.name for insp in inspections)
        if all_match:
            print(f"\n   ✅ SUCCESS! All inspections now show: '{google_client.name}'")
        else:
            print(f"\n   ⚠️  Some inspections don't match Google Sheets")
            print(f"   Expected: '{google_client.name}'")

    # Show 3 sample inspections
    print(f"\n   Sample inspections:")
    for idx, insp in enumerate(inspections[:3], 1):
        print(f"\n   {idx}. Inspection #{insp.id}")
        print(f"      Client Name: {insp.client_name}")
        print(f"      Account Code: {insp.internal_account_code}")
        print(f"      Date: {insp.date_of_inspection}")
        print(f"      Inspector: {insp.inspector_name}")

else:
    print(f"   ❌ No inspections found with this account code")
    print(f"   The sync may not have completed yet")

print("\n" + "="*80 + "\n")
