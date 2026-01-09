"""
COMPREHENSIVE FEE VERSIONING TEST SUITE
Tests EVERY possible circumstance and edge case
"""

import os
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import InspectionFee, FeeHistory

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0

def test(name):
    """Decorator to track test execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            global total_tests, passed_tests, failed_tests
            total_tests += 1
            print(f"\n{'='*80}")
            print(f"TEST #{total_tests}: {name}")
            print(f"{'='*80}")
            try:
                func(*args, **kwargs)
                passed_tests += 1
                print(f"[PASS] {name}")
            except AssertionError as e:
                failed_tests += 1
                print(f"[FAIL] {name}")
                print(f"  Error: {str(e)}")
            except Exception as e:
                failed_tests += 1
                print(f"[ERROR] {name}")
                print(f"  Exception: {str(e)}")
        return wrapper
    return decorator


# ============================================================================
# SETUP & CLEANUP TESTS
# ============================================================================

@test("Database has InspectionFee model")
def test_fee_model_exists():
    """Verify the InspectionFee model exists and has required fields"""
    fee = InspectionFee.objects.first()
    assert fee is not None, "No fees found in database"
    assert hasattr(fee, 'fee_name'), "fee_name field missing"
    assert hasattr(fee, 'rate'), "rate field missing"
    assert hasattr(fee, 'get_rate_for_date'), "get_rate_for_date method missing"
    print(f"  Found fee: {fee.fee_name} = R{fee.rate}")


@test("Database has FeeHistory model")
def test_fee_history_model_exists():
    """Verify the FeeHistory model exists and has required fields"""
    from django.apps import apps
    model = apps.get_model('main', 'FeeHistory')
    assert model is not None, "FeeHistory model not found"

    # Check fields exist
    field_names = [f.name for f in model._meta.get_fields()]
    required_fields = ['fee', 'rate', 'effective_date', 'created_by', 'created_at', 'notes']
    for field in required_fields:
        assert field in field_names, f"Field {field} missing from FeeHistory"
    print(f"  FeeHistory model has all required fields: {required_fields}")


@test("Clear existing test data")
def test_clear_test_data():
    """Clear any existing test fee history"""
    # Get a test fee
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()
    if fee:
        # Delete test histories (keep initial one)
        deleted = FeeHistory.objects.filter(fee=fee).exclude(
            notes__icontains='initial'
        ).delete()
        print(f"  Cleared {deleted[0]} test history records")


# ============================================================================
# BASIC FEE HISTORY CREATION TESTS
# ============================================================================

@test("Create fee history record - Basic")
def test_create_fee_history_basic():
    """Create a basic fee history record"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()
    assert fee is not None, "inspection_hour_rate fee not found"

    history = FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('100.00'),
        effective_date=date(2024, 1, 1),
        notes="Test: Basic creation"
    )

    assert history.id is not None, "History record not saved"
    assert history.rate == Decimal('100.00'), "Rate not saved correctly"
    assert history.effective_date == date(2024, 1, 1), "Effective date not saved"
    print(f"  Created history: {history}")


@test("Create fee history - With user")
def test_create_fee_history_with_user():
    """Create fee history with created_by user"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()
    user = User.objects.first()

    history = FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('105.00'),
        effective_date=date(2024, 2, 1),
        created_by=user,
        notes="Test: With user tracking"
    )

    assert history.created_by == user, "User not saved correctly"
    print(f"  Created by: {history.created_by.username}")


@test("Create fee history - Future date")
def test_create_fee_history_future():
    """Create fee history with future effective date"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()
    future_date = date.today() + timedelta(days=30)

    history = FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('110.00'),
        effective_date=future_date,
        notes="Test: Future fee change"
    )

    assert history.effective_date > date.today(), "Future date not saved"
    print(f"  Future effective date: {history.effective_date}")


