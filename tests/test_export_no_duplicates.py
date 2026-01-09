#!/usr/bin/env python3
"""
Test that the export has NO DUPLICATES, especially for RAW inspections
This verifies the composite key deduplication (commodity, remote_id) is working
"""
import os
import sys
import django
from datetime import datetime, timedelta
from collections import Counter

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 120)
print("DUPLICATE CHECK TEST FOR EXPORT")
print("=" * 120)

# Test with December 5, 2025 (limited date for faster testing)
start_date = datetime(2025, 12, 5).date()
end_date = datetime(2025, 12, 5).date()

print(f"\nTesting date range: {start_date} to {end_date}")

# Run the EXACT query from export_sheet function
inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=start_date,
    date_of_inspection__lte=end_date
).select_related(
    'sent_by', 'rfi_uploaded_by', 'invoice_uploaded_by'
).distinct('commodity', 'remote_id').order_by('commodity', 'remote_id', '-date_of_inspection', 'inspector_name')

total_count = inspections.count()
print(f"Total inspections returned: {total_count}")

# Create list of (commodity, remote_id) tuples
composite_keys = [(insp.commodity, insp.remote_id) for insp in inspections]

# Check for duplicates
key_counts = Counter(composite_keys)
duplicates = {key: count for key, count in key_counts.items() if count > 1}

print("\n" + "=" * 120)
print("DUPLICATE CHECK RESULTS")
print("=" * 120)

if duplicates:
    print(f"\n[ERROR] FOUND {len(duplicates)} DUPLICATE COMPOSITE KEYS!")
    print("\nDuplicate (commodity, remote_id) combinations:")
    for (commodity, remote_id), count in duplicates.items():
        print(f"  - {commodity}-{remote_id}: appears {count} times")

        # Show details of duplicates
        dupes = [insp for insp in inspections if insp.commodity == commodity and insp.remote_id == remote_id]
        for insp in dupes:
            print(f"      {insp.client_name} | {insp.date_of_inspection} | {insp.inspector_name}")
else:
    print("\n[OK] NO DUPLICATES FOUND - All (commodity, remote_id) combinations are unique!")

# Specifically check RAW inspections
print("\n" + "=" * 120)
print("RAW INSPECTIONS CHECK")
print("=" * 120)

raw_inspections = [insp for insp in inspections if insp.commodity == 'RAW']
raw_keys = [(insp.commodity, insp.remote_id) for insp in raw_inspections]
raw_key_counts = Counter(raw_keys)
raw_duplicates = {key: count for key, count in raw_key_counts.items() if count > 1}

print(f"\nTotal RAW inspections: {len(raw_inspections)}")
print(f"Unique RAW remote_ids: {len(set(insp.remote_id for insp in raw_inspections))}")

if raw_duplicates:
    print(f"\n[ERROR] FOUND {len(raw_duplicates)} DUPLICATE RAW INSPECTIONS!")
    for (commodity, remote_id), count in raw_duplicates.items():
        print(f"  - RAW-{remote_id}: appears {count} times")
else:
    print("\n[OK] NO RAW DUPLICATES - All RAW inspections are unique!")

# Check PMP inspections too
print("\n" + "=" * 120)
print("PMP INSPECTIONS CHECK")
print("=" * 120)

pmp_inspections = [insp for insp in inspections if insp.commodity == 'PMP']
pmp_keys = [(insp.commodity, insp.remote_id) for insp in pmp_inspections]
pmp_key_counts = Counter(pmp_keys)
pmp_duplicates = {key: count for key, count in pmp_key_counts.items() if count > 1}

print(f"\nTotal PMP inspections: {len(pmp_inspections)}")
print(f"Unique PMP remote_ids: {len(set(insp.remote_id for insp in pmp_inspections))}")

if pmp_duplicates:
    print(f"\n[ERROR] FOUND {len(pmp_duplicates)} DUPLICATE PMP INSPECTIONS!")
    for (commodity, remote_id), count in pmp_duplicates.items():
        print(f"  - PMP-{remote_id}: appears {count} times")
else:
    print("\n[OK] NO PMP DUPLICATES - All PMP inspections are unique!")

# Check if same remote_id exists in both RAW and PMP (this is OK!)
print("\n" + "=" * 120)
print("CROSS-COMMODITY CHECK (RAW vs PMP with same remote_id)")
print("=" * 120)

raw_ids = set(insp.remote_id for insp in raw_inspections)
pmp_ids = set(insp.remote_id for insp in pmp_inspections)
shared_ids = raw_ids & pmp_ids

if shared_ids:
    print(f"\n[OK] Found {len(shared_ids)} remote_ids that exist in BOTH RAW and PMP (this is CORRECT)")
    print("   These are different inspections for different commodity types:")
    for remote_id in sorted(list(shared_ids))[:10]:  # Show first 10
        raw = [insp for insp in raw_inspections if insp.remote_id == remote_id][0]
        pmp = [insp for insp in pmp_inspections if insp.remote_id == remote_id][0]
        print(f"      Remote ID {remote_id}:")
        print(f"        RAW: {raw.client_name} ({raw.date_of_inspection})")
        print(f"        PMP: {pmp.client_name} ({pmp.date_of_inspection})")
    if len(shared_ids) > 10:
        print(f"      ... and {len(shared_ids) - 10} more")
else:
    print("\n   No remote_ids are shared between RAW and PMP")

print("\n" + "=" * 120)
print("FINAL VERDICT")
print("=" * 120)

if not duplicates and not raw_duplicates and not pmp_duplicates:
    print("\n[OK][OK][OK] EXPORT IS CORRECT - NO DUPLICATES FOUND!")
    print("     The composite key (commodity, remote_id) deduplication is working perfectly.")
else:
    print("\n[ERROR][ERROR][ERROR] EXPORT HAS DUPLICATES - NEEDS FIXING!")

print("\n" + "=" * 120)