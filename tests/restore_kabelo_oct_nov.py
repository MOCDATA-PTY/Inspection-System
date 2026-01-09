#!/usr/bin/env python
"""
Restore Kabelo Percy's KM and Hours data for October-November 2025
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
from django.db import transaction

print("="*80)
print("RESTORING KABELO PERCY DATA - OCTOBER-NOVEMBER 2025")
print("="*80)

# Data from spreadsheet - only entries with hours and km
data = [
    # October 2025
    {'date': '2025-10-01', 'client': 'OBC Chicken', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-01', 'client': 'OBC Chicken', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-01', 'client': 'OBC Chicken', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-01', 'client': 'OBC Chicken', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-10-01', 'client': 'Roots Butchery-Cosmo', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-01', 'client': 'Roots Butchery-Cosmo', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-01', 'client': 'Roots Butchery-Cosmo', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-01', 'client': 'Roots Butchery-Cosmo', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-10-01', 'client': 'Boxer Superstores-Cosmo', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-01', 'client': 'Boxer Superstores-Cosmo', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-01', 'client': 'Boxer Superstores-Cosmo', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-01', 'client': 'Boxer Superstores-Cosmo', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-10-02', 'client': 'Pick n Pay-Northcliff', 'commodity': 'RAW', 'hours': 1, 'km': 50},
    {'date': '2025-10-02', 'client': 'Pick n Pay-Northcliff', 'commodity': 'PMP', 'hours': 1, 'km': 50},
    {'date': '2025-10-02', 'client': 'Pick n Pay-Northcliff', 'commodity': 'POULTRY', 'hours': 1, 'km': 50},
    {'date': '2025-10-02', 'client': 'Pick n Pay-Northcliff', 'commodity': 'EGGS', 'hours': 1, 'km': 50},
    {'date': '2025-10-03', 'client': 'T & F Meat', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-03', 'client': 'T & F Meat', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-03', 'client': 'T & F Meat', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-03', 'client': 'T & F Meat', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-10-03', 'client': 'Spar-Randjespark', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-03', 'client': 'Spar-Randjespark', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-03', 'client': 'Spar-Randjespark', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-03', 'client': 'Spar-Randjespark', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-10-16', 'client': 'Food Lovers Market-Waterfall', 'commodity': 'RAW', 'hours': 1, 'km': 90},
    {'date': '2025-10-16', 'client': 'Food Lovers Market-Waterfall', 'commodity': 'EGGS', 'hours': 1, 'km': 90},
    {'date': '2025-10-16', 'client': 'Superspar-Vorna', 'commodity': 'RAW', 'hours': 1, 'km': 90},
    {'date': '2025-10-16', 'client': 'Superspar-Vorna', 'commodity': 'POULTRY', 'hours': 1, 'km': 90},
    {'date': '2025-10-17', 'client': 'Roots Butchery-Festival', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-17', 'client': 'Roots Butchery-Festival', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-17', 'client': 'Roots Butchery-Festival', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-17', 'client': 'Roots Butchery-Festival', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-10-17', 'client': 'Ma Kong', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-17', 'client': 'Ma Kong', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-20', 'client': 'The Meat Boss', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-20', 'client': 'The Meat Boss', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-20', 'client': 'The Meat Boss', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-10-20', 'client': 'Plus Butchery', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-20', 'client': 'Plus Butchery', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-20', 'client': 'Plus Butchery', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-20', 'client': 'Plus Butchery', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-10-20', 'client': 'Roots Choice', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-20', 'client': 'Roots Choice', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-20', 'client': 'Roots Choice', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-20', 'client': 'Roots Choice', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-10-21', 'client': 'Spar Heidelberg', 'commodity': 'RAW', 'hours': 1, 'km': 80},
    {'date': '2025-10-21', 'client': 'Spar Heidelberg', 'commodity': 'PMP', 'hours': 1, 'km': 80},
    {'date': '2025-10-21', 'client': 'Spar Heidelberg', 'commodity': 'POULTRY', 'hours': 1, 'km': 80},
    {'date': '2025-10-21', 'client': 'Spar Heidelberg', 'commodity': 'EGGS', 'hours': 1, 'km': 80},
    {'date': '2025-10-21', 'client': 'Eskort Heidelberg', 'commodity': 'PMP', 'hours': 1, 'km': 80},
    {'date': '2025-10-21', 'client': 'Eskort Heidelberg', 'commodity': 'RAW', 'hours': 1, 'km': 80},
    {'date': '2025-10-22', 'client': 'Altamash Halaal', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-22', 'client': 'Altamash Halaal', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-22', 'client': 'Spar Noordwyk', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-22', 'client': 'Spar Noordwyk', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-22', 'client': 'Spar Noordwyk', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-10-24', 'client': 'B Nagiahs', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-24', 'client': 'B Nagiahs', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-24', 'client': 'B Nagiahs', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-24', 'client': "DB'S Butchery", 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-24', 'client': "DB'S Butchery", 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-24', 'client': "DB'S Butchery", 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-10-24', 'client': 'Food Lovers Market Fourways', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-24', 'client': 'Food Lovers Market Fourways', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-24', 'client': 'Food Lovers Market Fourways', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-24', 'client': 'Food Lovers Market Fourways', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-10-27', 'client': 'Kruinsig', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-27', 'client': 'Kruinsig', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-27', 'client': 'Kruinsig', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-27', 'client': 'Superspar Ruimsig', 'commodity': 'RAW', 'hours': 1, 'km': 60},
    {'date': '2025-10-27', 'client': 'Superspar Ruimsig', 'commodity': 'PMP', 'hours': 1, 'km': 60},
    {'date': '2025-10-27', 'client': 'Superspar Ruimsig', 'commodity': 'POULTRY', 'hours': 1, 'km': 60},
    {'date': '2025-10-27', 'client': 'Superspar Ruimsig', 'commodity': 'EGGS', 'hours': 1, 'km': 60},
    {'date': '2025-10-28', 'client': 'Metro Cash', 'commodity': 'RAW', 'hours': 1, 'km': 60},
    {'date': '2025-10-28', 'client': 'Metro Cash', 'commodity': 'PMP', 'hours': 1, 'km': 60},
    {'date': '2025-10-28', 'client': 'Metro Cash', 'commodity': 'POULTRY', 'hours': 1, 'km': 60},
    {'date': '2025-10-28', 'client': 'Metro Cash', 'commodity': 'EGGS', 'hours': 1, 'km': 60},
    {'date': '2025-10-29', 'client': 'Roots Butchery Diepsloot', 'commodity': 'RAW', 'hours': 1, 'km': 60},
    {'date': '2025-10-29', 'client': 'Roots Butchery Diepsloot', 'commodity': 'PMP', 'hours': 1, 'km': 60},
    {'date': '2025-10-29', 'client': 'Roots Butchery Diepsloot', 'commodity': 'POULTRY', 'hours': 1, 'km': 60},
    {'date': '2025-10-29', 'client': 'Roots Butchery Diepsloot', 'commodity': 'EGGS', 'hours': 1, 'km': 60},
    {'date': '2025-10-30', 'client': 'Van Wyngraahrt', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-30', 'client': 'Northcliff Halaal', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-30', 'client': 'Northcliff Halaal', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-30', 'client': 'Northcliff Halaal', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-31', 'client': 'Superspar Carlswald', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-10-31', 'client': 'Superspar Carlswald', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-10-31', 'client': 'Superspar Carlswald', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-10-31', 'client': 'Superspar Carlswald', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    # November 2025
    {'date': '2025-11-03', 'client': 'Roots Butchery', 'commodity': 'RAW', 'hours': 1, 'km': 60},
    {'date': '2025-11-03', 'client': 'Roots Butchery', 'commodity': 'PMP', 'hours': 1, 'km': 60},
    {'date': '2025-11-03', 'client': 'Roots Butchery', 'commodity': 'POULTRY', 'hours': 1, 'km': 60},
    {'date': '2025-11-03', 'client': 'Roots Butchery', 'commodity': 'EGGS', 'hours': 1, 'km': 60},
    {'date': '2025-11-04', 'client': 'SUPERSPAR', 'commodity': 'RAW', 'hours': 1, 'km': 60},
    {'date': '2025-11-04', 'client': 'SUPERSPAR', 'commodity': 'POULTRY', 'hours': 1, 'km': 60},
    {'date': '2025-11-04', 'client': 'SUPERSPAR', 'commodity': 'EGGS', 'hours': 1, 'km': 60},
    {'date': '2025-11-04', 'client': 'Food Lovers Market Ferndale', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-11-05', 'client': 'Food Lovers Market Ferndale', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-11-05', 'client': 'Food Lovers Market Ferndale', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-11-05', 'client': 'Food Lovers Market Ferndale', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-11-05', 'client': 'Pick n Pay Blue', 'commodity': 'RAW', 'hours': 1, 'km': 50},
    {'date': '2025-11-05', 'client': 'Pick n Pay Blue', 'commodity': 'PMP', 'hours': 1, 'km': 50},
    {'date': '2025-11-05', 'client': 'Pick n Pay Blue', 'commodity': 'POULTRY', 'hours': 1, 'km': 50},
    {'date': '2025-11-05', 'client': 'Pick n Pay Blue', 'commodity': 'EGGS', 'hours': 1, 'km': 50},
    {'date': '2025-11-07', 'client': 'Pick n Pay', 'commodity': 'RAW', 'hours': 1, 'km': 50},
    {'date': '2025-11-07', 'client': 'Pick n Pay', 'commodity': 'PMP', 'hours': 1, 'km': 50},
    {'date': '2025-11-07', 'client': 'Pick n Pay', 'commodity': 'POULTRY', 'hours': 1, 'km': 50},
    {'date': '2025-11-07', 'client': 'Pick n Pay', 'commodity': 'EGGS', 'hours': 1, 'km': 50},
    {'date': '2025-11-07', 'client': 'Boma Meat', 'commodity': 'RAW', 'hours': 1, 'km': 50},
    {'date': '2025-11-07', 'client': 'Boma Meat', 'commodity': 'PMP', 'hours': 1, 'km': 50},
    {'date': '2025-11-10', 'client': 'Superspar Polofields', 'commodity': 'RAW', 'hours': 1, 'km': 30},
    {'date': '2025-11-10', 'client': 'Superspar Polofields', 'commodity': 'PMP', 'hours': 1, 'km': 30},
    {'date': '2025-11-10', 'client': 'Superspar Polofields', 'commodity': 'POULTRY', 'hours': 1, 'km': 30},
    {'date': '2025-11-10', 'client': 'Superspar Polofields', 'commodity': 'EGGS', 'hours': 1, 'km': 30},
    {'date': '2025-11-11', 'client': 'Chester Butcheries', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-11-11', 'client': 'Chester Butcheries', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-11-11', 'client': 'Chester Butcheries', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-11-11', 'client': 'Chester Butcheries', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-11-11', 'client': 'Waltloo Meat', 'commodity': 'RAW', 'hours': 1, 'km': 40},
    {'date': '2025-11-11', 'client': 'Waltloo Meat', 'commodity': 'PMP', 'hours': 1, 'km': 40},
    {'date': '2025-11-11', 'client': 'Waltloo Meat', 'commodity': 'POULTRY', 'hours': 1, 'km': 40},
    {'date': '2025-11-11', 'client': 'Waltloo Meat', 'commodity': 'EGGS', 'hours': 1, 'km': 40},
    {'date': '2025-11-11', 'client': 'Kwikspar Stop', 'commodity': 'RAW', 'hours': 1, 'km': 30},
    {'date': '2025-11-11', 'client': 'Kwikspar Stop', 'commodity': 'POULTRY', 'hours': 1, 'km': 30},
    {'date': '2025-11-11', 'client': 'Kwikspar Stop', 'commodity': 'EGGS', 'hours': 1, 'km': 30},
]

inspector_name = 'PERCY MALEKA'
updated_count = 0
not_found = []

print(f"\nSearching for {len(data)} inspection records for {inspector_name}...")
print(f"Date range: October-November 2025\n")

with transaction.atomic():
    for entry in data:
        try:
            date = datetime.strptime(entry['date'], '%Y-%m-%d').date()
            client_search = entry['client'].replace("'", "").split()[0]

            inspections = FoodSafetyAgencyInspection.objects.filter(
                inspector_name__iexact=inspector_name,
                date_of_inspection=date,
                client_name__icontains=client_search,
                commodity__iexact=entry['commodity']
            )

            if inspections.exists():
                inspections.update(km_traveled=entry['km'], hours=entry['hours'])
                count = inspections.count()
                updated_count += count
                print(f"[OK] Updated {count}: {entry['client']} on {entry['date']} ({entry['hours']}h, {entry['km']}km)")
            else:
                not_found.append(entry)
                print(f"[NOT FOUND] {entry['client']} on {entry['date']}")
        except Exception as e:
            print(f"[ERROR] {entry['client']}: {e}")

print("\n" + "="*80)
print(f"RESTORATION COMPLETE")
print("="*80)
print(f"[OK] Updated: {updated_count} inspections")
print(f"[NOT FOUND]: {len(not_found)} inspections")
print("="*80)