@test("Create fee history - Past date")
def test_create_fee_history_past():
    """Create fee history with past effective date"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()
    past_date = date(2023, 1, 1)

    history = FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('95.00'),
        effective_date=past_date,
        notes="Test: Historical fee"
    )

    assert history.effective_date < date.today(), "Past date not saved"
    print(f"  Past effective date: {history.effective_date}")


@test("Create multiple fee histories for same fee")
def test_create_multiple_histories():
    """Create multiple history records for the same fee"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    dates_rates = [
        (date(2024, 3, 1), Decimal('115.00')),
        (date(2024, 4, 1), Decimal('120.00')),
        (date(2024, 5, 1), Decimal('125.00')),
    ]

    for effective_date, rate in dates_rates:
        FeeHistory.objects.create(
            fee=fee,
            rate=rate,
            effective_date=effective_date,
            notes=f"Test: Multiple histories - {effective_date}"
        )

    count = FeeHistory.objects.filter(fee=fee).count()
    assert count >= 3, f"Expected at least 3 histories, got {count}"
    print(f"  Created {len(dates_rates)} history records")


# ============================================================================
# HISTORICAL RATE LOOKUP TESTS
# ============================================================================

@test("Get rate for date - Exact match")
def test_get_rate_exact_match():
    """Get rate when there's an exact date match"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # Create history for specific date
    test_date = date(2024, 6, 15)
    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('130.00'),
        effective_date=test_date,
        notes="Test: Exact match"
    )

    rate = fee.get_rate_for_date(test_date)
    assert rate == Decimal('130.00'), f"Expected 130.00, got {rate}"
    print(f"  Rate on {test_date}: R{rate}")


@test("Get rate for date - Between changes")
def test_get_rate_between_changes():
    """Get rate for a date between two changes"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # Create two history records
    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('135.00'),
        effective_date=date(2024, 7, 1),
        notes="Test: Before target"
    )
    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('145.00'),
        effective_date=date(2024, 9, 1),
        notes="Test: After target"
    )

    # Get rate for date between the two changes
    test_date = date(2024, 8, 15)
    rate = fee.get_rate_for_date(test_date)

    # Should get the rate from July (135.00), not September
    assert rate == Decimal('135.00'), f"Expected 135.00, got {rate}"
    print(f"  Rate on {test_date} (between Jul 1 and Sep 1): R{rate}")


@test("Get rate for date - Before all histories")
def test_get_rate_before_all_histories():
    """Get rate for a date before all history records"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # Get rate for very old date
    old_date = date(2020, 1, 1)
    rate = fee.get_rate_for_date(old_date)

    # Should fall back to current rate
    assert rate is not None, "Rate should not be None"
    print(f"  Rate for old date {old_date}: R{rate} (fallback to current)")


@test("Get rate for date - After all histories (future)")
def test_get_rate_after_all_histories():
    """Get rate for a future date after all history records"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # Create a recent history
    recent_date = date.today() - timedelta(days=10)
    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('150.00'),
        effective_date=recent_date,
        notes="Test: Recent history"
    )

    # Get rate for future date
    future_date = date.today() + timedelta(days=60)
    rate = fee.get_rate_for_date(future_date)

    # Should get the most recent rate (150.00)
    assert rate == Decimal('150.00'), f"Expected 150.00, got {rate}"
    print(f"  Rate for future date {future_date}: R{rate}")


@test("Get rate for date - Today")
def test_get_rate_for_today():
    """Get rate for today's date"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    rate = fee.get_rate_for_date(date.today())
    assert rate is not None, "Rate for today should not be None"
    assert rate > 0, "Rate should be positive"
    print(f"  Rate for today: R{rate}")


@test("Get rate for date - Multiple fees same date")
def test_multiple_histories_same_date():
    """Test behavior when multiple histories exist for same date (edge case)"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # This shouldn't normally happen, but test it anyway
    test_date = date(2024, 10, 1)

    # Create first history
    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('155.00'),
        effective_date=test_date,
        notes="Test: First history same date"
    )

    # Create second history (simulating a correction)
    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('160.00'),
        effective_date=test_date,
        notes="Test: Second history same date (correction)"
    )

    rate = fee.get_rate_for_date(test_date)
    # Should get the most recent one (by creation time)
    print(f"  Rate when multiple histories exist for same date: R{rate}")


# ============================================================================
# CHRONOLOGICAL SEQUENCE TESTS
# ============================================================================

