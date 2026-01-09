"""
Restore Lwandile Maqina's KM and hours data for October-November 2025
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

# Get Lwandile's user
try:
    lwandile = User.objects.get(username='Lwandile')
    print(f"Found user: {lwandile.username} ({lwandile.first_name} {lwandile.last_name})")
except User.DoesNotExist:
    # Try alternative search
    try:
        lwandile = User.objects.get(first_name__icontains='Lwandile')
        print(f"Found user: {lwandile.username} ({lwandile.first_name} {lwandile.last_name})")
    except:
        print("ERROR: Could not find Lwandile user")
        exit(1)

# Data from spreadsheet - (date, client, hours, km)
# Format: DD/MM/YYYY
# Only actual inspections with KM/hours (excluding admin tasks, meetings, failed inspections)
inspection_data = [
    # October
    ('01/10/2025', 'Jwayelani 1', 1, 38),
    ('01/10/2025', 'Superspar Mega', 1.5, 38),
    ('02/10/2025', 'Bluff Meat Supply', 1, 68),
    ('03/10/2025', 'OBC Meat & Chicken', 1, 60),
    ('03/10/2025', 'Superspar Bridge city mall', 1, 60),
    ('06/10/2025', 'Food Lovers Market', 1, 77),
    ('06/10/2025', 'Kwiksapr Mount Edgecomb', 1, 77),
    ('07/10/2025', 'Bluff Meat Supply-Springfield', 1, 60),
    ('07/10/2025', 'Food Lovers Market-Springfield', 1.5, 60),
    ('08/10/2025', 'Jwayelani 2', 1, 10),
    ('10/10/2025', 'Jwayelani Bridge City Mall', 1, 67),
    ('10/10/2025', 'Dirks Meat Market', 1, 67),
    ('13/10/2025', 'Chester Butchery Queen Street', 1, 70),
    ('13/10/2025', 'Superspar Avenmore', 1, 70),
    ('16/10/2025', 'Pick n Pay Florida Road', 1.5, 73),
    ('16/10/2025', 'Superspar Mega Workshop', 1, 73),
    ('17/10/2025', 'Boxersuperstore Bridge City Mall', 1, 66),
    ('17/10/2025', 'Chester Butchery Mngeni road', 1, 66),
    ('20/10/2025', 'Kwikspar The Ridge', 1, 69),
    ('20/10/2025', 'Pick n Pay Umhlanga', 1.5, 69),
    ('24/10/2025', 'Shoprite Bridge City Mall', 1.5, 62),
    ('24/10/2025', 'Superspar Westville', 1, 62),
    ('27/10/2025', 'Premier Meat Products', 1, 69),
    ('27/10/2025', 'Point Meats', 1, 69),
    ('28/10/2025', 'Bluff Meat Supply Hillcrest', 1, 65),
    ('29/10/2025', 'Jwayelani Mid Town', 1, 51),
    ('29/10/2025', 'Waltloo Meat & Chicken Retief', 1, 51),
    ('30/10/2025', 'Chester Butchery Lancers', 1, 75),
    ('30/10/2025', 'Oxford Fresh Market', 1.5, 75),
    ('31/10/2025', 'Boxer Superstore1 Nyala Center', 1, 80),
    # November
    ('04/11/2025', 'The Meat Familia', 1, 41),
    ('04/11/2025', 'Bluff Meat Supply-Malvern', 1, 41),
    ('04/11/2025', 'Jwayelani Lancers', 1, 41),
    ('05/11/2025', 'Pollyshorts Superspar', 1, 78),
    ('06/11/2025', 'Kwikspar-Hillcrest', 1, 73),
    ('06/11/2025', 'Pick n Pay Christian Village', 1, 73),
    ('07/11/2025', 'Bluff Meat Supply-Durban North', 1, 80),
    ('07/11/2025', 'Spar Riverside', 1, 80),
    ('10/11/2025', 'Chester Butchery-Isipingo', 1, 88),
    ('10/11/2025', 'Superspar Yellow Wood Park', 1, 88),
    ('11/11/2025', 'Bluff Meat Supply-Bluff', 1, 53),
]

print("="*80)
print("RESTORING LWANDILE MAQINA'S KM AND HOURS DATA")
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
            inspector_id=lwandile.id
        )
        print(f"UPDATED {count} inspections: {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count
        multiple_found_count += 1
    else:
        # Update single inspection
        inspection = inspections.first()
        inspection.hours = hours
        inspection.km_traveled = km
        inspection.inspector_id = lwandile.id
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
