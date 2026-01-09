"""
Restore Kabelo Percy's KM and hours data for October-November 2025
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

# Get Kabelo's user (username is Percy)
try:
    kabelo = User.objects.get(username='Percy')
    print(f"Found user: {kabelo.username} ({kabelo.first_name} {kabelo.last_name})")
except User.DoesNotExist:
    print("ERROR: Could not find Percy user")
    exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
# Only actual inspections with KM/hours (excluding admin tasks, annual leave, etc.)
inspection_data = [
    # October
    ('01/10/2025', 'OBC Chicken &Meat-Cosmo City', 1, 40),
    ('01/10/2025', 'Roots Butchery-Cosmo City', 1, 40),
    ('01/10/2025', 'Boxer Superstores-Cosmo City', 1, 40),
    ('02/10/2025', 'Pick n Pay-Northcliff Square', 1, 50),
    ('03/10/2025', 'T & F Meat Market', 1, 40),
    ('03/10/2025', 'Spar-Randjespark', 1, 40),
    ('16/10/2025', 'Food Lovers Market-Waterfall Ridge', 1, 90),
    ('16/10/2025', 'Superspar-Vorna Valley', 1, 90),
    ('17/10/2025', 'Roots Butchery-Festival Mall', 1, 40),
    ('17/10/2025', 'Ma Kong Butchery', 1, 40),
    ('20/10/2025', 'The Meat Boss', 1, 40),
    ('20/10/2025', 'Plus Butchery Cosmo City', 1, 40),
    ('20/10/2025', 'Roots Choice Butchery Cosmo City', 1, 40),
    ('21/10/2025', 'Spar Heidelberg', 1, 80),
    ('21/10/2025', 'Eskort Heidelberg', 1, 80),
    ('22/10/2025', 'Altamash Halaal Butchery', 1, 40),
    ('22/10/2025', 'Spar Noordwyk', 1, 40),
    ('24/10/2025', 'B Nagiahs Butchery', 1, 40),
    ('24/10/2025', 'DB\'S Butchery Kyalami', 1, 40),
    ('24/10/2025', 'Food Lovers Market Fourways', 1, 40),
    ('27/10/2025', 'Kruinsig Slaghuis', 1, 40),
    ('27/10/2025', 'Superspar Ruimsig', 1, 60),
    ('28/10/2025', 'Metro Cash Butchery', 1, 60),
    ('29/10/2025', 'Roots Butchery Diepsloot', 1, 60),
    ('30/10/2025', 'Van Wyngraahrt', 1, 40),
    ('30/10/2025', 'Northcliff Halaal Butchery', 1, 40),
    ('31/10/2025', 'Superspar Carlswald', 1, 40),
    # November
    ('03/11/2025', 'Roots Butchery - Vosloorus', 1, 60),
    ('04/11/2025', 'SUPERSPAR - Crowthorne', 1, 60),
    ('05/11/2025', 'Food Lovers Market Ferndale', 1, 40),
    ('05/11/2025', 'Pick n Pay Blue Hills', 1, 50),
    ('07/11/2025', 'Pick n Pay Qualisave Diepsloot', 1, 50),
    ('07/11/2025', 'Boma Meat Deli Midstream', 1, 50),
    ('10/11/2025', 'Superspar Polofields', 1, 30),
    ('11/11/2025', 'Chester Butcheries Alexander', 1, 40),
    ('11/11/2025', 'Waltloo Meat and chicken Alexandra', 1, 40),
    ('11/11/2025', 'Kwikspar Stop n Go', 1, 30),
    ('13/11/2025', 'Frontline Hyper Endenvale', 1, 40),
    ('14/11/2025', 'Roots Butchery and Grill Randburg', 1, 40),
    ('14/11/2025', 'Superspar Horbart', 1, 40),
    ('17/11/2025', 'Roots Butchery Kaalfontein', 1, 30),
    ('17/11/2025', 'Superspar Ebony Park', 1, 40),
    ('18/11/2025', 'Kwikspar Norkem Park', 1, 40),
    ('20/11/2025', 'Wholesale Meat Services', 1, 40),
    ('20/11/2025', 'OBC Chicken and Meat Mall@55', 1, 40),
    ('24/11/2025', 'Meat Express Katlehong', 1, 60),
    ('24/11/2025', 'Roots Butchery Katlehong', 1, 60),
    ('25/11/2025', 'Spar Pineslope', 1, 40),
    ('26/11/2025', 'Food Lovers Market MorningGlen', 1, 40),
    ('27/11/2025', 'Plus Butchery Turffontein', 1, 40),
    ('27/11/2025', 'Azaan Butchery', 1, 30),
    ('28/11/2025', 'Grande Butcher Shoppe Randburg', 1, 40),
    ('28/11/2025', 'Spar Fourways Garden', 1, 40),
]

print("="*80)
print("RESTORING KABELO PERCY'S KM AND HOURS DATA")
print("="*80)

updated_count = 0
not_found_count = 0
multiple_found_count = 0

for date_str, client_name, hours, km in inspection_data:
    # Parse date
    date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()

    # Find inspection(s) for this date and client
    # Use the first part of client name before any special characters
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
            inspector_id=kabelo.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = kabelo.id
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