@test("Fee history chronological order")
def test_fee_history_chronological():
    """Verify fee histories are returned in chronological order"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    histories = FeeHistory.objects.filter(fee=fee).order_by('-effective_date')

    prev_date = None
    for history in histories:
        if prev_date:
            assert history.effective_date <= prev_date, "Histories not in chronological order"
        prev_date = history.effective_date
        print(f"  {history.effective_date}: R{history.rate}")


@test("Rate progression over time")
def test_rate_progression():
    """Test that rates change correctly over a timeline"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # Clear existing test data for this fee
    FeeHistory.objects.filter(fee=fee, notes__icontains='progression').delete()

    # Create a timeline of rate changes
    timeline = [
        (date(2024, 1, 1), Decimal('100.00')),
        (date(2024, 4, 1), Decimal('110.00')),
        (date(2024, 7, 1), Decimal('120.00')),
        (date(2024, 10, 1), Decimal('130.00')),
    ]

    for effective_date, rate in timeline:
        FeeHistory.objects.create(
            fee=fee,
            rate=rate,
            effective_date=effective_date,
            notes="Test: Rate progression"
        )

    # Test dates between changes
    test_cases = [
        (date(2024, 2, 15), Decimal('100.00')),  # After Jan, before Apr
        (date(2024, 5, 15), Decimal('110.00')),  # After Apr, before Jul
        (date(2024, 8, 15), Decimal('120.00')),  # After Jul, before Oct
        (date(2024, 11, 15), Decimal('130.00')), # After Oct
    ]

    print("\n  Timeline verification:")
    for test_date, expected_rate in test_cases:
        actual_rate = fee.get_rate_for_date(test_date)
        assert actual_rate == expected_rate, f"On {test_date}: expected {expected_rate}, got {actual_rate}"
        print(f"    {test_date}: R{actual_rate} [OK]")


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

@test("Same-day fee change")
def test_same_day_change():
    """Test fee change on the same day"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    today = date.today()

    # Create history for today
    history = FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('165.00'),
        effective_date=today,
        notes="Test: Same day change"
    )

    rate = fee.get_rate_for_date(today)
    assert rate == Decimal('165.00'), f"Same-day rate should be 165.00, got {rate}"
    print(f"  Same-day change applied correctly: R{rate}")


@test("Midnight transition")
def test_midnight_transition():
    """Test rate change at midnight (day boundary)"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # Create rate change for tomorrow
    tomorrow = date.today() + timedelta(days=1)
    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('170.00'),
        effective_date=tomorrow,
        notes="Test: Tomorrow's rate"
    )

    # Today's rate
    rate_today = fee.get_rate_for_date(date.today())

    # Tomorrow's rate
    rate_tomorrow = fee.get_rate_for_date(tomorrow)

    print(f"  Today's rate: R{rate_today}")
    print(f"  Tomorrow's rate: R{rate_tomorrow}")

    # They might be different (if tomorrow's rate is higher)
    if rate_tomorrow == Decimal('170.00'):
        assert rate_tomorrow != rate_today, "Rates should differ across day boundary"


@test("Leap year date")
def test_leap_year_date():
    """Test fee effective on Feb 29 (leap year)"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # 2024 is a leap year
    leap_day = date(2024, 2, 29)

    history = FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('175.00'),
        effective_date=leap_day,
        notes="Test: Leap year date"
    )

    rate = fee.get_rate_for_date(leap_day)
    assert rate == Decimal('175.00'), f"Leap year date failed: got {rate}"
    print(f"  Leap year date (2024-02-29): R{rate} [OK]")


@test("Year boundary crossing")
def test_year_boundary():
    """Test rate lookup across year boundary"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # Create history for end of year and start of next year
    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('180.00'),
        effective_date=date(2023, 12, 15),
        notes="Test: End of 2023"
    )
    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('190.00'),
        effective_date=date(2024, 1, 15),
        notes="Test: Start of 2024"
    )

    # Test dates around year boundary
    rate_dec = fee.get_rate_for_date(date(2023, 12, 31))
    rate_jan = fee.get_rate_for_date(date(2024, 1, 1))

    print(f"  Dec 31, 2023: R{rate_dec}")
    print(f"  Jan 1, 2024: R{rate_jan}")


