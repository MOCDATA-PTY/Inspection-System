"""Check Amans meat & deli export data from Django database (already synced from SQL Server)"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from collections import defaultdict

print("=" * 100)
print("CHECKING AMANS MEAT & DELI IN DJANGO DATABASE (SYNCED FROM SQL SERVER)")
print("=" * 100)

# Search for Amans inspections in December 2025
inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains="Amans",
    date_of_inspection__year=2025,
    date_of_inspection__month=12
).order_by('date_of_inspection', 'commodity', 'product_name')

print(f"\nFound {len(inspections)} inspections for 'Amans' in December 2025")

if not inspections:
    print("\nNo inspections found in December 2025. Showing recent Amans inspections...")
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains="Amans"
    ).order_by('-date_of_inspection')[:30]
    print(f"Found {len(inspections)} Amans inspections (showing recent 30):")
    for insp in inspections:
        print(f"  {insp.date_of_inspection}: {insp.commodity} - {insp.product_name} (Hours: {insp.hours}, KM: {insp.km_traveled})")
    print("=" * 100)
    exit()

print("\n" + "=" * 100)

# Group by visit
visits = defaultdict(list)
for inspection in inspections:
    visit_key = (
        str(inspection.date_of_inspection) if inspection.date_of_inspection else '',
        inspection.inspector_name or '',
        inspection.client_name or ''
    )
    visits[visit_key].append(inspection)

print(f"Grouped into {len(visits)} visit(s)\n")

# Process each visit
for visit_key, visit_inspections in visits.items():
    date_str, inspector_name, client_name = visit_key

    print("=" * 100)
    print(f"VISIT: {client_name}")
    print(f"Date: {date_str}")
    print(f"Inspector: {inspector_name}")
    print("=" * 100)

    # Get hours/km from first inspection
    first = visit_inspections[0]
    original_hours = float(first.hours) if first.hours else 0
    original_km = float(first.km_traveled) if first.km_traveled else 0

    print(f"\n[DATABASE VALUES (FIRST PRODUCT)]")
    print(f"  Hours: {original_hours}")
    print(f"  KM: {original_km}")

    # Show ALL products
    print(f"\n[ALL PRODUCTS IN THIS VISIT]")
    pmp_count = 0
    raw_count = 0

    for i, insp in enumerate(visit_inspections, 1):
        is_pmp = 'PMP' in (insp.commodity or '').upper()
        is_raw = 'RAW' in (insp.commodity or '').upper()

        if is_pmp:
            pmp_count += 1
        if is_raw:
            raw_count += 1

        print(f"\n  {i}. [{insp.commodity}] {insp.product_name}")
        print(f"     Django ID: {insp.id}")
        print(f"     Remote ID: {insp.remote_id}")
        print(f"     Hours: {insp.hours}, KM: {insp.km_traveled}")
        print(f"     Sample Taken: {insp.is_sample_taken}")
        print(f"     Tests: Fat={insp.fat}, Protein={insp.protein}, Calcium={insp.calcium}, DNA={insp.dna}")

    # Check commodity breakdown
    has_both = pmp_count > 0 and raw_count > 0

    print(f"\n[COMMODITY BREAKDOWN]")
    print(f"  PMP Products: {pmp_count}")
    print(f"  RAW Products: {raw_count}")
    print(f"  Has Both Types: {has_both}")

    # Show what SHOULD be generated for export
    print(f"\n[EXPECTED LINE ITEMS FOR EXPORT]")
    print(f"\n--- HOURS/KM Line Items ---")

    if has_both:
        split_hours = original_hours / 2
        split_km = original_km / 2

        print(f"  PMP 060: Inspection Hours = {split_hours} (was {original_hours}, split in half)")
        print(f"  PMP 061: Travel KM = {split_km} (was {original_km}, split in half)")
        print(f"  RAW 050: Inspection Hours = {split_hours} (was {original_hours}, split in half)")
        print(f"  RAW 051: Travel KM = {split_km} (was {original_km}, split in half)")
    else:
        commodity_type = 'RAW' if raw_count > 0 else 'PMP'
        print(f"  {commodity_type} 050/060: Inspection Hours = {original_hours} (no split - single commodity)")
        print(f"  {commodity_type} 051/061: Travel KM = {original_km} (no split - single commodity)")

    # Check for test line items
    print(f"\n--- TEST Line Items ---")

    pmp_needs_fat = any(i.fat and i.is_sample_taken and 'PMP' in (i.commodity or '').upper() for i in visit_inspections)
    pmp_needs_protein = any(i.protein and i.is_sample_taken and 'PMP' in (i.commodity or '').upper() for i in visit_inspections)
    pmp_needs_calcium = any(i.calcium and i.is_sample_taken and 'PMP' in (i.commodity or '').upper() for i in visit_inspections)

    raw_needs_fat = any(i.fat and i.is_sample_taken and 'RAW' in (i.commodity or '').upper() for i in visit_inspections)
    raw_needs_protein = any(i.protein and i.is_sample_taken and 'RAW' in (i.commodity or '').upper() for i in visit_inspections)
    raw_needs_dna = any(i.dna and i.is_sample_taken and 'RAW' in (i.commodity or '').upper() for i in visit_inspections)

    if pmp_count > 0:
        print(f"  PMP Tests:")
        if pmp_needs_fat:
            print(f"    PMP 062: Fat Content test")
        if pmp_needs_protein:
            print(f"    PMP 064: Protein Content test")
        if pmp_needs_calcium:
            print(f"    PMP 065: Calcium Content test")
        if not (pmp_needs_fat or pmp_needs_protein or pmp_needs_calcium):
            print(f"    (No PMP tests needed - no samples taken)")

    if raw_count > 0:
        print(f"  RAW Tests:")
        if raw_needs_fat:
            print(f"    RAW 052: Fat Content test")
        if raw_needs_protein:
            print(f"    RAW 054: Protein Content test")
        if raw_needs_dna:
            print(f"    RAW 053: DNA test")
        if not (raw_needs_fat or raw_needs_protein or raw_needs_dna):
            print(f"    (No RAW tests needed - no samples taken)")

    # Count total line items
    count = 4 if has_both else 2  # hours/km
    count += sum([pmp_needs_fat, pmp_needs_protein, pmp_needs_calcium])
    count += sum([raw_needs_fat, raw_needs_protein, raw_needs_dna])

    print(f"\n[TOTAL EXPECTED LINE ITEMS]: {count} line items")
    print()

print("=" * 100)
print("\nSUMMARY:")
print(f"- Google Sheet shows 6 line items (correct)")
print(f"- Your export function should also show {sum([4 if len([i for i in v if 'PMP' in (i.commodity or '').upper()]) > 0 and len([i for i in v if 'RAW' in (i.commodity or '').upper()]) > 0 else 2 for v in visits.values()])} hours/km items + test items")
print("=" * 100)
