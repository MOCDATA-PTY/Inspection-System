"""
Test that export uses correct historical rates
"""
import os
import sys
import django
from datetime import date

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, InspectionFee
from main.views.core_views import get_fee_rate

print('\n' + '='*60)
print(' TESTING EXPORT RATE CALCULATION')
print('='*60)

# Get some December inspections to test with
december_inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__year=2025,
    date_of_inspection__month=12,
    commodity__in=['RAW', 'PMP']
)[:5]

print(f'\nTesting with {december_inspections.count()} December 2025 inspections:')
print('-' * 60)

for inspection in december_inspections:
    # Simulate what the export code does
    calcium_rate = get_fee_rate('calcium_test_rate', 379.00, inspection.date_of_inspection)
    hour_rate = get_fee_rate('inspection_hour_rate', 510.00, inspection.date_of_inspection)
    travel_rate = get_fee_rate('travel_rate_per_km', 6.50, inspection.date_of_inspection)

    print(f'\nInspection on {inspection.date_of_inspection}:')
    print(f'  Client: {inspection.client_name}')
    print(f'  Calcium Test Rate: R{calcium_rate}')
    print(f'  Inspection Hour Rate: R{hour_rate}')
    print(f'  Travel Rate: R{travel_rate}/km')

# Now test with hypothetical July inspection
print('\n' + '='*60)
print(' SIMULATING JULY 2025 INSPECTION')
print('='*60)

july_date = date(2025, 7, 15)
calcium_rate_july = get_fee_rate('calcium_test_rate', 379.00, july_date)
hour_rate_july = get_fee_rate('inspection_hour_rate', 510.00, july_date)

print(f'\nInspection on {july_date}:')
print(f'  Calcium Test Rate: R{calcium_rate_july}')
print(f'  Inspection Hour Rate: R{hour_rate_july}')

# Test with November
print('\n' + '='*60)
print(' SIMULATING NOVEMBER 2025 INSPECTION')
print('='*60)

nov_date = date(2025, 11, 15)
calcium_rate_nov = get_fee_rate('calcium_test_rate', 379.00, nov_date)
hour_rate_nov = get_fee_rate('inspection_hour_rate', 510.00, nov_date)

print(f'\nInspection on {nov_date}:')
print(f'  Calcium Test Rate: R{calcium_rate_nov}')
print(f'  Inspection Hour Rate: R{hour_rate_nov}')

print('\n' + '='*60)
print(' SUMMARY')
print('='*60)

print(f'\nExpected rates:')
print(f'  July-November 2025: Calcium = R5000')
print(f'  December 2025: Calcium = R4000')
print(f'\nActual rates from simulation:')
print(f'  July 2025: Calcium = R{calcium_rate_july}')
print(f'  November 2025: Calcium = R{calcium_rate_nov}')
print(f'  December 2025: Calcium = R{calcium_rate}')

if calcium_rate_july == 5000 and calcium_rate_nov == 5000 and calcium_rate == 4000:
    print('\n[SUCCESS] Historical rates are working correctly!')
    print('\nYou can now:')
    print('1. Go to Export Sheet page')
    print('2. Export December 2025 data and verify Calcium tests show R4000')
    print('3. If you have July-November inspections, they would show R5000')
else:
    print('\n[WARNING] Rates do not match expected values!')

print('\n' + '='*60)
