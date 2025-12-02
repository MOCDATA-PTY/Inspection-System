"""
Restore Kutlwano Kuntwane's KM and hours data for October-November 2025
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

# Get Kutlwano's user
try:
    kutlwano = User.objects.get(username='Kutlwano')
    print(f"Found user: {kutlwano.username} ({kutlwano.first_name} {kutlwano.last_name})")
except User.DoesNotExist:
    # Try alternative search
    try:
        kutlwano = User.objects.get(first_name__icontains='Kutlwano')
        print(f"Found user: {kutlwano.username} ({kutlwano.first_name} {kutlwano.last_name})")
    except:
        print("ERROR: Could not find Kutlwano user")
        exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
# Only actual inspections with KM/hours (excluding admin tasks, meetings, sick leave)
inspection_data = [
    # October
    ('01/10/2025', 'Windmeul eggs', 4, 63),
    ('01/10/2025', 'Rosendal poultry farm', 1, 63),
    ('02/10/2025', 'Roots butcher belhar', 1, 40),
    ('02/10/2025', 'Trust meat', 1, 40),
    ('02/10/2025', 'Fairfield meat centre', 1, 40),
    ('02/10/2025', 'Meatrite', 1, 40),
    ('03/10/2025', 'Superspar paarl east', 1, 81),
    ('03/10/2025', 'DC meat paarl', 1, 81),
    ('03/10/2025', 'Swartland vleis meat', 1, 81),
    ('06/10/2025', 'Pick n pay wynberg', 1, 30),
    ('06/10/2025', 'Spar wynberg', 1, 30),
    ('06/10/2025', 'Food lover\'s market access park', 1, 30),
    ('07/10/2025', 'Superspar vangate mall', 1, 28),
    ('07/10/2025', 'Kekkel en kraai klipfontein', 1, 28),
    ('10/10/2025', 'Pick n Pay Malmesbury', 1, 89),
    ('10/10/2025', 'Food lover\'s market malmesbury', 1, 89),
    ('13/10/2025', 'Spar parow valley', 1, 26),
    ('13/10/2025', 'Spar Glenwood', 1, 26),
    ('13/10/2025', 'Kekkel en kraai Epping', 1, 26),
    ('14/10/2025', 'Sangiro chicken WC', 2, 71),
    ('14/10/2025', 'Spar cedar', 1, 71),
    ('15/10/2025', 'Superspar Robertson', 1, 50),
    ('15/10/2025', 'Brito\'s meat Robertson', 1, 50),
    ('15/10/2025', 'Kekkel en kraai Robertson', 1, 50),
    ('16/10/2025', 'Meat lovers halaal', 1, 63),
    ('16/10/2025', 'Blockman worcester', 1, 63),
    ('16/10/2025', 'Food lovers market mountain mill', 1, 63),
    ('20/10/2025', 'Kwikspar strand', 1, 27),
    ('20/10/2025', 'Strand halaal butchery', 1, 27),
    ('21/10/2025', 'Spar parow valley', 1, 19),
    ('21/10/2025', 'The butchers market watergate', 1, 19),
    ('21/10/2025', 'Kekkel en kraai Parow', 1, 19),
    ('22/10/2025', 'The bank spar', 1, 68),
    ('22/10/2025', 'Boxer paarl', 1, 68),
    ('24/10/2025', 'Boxer superstore somerset crossing', 1, 30),
    ('24/10/2025', 'Roots butchery somerset crossing', 1, 30),
    ('27/10/2025', 'Country fair abattoir', 6, 80),
    ('28/10/2025', 'Country fair abattoir', 7, 97),
    ('29/10/2025', 'Sunshine egg farm', 3, 134),
    ('29/10/2025', 'The butchers market watergate', 1, 20),
    ('30/10/2025', 'Blockman production plant', 1, 61),
    ('31/10/2025', 'Blockman Kuilsriver', 1, 56),
    ('31/10/2025', 'Winelands pork', 1, 56),
    # November
    ('03/11/2025', 'Food lovers market Kuilsriver', 1, 13),
    ('03/11/2025', 'Brito\'s meat center Kuilsriver', 1, 13),
    ('03/11/2025', 'Kekkel en kraai kuilsriver', 1, 13),
    ('05/11/2025', 'Superspar Haasendal', 1, 22),
    ('05/11/2025', 'Spar protea hoogte', 1, 22),
    ('06/11/2025', 'Pick n pay Brackenfell', 1, 33),
    ('06/11/2025', 'Excellent Meat Market', 1, 33),
    ('10/11/2025', 'Prime meat market', 1, 32),
    ('10/11/2025', 'Kekkel en Kraai Elsies River', 1, 32),
    ('11/11/2025', 'Table view butchery', 1, 32),
    ('11/11/2025', 'Spar sunningdale', 1, 32),
    ('12/11/2025', 'Golden yolk eggs', 5, 130),
    ('14/11/2025', 'Spek production', 3, 43),
    ('14/11/2025', 'Spar savemor Goodwood', 1, 43),
    ('17/11/2025', 'Spar cape quarter', 1, 53),
    ('17/11/2025', 'Spar groot schuur', 1, 53),
    ('18/11/2025', 'Tollie\'s vleismark', 1, 21),
    ('18/11/2025', 'Kwikspar Durbanville', 1, 21),
    ('19/11/2025', 'Stark everyday', 1, 55),
]

print("="*80)
print("RESTORING KUTLWANO KUNTWANE'S KM AND HOURS DATA")
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
            inspector_id=kutlwano.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = kutlwano.id
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
