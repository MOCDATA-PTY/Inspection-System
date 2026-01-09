"""
Restore Mpeluza Xola's KM and hours data for October-November 2025
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

# Get Xola's user
try:
    xola = User.objects.get(username='Xola')
    print(f"Found user: {xola.username} ({xola.first_name} {xola.last_name})")
except User.DoesNotExist:
    # Try alternative search
    try:
        xola = User.objects.get(first_name__icontains='Xola')
        print(f"Found user: {xola.username} ({xola.first_name} {xola.last_name})")
    except:
        print("ERROR: Could not find Xola user")
        exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
# Only actual inspections with KM/hours (excluding admin tasks, meetings, failed inspections)
inspection_data = [
    # October
    ('02/10/2025', 'Kwikspar Flimieda', 1, 50),
    ('03/10/2025', 'Superior Butchery', 1, 20),
    ('03/10/2025', 'OBC Butchery', 1, 20),
    ('07/10/2025', 'Robertos Supermarket', 1, 100),
    ('07/10/2025', 'Ori Butchery', 1, 100),
    ('09/10/2025', 'Superspar MCC', 1, 50),
    ('09/10/2025', 'Foodzone Supermarket', 1, 50),
    ('13/10/2025', 'Spar-Bloemhof', 1, 100),
    ('13/10/2025', 'Superspar-Christiana', 1, 120),
    ('13/10/2025', 'Vleis Boer', 1, 100),
    ('14/10/2025', 'Superspar-Vryburg', 1, 100),
    ('14/10/2025', 'Super Meat', 1, 100),
    ('14/10/2025', 'Boxer-Vryburg', 1, 100),
    ('15/10/2025', 'Jwayelani Foods', 1, 50),
    ('15/10/2025', 'Roots Butchery-Taung', 1, 50),
    ('15/10/2025', 'Boxer 1-Taung', 1, 50),
    ('20/10/2025', 'Spar Baillie Park', 1, 20),
    ('20/10/2025', 'Insleep Supermarket', 1, 20),
    ('24/10/2025', 'Spar Blyvoor', 1, 50),
    ('29/10/2025', 'Pick n Pay Mahikeng Crossing', 1, 100),
    ('29/10/2025', 'Riviera Butchery', 1, 100),
    ('31/10/2025', 'Superspar Palm Sands', 1, 100),
    # November
    ('04/11/2025', 'Roots Butchery-Klerksdorp', 1, 50),
    ('04/11/2025', 'Super S Butchery', 1, 50),
    ('07/11/2025', 'Pick n Pay Carletonville Mall', 1, 70),
    ('11/11/2025', 'Roots Butchery-Fochville', 1, 60),
    ('13/11/2025', 'Syfergat Vleis', 1, 100),
    ('17/11/2025', 'Superspar Mooi Nooi', 1, 80),
    ('17/11/2025', 'Waltloo Meat and Chicken-Marikana', 1, 80),
    ('17/11/2025', 'Boxer Superstore-Marikana', 1, 80),
    ('19/11/2025', 'Eskort Rustenburg', 1, 50),
    ('19/11/2025', 'SPAR-Kroondal', 1, 80),
    ('20/11/2025', 'Pennys Perfect Biltong', 1, 60),
    ('20/11/2025', 'Biltong and Braai Skuur', 1, 60),
    ('20/11/2025', 'The Legacy Butchery', 1, 60),
    ('24/11/2025', 'Polana Butchery', 1, 100),
    ('27/11/2025', 'Prima Meat Butchery', 1, 40),
    ('28/11/2025', 'The Biltong Shop', 1, 50),
]

print("="*80)
print("RESTORING MPELUZA XOLA'S KM AND HOURS DATA")
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
            inspector_id=xola.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = xola.id
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
