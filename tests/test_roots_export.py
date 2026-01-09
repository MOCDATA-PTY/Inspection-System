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
print("ROOTS BUTCHERY - VOSLOORUS EXPORT TEST")
print("=" * 100)

# Query all Roots Butchery inspections on 03/11/2025
date = datetime(2025, 11, 3).date()
inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains='Roots Butchery',
    client_name__icontains='Vosloorus',
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
    print(f"  Product Class:    {insp.product_class}")
    print(f"  Hours:            {insp.hours}")
    print(f"  KM Traveled:      {insp.km_traveled}")
    print(f"  Fat:              {insp.fat}")
    print(f"  Protein:          {insp.protein}")
    print(f"  Calcium:          {insp.calcium}")
    print(f"  DNA:              {insp.dna}")
    print(f"  Bought Sample:    {insp.bought_sample}")

    # Check if meets export criteria
    has_hours_km = insp.hours is not None and insp.km_traveled is not None
    has_lab_sample = (insp.fat or insp.protein or insp.calcium or insp.dna or
                     insp.bought_sample is not None)

    meets_export = has_hours_km and has_lab_sample
    print(f"\n  >>> EXPORT ELIGIBLE: {meets_export}")
    if not meets_export:
        if not has_hours_km:
            print(f"      - Missing hours/km")
        if not has_lab_sample:
            print(f"      - Missing lab sample")

print("\n" + "=" * 100)
print("\nNow testing export query with deduplication...")
print("=" * 100)

# Test the actual export query
export_inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains='Roots Butchery',
    client_name__icontains='Vosloorus',
    date_of_inspection=date,
    hours__isnull=False,
    km_traveled__isnull=False
).filter(
    Q(fat=True) |
    Q(protein=True) |
    Q(calcium=True) |
    Q(dna=True) |
    Q(bought_sample__isnull=False)
).distinct('commodity', 'remote_id').order_by('commodity', 'remote_id', '-date_of_inspection', 'inspector_name')

print(f"\nExport query returned {export_inspections.count()} inspections:")
for idx, insp in enumerate(export_inspections, 1):
    print(f"\n  {idx}. {insp.commodity}-{insp.remote_id} | {insp.inspector_name} | {insp.product_name}")

print("\n" + "=" * 100)