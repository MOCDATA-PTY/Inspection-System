"""
Fix Dimakatso's inspector ID - should be 202, not 107
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
print("FIXING DIMAKATSO'S INSPECTOR ID")
print("="*80)

# Check user ID 202
try:
    correct_user = User.objects.get(id=202)
    print(f"User with ID 202: {correct_user.username} - {correct_user.first_name} {correct_user.last_name}")
except User.DoesNotExist:
    print("ERROR: Could not find user with ID 202")
    exit(1)

# Check current user (ID 107)
try:
    wrong_user = User.objects.get(id=107)
    print(f"User with ID 107: {wrong_user.username} - {wrong_user.first_name} {wrong_user.last_name}")
except User.DoesNotExist:
    print("Note: No user with ID 107")

# Count inspections
inspections_107 = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=107
).count()
print(f"\nInspections currently assigned to ID 107: {inspections_107}")

inspections_202 = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=202
).count()
print(f"Inspections currently assigned to ID 202: {inspections_202}")

# Transfer all inspections from ID 107 to ID 202
print("\nTransferring inspections from ID 107 to ID 202...")
updated_count = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=107
).update(inspector_id=202)

print(f"Transferred {updated_count} inspections")

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
print(f"Inspections for ID 107 after transfer: {after_107}")
print(f"Inspections for ID 202 after transfer: {after_202}")

# Check Oct-Nov specifically for ID 202
oct_nov = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=202,
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date()
).count()

oct_nov_with_km = FoodSafetyAgencyInspection.objects.filter(
    inspector_id=202,
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    km_traveled__isnull=False
).exclude(km_traveled=0).count()

print(f"\nUser ID 202 Oct-Nov 2025 inspections: {oct_nov}")
print(f"User ID 202 Oct-Nov 2025 with KM data: {oct_nov_with_km}")

print("\n" + "="*80)
print("Done!")
