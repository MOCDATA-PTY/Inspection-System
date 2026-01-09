#!/usr/bin/env python3
"""
Quick check for duplicate inspections in database
"""
import os
import sys
import django
from datetime import datetime
from collections import Counter

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 100)
print("QUICK DUPLICATE CHECK")
print("=" * 100)

# December 2025
start_date = datetime(2025, 12, 1).date()
end_date = datetime(2025, 12, 31).date()

print(f"\nDate range: {start_date} to {end_date}")

# Get inspections WITHOUT distinct
all_inspections = list(FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=start_date,
    date_of_inspection__lte=end_date
).order_by('commodity', 'remote_id'))

print(f"Total inspections (without distinct): {len(all_inspections)}")

# Get inspections WITH distinct
distinct_inspections = list(FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=start_date,
    date_of_inspection__lte=end_date
).distinct('commodity', 'remote_id').order_by('commodity', 'remote_id', '-date_of_inspection'))

print(f"Total inspections (with distinct): {len(distinct_inspections)}")
print(f"Difference: {len(all_inspections) - len(distinct_inspections)}")

# Check for duplicates in ALL inspections
keys = [(insp.commodity, insp.remote_id) for insp in all_inspections]
key_counts = Counter(keys)
duplicates = {key: count for key, count in key_counts.items() if count > 1}

if duplicates:
    print(f"\n[FOUND] {len(duplicates)} duplicate (commodity, remote_id) combinations:")
    for (commodity, remote_id), count in list(duplicates.items())[:5]:
        print(f"\n  {commodity}-{remote_id}: {count} inspections")

        # Show the duplicates
        dupes = [insp for insp in all_inspections if insp.commodity == commodity and insp.remote_id == remote_id]
        for dupe in dupes:
            print(f"    - ID: {dupe.id}, Date: {dupe.date_of_inspection}, Client: {dupe.client_name}")
else:
    print("\n[OK] No duplicates found in raw data")

# Check distinct list
print("\n" + "=" * 100)
print("CHECKING DISTINCT LIST")
print("=" * 100)

distinct_keys = [(insp.commodity, insp.remote_id) for insp in distinct_inspections]
distinct_counts = Counter(distinct_keys)
distinct_duplicates = {key: count for key, count in distinct_counts.items() if count > 1}

if distinct_duplicates:
    print(f"\n[ERROR] DISTINCT NOT WORKING! Found {len(distinct_duplicates)} duplicates in distinct list:")
    for (commodity, remote_id), count in list(distinct_duplicates.items())[:5]:
        print(f"  {commodity}-{remote_id}: {count} times")
else:
    print("\n[OK] Distinct working correctly - no duplicates")

print("\n" + "=" * 100)