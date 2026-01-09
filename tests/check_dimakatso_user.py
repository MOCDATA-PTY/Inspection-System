"""
Check Dimakatso user and inspections
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
print("CHECKING DIMAKATSO AND HELLEN USERS")
print("="*80)

# Check for Dimakatso user
print("\nSearching for Dimakatso user...")
dimakatso_users = User.objects.filter(username__icontains='dimakatso')
print(f"Users with 'dimakatso' in username: {dimakatso_users.count()}")
for user in dimakatso_users:
    print(f"  - Username: {user.username}, Name: {user.first_name} {user.last_name}, ID: {user.id}")

# Also search by first name
dimakatso_by_name = User.objects.filter(first_name__icontains='dimakatso')
print(f"\nUsers with 'dimakatso' in first name: {dimakatso_by_name.count()}")
for user in dimakatso_by_name:
    print(f"  - Username: {user.username}, Name: {user.first_name} {user.last_name}, ID: {user.id}")

# Check for Hellen user
print("\n" + "-"*80)
print("Searching for Hellen user...")
hellen_users = User.objects.filter(username__icontains='hellen')
print(f"Users with 'hellen' in username: {hellen_users.count()}")
for user in hellen_users:
    print(f"  - Username: {user.username}, Name: {user.first_name} {user.last_name}, ID: {user.id}")

# Also search by first name
hellen_by_name = User.objects.filter(first_name__icontains='hellen')
print(f"\nUsers with 'hellen' in first name: {hellen_by_name.count()}")
for user in hellen_by_name:
    print(f"  - Username: {user.username}, Name: {user.first_name} {user.last_name}, ID: {user.id}")

# Check inspections for each user found
print("\n" + "="*80)
print("CHECKING INSPECTIONS FOR OCTOBER-NOVEMBER 2025")
print("="*80)

all_users = list(dimakatso_users) + list(dimakatso_by_name) + list(hellen_users) + list(hellen_by_name)
unique_users = {user.id: user for user in all_users}.values()

for user in unique_users:
    print(f"\nUser: {user.username} ({user.first_name} {user.last_name}) - ID: {user.id}")

    # Total inspections
    total_inspections = FoodSafetyAgencyInspection.objects.filter(
        inspector_id=user.id,
        date_of_inspection__gte=datetime(2025, 10, 1).date(),
        date_of_inspection__lte=datetime(2025, 11, 30).date()
    ).count()
    print(f"  Total Oct-Nov inspections: {total_inspections}")

    # Inspections with KM data
    with_km = FoodSafetyAgencyInspection.objects.filter(
        inspector_id=user.id,
        date_of_inspection__gte=datetime(2025, 10, 1).date(),
        date_of_inspection__lte=datetime(2025, 11, 30).date(),
        km_traveled__isnull=False
    ).exclude(km_traveled=0).count()
    print(f"  Inspections with KM data: {with_km}")

    # Inspections with hours data
    with_hours = FoodSafetyAgencyInspection.objects.filter(
        inspector_id=user.id,
        date_of_inspection__gte=datetime(2025, 10, 1).date(),
        date_of_inspection__lte=datetime(2025, 11, 30).date(),
        hours__isnull=False
    ).exclude(hours=0).count()
    print(f"  Inspections with hours data: {with_hours}")

    # Sample some inspections
    sample_inspections = FoodSafetyAgencyInspection.objects.filter(
        inspector_id=user.id,
        date_of_inspection__gte=datetime(2025, 10, 1).date(),
        date_of_inspection__lte=datetime(2025, 11, 30).date()
    ).order_by('date_of_inspection')[:5]

    if sample_inspections:
        print(f"  Sample inspections:")
        for insp in sample_inspections:
            print(f"    - {insp.date_of_inspection}: {insp.client_name} (KM: {insp.km_traveled}, Hours: {insp.hours})")

print("\n" + "="*80)
print("Done!")
