"""
Clean up Calcium fee history for testing - keep only July and December test records
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import InspectionFee, FeeHistory
from datetime import date

print('\n' + '='*60)
print(' CLEANING UP CALCIUM FEE HISTORY FOR TEST')
print('='*60)

calcium_fee = InspectionFee.objects.filter(fee_code='calcium_test_rate').first()

if not calcium_fee:
    print('\n[ERROR] Calcium fee not found!')
    sys.exit(1)

print(f'\nCurrent Calcium Rate: R{calcium_fee.rate}')
print(f'Current history records: {calcium_fee.history.count()}')

# Delete all history EXCEPT July 1 and Dec 1
july_date = date(2025, 7, 1)
dec_date = date(2025, 12, 1)

records_to_keep = calcium_fee.history.filter(
    effective_date__in=[july_date, dec_date]
).values_list('id', flat=True)

records_to_delete = calcium_fee.history.exclude(id__in=records_to_keep)

print(f'\nRecords to delete: {records_to_delete.count()}')
for record in records_to_delete:
    print(f'  - {record.effective_date}: R{record.rate}')

if records_to_delete.count() > 0:
    deleted = records_to_delete.delete()[0]
    print(f'\n[OK] Deleted {deleted} records')
else:
    print('\n[OK] No records to delete')

# Ensure July and Dec 1 records exist with correct values
from django.contrib.auth.models import User
admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()

# July: R5000
july_record, created = FeeHistory.objects.update_or_create(
    fee=calcium_fee,
    effective_date=july_date,
    defaults={
        'rate': 5000.00,
        'created_by': admin_user,
        'notes': 'TEST: July rate change'
    }
)
print(f'\nJuly 2025: R{july_record.rate}')

# December: R4000
dec_record, created = FeeHistory.objects.update_or_create(
    fee=calcium_fee,
    effective_date=dec_date,
    defaults={
        'rate': 4000.00,
        'created_by': admin_user,
        'notes': 'TEST: December rate change'
    }
)
print(f'December 2025: R{dec_record.rate}')

# Update current rate to December rate
calcium_fee.rate = 4000.00
calcium_fee.save(update_fields=['rate'])

print(f'\nFinal state:')
print(f'  Total history records: {calcium_fee.history.count()}')
print(f'  Current rate: R{calcium_fee.rate}')

print('\n' + '='*60)
print(' TESTING HISTORICAL LOOKUPS')
print('='*60)

test_dates = [
    (date(2025, 6, 15), 'June 15, 2025'),
    (date(2025, 7, 15), 'July 15, 2025'),
    (date(2025, 8, 15), 'August 15, 2025'),
    (date(2025, 11, 15), 'November 15, 2025'),
    (date(2025, 12, 15), 'December 15, 2025'),
]

for test_date, description in test_dates:
    rate = calcium_fee.get_rate_for_date(test_date)
    print(f'{description}: R{rate}')

print('\n' + '='*60)
