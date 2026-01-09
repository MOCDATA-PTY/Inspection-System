#!/usr/bin/env python
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import datetime

print('=== NOVEMBER 2025 DATA ===')
nov = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=datetime(2025, 11, 1).date(),
    date_of_inspection__lte=datetime(2025, 11, 30).date()
)

total = nov.count()
with_km = nov.filter(km_traveled__gt=0).count()
with_hours = nov.filter(hours__gt=0).count()

print(f'Total inspections: {total:,}')
print(f'With KM: {with_km:,} ({with_km/total*100 if total > 0 else 0:.1f}%)')
print(f'With hours: {with_hours:,} ({with_hours/total*100 if total > 0 else 0:.1f}%)')
print(f'\nMissing data: {total - with_km:,} inspections')

print('\nSample inspections WITH km/hours:')
for i in nov.filter(km_traveled__gt=0)[:5]:
    print(f'  {i.date_of_inspection} - {i.client_name} - KM:{i.km_traveled} Hours:{i.hours}')

print('\nSample inspections WITHOUT km/hours:')
for i in nov.filter(km_traveled=0)[:5]:
    print(f'  {i.date_of_inspection} - {i.client_name} - Inspector:{i.inspector_name}')
