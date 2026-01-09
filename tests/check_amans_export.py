"""Check Amans meat & deli export data generation"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from collections import defaultdict

print("=" * 100)
print("CHECKING AMANS MEAT & DELI INSPECTION EXPORT")
print("=" * 100)

# Find Amans meat & deli inspections around December 3rd
client_name = "Amans"
date_target = "2025-12-03"  # December 3rd, 2025

inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains=client_name,
    date_of_inspection=date_target
).order_by('commodity', 'product_name')

print(f"\nFound {len(inspections)} inspections for '{client_name}' on {date_target}")
print("\n" + "=" * 100)

if not inspections:
    print(f"No inspections found. Let me search for any Amans inspections...")
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains="Amans"
    ).order_by('-date_of_inspection')[:20]
    print(f"Found {len(inspections)} Amans inspections (showing recent 20):")
    for insp in inspections:
        print(f"  - {insp.date_of_inspection}: {insp.commodity} - {insp.product_name} (Hours: {insp.hours}, KM: {insp.km_traveled})")
    exit()

# Group by visit
visits = defaultdict(list)
for inspection in inspections:
    visit_key = (
        inspection.inspector_name or '',
        inspection.client_name or '',
        str(inspection.date_of_inspection) if inspection.date_of_inspection else ''
    )
    visits[visit_key].append(inspection)

print(f"Grouped into {len(visits)} visit(s)\n")

# Process each visit
for visit_key, visit_inspections in visits.items():
    inspector_name, client_name, date_str = visit_key

    print("=" * 100)
    print(f"VISIT: {client_name}")
    print(f"Date: {date_str}")
    print(f"Inspector: {inspector_name}")
    print("=" * 100)

    # Get hours/km from first inspection
    first = visit_inspections[0]
    original_hours = float(first.hours) if first.hours else 0
    original_km = float(first.km_traveled) if first.km_traveled else 0

    print(f"\n[DATABASE VALUES]")
    print(f"  Original Hours: {original_hours}")
    print(f"  Original KM: {original_km}")

    # Check commodity breakdown
    pmp_products = [i for i in visit_inspections if 'PMP' in (i.commodity or '').upper()]
    raw_products = [i for i in visit_inspections if 'RAW' in (i.commodity or '').upper()]

    has_both = len(pmp_products) > 0 and len(raw_products) > 0

    print(f"\n[COMMODITY BREAKDOWN]")
    print(f"  PMP Products: {len(pmp_products)}")
    print(f"  RAW Products: {len(raw_products)}")
    print(f"  Has Both Types: {has_both}")

    # Show what SHOULD be generated
    print(f"\n[EXPECTED LINE ITEMS]")
    print(f"\n--- HOURS/KM Line Items ---")

    if has_both:
        split_hours = original_hours / 2
        split_km = original_km / 2

        print(f"  PMP 060: Inspection Hours = {split_hours}")
        print(f"  PMP 061: Travel KM = {split_km}")
        print(f"  RAW 050: Inspection Hours = {split_hours}")
        print(f"  RAW 051: Travel KM = {split_km}")
    else:
        commodity_type = 'RAW' if raw_products else 'PMP'
        print(f"  {commodity_type} Hours: {original_hours}")
        print(f"  {commodity_type} KM: {original_km}")

    # Check for test line items
    print(f"\n--- TEST Line Items ---")

    if pmp_products:
        print(f"  PMP Products:")
        for i, insp in enumerate(pmp_products, 1):
            print(f"    {i}. {insp.product_name}")
            print(f"       Sample taken: {insp.is_sample_taken}")
            print(f"       Fat: {insp.fat}, Protein: {insp.protein}, Calcium: {insp.calcium}")

        # Check which tests are needed
        pmp_needs_fat = any(i.fat and i.is_sample_taken for i in pmp_products)
        pmp_needs_protein = any(i.protein and i.is_sample_taken for i in pmp_products)
        pmp_needs_calcium = any(i.calcium and i.is_sample_taken for i in pmp_products)

        print(f"\n  PMP Tests Needed:")
        if pmp_needs_fat:
            print(f"    PMP 062: Fat Content test")
        if pmp_needs_protein:
            print(f"    PMP 064: Protein Content test")
        if pmp_needs_calcium:
            print(f"    PMP 065: Calcium Content test")

    if raw_products:
        print(f"\n  RAW Products:")
        for i, insp in enumerate(raw_products, 1):
            print(f"    {i}. {insp.product_name}")
            print(f"       Sample taken: {insp.is_sample_taken}")
            print(f"       Fat: {insp.fat}, Protein: {insp.protein}, DNA: {insp.dna}")

        # Check which tests are needed
        raw_needs_fat = any(i.fat and i.is_sample_taken for i in raw_products)
        raw_needs_protein = any(i.protein and i.is_sample_taken for i in raw_products)
        raw_needs_dna = any(i.dna and i.is_sample_taken for i in raw_products)

        print(f"\n  RAW Tests Needed:")
        if raw_needs_fat:
            print(f"    RAW 052: Fat Content test")
        if raw_needs_protein:
            print(f"    RAW 054: Protein Content test")
        if raw_needs_dna:
            print(f"    RAW 053: DNA test")

    print(f"\n[TOTAL EXPECTED LINE ITEMS]: ", end="")
    count = 0
    if has_both:
        count += 4  # 2 PMP + 2 RAW hours/km
    else:
        count += 2  # hours + km for one commodity

    # Add test items
    if pmp_products:
        pmp_needs_fat = any(i.fat and i.is_sample_taken for i in pmp_products)
        pmp_needs_protein = any(i.protein and i.is_sample_taken for i in pmp_products)
        pmp_needs_calcium = any(i.calcium and i.is_sample_taken for i in pmp_products)
        count += sum([pmp_needs_fat, pmp_needs_protein, pmp_needs_calcium])

    if raw_products:
        raw_needs_fat = any(i.fat and i.is_sample_taken for i in raw_products)
        raw_needs_protein = any(i.protein and i.is_sample_taken for i in raw_products)
        raw_needs_dna = any(i.dna and i.is_sample_taken for i in raw_products)
        count += sum([raw_needs_fat, raw_needs_protein, raw_needs_dna])

    print(f"{count} line items")

print("\n" + "=" * 100)
