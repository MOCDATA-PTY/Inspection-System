"""
Restore Sandisiwe Dlisani's KM and hours data for October-November 2025
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

# Get Sandisiwe's user
try:
    sandisiwe = User.objects.get(username='Sandisiwe')
    print(f"Found user: {sandisiwe.username} ({sandisiwe.first_name} {sandisiwe.last_name})")
except User.DoesNotExist:
    # Try alternative search
    try:
        sandisiwe = User.objects.get(first_name__icontains='Sandisiwe')
        print(f"Found user: {sandisiwe.username} ({sandisiwe.first_name} {sandisiwe.last_name})")
    except:
        print("ERROR: Could not find Sandisiwe user")
        exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
# Only actual inspections with KM/hours (excluding admin tasks, meetings, annual leave)
inspection_data = [
    # October
    ('01/10/2025', 'Superspar-Gonubie', 1, 48),
    ('01/10/2025', 'Gonubie Butchery', 1, 46),
    ('02/10/2025', 'Nick\'s Foods Berlin Spar', 1, 86),
    ('03/10/2025', 'Superspar Vincent', 1, 20),
    ('08/10/2025', 'Superspar nick\'s foods EL', 1, 14),
    ('08/10/2025', 'Barakah halaal meats', 1, 16),
    ('10/10/2025', 'Berlin Meats', 1, 86),
    ('10/10/2025', 'Superspar Zwelitsha', 1, 90),
    ('13/10/2025', 'Food lover\'s Market Vincent', 1, 24),
    ('15/10/2025', 'Cathcart Butchery', 1, 139),
    ('16/10/2025', 'Spar Lady frere', 1, 115),
    ('17/10/2025', 'Spar Cala', 1, 167),
    ('20/10/2025', 'Spar kwa wicks', 1, 167),
    ('20/10/2025', 'Jumbo wholesale Maclear', 2, 167),
    ('21/10/2025', 'Shoprite Sp-Elliot', 1, 100),
    ('22/10/2025', 'Boxer Engcobo', 1, 130),
    ('22/10/2025', 'Spargs Superspar Engcobo', 1, 130),
    ('22/10/2025', 'Eat sum meat west', 1, 130),
    ('23/10/2025', 'Boytjies Butcher west bank', 1, 10),
    ('24/10/2025', 'Superspar nick\'s foods berea', 1, 20),
    ('27/10/2025', 'Econo Foods', 1, 16),
    ('27/10/2025', 'AL Mawashi halaal butchery', 1, 20),
    ('27/10/2025', 'Superspar Nahoon', 1, 24),
    ('28/10/2025', 'Kenton Butchery', 1, 157),
    ('28/10/2025', 'Spar-Kenton-on-sea', 1, 157),
    ('29/10/2025', 'Superspar-Mdantsane', 1, 68),
    ('29/10/2025', 'Prime Meats', 1, 50),
    ('30/10/2025', 'Dhayson\'s Kwik Spar', 1, 66),
    ('30/10/2025', 'Spar nick\'s foods daily', 1, 66),
    ('31/10/2025', 'Savemor Hoogsback', 1, 100),
    ('31/10/2025', 'Superspar Kwantu', 1, 100),
    # November
    ('03/11/2025', 'Superspar spargs beacon bay north', 1, 28),
    ('03/11/2025', 'Econo Foods beacon bay', 1, 26),
    ('05/11/2025', 'Mooiplaas Butchery', 1, 50),
    ('06/11/2025', 'Spar Savemor-Mdantsane', 1, 60),
    ('06/11/2025', 'Obc better butchery', 1, 60),
    ('17/11/2025', 'Spar Ugie', 1, 210),
    ('18/11/2025', 'Spar Indwe', 1, 230),
    ('18/11/2025', 'Power Save Indwe', 1, 230),
    ('19/11/2025', 'Spar Ngqamakwe', 1, 124),
    ('24/11/2025', 'Spar savemor kei mouth', 1, 85),
    ('24/11/2025', 'Kei mouth Butchery', 1, 85),
    ('26/11/2025', 'Parkside Butchery', 1, 14),
    ('26/11/2025', 'Spar Buffalo flats', 1, 24),
    ('27/11/2025', 'Spargs Superspar-Queenstown', 1, 96),
    ('28/11/2025', 'Spar Dordrecht', 1, 150),
    ('28/11/2025', 'M and M Butchery and Braai', 1, 150),
]

print("="*80)
print("RESTORING SANDISIWE DLISANI'S KM AND HOURS DATA")
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
            inspector_id=sandisiwe.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = sandisiwe.id
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
