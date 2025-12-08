#!/usr/bin/env python3
"""
Debug exactly what the export function generates for Roots Butchery Birch Acres
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

print("=" * 100)
print("DEBUG: EXPORT LINE ITEM GENERATION FOR ROOTS BUTCHERY BIRCH ACRES")
print("=" * 100)

# Test date
test_date = datetime(2025, 12, 5).date()

# Get the exact inspections
inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    client_name__icontains='Roots Butchery Birch Acres',
    date_of_inspection=test_date,
    hours__isnull=False,
    km_traveled__isnull=False
).distinct('commodity', 'remote_id').order_by('commodity', 'remote_id', '-date_of_inspection', 'inspector_name')

print(f"\nInspections found: {inspections.count()}")

for insp in inspections:
    print("\n" + "-" * 100)
    print(f"INSPECTION: {insp.commodity}-{insp.remote_id}")
    print(f"  Client: {insp.client_name}")
    print(f"  Product: {insp.product_name}")
    print(f"  Inspector: {insp.inspector_name}")
    print(f"  Date: {insp.date_of_inspection}")
    print(f"  Hours: {insp.hours}")
    print(f"  KM: {insp.km_traveled}")
    print(f"  Commodity: '{insp.commodity}'")
    print(f"  Fat: {insp.fat}")
    print(f"  Protein: {insp.protein}")

    # Determine product type (same logic as export function)
    product_type = 'RAW' if insp.commodity and 'RAW' in insp.commodity.upper() else 'PMP'
    print(f"\n  >>> PRODUCT_TYPE DETERMINED: '{product_type}'")

    # Check what line items would be generated
    print(f"\n  LINE ITEMS THAT WILL BE GENERATED:")

    if product_type == 'PMP':
        print(f"    - PMP 060 (Inspection hours: {insp.hours})")
        print(f"    - PMP 061 (Travel km: {insp.km_traveled})")
        if insp.fat:
            print(f"    - PMP 062 (Fat test)")
        if insp.protein:
            print(f"    - PMP 064 (Protein test)")
    else:  # RAW
        print(f"    - RAW 050 (Inspection hours: {insp.hours})")
        print(f"    - RAW 051 (Travel km: {insp.km_traveled})")
        if insp.fat:
            print(f"    - RAW 052 (Fat test)")
        if insp.protein:
            print(f"    - RAW 053 (Protein test)")

    print()

print("\n" + "=" * 100)
print("CHECKING IF COMMODITY FIELD HAS UNEXPECTED CHARACTERS")
print("=" * 100)

for insp in inspections:
    commodity_repr = repr(insp.commodity)
    print(f"\n{insp.commodity}-{insp.remote_id}:")
    print(f"  commodity repr: {commodity_repr}")
    print(f"  commodity length: {len(insp.commodity) if insp.commodity else 0}")
    print(f"  'RAW' in commodity.upper(): {'RAW' in insp.commodity.upper() if insp.commodity else False}")
    print(f"  commodity.strip().upper(): '{insp.commodity.strip().upper()}' if insp.commodity else 'None'")

print("\n" + "=" * 100)