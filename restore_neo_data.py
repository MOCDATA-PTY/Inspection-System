"""
Restore Neo Noe's KM and hours data for October-November 2025
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

# Get Neo's user
try:
    neo = User.objects.get(username='Neo')
except User.DoesNotExist:
    print("ERROR: User 'Neo' not found")
    # Try alternative username
    try:
        neo = User.objects.get(first_name='Neo', last_name='Noe')
        print(f"Found user: {neo.username}")
    except:
        print("ERROR: Could not find Neo Noe user")
        exit(1)

# Data from spreadsheet - Only inspections with KM/hours (most of Neo's entries are admin tasks)
# Format: (date, client, hours, km)
inspection_data = [
    ('27/10/2025', 'Feinschmecker Deli', 1, 40),  # 2 inspections on this date
]

print("="*80)
print("RESTORING NEO NOE'S KM AND HOURS DATA")
print("="*80)

updated_count = 0
not_found_count = 0

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
    else:
        # Update all matching inspections
        inspections.update(
            hours=hours,
            km_traveled=km,
            inspector_id=neo.id
        )
        print(f"UPDATED {count} inspection(s): {date_str} - {client_name} (Hours: {hours}, KM: {km})")
        updated_count += count

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total data entries: {len(inspection_data)}")
print(f"Inspections updated: {updated_count}")
print(f"Not found: {not_found_count}")
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
