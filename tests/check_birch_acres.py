import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Q
from datetime import datetime

print("=" * 100)
print("ROOTS BUTCHERY BIRCH ACRES - DUPLICATE CHECK")
print("=" * 100)

# Check all Roots Butchery Birch Acres on 05/12/2025
date = datetime(2025, 12, 5).date()
inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains='Roots Butchery Birch Acres',
    date_of_inspection=date
).order_by('commodity', 'remote_id')

print(f"\nTotal inspections found: {inspections.count()}")
print("\n" + "=" * 100)

for idx, insp in enumerate(inspections, 1):
    print(f"\nINSPECTION {idx}:")
    print(f"  Commodity:        {insp.commodity}")
    print(f"  Remote ID:        {insp.remote_id}")
    print(f"  Unique Key:       {insp.commodity}-{insp.remote_id}")
    print(f"  Inspector:        {insp.inspector_name}")
    print(f"  Client:           {insp.client_name}")
    print(f"  Date:             {insp.date_of_inspection}")
    print(f"  Product Name:     {insp.product_name}")
    print(f"  Hours:            {insp.hours}")
    print(f"  KM:               {insp.km_traveled}")
    print(f"  Fat:              {insp.fat}")
    print(f"  Protein:          {insp.protein}")

print("\n" + "=" * 100)
print("\nNow checking SUPERSPAR Knysna duplicates...")
print("=" * 100)

date = datetime(2025, 12, 3).date()
knysna = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains='Knysna',
    date_of_inspection=date,
    commodity='RAW'
).order_by('remote_id')

print(f"\nTotal RAW inspections at SUPERSPAR Knysna: {knysna.count()}")

for idx, insp in enumerate(knysna, 1):
    print(f"\n  {idx}. RAW-{insp.remote_id} | {insp.product_name} | Hours: {insp.hours} | KM: {insp.km_traveled}")

print("\n" + "=" * 100)
print("\nChecking export query with current filters...")
print("=" * 100)

# Test the actual export query (NO LAB SAMPLE FILTER)
export_inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    client_name__icontains='Roots Butchery Birch Acres',
    date_of_inspection=datetime(2025, 12, 5).date(),
    hours__isnull=False,
    km_traveled__isnull=False
).order_by('commodity', 'remote_id')

print(f"\nBefore distinct: {export_inspections.count()} inspections")
for insp in export_inspections:
    print(f"  - {insp.commodity}-{insp.remote_id} | {insp.product_name}")

# Now with distinct
export_distinct = export_inspections.distinct('commodity', 'remote_id').order_by('commodity', 'remote_id', '-date_of_inspection', 'inspector_name')

print(f"\nAfter distinct('commodity', 'remote_id'): {export_distinct.count()} inspections")
for insp in export_distinct:
    print(f"  - {insp.commodity}-{insp.remote_id} | {insp.product_name}")

print("\n" + "=" * 100)