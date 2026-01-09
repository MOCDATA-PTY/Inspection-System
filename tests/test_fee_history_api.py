"""
Test the fee history API directly
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FeeHistory
import json

print('\n' + '='*60)
print(' TESTING FEE HISTORY API DATA')
print('='*60)

# Get all fee history ordered by effective date (most recent first)
history = FeeHistory.objects.select_related('fee', 'created_by').order_by('-effective_date', '-created_at')

history_data = []
for record in history[:5]:  # Just first 5
    # Get the previous rate by finding the next older history record for the same fee
    previous_history = FeeHistory.objects.filter(
        fee=record.fee,
        effective_date__lt=record.effective_date
    ).order_by('-effective_date').first()

    history_dict = {
        'id': record.id,
        'fee_name': record.fee.fee_name,
        'fee_code': record.fee.fee_code,
        'rate': float(record.rate),
        'previous_rate': float(previous_history.rate) if previous_history else None,
        'effective_date': record.effective_date.isoformat(),
        'created_at': record.created_at.isoformat(),
        'created_by': record.created_by.username if record.created_by else None,
        'notes': record.notes or ''
    }
    history_data.append(history_dict)

print('\nFirst 5 history records (as API would return):')
print(json.dumps(history_data, indent=2))

print('\n' + '='*60)
