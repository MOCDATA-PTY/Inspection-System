"""
Check how many inspections were done between October and November
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import datetime

print("="*80)
print("INSPECTIONS BETWEEN OCTOBER AND NOVEMBER 2025")
print("="*80)

# October 2025 inspections
oct_start = datetime(2025, 10, 1).date()
oct_end = datetime(2025, 10, 31).date()

oct_inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=oct_start,
    date_of_inspection__lte=oct_end
)

oct_count = oct_inspections.count()

print(f"\nOCTOBER 2025: {oct_count} inspections")
print("-"*80)

# November 2025 inspections
nov_start = datetime(2025, 11, 1).date()
nov_end = datetime(2025, 11, 30).date()

nov_inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=nov_start,
    date_of_inspection__lte=nov_end
)

nov_count = nov_inspections.count()

print(f"\nNOVEMBER 2025: {nov_count} inspections")
print("-"*80)

# Total
total = oct_count + nov_count
print(f"\nTOTAL (Oct + Nov): {total} inspections")

# Check KM data for these inspections
print("\n" + "="*80)
print("CHECKING KM DATA FOR OCT-NOV INSPECTIONS")
print("="*80)

oct_nov_inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=oct_start,
    date_of_inspection__lte=nov_end
)

with_km_traveled = oct_nov_inspections.filter(
    km_traveled__isnull=False
).exclude(km_traveled=0).count()

with_inspection_km = oct_nov_inspections.filter(
    inspection_travel_distance_km__isnull=False
).exclude(inspection_travel_distance_km=0).count()

with_hours = oct_nov_inspections.filter(
    hours__isnull=False
).exclude(hours=0).count()

print(f"\nInspections with km_traveled: {with_km_traveled}/{total}")
print(f"Inspections with inspection_travel_distance_km: {with_inspection_km}/{total}")
print(f"Inspections with hours: {with_hours}/{total}")

# Show sample inspections
print("\n" + "="*80)
print("SAMPLE OCTOBER INSPECTIONS (first 10)")
print("="*80)

for insp in oct_inspections[:10]:
    print(f"\nID: {insp.remote_id}")
    print(f"  Date: {insp.date_of_inspection}")
    print(f"  Client: {insp.client_name}")
    print(f"  Inspector ID: {insp.inspector_id}")
    print(f"  KM Traveled: {insp.km_traveled}")
    print(f"  Inspection Travel KM: {insp.inspection_travel_distance_km}")
    print(f"  Hours: {insp.hours}")

print("\n" + "="*80)
print("SAMPLE NOVEMBER INSPECTIONS (first 10)")
print("="*80)

for insp in nov_inspections[:10]:
    print(f"\nID: {insp.remote_id}")
    print(f"  Date: {insp.date_of_inspection}")
    print(f"  Client: {insp.client_name}")
    print(f"  Inspector ID: {insp.inspector_id}")
    print(f"  KM Traveled: {insp.km_traveled}")
    print(f"  Inspection Travel KM: {insp.inspection_travel_distance_km}")
    print(f"  Hours: {insp.hours}")

print("\n" + "="*80)
