"""
Restore Jofred Steyn's KM and hours data for October-November 2025
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

# Get Jofred's user
try:
    jofred = User.objects.get(username='Jofred')
    print(f"Found user: {jofred.username} ({jofred.first_name} {jofred.last_name})")
except User.DoesNotExist:
    # Try alternative search
    try:
        jofred = User.objects.get(first_name__icontains='Jofred')
        print(f"Found user: {jofred.username} ({jofred.first_name} {jofred.last_name})")
    except:
        print("ERROR: Could not find Jofred user")
        exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
# Only actual inspections with KM/hours (excluding admin tasks, meetings, failed inspections)
inspection_data = [
    # October
    ('01/10/2025', 'Spar Aspen', 1, 50),
    ('01/10/2025', 'Springbok Discount Meat Centre', 1, 50),
    ('02/10/2025', 'Taylor Made Foods Cleary Park', 1, 45),
    ('03/10/2025', 'Kwikspar KwaMagXaki', 1.5, 50),
    ('08/10/2025', 'Superspar Zonke', 1, 50),
    ('08/10/2025', 'Superspar Our Walmer', 1.5, 50),
    ('14/10/2025', 'Die Hoenderhok Slaghuis', 1, 55),
    ('14/10/2025', 'Spar The Stadium', 1, 50),
    ('15/10/2025', 'The Stadium Butchery', 1, 50),
    ('15/10/2025', 'Lima Farms Butchery', 1, 50),
    ('17/10/2025', 'KarooGoud Slaghuis', 1, 25),
    ('17/10/2025', 'Superspar Summerbreezz', 1.5, 60),
    ('20/10/2025', 'Boxer Superstore Commercial Road', 1.5, 50),
    ('21/10/2025', 'Mabovula Butchery Walmer', 2, 70),
    ('21/10/2025', 'Westvill Deli', 1, 25),
    ('22/10/2025', 'Lekker Meat Shop', 1, 50),
    ('22/10/2025', 'Stadium Meat Market', 1, 25),
    ('23/10/2025', 'Superspar Jeffrey\'s Bay', 1, 70),
    ('27/10/2025', 'Spar Linton Grange', 1, 70),
    ('27/10/2025', 'Kwikspar Miramar', 1, 35),
    ('28/10/2025', 'Heydenrychs Quality Meat', 2, 60),
    ('29/10/2025', 'Spar Kwanobuhle', 1, 40),
    ('29/10/2025', 'Kwikspar Rink Street', 1, 40),
    ('29/10/2025', 'Kwikspar Beetlestone', 1, 35),
    ('30/10/2025', 'Spar Oak Cottage', 1, 100),
    # November
    ('03/11/2025', 'Superspar Bluewater Bay', 1.5, 65),
    ('05/11/2025', 'Spar Cradock', 1, 90),
    ('06/11/2025', 'Avon Butchery Fort Beaufort', 1.5, 70),
    ('06/11/2025', 'Butcher Block Fort Beaufort', 1, 60),
    ('07/11/2025', 'Matador Slaghuis', 1, 65),
    ('10/11/2025', 'Sovereign Further Processing Plant', 1, 30),
    ('11/11/2025', 'Econo Meats', 1, 50),
    ('12/11/2025', 'Pick n Pay Bluewater Bay', 1.5, 60),
    ('13/11/2025', 'Spar Dagbreek', 1, 65),
    ('14/11/2025', 'Ziqenye Food Services', 3.5, 60),
    ('14/11/2025', 'Spar Gelvandale', 1, 30),
    ('18/11/2025', 'Kwikspar Colchester', 1, 85),
    ('19/11/2025', 'Kouga Beef', 1, 90),
    ('19/11/2025', 'Bokmakierie Holdings Slaghuis', 1.5, 100),
    ('20/11/2025', 'Royal Stores Stormsriver', 1, 85),
    ('21/11/2025', 'Sebastians Butchery', 1, 75),
    ('21/11/2025', 'Blikkiesbraai Butchery and Deli', 1, 50),
    ('21/11/2025', 'Beesland Slaghuis & Deli', 1, 45),
    ('25/11/2025', 'Drunken Butcher', 1, 85),
    ('25/11/2025', 'Wolwekloof Karoo', 1, 80),
]

print("="*80)
print("RESTORING JOFRED STEYN'S KM AND HOURS DATA")
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
            inspector_id=jofred.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = jofred.id
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
