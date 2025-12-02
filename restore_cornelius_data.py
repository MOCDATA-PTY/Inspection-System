"""
Restore Cornelius Adams' KM and hours data for October-November 2025
Based on spreadsheet data provided
"""
import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User

# Get Cornelius's user
try:
    cornelius = User.objects.get(username='Cornelius')
    print(f"Found user: {cornelius.username} ({cornelius.first_name} {cornelius.last_name})")
except User.DoesNotExist:
    # Try alternative search
    try:
        cornelius = User.objects.get(first_name__icontains='Cornelius')
        print(f"Found user: {cornelius.username} ({cornelius.first_name} {cornelius.last_name})")
    except:
        print("ERROR: Could not find Cornelius user")
        exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
# Only actual inspections with KM/hours
inspection_data = [
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

print("="*80)
print("RESTORING CORNELIUS ADAMS' KM AND HOURS DATA")
print("="*80)

updated_count = 0
not_found_count = 0
multiple_found_count = 0

for date_str, client_name, hours, km in inspection_data:
    # Parse date
    date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()

    # Find inspection(s) for this date and client
    client_search = client_name.split('-')[0].strip()

    inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection=date_obj,
        client_name__icontains=client_search
    )

    count = inspections.count()

    if count == 0:
        print(f"NOT FOUND: {date_str} - {client_name}")
        not_found_count += 1
    elif count > 1:
        # Update all matching inspections
        inspections.update(
            hours=hours,
            km_traveled=km,
            inspector_id=cornelius.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = cornelius.id
        inspection.save()
        print(f"UPDATED: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += 1

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total data entries: {len(inspection_data)}")
print(f"Inspections updated: {updated_count}")
print(f"Not found: {not_found_count}")
print(f"Multiple matches: {multiple_found_count}")
print("="*80)

# Verify
print("\nVERIFYING UPDATES...")
oct_nov_with_km = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    km_traveled__isnull=False
).exclude(km_traveled=0).count()

oct_nov_with_hours = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    hours__isnull=False
).exclude(hours=0).count()

print(f"\nTotal Oct-Nov inspections with KM data: {oct_nov_with_km}")
print(f"Total Oct-Nov inspections with hours data: {oct_nov_with_hours}")
print("\nDone!")
