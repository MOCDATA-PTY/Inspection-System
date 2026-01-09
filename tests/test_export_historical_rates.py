"""
Test that export functionality uses historical fee rates correctly
"""
import os
import django
from datetime import date, datetime
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import InspectionFee, FeeHistory, FoodSafetyAgencyInspection
from main.views.core_views import get_fee_rate, generate_visit_hours_km_items


def test_export_uses_historical_rates():
    """
    Scenario: Fee changed mid-November
    - Nov 1-14: Inspection hour rate = R400/hour, Travel = R5/km
    - Nov 15+: Inspection hour rate = R510/hour, Travel = R6.50/km

    Test that exports use correct historical rates for each inspection date
    """

    print("\n" + "="*80)
    print("TESTING: Export Uses Historical Fee Rates")
    print("="*80)

    # Step 1: Get or create fees
    hour_fee, _ = InspectionFee.objects.get_or_create(
        fee_code='inspection_hour_rate',
        defaults={
            'fee_name': 'Inspection Hour Rate (Normal Time 08:00-16:00)',
            'rate': Decimal('510.00')
        }
    )

    km_fee, _ = InspectionFee.objects.get_or_create(
        fee_code='travel_rate_per_km',
        defaults={
            'fee_name': 'Travel Rate per KM',
            'rate': Decimal('6.50')
        }
    )

    print(f"\nCurrent Fees:")
    print(f"  Hour Rate: R{hour_fee.rate}")
    print(f"  KM Rate: R{km_fee.rate}")

    # Step 2: Clear any existing test history for these fees
    # Use unique November dates to avoid conflicts with October data
    test_dates = [date(2024, 11, 1), date(2024, 11, 15)]
    FeeHistory.objects.filter(
        fee__in=[hour_fee, km_fee],
        effective_date__in=test_dates
    ).delete()

    # Step 3: Create historical rates for November scenario (using Nov to avoid conflicts)
    print(f"\nCreating historical rates:")

    # Old rates (Nov 1-14)
    old_hour_history, _ = FeeHistory.objects.get_or_create(
        fee=hour_fee,
        effective_date=date(2024, 11, 1),
        defaults={
            'rate': Decimal('400.00'),
            'notes': 'Export Test: Old rate before mid-month change'
        }
    )
    print(f"  Nov 1-14: Hour = R{old_hour_history.rate}, KM = R5.00")

    old_km_history, _ = FeeHistory.objects.get_or_create(
        fee=km_fee,
        effective_date=date(2024, 11, 1),
        defaults={
            'rate': Decimal('5.00'),
            'notes': 'Export Test: Old rate before mid-month change'
        }
    )

    # New rates (Nov 15+)
    new_hour_history, _ = FeeHistory.objects.get_or_create(
        fee=hour_fee,
        effective_date=date(2024, 11, 15),
        defaults={
            'rate': Decimal('510.00'),
            'notes': 'Export Test: New rate after mid-month change'
        }
    )
    print(f"  Nov 15+: Hour = R{new_hour_history.rate}, KM = R{km_fee.rate}")

    new_km_history, _ = FeeHistory.objects.get_or_create(
        fee=km_fee,
        effective_date=date(2024, 11, 15),
        defaults={
            'rate': Decimal('6.50'),
            'notes': 'Export Test: New rate after mid-month change'
        }
    )

    # Step 4: Test get_fee_rate() function with different dates
    print(f"\n" + "="*80)
    print("TEST 1: get_fee_rate() returns correct historical rates")
    print("="*80)

    # Test Nov 5 (before change)
    nov_5_hour_rate = get_fee_rate('inspection_hour_rate', 510.00, date(2024, 11, 5))
    nov_5_km_rate = get_fee_rate('travel_rate_per_km', 6.50, date(2024, 11, 5))

    print(f"\nNov 5, 2024 (BEFORE change):")
    print(f"  Hour rate: R{nov_5_hour_rate} (expected R400.00)")
    print(f"  KM rate: R{nov_5_km_rate} (expected R5.00)")

    assert nov_5_hour_rate == 400.00, f"Nov 5 hour rate should be 400.00, got {nov_5_hour_rate}"
    assert nov_5_km_rate == 5.00, f"Nov 5 km rate should be 5.00, got {nov_5_km_rate}"
    print("  [PASS] Correct rates for Nov 5")

    # Test Nov 20 (after change)
    nov_20_hour_rate = get_fee_rate('inspection_hour_rate', 510.00, date(2024, 11, 20))
    nov_20_km_rate = get_fee_rate('travel_rate_per_km', 6.50, date(2024, 11, 20))

    print(f"\nNov 20, 2024 (AFTER change):")
    print(f"  Hour rate: R{nov_20_hour_rate} (expected R510.00)")
    print(f"  KM rate: R{nov_20_km_rate} (expected R6.50)")

    assert nov_20_hour_rate == 510.00, f"Nov 20 hour rate should be 510.00, got {nov_20_hour_rate}"
    assert nov_20_km_rate == 6.50, f"Nov 20 km rate should be 6.50, got {nov_20_km_rate}"
    print("  [PASS] Correct rates for Nov 20")

    # Step 5: Create mock inspections to test export generation
    print(f"\n" + "="*80)
    print("TEST 2: Export line items use correct historical rates")
    print("="*80)

    # Create a test user
    test_user, _ = User.objects.get_or_create(
        username='test_inspector_export',
        defaults={'first_name': 'Test', 'last_name': 'Inspector'}
    )

    # Create mock inspection for Nov 5 (before change)
    print("\nCreating mock inspection for Nov 5 (before change)...")

    class MockInspection:
        """Mock inspection object for testing"""
        def __init__(self, date_val, hours_val, km_val):
            self.id = 1
            self.date_of_inspection = date_val
            self.inspector_name = 'Test Inspector'
            self.client_name = 'Test Client Ltd'
            self.product_name = 'Test Product'
            self.product_class = 'A'
            self.commodity = 'PMP'
            self.hours = hours_val
            self.km_traveled = km_val
            self.invoice_number = 'TEST-001'

    # Test Nov 5 inspection (3 hours, 50 km)
    nov_5_inspection = MockInspection(date(2024, 11, 5), 3.0, 50.0)
    nov_5_items = generate_visit_hours_km_items(
        inspection_id=1,
        inspection=nov_5_inspection,
        invoice_ref='TEST-001',
        rfi_ref='TEST-RFI-001',
        product_type='PMP',
        city='Johannesburg',
        lab_name='Test Lab',
        total_hours=3.0,
        total_km=50.0
    )

    print(f"\nNov 5 Inspection (3 hours, 50 km) - BEFORE rate change:")
    for item in nov_5_items:
        if 'hours' in item['description'].lower():
            print(f"  Hours: {item['quantity']} x R{item['unit_amount']} = R{item['total']}")
            print(f"    Expected: 3 x R400.00 = R1200.00")
            assert item['unit_amount'] == 400.00, f"Hour rate should be 400.00, got {item['unit_amount']}"
            assert item['total'] == 1200.00, f"Hour total should be 1200.00, got {item['total']}"
        elif 'km' in item['description'].lower() or 'travel' in item['description'].lower():
            print(f"  KM: {item['quantity']} x R{item['unit_amount']} = R{item['total']}")
            print(f"    Expected: 50 x R5.00 = R250.00")
            assert item['unit_amount'] == 5.00, f"KM rate should be 5.00, got {item['unit_amount']}"
            assert item['total'] == 250.00, f"KM total should be 250.00, got {item['total']}"

    print("  [PASS] Nov 5 inspection uses old rates correctly")

    # Test Nov 20 inspection (3 hours, 50 km)
    nov_20_inspection = MockInspection(date(2024, 11, 20), 3.0, 50.0)
    nov_20_items = generate_visit_hours_km_items(
        inspection_id=2,
        inspection=nov_20_inspection,
        invoice_ref='TEST-002',
        rfi_ref='TEST-RFI-002',
        product_type='PMP',
        city='Johannesburg',
        lab_name='Test Lab',
        total_hours=3.0,
        total_km=50.0
    )

    print(f"\nNov 20 Inspection (3 hours, 50 km) - AFTER rate change:")
    for item in nov_20_items:
        if 'hours' in item['description'].lower():
            print(f"  Hours: {item['quantity']} x R{item['unit_amount']} = R{item['total']}")
            print(f"    Expected: 3 x R510.00 = R1530.00")
            assert item['unit_amount'] == 510.00, f"Hour rate should be 510.00, got {item['unit_amount']}"
            assert item['total'] == 1530.00, f"Hour total should be 1530.00, got {item['total']}"
        elif 'km' in item['description'].lower() or 'travel' in item['description'].lower():
            print(f"  KM: {item['quantity']} x R{item['unit_amount']} = R{item['total']}")
            print(f"    Expected: 50 x R6.50 = R325.00")
            assert item['unit_amount'] == 6.50, f"KM rate should be 6.50, got {item['unit_amount']}"
            assert item['total'] == 325.00, f"KM total should be 325.00, got {item['total']}"

    print("  [PASS] Nov 20 inspection uses new rates correctly")

    # Summary
    print(f"\n" + "="*80)
    print("SUMMARY: Cost Comparison")
    print("="*80)
    print(f"\nSame inspection (3 hours, 50 km) on different dates:")
    print(f"  Nov 5 (old rates): R1200 + R250 = R1450.00")
    print(f"  Nov 20 (new rates): R1530 + R325 = R1855.00")
    print(f"  Difference: R405.00 (28% increase)")

    print(f"\n" + "="*80)
    print("[SUCCESS] All tests passed!")
    print("Export functionality correctly uses historical fee rates!")
    print("="*80)

    # Cleanup
    print(f"\nCleaning up test data...")
    FeeHistory.objects.filter(
        fee__in=[hour_fee, km_fee],
        effective_date__in=test_dates
    ).delete()
    User.objects.filter(username='test_inspector_export').delete()
    print("Cleanup complete.")


if __name__ == '__main__':
    test_export_uses_historical_rates()
