#!/usr/bin/env python
"""
Master script to restore ALL inspector KM and hours data
Runs all individual restore scripts with proper path setup
"""
import os
import sys
import django
from datetime import datetime

# Setup Django with correct path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User
from django.db import transaction

print("="*80)
print("MASTER DATA RESTORATION - ALL INSPECTORS")
print("="*80)
print(f"Target database: PostgreSQL")
print(f"Date range: October-November 2025")
print("="*80)

# Check initial state
initial_with_km = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    km_traveled__gt=0
).count()
print(f"\nInitial Oct-Nov inspections with KM: {initial_with_km}")

initial_with_hours = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    hours__gt=0
).count()
print(f"Initial Oct-Nov inspections with hours: {initial_with_hours}")

# Define all restore scripts to run
restore_scripts = [
    'tests/restore_cornelius_data.py',
    'tests/restore_gladys_data.py',
    'tests/restore_hellen_data.py',
    'tests/restore_jofred_data.py',
    'tests/restore_kabelo_data.py',
    'tests/restore_kutlwano_data.py',
    'tests/restore_lwandile_data.py',
    'tests/restore_mokgadi_data.py',
    'tests/restore_nelisa_data.py',
    'tests/restore_neo_data.py',
    'tests/restore_sandisiwe_data.py',
    'tests/restore_thato_data.py',
    'tests/restore_xola_data.py',
]

print(f"\nFound {len(restore_scripts)} restore scripts to run\n")

# Run each restore script
total_updated = 0
for script_path in restore_scripts:
    if os.path.exists(script_path):
        inspector_name = script_path.split('restore_')[1].split('_data.py')[0].title()
        print(f"\n{'='*80}")
        print(f"Running restore for: {inspector_name}")
        print(f"{'='*80}")

        try:
            # Execute the script
            with open(script_path, 'r') as f:
                script_code = f.read()
                # Replace the Django setup part since we already did it
                script_code = script_code.replace(
                    "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')\ndjango.setup()",
                    "# Django already set up"
                )
                exec(script_code)
        except Exception as e:
            print(f"ERROR running {inspector_name} restore: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"WARNING: Script not found: {script_path}")

# Final verification
print("\n" + "="*80)
print("FINAL VERIFICATION")
print("="*80)

final_with_km = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
    km_traveled__gt=0
).count()

final_with_hours = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 10, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date(),
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

print("\n" + "="*80)
print("ALL DATA RESTORATION COMPLETE!")
print("="*80)
