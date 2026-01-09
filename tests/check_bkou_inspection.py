"""Check Bkou Bul Meat Market inspection to see original hours/km before split"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 100)
print("CHECKING BKOU BUL MEAT MARKET INSPECTION")
print("=" * 100)

# Find inspections for Bkou Bul Meat Market on 02/12/2025
client_name = "Bkou Bul Meat Market"
date_str = "2025-02-12"  # Assuming this is the date from the screenshot

inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains="Bul Meat"
).order_by('-date_of_inspection')[:20]

print(f"\nFound {len(inspections)} inspections matching 'Bul Meat'")
print("\n" + "=" * 100)

# Group by date and inspector to identify visits
from collections import defaultdict
visits = defaultdict(list)

for insp in inspections:
    visit_key = (
        str(insp.date_of_inspection) if insp.date_of_inspection else '',
        insp.inspector_name or '',
        insp.client_name or ''
    )
    visits[visit_key].append(insp)

print(f"Grouped into {len(visits)} unique visits\n")

# Show details for each visit
for visit_key, visit_inspections in visits.items():
    date_str, inspector, client = visit_key

    print("=" * 100)
    print(f"VISIT: {client}")
    print(f"Date: {date_str}")
    print(f"Inspector: {inspector}")
    print("=" * 100)

    # Get first inspection's hours/km (this is what's stored in DB)
    first = visit_inspections[0]
    original_hours = float(first.hours) if first.hours else 0
    original_km = float(first.km_traveled) if first.km_traveled else 0

    print(f"\n[ORIGINAL VALUES FROM DATABASE]")
    print(f"  Hours: {original_hours}")
    print(f"  KM: {original_km}")

    # Check commodity types in this visit
    pmp_products = [i for i in visit_inspections if 'PMP' in (i.commodity or '').upper()]
    raw_products = [i for i in visit_inspections if 'RAW' in (i.commodity or '').upper()]

    has_both = len(pmp_products) > 0 and len(raw_products) > 0

    print(f"\n[COMMODITY BREAKDOWN]")
    print(f"  PMP Products: {len(pmp_products)}")
    print(f"  RAW Products: {len(raw_products)}")
    print(f"  Has Both Types: {has_both}")

    if has_both:
        print(f"\n[SPLIT CALCULATION]")
        print(f"  This visit has BOTH PMP and RAW, so hours/km will be split:")
        print(f"  PMP gets: {original_hours / 2} hours, {original_km / 2} km")
        print(f"  RAW gets: {original_hours / 2} hours, {original_km / 2} km")
    else:
        print(f"\n[NO SPLIT]")
        print(f"  This visit has only one commodity type, so full amount charged:")
        print(f"  Full charge: {original_hours} hours, {original_km} km")

    print(f"\n[PRODUCTS IN THIS VISIT]")
    for i, insp in enumerate(visit_inspections, 1):
        print(f"  {i}. {insp.commodity} - {insp.product_name}")
        print(f"     Hours: {insp.hours}, KM: {insp.km_traveled}")
        print(f"     Sample taken: {insp.is_sample_taken}")

    print()

print("=" * 100)
