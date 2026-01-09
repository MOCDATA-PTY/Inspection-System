"""Check what's currently in PostgreSQL"""
import sys
import os
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Min, Max

print('Current inspections in PostgreSQL:')
print(f'Total count: {FoodSafetyAgencyInspection.objects.count():,}')
print()

dates = FoodSafetyAgencyInspection.objects.aggregate(Min('created_at'), Max('created_at'))
print(f'Oldest created: {dates["created_at__min"]}')
print(f'Newest created: {dates["created_at__max"]}')
print()

print('Checking problematic inspections (65931-65933):')
for insp_id in [65931, 65932, 65933]:
    i = FoodSafetyAgencyInspection.objects.filter(remote_id=insp_id).first()
    if i:
        print(f'  {insp_id}: {i.commodity} / {i.product_name}')
        print(f'    Client: {i.client_name}')
        print(f'    Created: {i.created_at}')
    else:
        print(f'  {insp_id}: NOT FOUND')
