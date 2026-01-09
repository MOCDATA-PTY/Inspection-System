#!/usr/bin/env python
"""
FAST bulk restore for ALL inspector KM and hours data
Loads all data into memory and uses bulk operations
"""
import os
import sys
import django
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User
from django.db import transaction

print("=" * 80)
print("FAST BULK RESTORE - ALL INSPECTORS")
print("=" * 80)

# Check initial state
initial_with_km = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 12, 31).date(),
    km_traveled__gt=0
).count()

initial_with_hours = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 12, 31).date(),
    hours__gt=0
).count()

print(f"\nInitial Oct-Dec inspections with KM: {initial_with_km}")
print(f"Initial Oct-Dec inspections with hours: {initial_with_hours}")

# Read Google Sheets data for all inspectors
print("\n" + "=" * 80)
print("READING GOOGLE SHEETS DATA")
print("=" * 80)

try:
    import gspread
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    import pickle
    import os

    # Try to use existing token.pickle (OAuth)
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, try to refresh
    if creds and creds.expired and creds.refresh_token:
        print("Refreshing OAuth token...")
        creds.refresh(Request())
        # Save the refreshed token
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    if not creds or not creds.valid:
        print("ERROR: No valid OAuth credentials found")
        print("Please ensure token.pickle exists and is valid")
        raise Exception("No valid credentials")

    client = gspread.authorize(creds)

    # Open the spreadsheet
    sheet_url = 'https://docs.google.com/spreadsheets/d/1Fy7HuSCb2h_62xTuwcjmvEd5YX8KLB8B3CWG_70FTdw/edit'
    spreadsheet = client.open_by_url(sheet_url)

    # Inspector sheet mapping (username -> sheet tab name)
    inspector_sheets = {
        'Cornelius': 'Corneluis Adams',
        'Gladys': 'Gladys Manganye',
        'Hellen': 'Hellen Modiba',
        'Jofred': 'Jofred Steyn',
        'Percy': 'Kabelo Percy',
        'Kutlwano': 'Kutlwano Kuntwane',
        'Lwandile': 'Lwandile Maqina',
        'Mokgadi': 'Mokgadi Selone',
        'Nelisa': 'Nelisa Ntoyaphi',
        'Neo': 'Neo Noe',
        'Sandisiwe': 'Sandisiwe Dlisani',
        'Thato': 'Thato Sekhotho',
        'Xola': 'Mpeluza Xola',
        'Cinga': 'Cinga Ngongo',
        'Ben': 'Ben Visagie',
        'Hazel': 'Hazel Sosibo',
        'Palesa': 'Palesa Mpana',
    }

    # Collect all data from all sheets
    all_data = []

    for username, sheet_name in inspector_sheets.items():
        print(f"\nReading sheet: '{sheet_name}'...", end=' ')

        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            rows = worksheet.get_all_values()

            # Parse rows (skip header rows - starts at row 3 based on actual format)
            inspector_data = []
            for row in rows[3:]:  # Skip header and example rows
                if len(row) < 14:  # Need at least 14 columns (0-13)
                    continue

                # Column 4: Date, Column 5: Client Name, Column 12: Hours, Column 13: KM
                date_str = row[4].strip() if len(row) > 4 else ''
                client_name = row[5].strip() if len(row) > 5 else ''

                try:
                    hours_str = row[12].strip() if len(row) > 12 else ''
                    km_str = row[13].strip() if len(row) > 13 else ''
                    hours = float(hours_str) if hours_str else 0
                    km = float(km_str) if km_str else 0
                except (ValueError, IndexError):
                    continue

                # Only process rows with actual data
                if hours > 0 or km > 0:
                    try:
                        if '/' in date_str:
                            date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
                        else:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

                        # Only October-December 2025
                        if date_obj.year == 2025 and date_obj.month >= 10:
                            inspector_data.append({
                                'username': username,
                                'date': date_obj,
                                'client': client_name,
                                'hours': hours,
                                'km': km
                            })
                    except ValueError:
                        continue

            print(f"Found {len(inspector_data)} entries")
            all_data.extend(inspector_data)

        except Exception as e:
            print(f"ERROR: {e}")
            continue

    print(f"\nTotal entries collected: {len(all_data)}")

