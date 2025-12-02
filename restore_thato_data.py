"""
Restore Thato Sekhotho's KM and hours data for October-November 2025
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

# Get Thato's user
try:
    thato = User.objects.get(username='Thato')
    print(f"Found user: {thato.username} ({thato.first_name} {thato.last_name})")
except User.DoesNotExist:
    # Try alternative username
    try:
        thato = User.objects.get(first_name__icontains='Thato')
        print(f"Found user: {thato.username} ({thato.first_name} {thato.last_name})")
    except:
        print("ERROR: Could not find Thato user")
        exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
# Only actual inspections with KM/hours (excluding annual leave, admin tasks, etc.)
inspection_data = [
    # October
    ('01/10/2025', 'Taylor made foods-Bloemfontein', 1, 22),
    ('01/10/2025', 'Jwayelani Foods Bloemfontein', 1, 10),
    ('02/10/2025', 'Tfs wholesale Bloemfontein', 1, 10),
    ('02/10/2025', 'Super Jumbo Bloemfontein', 1, 10),
    ('03/10/2025', 'Bibi cash and Carry-Harrismith', 1, 100),
    ('03/10/2025', 'Pick n Pay Family Harrismith', 1, 100),
    ('03/10/2025', 'Qwaqwa fruit and verg Market', 1, 100),
    ('13/10/2025', 'Food Lovers Market showgate', 1, 16),
    ('13/10/2025', 'Econo foods-Fauna', 1, 10),
    ('15/10/2025', 'Free State Meat Wholesalers', 1, 8),
    ('16/10/2025', 'Econo foods-Hilton', 1, 16),
    ('17/10/2025', 'Econo foods-Dan Pienaar', 1, 26),
    ('20/10/2025', 'Roots butchery Welkom-Mannys', 1, 84),
    ('23/10/2025', 'Sernick Butchery and deli', 1, 100),
    ('23/10/2025', 'Econo foods-Kroonstad', 1, 100),
    ('27/10/2025', 'Obc better butchery-Heidedal', 1, 10),
    ('28/10/2025', 'Sky country fresh meat-Thaba nchu', 1, 36.5),
    ('28/10/2025', 'Sun African products', 1, 36.5),
    ('28/10/2025', 'Sky country processed meats-Thaba nchu', 1, 36.5),
    ('31/10/2025', 'Boxer Superstore 1-Kimberley', 1, 84.5),
    ('31/10/2025', 'Boxer Superstore 2-Kimberley', 1, 84.5),
    # November
    ('04/11/2025', 'Pick n Pay-Lemo Mall', 1, 16),
    ('05/11/2025', 'Pick n Pay Family-Parys', 1, 100),
    ('05/11/2025', 'Spar-Parys', 1, 100),
    ('06/11/2025', 'Watloo Meat and chicken-Virginia', 1, 88),
    ('06/11/2025', 'Spar-Goldfields', 1, 88),
    ('07/11/2025', 'Jwayelani Botshabelo', 1, 60),
    ('07/11/2025', 'Econo foods-Botshabelo', 1, 60),
    ('10/11/2025', 'Ok Grocer-Brandfort', 1, 43),
    ('11/11/2025', 'Taylor made foods-Bloemfontein', 1, 22),
    ('12/11/2025', 'Heatherdale Slaghuis', 1, 15),
    ('12/11/2025', 'Ronnie\'s Meat Market', 1, 15),
    ('17/11/2025', 'Feiners meat market-CBD', 1, 15),
    ('17/11/2025', 'Roots Butchery-Heidedal', 1, 15),
    ('18/11/2025', 'Feiners meat market-Heidedal', 1, 10),
    ('24/11/2025', 'Highveld Butchery', 1, 11),
    ('25/11/2025', 'Simunye Spar-Senekal', 1, 100),
]

print("="*80)
print("RESTORING THATO SEKHOTHO'S KM AND HOURS DATA")
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
            inspector_id=thato.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = thato.id
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
