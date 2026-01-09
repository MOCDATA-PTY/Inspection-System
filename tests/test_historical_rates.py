"""
Test historical fee rates with July and December changes
"""
import os
import sys
import django
from datetime import date

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import InspectionFee, FeeHistory, FoodSafetyAgencyInspection
from django.contrib.auth.models import User

print('\n' + '='*60)
print(' TESTING HISTORICAL FEE RATES')
print('='*60)

# Get Calcium fee
calcium_fee = InspectionFee.objects.filter(fee_code='calcium_test_rate').first()

if not calcium_fee:
    print('\n[ERROR] Calcium fee not found!')
    sys.exit(1)

print(f'\nCurrent Calcium Rate: R{calcium_fee.rate}')

# Create test fee history records
print('\n' + '-'*60)
print(' STEP 1: Creating test fee history records')
print('-'*60)

# Get or create a test user
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = User.objects.first()

# July 2025 rate change to R5000
july_date = date(2025, 7, 1)
july_history, created = FeeHistory.objects.get_or_create(
    fee=calcium_fee,
    effective_date=july_date,
    defaults={
        'rate': 5000.00,
        'created_by': admin_user,
        'notes': 'TEST: July rate change'
    }
)
if created:
    print(f'[OK] Created July 2025 history: R5000')
else:
    print(f'  July 2025 history already exists: R{july_history.rate}')

# December 2025 rate change to R4000
december_date = date(2025, 12, 1)
december_history, created = FeeHistory.objects.get_or_create(
    fee=calcium_fee,
    effective_date=december_date,
    defaults={
        'rate': 4000.00,
        'created_by': admin_user,
        'notes': 'TEST: December rate change'
    }
)
if created:
    print(f'[OK] Created December 2025 history: R4000')
else:
    print(f'  December 2025 history already exists: R{december_history.rate}')

# Update current rate to match December
calcium_fee.rate = 4000.00
calcium_fee.save(update_fields=['rate'])
print(f'\nUpdated current Calcium rate to: R{calcium_fee.rate}')

# Test the historical rate lookup
print('\n' + '-'*60)
print(' STEP 2: Testing historical rate lookup')
print('-'*60)

test_dates = [
    (date(2025, 6, 15), 'June 2025 (before July change)'),
    (date(2025, 8, 15), 'August 2025 (after July change)'),
    (date(2025, 11, 15), 'November 2025 (after July, before December)'),
    (date(2025, 12, 15), 'December 2025 (after December change)'),
]

for test_date, description in test_dates:
    rate = calcium_fee.get_rate_for_date(test_date)
    print(f'{description}: R{rate}')

# Find inspections from different months to test with
print('\n' + '-'*60)
print(' STEP 3: Finding inspections for export test')
print('-'*60)

# Find some inspections from different months
july_inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__year=2025,
    date_of_inspection__month=7,
    commodity__in=['RAW', 'PMP']
).count()

august_inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__year=2025,
    date_of_inspection__month=8,
    commodity__in=['RAW', 'PMP']
).count()

december_inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__year=2025,
    date_of_inspection__month=12,
    commodity__in=['RAW', 'PMP']
).count()

print(f'\nJuly 2025 inspections: {july_inspections}')
print(f'August 2025 inspections: {august_inspections}')
print(f'December 2025 inspections: {december_inspections}')

if july_inspections == 0 and august_inspections == 0 and december_inspections == 0:
    print('\n[WARNING] No inspections found from these months to test with!')
    print('You may need to create test inspection data or use a different date range.')
else:
    print('\n[SUCCESS] Ready to test export!')
    print('\nNext steps:')
    print('1. Go to Export Sheet page')
    print('2. Filter for July-August 2025 (should show R5000 for Calcium tests)')
    print('3. Filter for December 2025 (should show R4000 for Calcium tests)')
    print('4. Export to Excel and verify rates are different')

print('\n' + '='*60)
