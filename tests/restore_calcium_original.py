"""
Restore Calcium to its original rate of R379
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import InspectionFee, FeeHistory
from django.db import transaction

print('\n' + '='*60)
print(' RESTORING CALCIUM TO ORIGINAL RATE')
print('='*60)

calcium_fee = InspectionFee.objects.filter(fee_code='calcium_test_rate').first()

if not calcium_fee:
    print('\n[ERROR] Calcium fee not found!')
    sys.exit(1)

print(f'\nCurrent Calcium Rate: R{calcium_fee.rate}')
print(f'Current history records: {calcium_fee.history.count()}')

# Show all history
if calcium_fee.history.exists():
    print('\nExisting history:')
    for record in calcium_fee.history.all().order_by('effective_date'):
        print(f'  - {record.effective_date}: R{record.rate}')

# Delete ALL history records for Calcium
with transaction.atomic():
    deleted = calcium_fee.history.all().delete()[0]
    if deleted > 0:
        print(f'\n[OK] Deleted {deleted} history records')

    # Set Calcium back to original R379
    calcium_fee.rate = 379.00
    calcium_fee.save(update_fields=['rate'])
    print(f'[OK] Restored Calcium rate to R{calcium_fee.rate}')

# Verify
print(f'\n[FINAL STATE]')
print(f'  Calcium Rate: R{calcium_fee.rate}')
print(f'  History Records: {calcium_fee.history.count()}')

print('\n' + '='*60)
print(' RESTORATION COMPLETE')
print('='*60 + '\n')
