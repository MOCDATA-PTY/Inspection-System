"""
Verify all fees have exactly one initial history record
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FeeHistory, InspectionFee

print('\n' + '='*60)
print(' VERIFYING FEE CLEANUP')
print('='*60)

all_fees = InspectionFee.objects.all()
print(f'\nTotal fees: {all_fees.count()}')

issues = []
for fee in all_fees:
    history_count = FeeHistory.objects.filter(fee=fee).count()

    if history_count != 1:
        issues.append(f'{fee.fee_name}: {history_count} records (expected 1)')
    else:
        initial = FeeHistory.objects.filter(fee=fee).first()
        # Check if it's truly an initial record (no previous rate in the chain)
        older_records = FeeHistory.objects.filter(
            fee=fee,
            effective_date__lt=initial.effective_date
        ).count()

        if older_records > 0:
            issues.append(f'{fee.fee_name}: has {older_records} older records!')
        else:
            print(f'[OK] {fee.fee_name}: R{fee.rate} (1 initial record)')

if issues:
    print('\n' + '='*60)
    print(' ISSUES FOUND:')
    print('='*60)
    for issue in issues:
        print(f'  [X] {issue}')
else:
    print('\n' + '='*60)
    print(' ALL FEES VERIFIED - CLEANUP SUCCESSFUL!')
    print('='*60)

print('\nTotal history records in database: ' + str(FeeHistory.objects.count()))
print('\n' + '='*60 + '\n')
