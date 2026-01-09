"""
Check fee history for recent changes
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FeeHistory, InspectionFee
from datetime import datetime, timedelta

print('\n' + '='*60)
print(' CHECKING FEE HISTORY')
print('='*60)

# Get Calcium fee
calcium_fee = InspectionFee.objects.filter(fee_name__icontains='Calcium').first()

if calcium_fee:
    print(f'\nFee: {calcium_fee.fee_name}')
    print(f'Current Rate: R{calcium_fee.rate}')
    print(f'\nHistory records (most recent first):')
    print('-' * 60)

    history = FeeHistory.objects.filter(fee=calcium_fee).order_by('-effective_date', '-created_at')[:10]

    for record in history:
        print(f'  Effective: {record.effective_date}')
        print(f'  Rate: R{record.rate}')
        print(f'  Created: {record.created_at}')
        print(f'  Created by: {record.created_by.username if record.created_by else "N/A"}')
        print('-' * 60)

    print(f'\nTotal history records for this fee: {FeeHistory.objects.filter(fee=calcium_fee).count()}')
else:
    print('\nCalcium fee not found!')

print('\n' + '='*60)
