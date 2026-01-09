"""
Set Dimakatso's inspections to have inspector_id = 202
"""
import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User

print("="*80)
print("SETTING DIMAKATSO'S INSPECTOR ID TO 202")
print("="*80)

# Get Dimakatso user
try:
    dimakatso = User.objects.get(id=107)
    print(f"Dimakatso user: ID {dimakatso.id}, Username: {dimakatso.username}, Name: {dimakatso.first_name} {dimakatso.last_name}")
except User.DoesNotExist:
    print("ERROR: Could not find Dimakatso user with ID 107")
    exit(1)

# Count current inspections with inspector_id=107
inspections_107 = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=107
).count()
print(f"\nInspections currently with inspector_id=107: {inspections_107}")

# Count current inspections with inspector_id=202
inspections_202_before = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=202
).count()
print(f"Inspections currently with inspector_id=202: {inspections_202_before}")

# Update all inspections from inspector_id=107 to inspector_id=202
print("\nUpdating inspector_id from 107 to 202...")
updated_count = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=107
).update(inspector_id=202)

print(f"Updated {updated_count} inspections")

# Verify
after_107 = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=107
).count()
after_202 = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=202
).count()

print("\n" + "="*80)
print("VERIFICATION")
print("="*80)
print(f"Inspections with inspector_id=107: {after_107}")
print(f"Inspections with inspector_id=202: {after_202}")

# Check Oct-Nov specifically
oct_nov_202 = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=202,
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date()
).count()

oct_nov_202_with_km = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=202,
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    km_traveled__isnull=False
).exclude(km_traveled=0).count()

print(f"\nInspector 202 Oct-Nov 2025 inspections: {oct_nov_202}")
print(f"Inspector 202 Oct-Nov 2025 with KM data: {oct_nov_202_with_km}")

print("\n" + "="*80)
print("Done!")
