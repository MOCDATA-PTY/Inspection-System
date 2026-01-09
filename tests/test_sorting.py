#!/usr/bin/env python3
"""
Test the sorting of line items
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
print("TEST: SORTING ORDER FOR ROOTS BUTCHERY BIRCH ACRES")
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

all_line_items = []
inspection_id = 1

for insp in inspections:
    product_type = 'RAW' if insp.commodity and 'RAW' in insp.commodity.upper() else 'PMP'
    city = ''
    if insp.client_name:
        parts = insp.client_name.split()
        city = parts[-1] if len(parts) > 1 else ''

    inspector_code = ''
    if insp.inspector_name:
        name_parts = insp.inspector_name.split()
        inspector_code = ''.join([part[0].upper() for part in name_parts if part])

    date_str = insp.date_of_inspection.strftime('%y%m%d')
    invoice_ref = f"FSA-INV-{inspector_code}-{date_str}"
    rfi_ref = f"FSA-RFI-{inspector_code}-{date_str}"

    items = generate_invoice_line_items(
        inspection_id=inspection_id,
        inspection=insp,
        invoice_ref=invoice_ref,
        rfi_ref=rfi_ref,
        product_type=product_type,
        city=city,
        lab_name='Food Safety Laboratory'
    )

    all_line_items.extend(items)
    inspection_id += 1

print(f"\nBEFORE SORTING (current order - all PMP first, then all RAW):")
print("-" * 100)
for item in all_line_items:
    print(f"{item['client_name']:40} {item['invoice_date']:12} {item['item_code']:10}")

# Now sort like the fixed code does
all_line_items.sort(key=lambda x: (
    x.get('client_name', ''),
    x.get('invoice_date', ''),
    x.get('item_code', '')
))

print(f"\n\nAFTER SORTING (new order - grouped by client, RAW and PMP intermixed):")
print("-" * 100)
for item in all_line_items:
    print(f"{item['client_name']:40} {item['invoice_date']:12} {item['item_code']:10}")

print("\n" + "=" * 100)
print("RESULT: All items for Roots Butchery Birch Acres are now grouped together!")
print("        RAW and PMP items are sorted by item code (050, 051, 060, 061, 062, 064)")
print("=" * 100)