#!/usr/bin/env python3
"""
Verify what code is actually running in production.
This imports the actual export function and shows what query it will execute.
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

print("=" * 100)
print("PRODUCTION CODE VERIFICATION")
print("=" * 100)

# Read the actual export function code
import inspect
from main.views.core_views import export_sheet

print("\n1. CHECKING EXPORT FUNCTION CODE:")
print("-" * 100)
source_lines = inspect.getsourcelines(export_sheet)[0]
for i, line in enumerate(source_lines[4890-4850:4920-4850], start=4890):
    if i >= 4894 and i <= 4910:
        print(f"{i}: {line.rstrip()}")

print("\n" + "=" * 100)
print("2. TESTING EXPORT QUERY DIRECTLY:")
print("-" * 100)

# Test with Roots Butchery Birch Acres date
test_date = datetime(2025, 12, 5).date()
start_date = test_date
end_date = test_date

print(f"\nTest date range: {start_date} to {end_date}")

# Exact query from export function
inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=start_date,
    date_of_inspection__lte=end_date
).select_related(
    'sent_by', 'rfi_uploaded_by', 'invoice_uploaded_by'
).distinct('commodity', 'remote_id').order_by('commodity', 'remote_id', '-date_of_inspection', 'inspector_name')

print(f"\nTotal inspections returned: {inspections.count()}")

# Show Roots Butchery Birch Acres specifically
roots_birch = [insp for insp in inspections if 'Birch Acres' in insp.client_name and 'Roots' in insp.client_name]
print(f"\nRoots Butchery Birch Acres inspections: {len(roots_birch)}")
for insp in roots_birch:
    print(f"  - {insp.commodity}-{insp.remote_id} | {insp.product_name} | Hours: {insp.hours} | KM: {insp.km_traveled}")

print("\n" + "=" * 100)
print("3. RAW DATABASE CHECK:")
print("-" * 100)

# Check raw data without distinct
raw_inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains='Roots Butchery Birch Acres',
    date_of_inspection=test_date,
    hours__isnull=False,
    km_traveled__isnull=False
).order_by('commodity', 'remote_id')

print(f"\nRaw inspections for Roots Birch Acres (no distinct): {raw_inspections.count()}")
for insp in raw_inspections:
    print(f"  - {insp.commodity}-{insp.remote_id} | {insp.product_name}")

print("\n" + "=" * 100)
print("VERIFICATION COMPLETE")
print("=" * 100)
print("\nIf this shows RAW inspections but the export doesn't, then:")
print("1. Python bytecode cache needs clearing (run force_clear_cache.py)")
print("2. Gunicorn workers need full restart (sudo systemctl restart gunicorn)")
print()