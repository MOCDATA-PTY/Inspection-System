"""
Clean up test fee history records - keep only initial rates
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FeeHistory, InspectionFee
from django.db import transaction

print('\n' + '='*60)
print(' CLEANING UP TEST FEE HISTORY')
print('='*60)

# Get all fee history records
all_history = FeeHistory.objects.all()
print(f'\nTotal fee history records: {all_history.count()}')

# Find records that are NOT initial rates (have previous_rate or are test data)
test_records = FeeHistory.objects.exclude(
    id__in=[
        # Keep only the FIRST (initial) record for each fee
        FeeHistory.objects.filter(fee=fee).order_by('created_at').first().id
        for fee in InspectionFee.objects.all()
    ]
)

print(f'Test/non-initial records to delete: {test_records.count()}')

if test_records.count() > 0:
    print('\nRecords to be deleted:')
    for record in test_records.order_by('fee__fee_name', '-effective_date')[:20]:
        print(f'  - {record.fee.fee_name}: R{record.rate} (effective {record.effective_date})')

    if test_records.count() > 20:
        print(f'  ... and {test_records.count() - 20} more')

    print(f'\nDeleting {test_records.count()} test records...')
    if True:
        with transaction.atomic():
            deleted_count = test_records.delete()[0]
            print(f'\n[OK] Deleted {deleted_count} test records!')

            # Now reset each fee's current rate to match its initial history rate
            for fee in InspectionFee.objects.all():
                initial_history = FeeHistory.objects.filter(fee=fee).order_by('created_at').first()
                if initial_history:
                    fee.rate = initial_history.rate
                    fee.save(update_fields=['rate'])
                    print(f'Reset {fee.fee_name} to R{fee.rate}')

        print('\n[SUCCESS] Fee history cleaned up!')
        print('Remaining records: ' + str(FeeHistory.objects.count()))
    else:
        print('Cancelled.')
else:
    print('\nNo test records to delete!')

print('\n' + '='*60)
