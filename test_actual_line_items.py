#!/usr/bin/env python3
"""
Test the ACTUAL line item generation for Roots Butchery Birch Acres
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
from main.views.core_views import generate_invoice_line_items

print("=" * 100)
print("TEST: ACTUAL LINE ITEM GENERATION FOR ROOTS BUTCHERY BIRCH ACRES")
print("=" * 100)

# Get the inspections
test_date = datetime(2025, 12, 5).date()
inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    client_name__icontains='Roots Butchery Birch Acres',
    date_of_inspection=test_date,
    hours__isnull=False,
    km_traveled__isnull=False
).distinct('commodity', 'remote_id').order_by('commodity', 'remote_id', '-date_of_inspection', 'inspector_name')

print(f"\nFound {inspections.count()} inspections")

all_line_items = []
inspection_id = 1

for insp in inspections:
    print("\n" + "=" * 100)
    print(f"PROCESSING: {insp.commodity}-{insp.remote_id}")
    print("=" * 100)
    print(f"Client: {insp.client_name}")
    print(f"Product: {insp.product_name}")
    print(f"Inspector: {insp.inspector_name}")
    print(f"Date: {insp.date_of_inspection}")
    print(f"Hours: {insp.hours}")
    print(f"KM: {insp.km_traveled}")
    print(f"Commodity: {insp.commodity}")
    print(f"Fat: {insp.fat}")
    print(f"Protein: {insp.protein}")

    # Determine product type (exact same logic as export_sheet)
    product_type = 'RAW' if insp.commodity and 'RAW' in insp.commodity.upper() else 'PMP'
    print(f"\nProduct Type: {product_type}")

    # Get city
    city = ''
    if insp.client_name:
        parts = insp.client_name.split()
        city = parts[-1] if len(parts) > 1 else ''

    # Generate inspector code
    inspector_code = ''
    if insp.inspector_name:
        name_parts = insp.inspector_name.split()
        inspector_code = ''.join([part[0].upper() for part in name_parts if part])

    # Generate refs
    date_str = insp.date_of_inspection.strftime('%y%m%d')
    invoice_ref = f"FSA-INV-{inspector_code}-{date_str}"
    rfi_ref = f"FSA-RFI-{inspector_code}-{date_str}"

    # Call the ACTUAL generate_invoice_line_items function
    print(f"\nCalling generate_invoice_line_items()...")
    items = generate_invoice_line_items(
        inspection_id=inspection_id,
        inspection=insp,
        invoice_ref=invoice_ref,
        rfi_ref=rfi_ref,
        product_type=product_type,
        city=city,
        lab_name='Food Safety Laboratory'
    )

    print(f"\nGenerated {len(items)} line items:")
    for item in items:
        print(f"  - {item['item_code']}: {item['description'][:80]}")
        print(f"    Quantity: {item['quantity']}, Unit Amount: {item['unit_amount']}, Account: {item['account_code']}")

    all_line_items.extend(items)
    inspection_id += 1

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"\nTotal inspections processed: {inspections.count()}")
print(f"Total line items generated: {len(all_line_items)}")

print("\nAll line items for export:")
for item in all_line_items:
    print(f"  {item['client_name']}: {item['item_code']} - {item['description'][:60]}...")

print("\n" + "=" * 100)
print("EXPECTED IN EXPORT:")
print("=" * 100)
print("\nRoots Butchery Birch Acres should show:")
pmp_items = [i for i in all_line_items if i['item_code'].startswith('PMP')]
raw_items = [i for i in all_line_items if i['item_code'].startswith('RAW')]

print(f"\nPMP items ({len(pmp_items)}):")
for item in pmp_items:
    print(f"  - {item['item_code']}")

print(f"\nRAW items ({len(raw_items)}):")
for item in raw_items:
    print(f"  - {item['item_code']}")

print("\n" + "=" * 100)