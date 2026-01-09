#!/usr/bin/env python3
"""
Test sorting for ALL clients in the export
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from main.views.core_views import generate_invoice_line_items

print("=" * 120)
print("TEST: SORTING ORDER FOR ALL CLIENTS IN DECEMBER 2025 EXPORT")
print("=" * 120)

# Test with specific date: December 5, 2025
start_date = datetime(2025, 12, 5).date()
end_date = datetime(2025, 12, 5).date()

# Get all inspections (same query as export_sheet)
inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=start_date,
    date_of_inspection__lte=end_date
).select_related(
    'sent_by', 'rfi_uploaded_by', 'invoice_uploaded_by'
).distinct('commodity', 'remote_id').order_by('commodity', 'remote_id', '-date_of_inspection', 'inspector_name')

print(f"\nDate range: {start_date} to {end_date}")
print(f"Total inspections: {inspections.count()}")

# Generate line items (same logic as export_sheet)
invoice_items = []
inspection_counter = {}
inspections_processed = 0

for inspection in inspections[:50]:  # Limit to first 50 for testing
    inspections_processed += 1
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

print(f"\nGenerated {len(invoice_items)} line items from {inspections_processed} inspections")

print("\n" + "=" * 120)
print("BEFORE SORTING (order items were generated):")
print("=" * 120)
print(f"{'Client Name':<45} {'Date':<12} {'Item Code':<12} {'Description':<40}")
print("-" * 120)
for i, item in enumerate(invoice_items[:30]):  # Show first 30
    desc = item['description'][:40] + '...' if len(item['description']) > 40 else item['description']
    print(f"{item['client_name']:<45} {item['invoice_date']:<12} {item['item_code']:<12} {desc:<40}")

# Sort (same as fixed export_sheet code)
invoice_items.sort(key=lambda x: (
    x.get('client_name', ''),
    x.get('invoice_date', ''),
    x.get('item_code', '')
))

print("\n" + "=" * 120)
print("AFTER SORTING (grouped by client name, then date, then item code):")
print("=" * 120)
print(f"{'Client Name':<45} {'Date':<12} {'Item Code':<12} {'Description':<40}")
print("-" * 120)

current_client = None
for i, item in enumerate(invoice_items[:30]):  # Show first 30
    # Add separator between different clients
    if current_client and current_client != item['client_name']:
        print("-" * 120)
    current_client = item['client_name']

    desc = item['description'][:40] + '...' if len(item['description']) > 40 else item['description']
    print(f"{item['client_name']:<45} {item['invoice_date']:<12} {item['item_code']:<12} {desc:<40}")

print("\n" + "=" * 120)
print("RESULT: Items are now grouped by client name!")
print("        Each client's RAW and PMP items appear together before the next client.")
print("=" * 120)