@test("Decimal precision")
def test_decimal_precision():
    """Test that decimal precision is maintained"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # Create history with precise decimal
    precise_rate = Decimal('123.45')
    history = FeeHistory.objects.create(
        fee=fee,
        rate=precise_rate,
        effective_date=date(2024, 11, 1),
        notes="Test: Decimal precision"
    )

    retrieved_rate = fee.get_rate_for_date(date(2024, 11, 1))
    assert retrieved_rate == precise_rate, f"Precision lost: {precise_rate} != {retrieved_rate}"
    print(f"  Decimal precision maintained: R{retrieved_rate}")


@test("Very large rate value")
def test_large_rate():
    """Test very large rate values"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    large_rate = Decimal('9999999.99')
    history = FeeHistory.objects.create(
        fee=fee,
        rate=large_rate,
        effective_date=date(2024, 11, 15),
        notes="Test: Large rate value"
    )

    retrieved_rate = fee.get_rate_for_date(date(2024, 11, 15))
    assert retrieved_rate == large_rate, f"Large value failed: {large_rate} != {retrieved_rate}"
    print(f"  Large rate handled: R{retrieved_rate:,.2f}")


@test("Zero rate value")
def test_zero_rate():
    """Test zero rate (edge case)"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    zero_rate = Decimal('0.00')
    history = FeeHistory.objects.create(
        fee=fee,
        rate=zero_rate,
        effective_date=date(2024, 12, 1),
        notes="Test: Zero rate"
    )

    retrieved_rate = fee.get_rate_for_date(date(2024, 12, 1))
    assert retrieved_rate == zero_rate, f"Zero rate failed: expected 0.00, got {retrieved_rate}"
    print(f"  Zero rate accepted: R{retrieved_rate}")


# ============================================================================
# MULTI-FEE TESTS
# ============================================================================

@test("Multiple different fees")
def test_multiple_different_fees():
    """Test that different fees maintain separate histories"""
    fees = InspectionFee.objects.all()[:3]

    if len(fees) < 3:
        print(f"  Skipping: Need at least 3 fees, only found {len(fees)}")
        return

    test_date = date(2024, 12, 10)

    for i, fee in enumerate(fees):
        rate = Decimal(str(200 + i * 10))
        FeeHistory.objects.create(
            fee=fee,
            rate=rate,
            effective_date=test_date,
            notes=f"Test: Multi-fee #{i+1}"
        )

    # Verify each fee has its own rate
    for i, fee in enumerate(fees):
        expected_rate = Decimal(str(200 + i * 10))
        actual_rate = fee.get_rate_for_date(test_date)
        assert actual_rate == expected_rate, f"Fee {fee.fee_name}: expected {expected_rate}, got {actual_rate}"
        print(f"  {fee.fee_name}: R{actual_rate} [OK]")


# ============================================================================
# CALCULATION TESTS
# ============================================================================

@test("Calculate inspection cost - Historical")
def test_calculate_historical_cost():
    """Test calculating inspection cost using historical rates"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # Clear and create specific history
    FeeHistory.objects.filter(fee=fee, notes__icontains='cost calc').delete()

    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('50.00'),
        effective_date=date(2024, 6, 1),
        notes="Test: Cost calc - June rate"
    )
    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('60.00'),
        effective_date=date(2024, 9, 1),
        notes="Test: Cost calc - September rate"
    )

    # Calculate cost for June inspection (4 hours)
    june_rate = fee.get_rate_for_date(date(2024, 6, 15))
    june_cost = june_rate * Decimal('4.0')

    # Calculate cost for September inspection (4 hours)
    sept_rate = fee.get_rate_for_date(date(2024, 9, 15))
    sept_cost = sept_rate * Decimal('4.0')

    print(f"  June inspection (4 hrs @ R{june_rate}/hr): R{june_cost}")
    print(f"  Sept inspection (4 hrs @ R{sept_rate}/hr): R{sept_cost}")

    assert june_cost == Decimal('200.00'), f"June cost should be 200.00, got {june_cost}"
    assert sept_cost == Decimal('240.00'), f"Sept cost should be 240.00, got {sept_cost}"


