"""
Transfer all inspections from Hellen user to Dimakatso user
Because Dimakatso Modiba is the correct user, not Hellen
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
print("TRANSFERRING INSPECTIONS FROM HELLEN TO DIMAKATSO")
print("="*80)

# Get users
try:
    hellen = User.objects.get(username='Hellen')
    print(f"Source user: {hellen.username} (ID: {hellen.id})")
except User.DoesNotExist:
    print("ERROR: Could not find Hellen user")
    exit(1)

try:
    dimakatso = User.objects.get(username='Dimakatso')
    print(f"Target user: {dimakatso.username} - {dimakatso.first_name} {dimakatso.last_name} (ID: {dimakatso.id})")
except User.DoesNotExist:
    print("ERROR: Could not find Dimakatso user")
    exit(1)

# Count inspections before transfer
hellen_inspections = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=hellen.id
).count()
print(f"\nInspections currently assigned to Hellen: {hellen_inspections}")

dimakatso_inspections_before = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=dimakatso.id
).count()
print(f"Inspections currently assigned to Dimakatso: {dimakatso_inspections_before}")

# Transfer all inspections from Hellen to Dimakatso
print("\nTransferring inspections...")
updated_count = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=hellen.id
).update(inspector_id=dimakatso.id)

print(f"Transferred {updated_count} inspections from Hellen to Dimakatso")

# Verify
hellen_after = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=hellen.id
).count()
dimakatso_after = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=dimakatso.id
).count()

print("\n" + "="*80)
print("VERIFICATION")
print("="*80)
print(f"Hellen inspections after transfer: {hellen_after}")
print(f"Dimakatso inspections after transfer: {dimakatso_after}")

# Check Oct-Nov specifically
dimakatso_oct_nov = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=dimakatso.id,
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date()
).count()

dimakatso_oct_nov_with_km = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=dimakatso.id,
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    km_traveled__isnull=False
).exclude(km_traveled=0).count()

print(f"\nDimakatso Oct-Nov 2025 inspections: {dimakatso_oct_nov}")
print(f"Dimakatso Oct-Nov 2025 with KM data: {dimakatso_oct_nov_with_km}")

print("\n" + "="*80)
print("Done!")
