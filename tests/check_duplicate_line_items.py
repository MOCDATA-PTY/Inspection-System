#!/usr/bin/env python3
"""
Check for duplicate line items in the export (not just duplicate inspections)
A duplicate line item = same client + date + item_code + description
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
from main.views.core_views import generate_invoice_line_items

print("=" * 120)
print("CHECKING FOR DUPLICATE LINE ITEMS IN EXPORT")
print("=" * 120)

# Use today's date for quick testing
from datetime import timedelta
today = datetime.now().date()
yesterday = today - timedelta(days=1)
start_date = yesterday
end_date = today

print(f"\nDate range: {start_date} to {end_date}")

# Get inspections using EXACT query from export_sheet
inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=start_date,
    date_of_inspection__lte=end_date
).select_related(
    'sent_by', 'rfi_uploaded_by', 'invoice_uploaded_by'
).distinct('commodity', 'remote_id').order_by('commodity', 'remote_id', '-date_of_inspection', 'inspector_name')

print(f"Total inspections (with distinct): {inspections.count()}")

# Generate line items using EXACT logic from export_sheet
invoice_items = []
inspection_counter = {}

for inspection in inspections:
    inspector_key = inspection.inspector_name or 'Unknown'
    if inspector_key not in inspection_counter:
        inspection_counter[inspector_key] = 1
    else:
        inspection_counter[inspector_key] += 1

    inspection_id = inspection_counter[inspector_key]

    inspector_code = ''
    if inspection.inspector_name:
        name_parts = inspection.inspector_name.split()
        inspector_code = ''.join([part[0].upper() for part in name_parts if part])

    date_str = ''
    if inspection.date_of_inspection:
        date_str = inspection.date_of_inspection.strftime('%y%m%d')

    invoice_ref = f"FSA-INV-{inspector_code}-{date_str}" if date_str else ''
    rfi_ref = f"FSA-RFI-{inspector_code}-{date_str}" if date_str else ''

    product_type = 'RAW' if inspection.commodity and 'RAW' in inspection.commodity.upper() else 'PMP'

    city = ''
    if inspection.client_name:
        parts = inspection.client_name.split()
        city = parts[-1] if len(parts) > 1 else ''

    lab_name = 'Food Safety Laboratory' if inspection.lab else ''

    items = generate_invoice_line_items(
        inspection_id=inspection_id,
        inspection=inspection,
        invoice_ref=invoice_ref,
        rfi_ref=rfi_ref,
        product_type=product_type,
        city=city,
        lab_name=lab_name
    )

    invoice_items.extend(items)

print(f"Total line items generated: {len(invoice_items)}")

# Sort (same as export_sheet)
invoice_items.sort(key=lambda x: (
    x.get('client_name', ''),
    x.get('invoice_date', ''),
    x.get('item_code', '')
))

print("\n" + "=" * 120)
print("CHECKING FOR DUPLICATE LINE ITEMS")
print("=" * 120)

# Create unique key for each line item
# Duplicates = same client + date + item_code (description can vary slightly)
line_item_keys = [
    (item['client_name'], item['invoice_date'], item['item_code'])
    for item in invoice_items
]

key_counts = Counter(line_item_keys)
duplicates = {key: count for key, count in key_counts.items() if count > 1}

if duplicates:
    print(f"\n[ERROR] Found {len(duplicates)} duplicate line item keys:")
    print(f"\nShowing first 10 duplicates:")

    for (client, date, code), count in list(duplicates.items())[:10]:
        print(f"\n  {client} | {date} | {code}")
        print(f"    Appears: {count} times")

        # Show the actual duplicate rows
        matching_items = [
            item for item in invoice_items
            if item['client_name'] == client
            and item['invoice_date'] == date
            and item['item_code'] == code
        ]

        for idx, item in enumerate(matching_items, 1):
            print(f"    Row {idx}:")
            print(f"      Description: {item['description'][:80]}")
            print(f"      Quantity: {item['quantity']}, Unit: {item['unit_amount']}")
            print(f"      Inspection ID: {item.get('inspection_id', 'N/A')}")
            print(f"      Product: {item.get('product_name', 'N/A')}")
else:
    print("\n[OK] NO DUPLICATE LINE ITEMS FOUND")
    print("Each (client + date + item_code) combination appears exactly once")

# Also check the inspections themselves for duplicates
print("\n" + "=" * 120)
print("DOUBLE-CHECKING INSPECTIONS FOR DUPLICATES")
print("=" * 120)

inspection_keys = [(insp.commodity, insp.remote_id) for insp in inspections]
inspection_counts = Counter(inspection_keys)
inspection_duplicates = {key: count for key, count in inspection_counts.items() if count > 1}

if inspection_duplicates:
    print(f"\n[ERROR] Found {len(inspection_duplicates)} duplicate inspections (this should be impossible with distinct!):")
    for (commodity, remote_id), count in list(inspection_duplicates.items())[:10]:
        print(f"  - {commodity}-{remote_id}: appears {count} times")
else:
    print("\n[OK] No duplicate inspections in queryset")

print("\n" + "=" * 120)