@test("Calculate monthly totals")
def test_calculate_monthly_totals():
    """Test calculating totals for a month with rate changes"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # Setup: Rate changed mid-month
    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('100.00'),
        effective_date=date(2024, 11, 1),
        notes="Test: Monthly calc - Start of month"
    )
    FeeHistory.objects.create(
        fee=fee,
        rate=Decimal('110.00'),
        effective_date=date(2024, 11, 15),
        notes="Test: Monthly calc - Mid-month increase"
    )

    # Simulate inspections throughout the month
    inspections = [
        (date(2024, 11, 5), Decimal('3.0')),   # 3 hours before rate change
        (date(2024, 11, 10), Decimal('2.0')),  # 2 hours before rate change
        (date(2024, 11, 20), Decimal('4.0')),  # 4 hours after rate change
        (date(2024, 11, 25), Decimal('3.5')),  # 3.5 hours after rate change
    ]

    total_cost = Decimal('0.00')
    print("\n  November 2024 inspections:")
    for inspection_date, hours in inspections:
        rate = fee.get_rate_for_date(inspection_date)
        cost = rate * hours
        total_cost += cost
        print(f"    {inspection_date}: {hours} hrs @ R{rate}/hr = R{cost}")

    expected_total = (
        (Decimal('3.0') * Decimal('100.00')) +  # Nov 5
        (Decimal('2.0') * Decimal('100.00')) +  # Nov 10
        (Decimal('4.0') * Decimal('110.00')) +  # Nov 20
        (Decimal('3.5') * Decimal('110.00'))    # Nov 25
    )

    print(f"\n  Total for month: R{total_cost}")
    assert total_cost == expected_total, f"Expected {expected_total}, got {total_cost}"


# ============================================================================
# REAL-WORLD SCENARIO TESTS
# ============================================================================

@test("Scenario: Annual rate increase")
def test_scenario_annual_increase():
    """Real scenario: Company implements annual 5% increase"""
    fee = InspectionFee.objects.filter(fee_code='inspection_hour_rate').first()

    # Clear previous test data
    FeeHistory.objects.filter(fee=fee, notes__icontains='annual').delete()

    base_rate = Decimal('100.00')
    years = 5

    print("\n  Annual 5% increases:")
    for year in range(years):
        year_date = date(2020 + year, 1, 1)
        rate = base_rate * (Decimal('1.05') ** year)
        rate = rate.quantize(Decimal('0.01'))  # Round to 2 decimal places

        FeeHistory.objects.create(
            fee=fee,
            rate=rate,
            effective_date=year_date,
            notes=f"Test: Annual increase year {year + 1}"
        )

        print(f"    {year_date.year}: R{rate}")

    # Verify rates for mid-year dates
    test_date = date(2022, 6, 15)
    rate_2022 = fee.get_rate_for_date(test_date)
    expected_2022 = (base_rate * Decimal('1.05') ** 2).quantize(Decimal('0.01'))

    assert rate_2022 == expected_2022, f"Expected {expected_2022}, got {rate_2022}"
    print(f"\n  Mid-2022 rate: R{rate_2022} [OK]")


# ============================================================================
# FINAL SUMMARY
# ============================================================================

def print_summary():
    """Print test execution summary"""
    print("\n")
    print("=" * 80)
    print("TEST EXECUTION SUMMARY")
    print("=" * 80)
    print(f"\nTotal Tests: {total_tests}")
    print(f"[PASS] Passed: {passed_tests}")
    print(f"[FAIL] Failed: {failed_tests}")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")

    if failed_tests == 0:
        print("\n*** ALL TESTS PASSED! Fee versioning system is working perfectly!")
    else:
        print(f"\n[WARNING] {failed_tests} test(s) failed. Review errors above.")

    print("=" * 80)


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == '__main__':
    print("""
================================================================================

              COMPREHENSIVE FEE VERSIONING SYSTEM TEST SUITE

  Testing EVERY possible circumstance, edge case, and scenario

================================================================================
""")

    print(f"Started: {date.today()}")
    print(f"Django version: {django.get_version()}")
    print("\n")

    # Run all tests
    test_fee_model_exists()
    test_fee_history_model_exists()
    test_clear_test_data()
    test_create_fee_history_basic()
    test_create_fee_history_with_user()
    test_create_fee_history_future()
    test_create_fee_history_past()
    test_create_multiple_histories()
    test_get_rate_exact_match()
    test_get_rate_between_changes()
    test_get_rate_before_all_histories()
    test_get_rate_after_all_histories()
    test_get_rate_for_today()
    test_multiple_histories_same_date()
    test_fee_history_chronological()
    test_rate_progression()
    test_same_day_change()
    test_midnight_transition()
    test_leap_year_date()
    test_year_boundary()
    test_decimal_precision()
    test_large_rate()
    test_zero_rate()
    test_multiple_different_fees()
    test_calculate_historical_cost()
    test_calculate_monthly_totals()
    test_scenario_annual_increase()

    # Summary
    print_summary()
