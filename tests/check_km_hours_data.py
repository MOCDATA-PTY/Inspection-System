#!/usr/bin/env python3
"""
Check if inspections have KM and Hours data
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

print("=" * 100)
print("CHECKING KM AND HOURS DATA IN DATABASE")
print("=" * 100)

# Get total inspections
total = FoodSafetyAgencyInspection.objects.count()
print(f"\nTotal inspections in database: {total:,}")

# Check how many have KM and Hours
with_km = FoodSafetyAgencyInspection.objects.filter(km_traveled__isnull=False).exclude(km_traveled=0).count()
with_hours = FoodSafetyAgencyInspection.objects.filter(hours__isnull=False).exclude(hours=0).count()
with_both = FoodSafetyAgencyInspection.objects.filter(
    km_traveled__isnull=False,
    hours__isnull=False
).exclude(km_traveled=0, hours=0).count()

print(f"\nInspections with KM data: {with_km:,} ({with_km/total*100:.1f}%)")
print(f"Inspections with Hours data: {with_hours:,} ({with_hours/total*100:.1f}%)")
print(f"Inspections with BOTH KM and Hours: {with_both:,} ({with_both/total*100:.1f}%)")

# Check by commodity
print("\n" + "=" * 100)
print("BY COMMODITY TYPE:")
print("=" * 100)

for commodity in ['RAW', 'PMP', 'POULTRY', 'EGGS']:
    total_commodity = FoodSafetyAgencyInspection.objects.filter(commodity=commodity).count()
    with_both_commodity = FoodSafetyAgencyInspection.objects.filter(
        commodity=commodity,
        km_traveled__isnull=False,
        hours__isnull=False
    ).exclude(km_traveled=0, hours=0).count()

    if total_commodity > 0:
        percentage = with_both_commodity / total_commodity * 100
        print(f"\n{commodity}:")
        print(f"  Total: {total_commodity:,}")
        print(f"  With KM & Hours: {with_both_commodity:,} ({percentage:.1f}%)")

# Show recent inspections with KM and Hours
print("\n" + "=" * 100)
print("RECENT INSPECTIONS WITH KM AND HOURS (last 10):")
print("=" * 100)

recent = FoodSafetyAgencyInspection.objects.filter(
    km_traveled__isnull=False,
    hours__isnull=False
).exclude(
    km_traveled=0,
    hours=0
).order_by('-date_of_inspection')[:10]

print(f"\n{'Date':<12} {'Commodity':<10} {'Client':<40} {'KM':<8} {'Hours':<8}")
print("-" * 100)

for insp in recent:
    client = (insp.client_name[:37] + '...') if len(insp.client_name) > 40 else insp.client_name
    print(f"{str(insp.date_of_inspection):<12} {insp.commodity:<10} {client:<40} {insp.km_traveled:<8} {insp.hours:<8}")

# Check December 2025 specifically (for the export)
print("\n" + "=" * 100)
print("DECEMBER 2025 DATA (FOR EXPORT):")
print("=" * 100)

dec_total = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__year=2025,
    date_of_inspection__month=12,
    commodity__in=['RAW', 'PMP']
).count()

dec_with_both = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__year=2025,
    date_of_inspection__month=12,
    commodity__in=['RAW', 'PMP'],
    km_traveled__isnull=False,
    hours__isnull=False
).exclude(km_traveled=0, hours=0).count()

print(f"\nDecember 2025 RAW/PMP inspections: {dec_total:,}")
print(f"December 2025 RAW/PMP with KM & Hours: {dec_with_both:,}")

if dec_total > 0:
    print(f"Percentage with KM & Hours: {dec_with_both/dec_total*100:.1f}%")

# Show export-eligible inspections
export_eligible = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__year=2025,
    date_of_inspection__month=12,
    commodity__in=['RAW', 'PMP'],
    km_traveled__isnull=False,
    hours__isnull=False
).exclude(km_traveled=0, hours=0).count()

print(f"\nEXPORT-ELIGIBLE INSPECTIONS (December 2025 RAW/PMP with KM & Hours): {export_eligible:,}")

print("\n" + "=" * 100)