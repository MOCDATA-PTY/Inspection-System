"""
Restore Gladys Manganye's KM and hours data for October-November 2025
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

# Get Gladys's user
try:
    gladys = User.objects.get(username='Gladys')
    print(f"Found user: {gladys.username} ({gladys.first_name} {gladys.last_name})")
except User.DoesNotExist:
    # Try alternative search
    try:
        gladys = User.objects.get(first_name__icontains='Gladys')
        print(f"Found user: {gladys.username} ({gladys.first_name} {gladys.last_name})")
    except:
        print("ERROR: Could not find Gladys user")
        exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
# Only actual inspections with KM/hours (excluding meetings, reschedules, admin tasks)
inspection_data = [
    # October
    ('02/10/2025', 'Spar-Ogies', 1, 100),
    ('02/10/2025', 'Boxer Superstore-Ogies', 1, 100),
    ('03/10/2025', 'Roots Butchery-Leandra', 1, 100),
    ('07/10/2025', 'Roots Butchery-Dayizenza', 1, 50),
    ('07/10/2025', 'Boxer Superstore-Dayizenza', 1, 50),
    ('08/10/2025', 'Roots Butchery-Barberton', 1, 50),
    ('09/10/2025', 'Boxer Superstore-Kabokweni', 1, 33),
    ('10/10/2025', 'Tjop-Chop Butchery', 1, 50),
    ('13/10/2025', 'Boxer Superstore-Bushbuckridge', 1, 100),
    ('13/10/2025', 'OBC-Bushbuckridge', 1, 100),
    ('15/10/2025', 'Superspar-Bushbuckridge', 1, 100),
    ('15/10/2025', 'Superspar-Dwarsloop', 1, 100),
    ('15/10/2025', 'Boxer Superstore-Dwarsloop', 1, 100),
    ('16/10/2025', 'OBC-Hazyview', 1, 70),
    ('17/10/2025', 'Superspar Westend', 1, 8),
    ('17/10/2025', 'Spar Courtside', 1, 8),
    ('20/10/2025', 'Boxer Superstore-Matsulu', 1, 50),
    ('20/10/2025', 'Spar-Matsulu', 1, 50),
    ('20/10/2025', 'National Park Butchery', 1, 50),
    ('21/10/2025', 'Boxer Superstore-Acornhoek', 1, 100),
    ('21/10/2025', 'Roots Butchery-Acornhoek', 1, 100),
    ('21/10/2025', 'Superspar-Acornhoek', 1, 100),
    ('22/10/2025', 'A1 Food Store', 1, 80),
    ('23/10/2025', 'Parkton meats', 1, 16),
    ('24/10/2025', 'Superspar-Komatipoort', 1, 100),
    ('24/10/2025', 'OBC-Komatipoort', 1, 100),
    ('27/10/2025', 'OBC-Tonga', 1, 100),
    ('27/10/2025', 'Roots Butchery-Tonga', 1, 100),
    ('27/10/2025', 'Roots Butchery-Malelane', 1, 100),
    ('28/10/2025', 'Boxer Superstore Nkomazi Plaza', 1, 100),
    ('28/10/2025', 'Roots Butchery Nkomazi Plaza', 1, 100),
    ('28/10/2025', 'Superspar Naas', 1, 100),
    ('28/10/2025', 'Boxer Superstore Kamaqhekeza', 1, 100),
    ('29/10/2025', 'Roots Butchery-Bushbuckridge', 2, 100),
    ('30/10/2025', 'Roots Butchery Acornhoek Plaza', 1, 100),
    ('30/10/2025', 'OBC-Acornhoek', 1, 100),
    # November
    ('03/11/2025', 'Crown Butchery', 1, 50),
    ('04/11/2025', 'Roots Butchery-Thulamahashe', 1, 100),
    ('05/11/2025', 'Spar Savemor Platsak', 1, 26),
    ('10/11/2025', 'Superspar-Piet Retief', 1, 100),
    ('10/11/2025', 'Boxer Superstore-Piet Retief', 1, 100),
    ('10/11/2025', 'Roots Butchery-Piet Retief', 1, 100),
    ('11/11/2025', 'Superspar-Volkrust', 1, 100),
    ('11/11/2025', 'Waltloo Meat and Chicken', 1, 100),
    ('12/11/2025', 'Checkrite - Piet Retief', 1, 100),
    ('12/11/2025', 'Pick \'n Pay Family - Piet Retief', 1, 100),
    ('13/11/2025', 'Four Sisters Butchery', 1, 100),
    ('13/11/2025', 'Hough\'s Butchery', 1, 100),
    ('14/11/2025', 'Roots Butchery Ermelo CBD', 1, 100),
    ('14/11/2025', 'Roots Butchery Ermelo Mall', 1, 100),
    ('14/11/2025', 'Superspar-Ermelo', 1, 100),
    ('18/11/2025', 'Boxer Superstore-Standerton', 1, 100),
    ('18/11/2025', 'Superspar-Standerton', 1, 100),
    ('19/11/2025', 'Checkrite-Secunda', 1, 100),
    ('19/11/2025', '5 Star Superspar', 1, 100),
    ('20/11/2025', 'Superspar Kriel', 1, 100),
    ('20/11/2025', 'Mooilaan Kwikspar', 1, 100),
    ('24/11/2025', 'Roots Butchery Promenade Centre', 1, 8),
    ('25/11/2025', 'Spar De Hallen', 1, 10),
    ('27/11/2025', 'A1 Food Centre', 1, 100),
    ('27/11/2025', 'Makhoma Butchery Acornhoek', 1, 100),
]

print("="*80)
print("RESTORING GLADYS MANGANYE'S KM AND HOURS DATA")
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
            inspector_id=gladys.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = gladys.id
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
