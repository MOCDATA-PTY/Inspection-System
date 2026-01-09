"""
Check if ANY inspections exist in the database
"""
import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("="*80)
print("CHECKING BASIC DATABASE CONNECTION AND DATA")
print("="*80)

# Total inspections
total = FoodSafetyAgencyInspection.objects.count()
print(f"\nTotal inspections in database: {total}")

# Oct-Nov 2025 inspections
oct_nov_total = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date()
).count()
print(f"Oct-Nov 2025 inspections: {oct_nov_total}")

# Inspections with hours
with_hours = FoodSafetyAgencyInspection.objects.filter(
    hours__isnull=False
).count()
print(f"Inspections with hours (not NULL): {with_hours}")

# Inspections with hours > 0
with_hours_gt_0 = FoodSafetyAgencyInspection.objects.filter(
    hours__gt=0
).count()
print(f"Inspections with hours > 0: {with_hours_gt_0}")

# Inspections with km
with_km = FoodSafetyAgencyInspection.objects.filter(
    km_traveled__isnull=False
).count()
print(f"Inspections with KM (not NULL): {with_km}")

# Inspections with km > 0
with_km_gt_0 = FoodSafetyAgencyInspection.objects.filter(
    km_traveled__gt=0
).count()
print(f"Inspections with KM > 0: {with_km_gt_0}")

# Oct-Nov with hours
oct_nov_with_hours = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    hours__gt=0
).count()
print(f"\nOct-Nov 2025 with hours > 0: {oct_nov_with_hours}")

# Oct-Nov with km
oct_nov_with_km = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    km_traveled__gt=0
).count()
print(f"Oct-Nov 2025 with KM > 0: {oct_nov_with_km}")

# Sample of Oct-Nov inspections
print("\n" + "-"*80)
print("SAMPLE OCT-NOV INSPECTIONS (first 5):")
print("-"*80)

sample = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date()
).order_by('date_of_inspection')[:5]

for insp in sample:
    print(f"\nDate: {insp.date_of_inspection}")
    print(f"  Client: {insp.client_name}")
    print(f"  Inspector ID: {insp.inspector_id}")
    print(f"  Hours: {insp.hours}")
    print(f"  KM: {insp.km_traveled}")

print("\n" + "="*80)
print("Done!")
