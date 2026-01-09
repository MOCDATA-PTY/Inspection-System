#!/usr/bin/env python
"""
Test script to verify inspection data compliance and integrity.
Checks that inspections have valid, complete data.
OPTIMIZED VERSION - Uses bulk queries for better performance.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, ClientAllocation
from datetime import datetime
from django.db.models import Q, Count
from collections import defaultdict

print("\n" + "="*80)
print("INSPECTION DATA COMPLIANCE TEST (OPTIMIZED)")
print("="*80)

# Get total count
total_count = FoodSafetyAgencyInspection.objects.count()
print(f"\n[INFO] Total inspections in database: {total_count:,}\n")

VALID_COMMODITIES = ['POULTRY', 'RAW', 'PMP', 'EGGS', 'EGG']

print("="*80)
print("RUNNING COMPLIANCE TESTS")
print("="*80)

# Test 1: Required Fields Check (using bulk queries)
print("\n[TEST 1] Checking required fields...")

# Check each required field efficiently
missing_commodity = FoodSafetyAgencyInspection.objects.filter(
    Q(commodity__isnull=True) | Q(commodity='')
).count()

missing_date = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__isnull=True
).count()

missing_inspector = FoodSafetyAgencyInspection.objects.filter(
    Q(inspector_name__isnull=True) | Q(inspector_name='')
).count()

missing_client = FoodSafetyAgencyInspection.objects.filter(
    Q(client_name__isnull=True) | Q(client_name='') | Q(client_name='-')
).count()

missing_account_code = FoodSafetyAgencyInspection.objects.filter(
    Q(internal_account_code__isnull=True) | Q(internal_account_code='')
).count()

missing_product = FoodSafetyAgencyInspection.objects.filter(
    Q(product_name__isnull=True) | Q(product_name='')
).count()

print(f"   Missing commodity: {missing_commodity}")
print(f"   Missing date: {missing_date}")
print(f"   Missing inspector name: {missing_inspector}")
print(f"   Missing client name (or '-'): {missing_client}")
print(f"   Missing account code: {missing_account_code}")
print(f"   Missing product name: {missing_product}")

total_missing = missing_commodity + missing_date + missing_inspector + missing_client + missing_account_code + missing_product

if total_missing > 0:
    print(f"   [WARNING] {total_missing} total missing field issues found")
else:
    print(f"   [OK] All inspections have required fields")

# Test 2: Valid Commodity Values
print("\n[TEST 2] Checking commodity values...")
invalid_commodities = FoodSafetyAgencyInspection.objects.exclude(
    commodity__in=VALID_COMMODITIES
).exclude(commodity__isnull=True).values_list('commodity', flat=True).distinct()

invalid_commodity_count = FoodSafetyAgencyInspection.objects.exclude(
    commodity__in=VALID_COMMODITIES
).exclude(commodity__isnull=True).count()

if invalid_commodity_count > 0:
    print(f"   [WARNING] {invalid_commodity_count} inspections have invalid commodity values")
    print(f"   Invalid values found: {list(invalid_commodities)}")
else:
    print(f"   [OK] All inspections have valid commodity values")

# Test 3: Time Logic Check
print("\n[TEST 3] Checking inspection time logic...")

# Find inspections where end time <= start time
time_logic_issues = 0
inspections_with_times = FoodSafetyAgencyInspection.objects.filter(
    start_of_inspection__isnull=False,
    end_of_inspection__isnull=False
)

print(f"   Checking {inspections_with_times.count()} inspections with both start and end times...")

for inspection in inspections_with_times:
    if inspection.end_of_inspection <= inspection.start_of_inspection:
        time_logic_issues += 1

if time_logic_issues > 0:
    print(f"   [WARNING] {time_logic_issues} inspections have end time <= start time")
else:
    print(f"   [OK] All inspections have valid time logic")

# Test 4: Client Name Matching with SQL Server
print("\n[TEST 4] Checking client name matching with SQL Server...")

# Build a lookup dictionary of account codes to client names
print("   Loading SQL Server client data...")
client_lookup = {}
for client in ClientAllocation.objects.filter(eclick_name__isnull=False).exclude(eclick_name=''):
    if client.internal_account_code:
        client_lookup[client.internal_account_code] = client.eclick_name.strip().lower()

print(f"   Loaded {len(client_lookup)} clients from SQL Server")

# Check inspections
client_mismatch_count = 0
missing_client_count = 0

inspections_with_codes = FoodSafetyAgencyInspection.objects.filter(
    internal_account_code__isnull=False
).exclude(internal_account_code='').exclude(client_name__isnull=True)

print(f"   Checking {inspections_with_codes.count()} inspections with account codes...")

for inspection in inspections_with_codes:
    account_code = inspection.internal_account_code

    if account_code in client_lookup:
        expected_name = client_lookup[account_code]
        actual_name = inspection.client_name.strip().lower() if inspection.client_name else ''

        if actual_name != expected_name and actual_name != '-':
            client_mismatch_count += 1
    else:
        if inspection.client_name != '-':
            missing_client_count += 1

if client_mismatch_count > 0 or missing_client_count > 0:
    print(f"   [WARNING] {client_mismatch_count} client name mismatches")
    print(f"   [WARNING] {missing_client_count} account codes not found in SQL Server")
else:
    print(f"   [OK] All client names match SQL Server data")

# Test 5: Date Validity
print("\n[TEST 5] Checking date validity...")

today = datetime.now().date()
future_dates = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gt=today
).count()

if future_dates > 0:
    print(f"   [WARNING] {future_dates} inspections have future dates")
else:
    print(f"   [OK] All inspections have valid dates (not in future)")

# Calculate compliant vs non-compliant
print("\n" + "="*80)
print("CALCULATING COMPLIANCE SUMMARY")
print("="*80)

# An inspection is non-compliant if it has any issues
non_compliant_ids = set()

# Add IDs with missing fields
non_compliant_ids.update(
    FoodSafetyAgencyInspection.objects.filter(
        Q(commodity__isnull=True) | Q(commodity='') |
        Q(date_of_inspection__isnull=True) |
        Q(inspector_name__isnull=True) | Q(inspector_name='') |
        Q(client_name__isnull=True) | Q(client_name='') | Q(client_name='-') |
        Q(internal_account_code__isnull=True) | Q(internal_account_code='') |
        Q(product_name__isnull=True) | Q(product_name='')
    ).values_list('id', flat=True)
)

# Add IDs with invalid commodities
non_compliant_ids.update(
    FoodSafetyAgencyInspection.objects.exclude(
        commodity__in=VALID_COMMODITIES
    ).exclude(commodity__isnull=True).values_list('id', flat=True)
)

# Add IDs with future dates
non_compliant_ids.update(
    FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gt=today
    ).values_list('id', flat=True)
)

non_compliant_count = len(non_compliant_ids)
compliant_count = total_count - non_compliant_count

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"\nTotal Inspections: {total_count:,}")
print(f"Compliant Inspections: {compliant_count:,} ({(compliant_count/total_count*100):.1f}%)")
print(f"Non-Compliant Inspections: {non_compliant_count:,} ({(non_compliant_count/total_count*100):.1f}%)")

# Show sample non-compliant inspections
if non_compliant_count > 0:
    print("\n" + "="*80)
    print("SAMPLE NON-COMPLIANT INSPECTIONS (First 10)")
    print("="*80)

    non_compliant_samples = FoodSafetyAgencyInspection.objects.filter(
        id__in=list(non_compliant_ids)[:10]
    )

    for i, inspection in enumerate(non_compliant_samples, 1):
        issues = []

        if not inspection.commodity:
            issues.append("Missing commodity")
        elif inspection.commodity not in VALID_COMMODITIES:
            issues.append(f"Invalid commodity: {inspection.commodity}")

        if not inspection.date_of_inspection:
            issues.append("Missing date")
        elif inspection.date_of_inspection > today:
            issues.append("Future date")

        if not inspection.inspector_name:
            issues.append("Missing inspector name")

        if not inspection.client_name or inspection.client_name == '-':
            issues.append("Missing client name")

        if not inspection.internal_account_code:
            issues.append("Missing account code")

        if not inspection.product_name:
            issues.append("Missing product name")

        print(f"\n[{i}] Inspection ID: {inspection.id} | Remote ID: {inspection.remote_id}")
        print(f"    Date: {inspection.date_of_inspection}")
        print(f"    Client: {inspection.client_name}")
        print(f"    Issues: {', '.join(issues)}")

    if non_compliant_count > 10:
        print(f"\n... and {non_compliant_count - 10} more non-compliant inspections")

# Final verdict
print("\n" + "="*80)
if non_compliant_count == 0:
    print("[SUCCESS] ALL INSPECTIONS ARE COMPLIANT!")
    print("All inspections have valid, complete data.")
else:
    print(f"[WARNING] {non_compliant_count:,} INSPECTIONS NEED ATTENTION")
    print("Review the issues above to improve data quality.")
print("="*80 + "\n")
