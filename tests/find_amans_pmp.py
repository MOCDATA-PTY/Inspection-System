"""Find ALL Amans inspections to locate the PMP products that the inspector manually entered"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from collections import defaultdict

print("=" * 100)
print("SEARCHING FOR ALL AMANS INSPECTIONS (ALL DATES, ALL COMMODITIES)")
print("=" * 100)

# Get ALL Amans inspections (no date filter)
inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains="Amans"
).order_by('-date_of_inspection', 'commodity', 'product_name')

print(f"\nFound {len(inspections)} total Amans inspections in the database")
print("\n" + "=" * 100)

# Group by date
by_date = defaultdict(list)
for insp in inspections:
    date_key = str(insp.date_of_inspection) if insp.date_of_inspection else 'Unknown'
    by_date[date_key].append(insp)

print(f"\nInspections grouped by {len(by_date)} different dates:\n")

for date_str in sorted(by_date.keys(), reverse=True):
    date_inspections = by_date[date_str]

    # Count commodities
    pmp_count = sum(1 for i in date_inspections if 'PMP' in (i.commodity or '').upper())
    raw_count = sum(1 for i in date_inspections if 'RAW' in (i.commodity or '').upper())

    # Count samples
    samples_count = sum(1 for i in date_inspections if i.is_sample_taken)

    # Count tests
    fat_count = sum(1 for i in date_inspections if i.fat)
    protein_count = sum(1 for i in date_inspections if i.protein)

    print(f"DATE: {date_str}")
    print(f"   Products: {len(date_inspections)} total ({pmp_count} PMP, {raw_count} RAW)")
    print(f"   Samples: {samples_count} products with samples taken")
    print(f"   Tests: Fat={fat_count}, Protein={protein_count}")

    # Show first product's hours/km
    first = date_inspections[0]
    print(f"   Hours: {first.hours}, KM: {first.km_traveled}")
    print(f"   Inspector: {first.inspector_name}")

    # If this date has both PMP and RAW, or has samples, show details
    if (pmp_count > 0 and raw_count > 0) or samples_count > 0:
        print(f"\n   >>> THIS DATE HAS BOTH PMP/RAW OR SAMPLES - SHOWING DETAILS:")
        for i, insp in enumerate(date_inspections, 1):
            print(f"      {i}. [{insp.commodity}] {insp.product_name}")
            print(f"         Hours: {insp.hours}, KM: {insp.km_traveled}")
            print(f"         Sample: {insp.is_sample_taken}, Fat: {insp.fat}, Protein: {insp.protein}")
            print(f"         Remote ID: {insp.remote_id}")

    print()

print("=" * 100)
print("\nSEARCH LOOKING FOR THE INSPECTION THAT MATCHES GOOGLE SHEET:")
print("   - Should have BOTH PMP and RAW products")
print("   - Should have samples taken with Fat and Protein tests")
print("   - Should have 0.5 hours and 35 km (split values)")
print("   - Or 1.0 hours and 70 km (before split)")
print("\n" + "=" * 100)

# Look for inspections with hours = 0.5 or 1.0 and km = 35 or 70
matching = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains="Amans",
    hours__in=[0.5, 1.0],
    km_traveled__in=[35.0, 70.0]
).order_by('-date_of_inspection')

print(f"\nFound {len(matching)} Amans inspections with hours=0.5/1.0 and km=35/70:\n")

for insp in matching:
    print(f"DATE: {insp.date_of_inspection}")
    print(f"   [{insp.commodity}] {insp.product_name}")
    print(f"   Hours: {insp.hours}, KM: {insp.km_traveled}")
    print(f"   Inspector: {insp.inspector_name}")
    print(f"   Sample: {insp.is_sample_taken}, Fat: {insp.fat}, Protein: {insp.protein}")
    print(f"   Remote ID: {insp.remote_id}")
    print()

print("=" * 100)
