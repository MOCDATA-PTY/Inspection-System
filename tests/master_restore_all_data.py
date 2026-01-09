"""
Master script to restore ALL inspector KM and hours data for October-November 2025
This runs all restorations with proper transaction handling
"""
import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User
from django.db import transaction

print("="*80)
print("MASTER DATA RESTORATION - ALL INSPECTORS")
print("="*80)
print(f"Target database: PostgreSQL at 82.25.97.159")
print(f"Date range: October-November 2025")
print("="*80)

# Check initial state
initial_with_km = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    km_traveled__gt=0
).count()
print(f"\nInitial Oct-Nov inspections with KM: {initial_with_km}")

total_updated = 0
total_not_found = 0

# Define all restoration data
ALL_RESTORATION_DATA = {
    'Cornelius': [
        # October
        ('01/10/2025', 'Kakamas Slaghuis', 1, 5),
        ('06/10/2025', 'wild beef kakamas', 1, 5),
        ('06/10/2025', 'one price store', 1, 5),
        ('07/10/2025', 'Oppi Draai Butchery', 1, 80),
        ('07/10/2025', 'Bravo meats', 1, 80),
        ('08/10/2025', 'Aftin Khan Supermarket', 1, 1),
        ('09/10/2025', 'Kekkel and Kraai Kakamas', 1, 5),
        ('10/10/2025', 'Kolskoot Vleismark', 1, 70),
        ('10/10/2025', 'Upington Slaghuis', 1, 70),
        ('10/10/2025', 'Try me supermarket', 1, 70),
        ('13/10/2025', 'PNP Upington', 1, 70),
        ('14/10/2025', 'Superspar Springbok Voortrekker', 1, 100),
        ('15/10/2025', 'Spar Port Nolloth', 1, 140),
        ('15/10/2025', 'DC meats springbok', 1, 100),
        ('15/10/2025', 'dieplaas slaghuis springbok', 1, 100),
        ('15/10/2025', 'Die Plaas Slaghuis Springbok', 1, 100),
        ('23/10/2025', 'Food Zone Keimoes', 1, 60),
        ('24/10/2025', 'Marchand slaghuis', 1, 24),
        ('31/10/2025', 'Foodzone Kakamas', 1, 5),
        # November
        ('03/11/2025', 'Wickens Vleismark', 1, 70),
        ('04/11/2025', 'Kekkel en kraai kakamas', 1, 5),
        ('05/11/2025', 'Superspar Kathu', 1, 150),
        ('05/11/2025', 'Food Lovers Kathu', 1, 150),
        ('06/11/2025', 'Pick n Pay Kathu', 1, 150),
        ('06/11/2025', 'Boxer Kathu', 1, 150),
        ('06/11/2025', 'Food Zone Kathu', 1, 50),
        ('06/11/2025', 'Superspar Kuruman', 1, 84),
        ('11/11/2025', 'Food lovers Upington', 1, 70),
        ('12/11/2025', 'spar keimoes', 1, 60),
        ('12/11/2025', 'Savemor Spar Keimoes', 1, 60),
        ('13/11/2025', 'Kalahari Vleishuis Keimoes', 1, 60),
    ]
}

# Process each inspector
for username, data in ALL_RESTORATION_DATA.items():
    print(f"\n{'='*80}")
    print(f"Processing: {username}")
    print(f"{'='*80}")

    # Get user
    try:
        user = User.objects.get(username=username)
        print(f"Found user: {user.username} (ID: {user.id})")
    except User.DoesNotExist:
        print(f"ERROR: User '{username}' not found!")
        continue

    updated = 0
    not_found = 0

    # Use explicit transaction
    with transaction.atomic():
        for date_str, client_name, hours, km in data:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
            client_search = client_name.split('-')[0].strip()

            # Find matching inspections
            inspections = FoodSafetyAgencyInspection.objects.filter(
                date_of_inspection=date_obj,
                client_name__icontains=client_search
            )

            count = inspections.count()

            if count == 0:
                print(f"  NOT FOUND: {date_str} - {client_name}")
                not_found += 1
            else:
                # Update all matching inspections
                inspections.update(
                    hours=hours,
                    km_traveled=km,
                    inspector_id=user.id
                )
                print(f"  UPDATED {count}: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
                updated += count

    print(f"\n{username} Summary: {updated} updated, {not_found} not found")
    total_updated += updated
    total_not_found += not_found

# Final verification
print("\n" + "="*80)
print("FINAL VERIFICATION")
print("="*80)

final_with_km = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    km_traveled__gt=0
).count()

final_with_hours = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    hours__gt=0
).count()

print(f"\nInitial with KM: {initial_with_km}")
print(f"Final with KM: {final_with_km}")
print(f"Final with hours: {final_with_hours}")
print(f"\nTotal updated: {total_updated}")
print(f"Total not found: {total_not_found}")
print(f"Increase: +{final_with_km - initial_with_km} inspections")

print("\n" + "="*80)
print("✅ RESTORATION COMPLETE!")
print("="*80)
