"""
Restore Cinga Ngongo's KM and hours data for October-November 2025
Based on spreadsheet data provided
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User

# Get Cinga's user
try:
    cinga = User.objects.get(username='Cinga')
except User.DoesNotExist:
    print("ERROR: User 'Cinga' not found")
    exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
inspection_data = [
    ('02/10/2025', 'Spath - Silverton Pretoria', 1, 28),
    ('02/10/2025', 'Mamashes Butchery', 1, 50),
    ('03/10/2025', 'Roots Butchery - Kempton Park CBD', 1, 70),
    ('06/10/2025', 'SA Supermarket', 1, 50),
    ('06/10/2025', 'Pick \'n Pay - The Grove', 1, 50),
    ('07/10/2025', 'Jumbo Supermarket SA', 1, 50),
    ('07/10/2025', 'Superspar - Wonderboom Junction', 1, 50),
    ('08/10/2025', 'Spar- Les Marais', 1, 50),
    ('09/10/2025', 'High road butchery', 1, 70),
    ('09/10/2025', 'Superspar- The falls', 1, 70),
    ('13/10/2025', 'Superspar - Queenswood', 1.5, 40),
    ('13/10/2025', 'Spar- Rietfontein', 1, 40),
    ('14/10/2025', 'C & E vleisverspeiders', 1, 40),
    ('14/10/2025', 'Superspar Menlo', 2, 40),
    ('20/10/2025', 'Hokaai meat market- Gift acres', 1, 30),
    ('20/10/2025', 'Kwikspar Wapadrand', 1, 30),
    ('21/10/2025', 'Superspar- Elardus', 1, 60),
    ('24/10/2025', 'Klipeiland slaghuis', 1, 70),
    ('24/10/2025', 'waltloo meat & chicken- Bronkhorstspruit', 2, 70),
    ('27/10/2025', 'Kwikspar Gaby\'s', 1, 40),
    ('27/10/2025', 'Miems & Seun', 1, 40),
    ('28/10/2025', 'Hawkers one stop', 1, 70),
    ('28/10/2025', 'Waltloo meat & chicken - Jubilee mall', 1, 70),
    ('29/10/2025', 'Superspar- westwood', 1, 70),
    ('29/10/2025', 'Venters wholesale meat', 1, 70),
    ('31/10/2025', 'Pick \'n Pay - Plantland', 1, 60),
    ('31/10/2025', 'Pick \'n Pay- Plantland', 1, 60),
    # November
    ('05/11/2025', 'Roots Butchery - Sunnyside', 1, 30),
    ('05/11/2025', 'Sunnyside meat & chicken.', 1, 30),
    ('05/11/2025', 'SPAR - Barclay\'s', 1, 40),
    ('06/11/2025', 'Southpansbergweg Slaghuis', 1, 30),
    ('06/11/2025', 'Superspar - Dely Road', 1, 30),
    ('06/11/2025', 'Maders Slaghuis', 1, 30),
    ('07/11/2025', 'Kwikspar - Waterkloof', 1, 40),
    ('07/11/2025', 'Kings Meat Deli Castle Walk', 1, 40),
    ('18/11/2025', 'Pick \'n Pay - Family Bronkhorstspruit', 1, 70),
    ('18/11/2025', 'Prazeres Foodzone- BHS', 1, 70),
    ('21/11/2025', 'Lynnpark foodhall', 1, 35),
    ('24/11/2025', 'New market butchery', 1, 40),
    ('24/11/2025', 'Vleishuys Riveria', 1, 40),
    ('27/11/2025', 'Frio Foods', 1, 40),
    ('27/11/2025', 'Spaths cold meat', 1, 40),
    ('28/11/2025', 'Boxer superstore- Denneboom', 1, 40),
    ('28/11/2025', 'Food lovers market- lynnwood lane', 1.5, 40),
]

print("="*80)
print("RESTORING CINGA NGONGO'S KM AND HOURS DATA")
print("="*80)

updated_count = 0
not_found_count = 0
multiple_found_count = 0

for date_str, client_name, hours, km in inspection_data:
    # Parse date
    date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()

    # Find inspection(s) for this date and client
    inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection=date_obj,
        client_name__icontains=client_name.split('-')[0].strip()
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
            inspector_id=cinga.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = cinga.id
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

print(f"\nOct-Nov inspections with KM data: {oct_nov_with_km}")
print(f"Oct-Nov inspections with hours data: {oct_nov_with_hours}")
print("\nDone!")
