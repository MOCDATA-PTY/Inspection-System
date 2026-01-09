#!/usr/bin/env python3
"""
Check if there are actual duplicate inspections in the database
that would cause duplicate export rows
"""
import os
import sys
import django
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from collections import Counter

print("=" * 120)
print("CHECKING FOR ACTUAL DUPLICATE INSPECTIONS IN DATABASE")
print("=" * 120)

# Check November 2025 (from screenshot)
start_date = datetime(2025, 11, 1).date()
end_date = datetime(2025, 11, 30).date()

print(f"\nChecking November 2025")

# Get ALL inspections WITHOUT distinct to see raw duplicates
all_inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    date_of_inspection__gte=start_date,
    date_of_inspection__lte=end_date
).order_by('commodity', 'remote_id', 'date_of_inspection')

print(f"Total RAW/PMP inspections (no distinct): {all_inspections.count()}")

# Count duplicates
keys = [(insp.commodity, insp.remote_id) for insp in all_inspections]
key_counts = Counter(keys)
duplicates = {key: count for key, count in key_counts.items() if count > 1}

if duplicates:
    print(f"\n[FOUND] {len(duplicates)} inspections with duplicate (commodity, remote_id):")
    print(f"\nShowing first 10 duplicates:")
    for (commodity, remote_id), count in list(duplicates.items())[:10]:
        print(f"\n  {commodity}-{remote_id}: {count} rows in database")

        # Show the duplicate rows
        dupes = FoodSafetyAgencyInspection.objects.filter(
            commodity=commodity,
            remote_id=remote_id,
            date_of_inspection__gte=start_date,
            date_of_inspection__lte=end_date
        )

        for dupe in dupes:
            print(f"    - Date: {dupe.date_of_inspection}, Client: {dupe.client_name}, Inspector: {dupe.inspector_name}, KM: {dupe.km_traveled}, Hours: {dupe.hours}")
else:
    print("\n[OK] No raw duplicates found (same commodity + remote_id)")

# Now check with distinct to see what export would get
print("\n" + "=" * 120)
print("WITH DISTINCT (what export uses):")
print("=" * 120)

distinct_inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    date_of_inspection__gte=start_date,
    date_of_inspection__lte=end_date
).distinct('commodity', 'remote_id').order_by('commodity', 'remote_id', '-date_of_inspection')

print(f"Total with distinct: {distinct_inspections.count()}")
print(f"Difference: {all_inspections.count() - distinct_inspections.count()} duplicates removed by distinct()")

print("\n" + "=" * 120)
