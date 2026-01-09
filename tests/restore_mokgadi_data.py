"""
Restore Mokgadi Selone's KM and hours data for October-November 2025
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

# Get Mokgadi's user
try:
    mokgadi = User.objects.get(username='Mokgadi')
    print(f"Found user: {mokgadi.username} ({mokgadi.first_name} {mokgadi.last_name})")
except User.DoesNotExist:
    # Try alternative search
    try:
        mokgadi = User.objects.get(first_name__icontains='Mokgadi')
        print(f"Found user: {mokgadi.username} ({mokgadi.first_name} {mokgadi.last_name})")
    except:
        print("ERROR: Could not find Mokgadi user")
        exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
# Only actual inspections with KM/hours (excluding E-Click approvals, leave, admin tasks)
inspection_data = [
    # October
    ('06/10/2025', 'Impala Meats', 1, 100),
    ('06/10/2025', 'Vleismark Marble Hall', 1, 100),
    ('07/10/2025', 'Nesta Foods Factory', 1, 100),
    ('07/10/2025', 'J&S Slaghuis', 1, 70),
    ('07/10/2025', 'Meatrite', 1, 120),
    ('14/10/2025', 'Roots Butchery Groblersdal', 1, 150),
    ('14/10/2025', 'Boxer Superstore Groblersdal', 1, 150),
    ('16/10/2025', 'Red Meat Butchery', 1, 70),
    ('16/10/2025', 'Jwayelani Food 1 Mokopane', 1, 100),
    ('20/10/2025', 'Superspar Platinum Park', 1, 100),
    ('20/10/2025', 'Roots Butchery Polokwane', 1, 100),
    ('22/10/2025', 'Prime Cutz The Halaal Butchery', 1, 100),
    ('22/10/2025', 'Westenburg Butchery', 1, 100),
    ('24/10/2025', 'Russelstone Foods', 1, 70),
    ('24/10/2025', 'Jwayelani Foods Polokwane', 1, 100),
    ('24/10/2025', 'Kwiksave Fresh & Frozen 2', 1, 100),
    ('27/10/2025', 'Roots Butchery Tibani', 1, 100),
    ('27/10/2025', 'Boxer Superstore Tibani', 1, 100),
    ('27/10/2025', 'Roots Butchery Steilloop', 1, 100),
    ('28/10/2025', 'Pick n Pay Lephalale Square', 1, 50),
    ('28/10/2025', 'Meat Boys Lephalele', 1, 100),
    ('28/10/2025', 'Boxer Superstore Lephalale', 1, 100),
    ('28/10/2025', 'Superspar Mogol', 1, 100),
    ('29/10/2025', 'Superspar Marapong', 1, 100),
    ('29/10/2025', 'Bosveld Biltong & Braai Vleismark', 1, 50),
    ('29/10/2025', 'Van Wyk Afribees Slaghuis', 1, 50),
    ('30/10/2025', 'Roots Butchery Thabazimbi', 1, 100),
    # November
    ('05/11/2025', 'Pick n Pay Local Polokwane', 1, 50),
    ('05/11/2025', 'Roots Butchery Mankweng', 1, 100),
    ('05/11/2025', 'Superspar Tzaneen', 1, 100),
    ('07/11/2025', 'Roots Butchery Tzaneen', 1, 100),
    ('07/11/2025', 'OBC Chicken & Meat Tzaneen', 1, 100),
    ('10/11/2025', 'Boxer Superstore Lebowakgomo', 1, 50),
    ('10/11/2025', 'Superspar Lebowakgomo', 1, 50),
    ('11/11/2025', 'Nesta Foods Factory', 1, 70),
    ('11/11/2025', 'Roots Butchery Mahwelereng', 1, 100),
    ('14/11/2025', 'Food Lover\'s Market - The Farmyard', 1, 100),
    ('18/11/2025', 'Roots Butchery Lebowakgomo', 1, 100),
    ('18/11/2025', 'Spar Modjadjiskloof', 1, 100),
    ('18/11/2025', 'Roots Butchery Modjadji', 1, 100),
    ('19/11/2025', 'Spar SaveMor Giyani A', 1, 100),
    ('19/11/2025', 'Boxer Superstore 1 Giyani', 1, 100),
    ('19/11/2025', 'Makhoma Butchery Taxi Rank', 1, 100),
    ('19/11/2025', 'Roots Butchery Express Giyani', 1, 100),
    ('20/11/2025', 'OBC Chicken Meat - Malamulele', 1, 100),
    ('20/11/2025', 'Roots Butchery Malamulele', 1, 100),
    ('20/11/2025', 'Boxer Superstore Malamulele', 1, 100),
    ('21/11/2025', 'OBC Chicken & Meat Giyani', 1, 100),
    ('21/11/2025', 'Makhoma Butchery Giyani', 1, 100),
    ('25/11/2025', 'Bloubul Butchery', 1, 70),
    ('27/11/2025', 'Meat Boys Mokopane', 1, 70),
]

print("="*80)
print("RESTORING MOKGADI SELONE'S KM AND HOURS DATA")
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
            inspector_id=mokgadi.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = mokgadi.id
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
