"""Test export line item generation to find duplicate sources"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import datetime, timedelta
from collections import defaultdict

print("=" * 100)
print("SIMULATING EXPORT LINE ITEM GENERATION")
print("=" * 100)

# Test with specific client that shows duplicates
client_name = "Bkou Bul Meat Market"

inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains=client_name,
    commodity__in=['RAW', 'PMP'],
    hours__isnull=False,
    km_traveled__isnull=False
).order_by('-date_of_inspection')[:20]

print(f"\nFound {len(inspections)} inspections for '{client_name}'")

if len(inspections) == 0:
    print("\nTrying partial match...")
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains="Bul Meat",
        commodity__in=['RAW', 'PMP'],
        hours__isnull=False,
        km_traveled__isnull=False
    ).order_by('-date_of_inspection')[:20]
    print(f"Found {len(inspections)} with partial match")

# Group by visit
visits = defaultdict(list)

for inspection in inspections:
    visit_key = (
        inspection.inspector_name or '',
        inspection.client_name or '',
        str(inspection.date_of_inspection) if inspection.date_of_inspection else ''
    )
    visits[visit_key].append(inspection)

print(f"\nGrouped into {len(visits)} unique visits\n")

# Simulate line item generation for each visit
for visit_key, visit_inspections in visits.items():
    inspector_name, client_name, date_str = visit_key

    print("=" * 100)
    print(f"VISIT: {client_name} - {date_str}")
    print("=" * 100)

    first_inspection = visit_inspections[0]

    # Get hours/km
    total_hours = float(first_inspection.hours) if first_inspection.hours else 0
    total_km = float(first_inspection.km_traveled) if first_inspection.km_traveled else 0

    print(f"\nVisit details:")
    print(f"  Inspector: {inspector_name}")
    print(f"  Hours: {total_hours}")
    print(f"  KM: {total_km}")
    print(f"  Products: {len(visit_inspections)}")

    # Count line items that would be generated
    line_item_count = 0

    # Hours/KM line items (ONCE per visit)
    if total_hours > 0 or total_km > 0:
        product_type = 'RAW' if first_inspection.commodity and 'RAW' in first_inspection.commodity.upper() else 'PMP'
        print(f"\nHours/KM line items (type: {product_type}):")
        print(f"  1. Inspector Travel ({product_type})")
        print(f"  2. Inspector Hours ({product_type})")
        line_item_count += 2

    # Test line items (FOR EACH PRODUCT)
    print(f"\nTest line items (per product):")
    for i, inspection in enumerate(visit_inspections, 1):
        product_type = 'RAW' if inspection.commodity and 'RAW' in inspection.commodity.upper() else 'PMP'
        print(f"\n  Product {i}: {inspection.product_name} ({product_type})")
        print(f"    Commodity: {inspection.commodity}")
        print(f"    Fat: {inspection.fat}, Protein: {inspection.protein}")
        print(f"    Sample taken: {inspection.is_sample_taken}")

        test_items = []

        if product_type == 'PMP':
            if inspection.fat and inspection.is_sample_taken:
                test_items.append("PMP 062 - Fat Test")
                line_item_count += 1
            if inspection.protein and inspection.is_sample_taken:
                test_items.append("PMP 064 - Protein Test")
                line_item_count += 1
            if inspection.calcium and inspection.is_sample_taken:
                test_items.append("PMP 066 - Calcium Test")
                line_item_count += 1
        else:  # RAW
            if inspection.fat and inspection.is_sample_taken:
                test_items.append("RAW 052 - Fat Test")
                line_item_count += 1
            if inspection.protein and inspection.is_sample_taken:
                test_items.append("RAW 053 - Protein Test")
                line_item_count += 1
            if inspection.dna and inspection.is_sample_taken:
                test_items.append("RAW 056 - DNA Test")
                line_item_count += 1

        if test_items:
            for item in test_items:
                print(f"      - {item}")
        else:
            print(f"      - No test items")

    print(f"\n[TOTAL] This visit generates {line_item_count} line items")

print("\n" + "=" * 100)
print("TEST COMPLETE")
print("=" * 100)
