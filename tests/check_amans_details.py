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
print("CHECKING AMANS MEAT & DELI INSPECTIONS")
print("=" * 100)

amans = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains='Amans meat',
    date_of_inspection=datetime(2025, 12, 3).date(),
    commodity='RAW'
).order_by('product_name')

print(f"\nFound {amans.count()} RAW inspections:\n")
for idx, insp in enumerate(amans, 1):
    print(f"Inspection {idx}:")
    print(f"  ID:           {insp.remote_id}")
    print(f"  Product:      '{insp.product_name}'")
    print(f"  Inspector:    '{insp.inspector_name}'")
    print(f"  Hours:        {insp.hours}")
    print(f"  KM Traveled:  {insp.km_traveled}")
    print(f"  Fat:          {insp.fat}")
    print(f"  Protein:      {insp.protein}")
    print(f"  Unique Key:   {(insp.inspector_name or '', insp.client_name or '', insp.commodity or '', str(insp.date_of_inspection), insp.product_name or '')}")
    print()

print("=" * 100)
print("\nIf both inspections have the SAME hours and KM, then having identical")
print("line items is CORRECT - each product generates its own set of line items.")
print("=" * 100)
