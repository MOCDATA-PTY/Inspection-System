"""
Fix trailing spaces in FoodSafetyAgencyInspection client names
This script strips leading/trailing spaces from all client names in PostgreSQL
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db import transaction

print('\n' + '='*60)
print(' FIXING TRAILING SPACES IN CLIENT NAMES')
print('='*60)

# Find all inspections with trailing/leading spaces
inspections_to_fix = []
for insp in FoodSafetyAgencyInspection.objects.all():
    if insp.client_name and insp.client_name != insp.client_name.strip():
        inspections_to_fix.append(insp)

print(f'\nFound {len(inspections_to_fix)} inspections with trailing/leading spaces')

if len(inspections_to_fix) == 0:
    print('\n[OK] No inspections need fixing!')
    sys.exit(0)

# Show sample before fixing
print(f'\nSample names BEFORE fixing (first 5):')
for i, insp in enumerate(inspections_to_fix[:5], 1):
    print(f'{i}. "{insp.client_name}" -> "{insp.client_name.strip()}"')

# Ask for confirmation
response = input(f'\nFix {len(inspections_to_fix)} inspection records? (yes/no): ')
if response.lower() != 'yes':
    print('Aborted.')
    sys.exit(0)

# Fix the trailing spaces
print('\nFixing records...')
fixed_count = 0

with transaction.atomic():
    for insp in inspections_to_fix:
        old_name = insp.client_name
        insp.client_name = insp.client_name.strip()
        insp.save(update_fields=['client_name'])
        fixed_count += 1

        if fixed_count % 100 == 0:
            print(f'  Fixed {fixed_count}/{len(inspections_to_fix)}...')

print(f'\n[OK] Successfully fixed {fixed_count} inspection records!')

# Verify the fix
remaining = 0
for insp in FoodSafetyAgencyInspection.objects.all():
    if insp.client_name and insp.client_name != insp.client_name.strip():
        remaining += 1

print(f'\nVerification: {remaining} records still have trailing spaces')

if remaining == 0:
    print('\n[SUCCESS] ALL TRAILING SPACES FIXED!')
else:
    print(f'\n[WARNING] {remaining} records still have issues')

print('\n' + '='*60)
print(' DONE - Refresh your browser to see the account codes!')
print('='*60 + '\n')
