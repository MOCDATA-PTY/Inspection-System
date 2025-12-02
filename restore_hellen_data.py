"""
Restore Hellen Modiba's KM and hours data for October-November 2025
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

# Get Hellen's user
try:
    hellen = User.objects.get(username='Hellen')
    print(f"Found user: {hellen.username} ({hellen.first_name} {hellen.last_name})")
except User.DoesNotExist:
    # Try alternative search
    try:
        hellen = User.objects.get(first_name__icontains='Hellen')
        print(f"Found user: {hellen.username} ({hellen.first_name} {hellen.last_name})")
    except:
        print("ERROR: Could not find Hellen user")
        exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
# Only actual inspections with KM/hours (excluding appointments, meetings, admin tasks, sick leave)
inspection_data = [
    # October
    ('01/10/2025', 'Abdul Family Butchery-1-Newcastle', 1, 114),
    ('01/10/2025', 'Roots Butchery-1-Newcastle', 1, 114),
    ('01/10/2025', 'Boxer Superstore-1-Newcastle', 1, 114),
    ('02/10/2025', 'Checkrite-Newcastle', 1, 114),
    ('02/10/2025', 'Bosco Meats Butchery-Downtown', 1, 114),
    ('03/10/2025', 'Roots Butchery-1-Vryheid', 1, 5),
    ('03/10/2025', 'Spar-Utrecht-Uncle Deli', 1, 45),
    ('07/10/2025', 'Savemor-Mduku', 1, 90),
    ('07/10/2025', 'Powerspar-Empangeni', 1, 20),
    ('08/10/2025', 'Spar-Gingindlovu', 1, 75),
    ('10/10/2025', 'Boxer Superstore-Empangeni Market', 1, 20),
    ('13/10/2025', 'Ikhwezi Cash & Carry-Mandini', 1, 100),
    ('15/10/2025', 'Savemor-Nyakaza', 1, 120),
    ('16/10/2025', 'Boxer Superstore-Sundumbili', 1, 100),
    ('17/10/2025', 'Roots Butchery-Pongola', 1, 100),
    ('17/10/2025', 'Arizona-Pongola', 1, 100),
    ('20/10/2025', 'Aheers Supermarket-Greytown', 1, 100),
    ('20/10/2025', 'Aheers Cash and Carry-Greytown', 1, 100),
    ('21/10/2025', 'Tugela Meat Market-Greytown', 1, 5),
    ('21/10/2025', 'Roots Butchery-Greytown', 1, 5),
    ('22/10/2025', 'Chester Butchery-Greytown', 1, 5),
    ('23/10/2025', 'Min Cash Foodtown-Greytown', 1, 5),
    ('24/10/2025', 'Superspar-Kranskop', 1, 100),
    ('24/10/2025', 'Siyabonga Powertrade-Kranskop', 1, 100),
    ('28/10/2025', 'Pick N Pay-Pioneer Park', 1, 100),
    ('28/10/2025', 'Boxer Superstore-Newcastle-2', 1, 100),
    ('29/10/2025', 'Superspar-Taxi City', 1, 5),
    ('29/10/2025', 'Bosco Meats-Foodtown', 1, 5),
    ('30/10/2025', 'The Meat Hook-Newcastle', 1, 5),
    ('31/10/2025', 'Chester Butchery-Newcastle', 1, 100),
    ('31/10/2025', 'Superspar-Henry\'s-Newcastle', 1, 100),
    # November
    ('04/11/2025', 'Spar-Pick & Save-St Lucia', 1, 70),
    ('05/11/2025', 'Banana box Wholesaler and Butchery-St Lucia', 1, 70),
    ('06/11/2025', 'Pop In Mtuba-Mtubatuba', 1, 50),
    ('06/11/2025', 'Boxer Superstore-1-Taxicity', 1, 50),
    ('07/11/2025', 'Boxer Superstore-2-North', 1, 50),
    ('10/11/2025', 'Superspar-Nquthu', 1, 125),
    ('10/11/2025', 'Boxer Superstore-Nquthu', 1, 125),
    ('11/11/2025', 'Superspar-Madadeni- Eyethu Mall', 1, 125),
    ('12/11/2025', 'Superspar-Charlie\'s-Dundee', 1, 75),
    ('12/11/2025', 'Pick N Pay-Dundee(Family)', 1, 75),
    ('13/11/2025', 'Cassims Butchery-Dundee', 1, 75),
    ('14/11/2025', 'Roots Xpress Butchery-Vryheid', 1, 5),
    ('14/11/2025', 'Enyameni Butchery', 1, 5),
    ('18/11/2025', 'Roots Butchery-eDumbe', 1, 100),
]

print("="*80)
print("RESTORING HELLEN MODIBA'S KM AND HOURS DATA")
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
            inspector_id=hellen.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = hellen.id
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
print(f"\nTotal Oct-Nov inspections with hours data: {oct_nov_with_hours}")
print("\nDone!")
