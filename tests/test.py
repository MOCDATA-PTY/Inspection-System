"""
Comprehensive test of historical fee rates - with automatic cleanup
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
from main.views.core_views import get_fee_rate
from django.contrib.auth.models import User

print('\n' + '='*80)
print(' COMPREHENSIVE HISTORICAL FEE RATE TEST')
print('='*80)

# Get Calcium fee
calcium_fee = InspectionFee.objects.filter(fee_code='calcium_test_rate').first()
if not calcium_fee:
    print('\n[ERROR] Calcium fee not found!')
    sys.exit(1)

# Save original state
original_rate = calcium_fee.rate
original_history_count = calcium_fee.history.count()

print(f'\n[ORIGINAL STATE]')
print(f'  Calcium Rate: R{original_rate}')
print(f'  History Records: {original_history_count}')

# STEP 1: Create test fee history records
print('\n' + '-'*80)
print(' STEP 1: Creating test fee history records')
print('-'*80)

admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()

# July 2025 -> R5000
july_date = date(2025, 7, 1)
july_history, july_created = FeeHistory.objects.get_or_create(
    fee=calcium_fee,
    effective_date=july_date,
    defaults={
        'rate': 5000.00,
        'created_by': admin_user,
        'notes': 'TEST: July rate change'
    }
)
print(f'[OK] July 2025 record: R{july_history.rate} ({"created" if july_created else "already exists"})')

# December 2025 -> R4000
december_date = date(2025, 12, 1)
december_history, dec_created = FeeHistory.objects.get_or_create(
    fee=calcium_fee,
    effective_date=december_date,
    defaults={
        'rate': 4000.00,
        'created_by': admin_user,
        'notes': 'TEST: December rate change'
    }
)
print(f'[OK] December 2025 record: R{december_history.rate} ({"created" if dec_created else "already exists"})')

# Update current rate to December rate
calcium_fee.rate = 4000.00
calcium_fee.save(update_fields=['rate'])

# STEP 2: Test historical rate lookup
print('\n' + '-'*80)
print(' STEP 2: Testing historical rate lookup')
print('-'*80)

test_cases = [
    (date(2025, 6, 15), 'June 15, 2025', None),  # Before July, should fallback
    (date(2025, 7, 15), 'July 15, 2025', 5000.00),
    (date(2025, 8, 15), 'August 15, 2025', 5000.00),
    (date(2025, 11, 15), 'November 15, 2025', 5000.00),
    (date(2025, 12, 15), 'December 15, 2025', 4000.00),
]

all_passed = True
for test_date, description, expected_rate in test_cases:
    actual_rate = float(calcium_fee.get_rate_for_date(test_date))

    if expected_rate is None:
        # For dates before any history, just show the result
        print(f'  {description}: R{actual_rate} (fallback to current rate)')
    else:
        status = '[OK]' if actual_rate == expected_rate else '[FAIL]'
        if actual_rate != expected_rate:
            all_passed = False
        print(f'  {status} {description}: R{actual_rate} (expected R{expected_rate})')

# STEP 3: Test export rate calculation (simulates actual export)
print('\n' + '-'*80)
print(' STEP 3: Testing export rate calculation (simulates actual export)')
print('-'*80)

# Test July
july_export_rate = get_fee_rate('calcium_test_rate', 379.00, date(2025, 7, 15))
july_ok = float(july_export_rate) == 5000.00
print(f'  {"[OK]" if july_ok else "[FAIL]"} July export rate: R{july_export_rate} (expected R5000)')
if not july_ok:
    all_passed = False

# Test December
dec_export_rate = get_fee_rate('calcium_test_rate', 379.00, date(2025, 12, 15))
dec_ok = float(dec_export_rate) == 4000.00
print(f'  {"[OK]" if dec_ok else "[FAIL]"} December export rate: R{dec_export_rate} (expected R4000)')
if not dec_ok:
    all_passed = False

# STEP 4: Test with actual December inspections
print('\n' + '-'*80)
print(' STEP 4: Testing with actual December 2025 inspections')
print('-'*80)

december_inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__year=2025,
    date_of_inspection__month=12,
    commodity__in=['RAW', 'PMP']
)[:3]

if december_inspections.exists():
    print(f'\nTesting with {december_inspections.count()} December inspections:')
    for inspection in december_inspections:
        rate = get_fee_rate('calcium_test_rate', 379.00, inspection.date_of_inspection)
        rate_ok = float(rate) == 4000.00
        print(f'  {"[OK]" if rate_ok else "[FAIL]"} {inspection.date_of_inspection} - {inspection.client_name}: R{rate}')
        if not rate_ok:
            all_passed = False
else:
    print('  [INFO] No December inspections found to test with')

# SUMMARY
print('\n' + '='*80)
print(' TEST SUMMARY')
print('='*80)

if all_passed:
    print('\n[SUCCESS] All tests passed! Historical fee tracking is working correctly.')
    print('\nWhat this means:')
    print('  - Inspections from July-November 2025 will use R5000 for Calcium tests')
    print('  - Inspections from December 2025 onwards will use R4000 for Calcium tests')
    print('  - When you export data, different rates will be applied based on inspection date')
else:
    print('\n[FAILURE] Some tests failed. Historical fee tracking may not be working correctly.')

# STEP 5: Cleanup
print('\n' + '-'*80)
print(' STEP 5: Cleaning up test records')
print('-'*80)

# Delete test records (July and December)
test_records = FeeHistory.objects.filter(
    fee=calcium_fee,
    effective_date__in=[july_date, december_date]
)

deleted_count = test_records.count()
if deleted_count > 0:
    print(f'\nDeleting {deleted_count} test records:')
    for record in test_records:
        print(f'  - {record.effective_date}: R{record.rate}')

    test_records.delete()
    print(f'\n[OK] Deleted {deleted_count} test records')

# Restore original rate
calcium_fee.rate = original_rate
calcium_fee.save(update_fields=['rate'])

# Verify cleanup
final_history_count = calcium_fee.history.count()
print(f'\n[RESTORED STATE]')
print(f'  Calcium Rate: R{calcium_fee.rate}')
print(f'  History Records: {final_history_count} (was {original_history_count} originally)')

if final_history_count == original_history_count and calcium_fee.rate == original_rate:
    print('\n[OK] Successfully restored to original state!')
else:
    print('\n[WARNING] State may not be fully restored')

print('\n' + '='*80)
print(' TEST COMPLETE')
print('='*80 + '\n')
