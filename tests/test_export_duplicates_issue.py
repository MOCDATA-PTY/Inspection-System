#!/usr/bin/env python3
"""
Test why the export has duplicates for the same client/date
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

print("=" * 120)
print("TESTING EXPORT DUPLICATES ISSUE")
print("=" * 120)

# Use November 2025 to match the screenshot
start_date = datetime(2025, 11, 1).date()
end_date = datetime(2025, 11, 30).date()

print(f"\nDate range: {start_date} to {end_date}")

# Get inspections with the EXACT query from export_sheet
inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=start_date,
    date_of_inspection__lte=end_date
).select_related(
    'sent_by', 'rfi_uploaded_by', 'invoice_uploaded_by'
).distinct('commodity', 'remote_id').order_by('commodity', 'remote_id', '-date_of_inspection', 'inspector_name')

print(f"Total inspections returned: {inspections.count()}")

# Check for any Inspector that might have duplicates
print("\n" + "=" * 120)
print("CHECKING FOR DUPLICATE INSPECTIONS (same commodity + remote_id)")
print("=" * 120)

from collections import Counter

# Count how many times each (commodity, remote_id) appears
inspection_keys = [(insp.commodity, insp.remote_id) for insp in inspections]
key_counts = Counter(inspection_keys)

duplicates = {key: count for key, count in key_counts.items() if count > 1}

if duplicates:
    print(f"\n[ERROR] Found {len(duplicates)} duplicate (commodity, remote_id) combinations:")
    for (commodity, remote_id), count in list(duplicates.items())[:10]:
        print(f"  - {commodity}-{remote_id}: appears {count} times")
else:
    print("\n[OK] No duplicate (commodity, remote_id) combinations")

# Now check line items generation
print("\n" + "=" * 120)
print("CHECKING LINE ITEMS GENERATION")
print("=" * 120)

# Get first few inspections and generate line items
test_inspections = list(inspections[:5])
print(f"\nTesting with {len(test_inspections)} inspections:")

for insp in test_inspections:
    print(f"\n  {insp.commodity}-{insp.remote_id}: {insp.client_name} ({insp.date_of_inspection})")

# Generate line items using same logic as export
invoice_items = []
inspection_counter = {}

for inspection in test_inspections:
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

    print(f"\n  Generated {len(items)} line items for {inspection.commodity}-{inspection.remote_id}")
    invoice_items.extend(items)

print(f"\n\nTotal line items generated: {len(invoice_items)}")

# Sort by client name
invoice_items.sort(key=lambda x: (
    x.get('client_name', ''),
    x.get('invoice_date', ''),
    x.get('item_code', '')
))

# Check for duplicate rows (same client, date, item_code, description)
print("\n" + "=" * 120)
print("CHECKING FOR DUPLICATE LINE ITEMS (same client + date + item_code + description)")
print("=" * 120)

line_item_keys = [
    (item['client_name'], item['invoice_date'], item['item_code'], item['description'])
    for item in invoice_items
]

line_counts = Counter(line_item_keys)
line_duplicates = {key: count for key, count in line_counts.items() if count > 1}

if line_duplicates:
    print(f"\n[ERROR] Found {len(line_duplicates)} duplicate line items:")
    for (client, date, code, desc), count in list(line_duplicates.items())[:5]:
        print(f"\n  {client} | {date} | {code}")
        print(f"    Description: {desc[:80]}")
        print(f"    Appears: {count} times")
else:
    print("\n[OK] No duplicate line items found")

print("\n" + "=" * 120)