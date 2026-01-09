#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for the Fee Versioning System

This script demonstrates how to:
1. Create fee history records
2. Query historical rates
3. Use time-based fee lookups

Run this script with:
    python test_fee_versioning.py
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import InspectionFee, FeeHistory, User


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_fee_versioning():
    """Test the fee versioning functionality"""

    print_header("Fee Versioning System Test")

    # Get or create a test fee
    fee, created = InspectionFee.objects.get_or_create(
        fee_code='test_sample_rate',
        defaults={
            'fee_name': 'Test Sample Rate',
            'rate': Decimal('100.00'),
            'description': 'Test fee for versioning system'
        }
    )

    if created:
        print(f"\n✓ Created test fee: {fee.fee_name}")
    else:
        print(f"\n✓ Using existing fee: {fee.fee_name}")

    print(f"  Current rate: R{fee.rate}")

    # Get admin user for creating history (or use None)
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
    except:
        admin_user = None

    # Test 1: Create some historical fee records
    print_header("Test 1: Creating Fee History")

    # Delete existing test history to start fresh
    FeeHistory.objects.filter(fee=fee).delete()
    print("\n✓ Cleared existing history")

    # Create fee history for different dates
    history_data = [
        (date(2023, 1, 1), Decimal('80.00'), "Initial rate for 2023"),
        (date(2023, 7, 1), Decimal('85.00'), "Mid-year adjustment"),
        (date(2024, 1, 1), Decimal('90.00'), "Annual increase for 2024"),
        (date(2024, 6, 1), Decimal('95.00'), "Mid-year increase"),
        (date(2025, 1, 1), Decimal('100.00'), "Annual increase for 2025"),
    ]

    for effective_date, rate, notes in history_data:
        FeeHistory.objects.create(
            fee=fee,
            rate=rate,
            effective_date=effective_date,
            created_by=admin_user,
            notes=notes
        )
        print(f"✓ Created history: {effective_date} → R{rate} ({notes})")

    # Update current rate to latest
    fee.rate = Decimal('100.00')
    fee.save()

    # Test 2: Query fee history
    print_header("Test 2: Viewing Fee History")

    all_history = fee.history.all().order_by('effective_date')
    print(f"\n✓ Total history records: {all_history.count()}")
    print("\nFee History Timeline:")
    print("-" * 80)

    for record in all_history:
        print(f"  {record.effective_date}  │  R{record.rate:>8.2f}  │  {record.notes}")

    # Test 3: Time-based fee lookups
    print_header("Test 3: Time-Based Fee Lookups")

    test_dates = [
        date(2022, 12, 31),  # Before any history
        date(2023, 3, 15),   # Q1 2023
        date(2023, 9, 1),    # After July increase
        date(2024, 3, 1),    # Q1 2024
        date(2024, 8, 15),   # After June increase
        date(2025, 6, 1),    # Mid 2025
    ]

    print("\nLooking up rates for different dates:")
    print("-" * 80)
    print(f"{'Date':<15} │ {'Rate':<10} │ Description")
    print("-" * 80)

    for test_date in test_dates:
        rate = fee.get_rate_for_date(test_date)
        print(f"{test_date} │ R{rate:>8.2f} │ Rate active on this date")

    # Test 4: Simulate inspection cost calculations
    print_header("Test 4: Historical Inspection Cost Calculation")

    # Simulate some inspections at different dates
    inspections = [
        {'date': date(2023, 2, 15), 'quantity': 5, 'description': 'Early 2023 inspection'},
        {'date': date(2023, 8, 20), 'quantity': 3, 'description': 'After mid-year increase'},
        {'date': date(2024, 3, 10), 'quantity': 4, 'description': 'Q1 2024 inspection'},
        {'date': date(2024, 11, 5), 'quantity': 6, 'description': 'Late 2024 inspection'},
        {'date': date(2025, 3, 1), 'quantity': 2, 'description': 'Early 2025 inspection'},
    ]

    print("\nCalculating costs using historical rates:")
    print("-" * 80)
    print(f"{'Date':<12} │ {'Qty':<4} │ {'Rate':<10} │ {'Total':<10} │ Description")
    print("-" * 80)

    total_cost = Decimal('0.00')
    for inspection in inspections:
        rate = fee.get_rate_for_date(inspection['date'])
        cost = rate * inspection['quantity']
        total_cost += cost
        print(f"{inspection['date']} │ {inspection['quantity']:<4} │ R{rate:>8.2f} │ R{cost:>8.2f} │ {inspection['description']}")

    print("-" * 80)
    print(f"{'TOTAL':<12} │ {'':4} │ {'':10} │ R{total_cost:>8.2f} │")
    print("-" * 80)

    # Test 5: Future fee changes
    print_header("Test 5: Pre-Scheduling Future Fee Changes")

    future_date = date.today() + timedelta(days=90)
    future_rate = Decimal('110.00')

    # Check if future record already exists
    future_exists = FeeHistory.objects.filter(
        fee=fee,
        effective_date=future_date
    ).exists()

    if not future_exists:
        FeeHistory.objects.create(
            fee=fee,
            rate=future_rate,
            effective_date=future_date,
            created_by=admin_user,
            notes="Scheduled rate increase for next quarter"
        )
        print(f"\n✓ Created future fee change:")
        print(f"  Effective Date: {future_date}")
        print(f"  New Rate: R{future_rate}")
        print(f"  Days until effective: {(future_date - date.today()).days}")
    else:
        print(f"\n✓ Future fee change already exists for {future_date}")

    # Show what rate would be used for dates before and after the future change
    print("\n  Rate lookups around the future change:")
    test_date_before = future_date - timedelta(days=1)
    test_date_after = future_date + timedelta(days=1)

    rate_before = fee.get_rate_for_date(test_date_before)
    rate_after = fee.get_rate_for_date(test_date_after)

    print(f"    {test_date_before} (before): R{rate_before}")
    print(f"    {future_date} (effective):   R{future_rate}")
    print(f"    {test_date_after} (after):  R{rate_after}")

    # Summary
    print_header("Test Summary")

    total_versions = fee.history.count()
    earliest = fee.history.order_by('effective_date').first()
    latest = fee.history.order_by('-effective_date').first()

    print(f"\n✓ Fee: {fee.fee_name}")
    print(f"✓ Current Rate: R{fee.rate}")
    print(f"✓ Total Versions: {total_versions}")
    print(f"✓ Earliest Record: {earliest.effective_date if earliest else 'None'} (R{earliest.rate if earliest else 0})")
    print(f"✓ Latest Record: {latest.effective_date if latest else 'None'} (R{latest.rate if latest else 0})")
    print(f"\n✓ All tests completed successfully!")
    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    try:
        test_fee_versioning()
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
