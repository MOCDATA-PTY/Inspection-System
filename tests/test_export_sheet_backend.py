"""Test the export_sheet view backend to see what invoice_items are generated for Amans"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from collections import defaultdict

print("=" * 100)
print("TESTING EXPORT_SHEET BACKEND FOR AMANS MEAT & DELI")
print("=" * 100)

# Simulate what the export_sheet view does
# From lines 4915-5095 in core_views.py

# Get date range (yesterday to today by default, but we'll use Dec 3rd)
start_date = '2025-12-03'
end_date = '2025-12-03'

print(f"\nQuery parameters:")
print(f"  Date range: {start_date} to {end_date}")
print()

# Query inspections
inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=start_date,
    date_of_inspection__lte=end_date,
    client_name__icontains="Amans"
).order_by('date_of_inspection', 'client_name', 'inspector_name')

print(f"Found {len(inspections)} inspections from database")
print()

# Group by visit (same logic as export_sheet view)
visits = defaultdict(list)
for inspection in inspections:
    visit_key = (
        inspection.inspector_name or '',
        inspection.client_name or '',
        str(inspection.date_of_inspection) if inspection.date_of_inspection else ''
    )
    visits[visit_key].append(inspection)

print(f"Grouped into {len(visits)} visit(s)")
print()

# Process each visit and generate line items (same logic as export_sheet view)
invoice_items = []

for visit_key, visit_inspections in visits.items():
    inspector_name, client_name, date_str = visit_key

    print("=" * 100)
    print(f"Processing visit: {client_name} - {date_str} - {inspector_name}")
    print("=" * 100)

    # Get hours/km from first inspection
    first = visit_inspections[0]
    hours = float(first.hours) if first.hours else 0
    km = float(first.km_traveled) if first.km_traveled else 0

    print(f"\nVisit details:")
    print(f"  Products in visit: {len(visit_inspections)}")
    print(f"  Hours: {hours}")
    print(f"  KM: {km}")

    # Check commodities
    pmp_products = [i for i in visit_inspections if 'PMP' in (i.commodity or '').upper()]
    raw_products = [i for i in visit_inspections if 'RAW' in (i.commodity or '').upper()]
    has_both = len(pmp_products) > 0 and len(raw_products) > 0

    print(f"  PMP products: {len(pmp_products)}")
    print(f"  RAW products: {len(raw_products)}")
    print(f"  Has both: {has_both}")

    # Generate hours/km line items
    print(f"\nGenerating line items:")

    if has_both:
        # Split hours/km between PMP and RAW
        split_hours = hours / 2
        split_km = km / 2

        print(f"  Splitting hours/km equally:")
        print(f"    PMP: {split_hours} hours, {split_km} km")
        print(f"    RAW: {split_hours} hours, {split_km} km")

        # PMP hours line item
        invoice_items.append({
            'item_code': 'PMP 060',
            'description': f'Inspection on Regulated Animal Products (Processed Meat Products): Inspection (hours) - {date_str} - {inspector_name} - {client_name}',
            'quantity': split_hours,
            'unit_amount': 510,
            'client_name': client_name,
            'invoice_date': date_str,
            'inspector_name': inspector_name
        })

        # PMP km line item
        invoice_items.append({
            'item_code': 'PMP 061',
            'description': f'Inspection on Regulated Animal Products (Processed Meat Products): Travel Cost (Km\'s) - {date_str}',
            'quantity': split_km,
            'unit_amount': 6.5,
            'client_name': client_name,
            'invoice_date': date_str,
            'inspector_name': inspector_name
        })

        # RAW hours line item
        invoice_items.append({
            'item_code': 'RAW 050',
            'description': f'Inspection on Regulated Animal Products (Certain Raw Processed Meat Products): Inspection (Hours) - {date_str} - {inspector_name} - {client_name}',
            'quantity': split_hours,
            'unit_amount': 510,
            'client_name': client_name,
            'invoice_date': date_str,
            'inspector_name': inspector_name
        })

        # RAW km line item
        invoice_items.append({
            'item_code': 'RAW 051',
            'description': f'Inspection on Regulated Animal Products (Certain Raw Processed Meat Products): Travel Cost (Km\'s) - {date_str}',
            'quantity': split_km,
            'unit_amount': 6.5,
            'client_name': client_name,
            'invoice_date': date_str,
            'inspector_name': inspector_name
        })

    else:
        # Single commodity type
        commodity_type = 'RAW' if len(raw_products) > 0 else 'PMP'
        hours_code = '050' if commodity_type == 'RAW' else '060'
        km_code = '051' if commodity_type == 'RAW' else '061'

        print(f"  Single commodity: {commodity_type}")
        print(f"    Hours: {hours}")
        print(f"    KM: {km}")

        # Hours line item
        invoice_items.append({
            'item_code': f'{commodity_type} {hours_code}',
            'description': f'Inspection - {date_str} - {inspector_name} - {client_name}',
            'quantity': hours,
            'unit_amount': 510,
            'client_name': client_name,
            'invoice_date': date_str,
            'inspector_name': inspector_name
        })

        # KM line item
        invoice_items.append({
            'item_code': f'{commodity_type} {km_code}',
            'description': f'Travel Cost - {date_str}',
            'quantity': km,
            'unit_amount': 6.5,
            'client_name': client_name,
            'invoice_date': date_str,
            'inspector_name': inspector_name
        })

    # Check for tests (same logic as view)
    pmp_needs_fat = any(i.fat and i.is_sample_taken for i in pmp_products)
    pmp_needs_protein = any(i.protein and i.is_sample_taken for i in pmp_products)
    pmp_needs_calcium = any(i.calcium and i.is_sample_taken for i in pmp_products)

    raw_needs_fat = any(i.fat and i.is_sample_taken for i in raw_products)
    raw_needs_protein = any(i.protein and i.is_sample_taken for i in raw_products)
    raw_needs_dna = any(i.dna and i.is_sample_taken for i in raw_products)

    print(f"\nTest line items:")
    if pmp_needs_fat:
        print(f"  PMP 062: Fat Content test")
        invoice_items.append({
            'item_code': 'PMP 062',
            'description': 'Sample Taking: Fat Content (Processed Meat Products)',
            'quantity': 1,
            'unit_amount': 826,
            'client_name': client_name,
            'invoice_date': date_str,
            'inspector_name': inspector_name
        })

    if pmp_needs_protein:
        print(f"  PMP 064: Protein Content test")
        invoice_items.append({
            'item_code': 'PMP 064',
            'description': 'Sample Taking: Protein Content (Processed Meat Products)',
            'quantity': 1,
            'unit_amount': 503,
            'client_name': client_name,
            'invoice_date': date_str,
            'inspector_name': inspector_name
        })

    if not (pmp_needs_fat or pmp_needs_protein or pmp_needs_calcium or raw_needs_fat or raw_needs_protein or raw_needs_dna):
        print(f"  (No test line items - no samples taken)")

print("\n" + "=" * 100)
print(f"TOTAL INVOICE ITEMS GENERATED: {len(invoice_items)}")
print("=" * 100)

for i, item in enumerate(invoice_items, 1):
    print(f"\n{i}. {item['item_code']} | {item['description'][:80]}")
    print(f"   Quantity: {item['quantity']}, Unit Amount: {item['unit_amount']}")

print("\n" + "=" * 100)
print("COMPARISON WITH GOOGLE SHEET:")
print("=" * 100)
print("\nGoogle Sheet shows: 6 line items (4 hours/km + 2 tests)")
print(f"Backend generated: {len(invoice_items)} line items")
print()

if len(invoice_items) == 2:
    print("PROBLEM CONFIRMED:")
    print("  Backend is only generating 2 line items (RAW hours + RAW km)")
    print("  Missing: PMP hours, PMP km, PMP Fat test, PMP Protein test")
    print()
    print("ROOT CAUSE:")
    print("  Database has no PMP products for this inspection")
    print("  has_both = False (only RAW products exist)")
elif len(invoice_items) == 6:
    print("BACKEND IS CORRECT:")
    print("  Backend generated all 6 line items correctly")
    print("  The problem must be elsewhere (frontend filters or export function)")

print("\n" + "=" * 100)