except Exception as e:
    print(f"ERROR reading Google Sheets: {e}")
    print("Cannot proceed without sheet data")
    exit(1)

if not all_data:
    print("No data to restore!")
    exit(0)

# Get all inspector users
print("\n" + "=" * 80)
print("LOADING INSPECTOR USERS")
print("=" * 80)

user_map = {}
for username in inspector_sheets.keys():
    try:
        user = User.objects.get(username=username)
        user_map[username] = user
        print(f"[OK] {username}")
    except User.DoesNotExist:
        print(f"[NOT FOUND] {username}")

# Load ALL Oct-Dec inspections into memory ONCE
print("\n" + "=" * 80)
print("LOADING INSPECTIONS FROM DATABASE")
print("=" * 80)

all_inspections = list(FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 12, 31).date()
))

print(f"Loaded {len(all_inspections)} inspections into memory")

# Create lookup index
print("Building lookup index...")
inspection_by_date = {}
for insp in all_inspections:
    date_key = insp.date_of_inspection
    if date_key not in inspection_by_date:
        inspection_by_date[date_key] = []
    inspection_by_date[date_key].append(insp)

print("Index built!")

# Match all data in memory
print("\n" + "=" * 80)
print("MATCHING INSPECTIONS")
print("=" * 80)

to_update = []
updated_count = 0
not_found_count = 0

for entry in all_data:
    username = entry['username']
    date_obj = entry['date']
    client_name = entry['client']
    hours = entry['hours']
    km = entry['km']

    # Get user
    user = user_map.get(username)
    if not user:
        not_found_count += 1
        continue

    # Find inspections on this date
    candidates = inspection_by_date.get(date_obj, [])

    # Try to match by client name
    matches = []
    client_search = client_name.split('-')[0].lower().strip()

    for insp in candidates:
        if insp.client_name and client_search in insp.client_name.lower():
            matches.append(insp)

    if matches:
        for insp in matches:
            insp.hours = hours
            insp.km_traveled = km
            insp.inspector_id = user.id
            to_update.append(insp)
            updated_count += 1
    else:
        not_found_count += 1

print(f"Matched {updated_count} inspections")
print(f"Not found: {not_found_count}")

# BULK UPDATE ALL AT ONCE
if to_update:
    print("\n" + "=" * 80)
    print(f"PERFORMING BULK UPDATE FOR {len(to_update)} INSPECTIONS")
    print("=" * 80)

    with transaction.atomic():
        # Update in batches
        batch_size = 500
        for i in range(0, len(to_update), batch_size):
            batch = to_update[i:i + batch_size]
            FoodSafetyAgencyInspection.objects.bulk_update(
                batch,
                ['hours', 'km_traveled', 'inspector_id'],
                batch_size=batch_size
            )
            print(f"Updated batch {i//batch_size + 1}/{(len(to_update) + batch_size - 1)//batch_size}")

    print("[OK] Bulk update complete!")

# Final verification
print("\n" + "=" * 80)
print("FINAL VERIFICATION")
print("=" * 80)

final_with_km = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 12, 31).date(),
    km_traveled__gt=0
).count()

final_with_hours = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 12, 31).date(),
    hours__gt=0
).count()

print(f"\nBefore restoration:")
print(f"  - Inspections with KM: {initial_with_km}")
print(f"  - Inspections with hours: {initial_with_hours}")
print(f"\nAfter restoration:")
print(f"  - Inspections with KM: {final_with_km}")
print(f"  - Inspections with hours: {final_with_hours}")
print(f"\nRestored:")
print(f"  - KM data added to: {final_with_km - initial_with_km} inspections")
print(f"  - Hours data added to: {final_with_hours - initial_with_hours} inspections")

print("\n" + "=" * 80)
print("[SUCCESS] ALL DATA RESTORATION COMPLETE!")
print("=" * 80)
