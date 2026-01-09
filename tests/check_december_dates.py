import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from collections import Counter

dates = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__year=2025,
    date_of_inspection__month=12
).values_list('date_of_inspection', flat=True)

date_counts = Counter([str(d) for d in dates])

print('December 2025 inspection dates (all):')
for date in sorted(date_counts.keys(), reverse=True):
    print(f'{date}: {date_counts[date]} inspections')
