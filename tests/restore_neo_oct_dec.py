#!/usr/bin/env python
"""
Restore Neo Noe's KM and Hours data for October-December 2025
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db import transaction
from datetime import datetime

print("="*80)
print("RESTORING NEO NOE DATA - OCTOBER-DECEMBER 2025")
print("="*80)

# Data from spreadsheet - only entries with hours and km
data = [
    # October 2025
    {'date': '2025-10-27', 'client': 'Feinschmecker Deli', 'commodity': 'PMP', 'hours': 1, 'km': 40},

    # July 2025 (included in the data)
    {'date': '2025-07-10', 'client': 'Fruit Stop-Wonderboom', 'commodity': 'PMP', 'hours': 1, 'km': 20},
    {'date': '2025-07-15', 'client': 'Pick \'n Pay - The Reeds', 'commodity': 'PMP', 'hours': 1, 'km': 50},
    {'date': '2025-07-15', 'client': 'Pick \'n Pay - The Reeds', 'commodity': 'RAW', 'hours': 1, 'km': 50},
    {'date': '2025-07-15', 'client': 'Superspar Saxby', 'commodity': 'PMP', 'hours': 1, 'km': 39},
    {'date': '2025-07-17', 'client': 'Boxer Superstore', 'commodity': 'RAW', 'hours': 1.5, 'km': 20},
    {'date': '2025-07-17', 'client': 'Boxer Superstore', 'commodity': 'PMP', 'hours': 1.5, 'km': 20},
    {'date': '2025-07-23', 'client': 'Sinoville Vleismark (Derdepark Supermarket)', 'commodity': 'RAW', 'hours': 2, 'km': 6},
    {'date': '2025-07-23', 'client': 'Sinoville Vleismark (Derdepark Supermarket)', 'commodity': 'PMP', 'hours': 2, 'km': 6},
    {'date': '2025-07-23', 'client': 'Sondelani', 'commodity': 'RAW', 'hours': 1, 'km': 6},
    {'date': '2025-07-23', 'client': 'Sondelani', 'commodity': 'PMP', 'hours': 1, 'km': 6},
    {'date': '2025-07-24', 'client': 'Woolworths - Kolonnade', 'commodity': 'RAW', 'hours': 1, 'km': 10},
    {'date': '2025-07-24', 'client': 'Woolworths - Kolonnade', 'commodity': 'PMP', 'hours': 1, 'km': 10},
    {'date': '2025-07-24', 'client': 'Checkers Kolonnade', 'commodity': 'RAW', 'hours': 1, 'km': 10},
    {'date': '2025-07-24', 'client': 'Checkers Kolonnade', 'commodity': 'PMP', 'hours': 1, 'km': 10},
]

inspector_name = 'Neo Noe'
updated_count = 0
not_found = []

print(f"\nSearching for {len(data)} inspection records for {inspector_name}...")
print(f"Date range: July-October 2025\n")

with transaction.atomic():
    for entry in data:
        try:
            # Parse date
            date = datetime.strptime(entry['date'], '%Y-%m-%d').date()

            # Find matching inspections using flexible matching
            # Match by date, inspector, commodity, and partial client name
            client_search = entry['client'].replace("'", "").split()[0]  # Get first word, handle apostrophes
            inspections = FoodSafetyAgencyInspection.objects.filter(
                inspector_name__iexact=inspector_name,
                date_of_inspection=date,
                client_name__icontains=client_search,
                commodity__iexact=entry['commodity']
            )

            if inspections.exists():
                inspections.update(
                    km_traveled=entry['km'],
                    hours=entry['hours']
                )
                count = inspections.count()
                updated_count += count
                print(f"[OK] Updated {count} inspection(s): {entry['client']} on {entry['date']} ({entry['hours']}h, {entry['km']}km)")
            else:
                not_found.append(entry)
                print(f"[NOT FOUND] {entry['client']} on {entry['date']}")

        except Exception as e:
            print(f"[ERROR] {entry['client']} on {entry['date']}: {e}")
            continue

print("\n" + "="*80)
print(f"RESTORATION COMPLETE")
print("="*80)
print(f"[OK] Updated: {updated_count} inspections")
print(f"[NOT FOUND]: {len(not_found)} inspections")

if not_found:
    print(f"\nInspections not found in database:")
    for entry in not_found[:5]:  # Show first 5
        print(f"  - {entry['client']} on {entry['date']}")
    if len(not_found) > 5:
        print(f"  ... and {len(not_found) - 5} more")

print("="*80)
