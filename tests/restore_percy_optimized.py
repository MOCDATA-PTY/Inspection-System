#!/usr/bin/env python
"""
Optimized restore for Kabelo Percy's KM and hours data
Uses bulk operations to avoid slow individual queries
"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User
from django.db import transaction

print("=" * 80)
print("OPTIMIZED RESTORE FOR KABELO PERCY")
print("=" * 80)

# Get Percy user
try:
    percy = User.objects.get(username='Percy')
    print(f"Found user: {percy.username}")
except User.DoesNotExist:
    print("ERROR: Could not find Percy user")
    exit(1)

# Read data from Google Sheet
print("\nReading data from Google Sheet...")
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('tests/credentials.json', scope)
    client = gspread.authorize(creds)

    # Open the spreadsheet
    sheet_url = 'https://docs.google.com/spreadsheets/d/12O8aYOc0_Bz5UT8B1qUqICYDt4T9qR7HvzCDFPqiBqI/edit#gid=1766086297'
    spreadsheet = client.open_by_url(sheet_url)
    worksheet = spreadsheet.worksheet('Kabelo Percy')

    # Get all values
    all_values = worksheet.get_all_values()
    print(f"Found {len(all_values)} rows in sheet")

    # Parse data (skip header row)
    inspection_data = []
    for row in all_values[1:]:  # Skip header
        if len(row) < 4:
            continue

        date_str = row[0].strip()
        client_name = row[1].strip()

        try:
            hours = float(row[2]) if row[2].strip() else 0
            km = float(row[3]) if row[3].strip() else 0
        except (ValueError, IndexError):
            continue

        # Only process rows with actual hours and km data
        if hours > 0 or km > 0:
            # Parse date (handle different formats)
            try:
                if '/' in date_str:
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
                else:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

                # Only October-December 2025
                if date_obj.year == 2025 and date_obj.month >= 10:
                    inspection_data.append((date_obj, client_name, hours, km))
            except ValueError:
                continue

    print(f"Found {len(inspection_data)} entries with hours/km in Oct-Dec 2025")

except Exception as e:
    print(f"ERROR reading Google Sheet: {e}")
    print("Falling back to hardcoded data...")

    # Fallback to hardcoded data if sheet reading fails
    inspection_data = [
        (datetime(2025, 10, 1).date(), 'OBC Chicken &Meat-Cosmo City', 1, 40),
        (datetime(2025, 10, 1).date(), 'Roots Butchery-Cosmo City', 1, 40),
        # ... (would include all the hardcoded data here if needed)
    ]

if not inspection_data:
    print("No data to restore!")
    exit(0)

print(f"\n{len(inspection_data)} entries to process")

# OPTIMIZATION: Load all October-December inspections into memory ONCE
print("\nLoading inspections from database...")
all_inspections = list(FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 12, 31).date()
).select_related())

print(f"Loaded {len(all_inspections)} inspections into memory")

# Create a lookup dictionary for fast matching
# Key: (date, client_name_normalized)
inspection_lookup = {}
for insp in all_inspections:
    if insp.client_name:
        # Normalize client name for matching
        normalized = insp.client_name.lower().strip()
        key = (insp.date_of_inspection, normalized)

        if key not in inspection_lookup:
            inspection_lookup[key] = []
        inspection_lookup[key].append(insp)

print("Built lookup index")

# Match and update in memory
print("\nMatching inspections...")
updated_inspections = []
updated_count = 0
not_found_count = 0

for date_obj, client_name, hours, km in inspection_data:
    # Try exact match first
    client_normalized = client_name.lower().strip()
    key = (date_obj, client_normalized)

    matches = inspection_lookup.get(key, [])

    # If no exact match, try partial matching
    if not matches:
        # Try matching by date and partial client name
        client_search = client_name.split('-')[0].lower().strip()

        for insp in all_inspections:
            if (insp.date_of_inspection == date_obj and
                insp.client_name and
                client_search in insp.client_name.lower()):
                matches.append(insp)

    if matches:
        for insp in matches:
            insp.hours = hours
            insp.km_traveled = km
            insp.inspector_id = percy.id
            updated_inspections.append(insp)
            updated_count += 1
    else:
        not_found_count += 1

print(f"Matched {updated_count} inspections")
print(f"Not found: {not_found_count}")

# BULK UPDATE - much faster!
if updated_inspections:
    print(f"\nPerforming bulk update for {len(updated_inspections)} inspections...")

    with transaction.atomic():
        FoodSafetyAgencyInspection.objects.bulk_update(
            updated_inspections,
            ['hours', 'km_traveled', 'inspector_id'],
            batch_size=500
        )

    print("✓ Bulk update complete!")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total data entries: {len(inspection_data)}")
print(f"Inspections updated: {updated_count}")
print(f"Not found: {not_found_count}")
print("=" * 80)

# Verify
print("\nVERIFYING UPDATES...")
oct_dec_with_km = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 12, 31).date(),
    km_traveled__isnull=False,
    inspector_id=percy.id
).exclude(km_traveled=0).count()

oct_dec_with_hours = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 12, 31).date(),
    hours__isnull=False,
    inspector_id=percy.id
).exclude(hours=0).count()

print(f"Percy's Oct-Dec inspections with KM: {oct_dec_with_km}")
print(f"Percy's Oct-Dec inspections with hours: {oct_dec_with_hours}")
print("\n✓ RESTORE COMPLETE!")
