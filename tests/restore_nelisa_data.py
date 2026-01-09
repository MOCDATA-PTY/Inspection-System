"""
Restore Nelisa Ntoyaphi's KM and hours data for October-November 2025
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

# Get Nelisa's user
try:
    nelisa = User.objects.get(username='Nelisa')
    print(f"Found user: {nelisa.username} ({nelisa.first_name} {nelisa.last_name})")
except User.DoesNotExist:
    # Try alternative search
    try:
        nelisa = User.objects.get(first_name__icontains='Nelisa')
        print(f"Found user: {nelisa.username} ({nelisa.first_name} {nelisa.last_name})")
    except:
        print("ERROR: Could not find Nelisa user")
        exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
# Only actual inspections with KM/hours (excluding admin, meetings, sample submissions)
inspection_data = [
    # October
    ('02/10/2025', 'kekkel en kraai', 1, 96),
    ('02/10/2025', 'super spar riversdal', 1, 96),
    ('06/10/2025', 'frozen foods', 1, 27),
    ('08/10/2025', 'boesmanland biltong', 1, 44),
    ('08/10/2025', 'bobby family butchery', 1, 44),
    ('09/10/2025', 'kwikspar beacon isle', 1, 66),
    ('14/10/2025', 'Theronsville butchery', 1, 82),
    ('15/10/2025', 'phumba butchery', 1, 45),
    ('15/10/2025', 'butchers butchery', 1, 45),
    ('16/10/2025', 'droevlakte butchery', 1, 93),
    ('17/10/2025', 'spar stillbay', 1, 117),
    ('17/10/2025', 'kekkel en kraai', 1, 117),
    ('17/10/2025', 'droevlakte butchery', 1, 117),
    ('20/10/2025', 'mubarak supermarket', 1, 117),
    ('20/10/2025', 'halal supermarket', 1, 117),
    ('20/10/2025', 'super joe supermarket', 1, 117),
    ('21/10/2025', 'small pot number two', 1, 10),
    ('21/10/2025', 'peoples cash store', 1, 10),
    ('22/10/2025', 'savy cuts', 1, 10),
    ('23/10/2025', 'de boer', 1, 42),
    ('23/10/2025', 'kekkel en kraai', 1, 42),
    ('24/10/2025', 'kekkel en kraai', 1, 70),
    ('27/10/2025', 'savemor', 1, 183),
    ('27/10/2025', 'karoo bossie apteek', 1, 183),
    ('28/10/2025', 'super spar', 1, 83),
    ('29/10/2025', 'savy cuts', 1, 16),
    ('30/10/2025', 'tonys butchery', 1, 86),
    ('30/10/2025', 'die vleiskombuis', 1, 126),
    ('30/10/2025', 'super spar swellendam', 1, 126),
    ('31/10/2025', 'spar heidelberg', 1, 126),
    ('31/10/2025', 'kruisrivier butchery', 1, 100),
    ('31/10/2025', 'biltong fabriek', 1, 86),
    # November
    ('03/11/2025', 'Karoo Hartland Supermarket', 1, 129),
    ('04/11/2025', 'calitzdorp maxi market', 1, 78),
    ('05/11/2025', 'venison man', 1, 51),
    ('06/11/2025', 'prime meat butchery', 1, 39),
    ('07/11/2025', 'boxer thembalethu', 1, 67),
    ('07/11/2025', 'Greef\'s Butchery and Meat Market - Knysna', 1, 67),
    ('11/11/2025', 'sentra slaghuis', 1, 90),
    ('11/11/2025', 'royal butchery', 1, 90),
    ('12/11/2025', 'hyper meat and veg', 1, 61),
    ('12/11/2025', 'Kalahari vleis and deli', 1, 61),
    ('13/11/2025', 'nostalgie winkel', 1, 47),
    ('13/11/2025', 'SPAR - De Dekke', 1, 47),
    ('17/11/2025', 'spar ladismith', 1, 161),
    ('18/11/2025', 'royal butchery', 1, 92),
    ('19/11/2025', 'kekkel en kraai', 1, 178),
    ('20/11/2025', 'Bounty Game and Meat', 1, 73),
    ('21/11/2025', 'biltongman', 1, 150),
    ('21/11/2025', 'badenhorst butchery', 1, 50),
    ('24/11/2025', 'food lovers market', 1, 79),
    ('24/11/2025', 'kekkel en kraai', 1, 79),
    ('25/11/2025', 'wittedrift butchery', 1, 112),
    ('25/11/2025', 'boxer kwa nokuthula', 1, 112),
    ('26/11/2025', 'food lovers market', 1, 72),
    ('26/11/2025', 'farmers butchery', 1, 72),
    ('27/11/2025', 'food lovers market', 1, 15),
    ('27/11/2025', 'kaya butchery', 1, 15),
    ('28/11/2025', 'kekkel en kraai', 1, 41),
    ('28/11/2025', 'savemor', 1, 41),
    ('28/11/2025', 'grootbrak butchery', 1, 41),
]

print("="*80)
print("RESTORING NELISA NTOYAPHI'S KM AND HOURS DATA")
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
            inspector_id=nelisa.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = nelisa.id
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
