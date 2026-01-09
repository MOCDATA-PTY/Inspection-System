#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for commodity type mismatches between facility registration and inspections
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()

from main.models import FoodSafetyAgencyInspection, Client
from django.db.models import Q


def test_commodity_mismatches():
    """Find facilities where account code doesn't match inspection commodity"""

    print(f"\n{'='*100}")
    print(f"COMMODITY MISMATCH DETECTION TEST")
    print(f"{'='*100}\n")

    # Get all clients with account codes
    clients = Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code='')

    print(f"Total clients with account codes: {clients.count()}\n")

    mismatches = []

    # Check each client
    for client in clients:
        account_code = client.internal_account_code or ''

        # Determine expected commodity from account code
        expected_commodity = None
        if 'RAW' in account_code.upper():
            expected_commodity = 'RAW'
        elif 'PMP' in account_code.upper() or 'PROCESSED' in account_code.upper():
            expected_commodity = 'PMP'
        elif 'POULTRY' in account_code.upper() or 'PTY' in account_code.upper():
            expected_commodity = 'POULTRY'
        elif 'EGG' in account_code.upper():
            expected_commodity = 'EGGS'

        if not expected_commodity:
            continue

        # Get inspections for this client
        inspections = FoodSafetyAgencyInspection.objects.filter(
            Q(client_name__iexact=client.name) |
            Q(internal_account_code=client.internal_account_code)
        )

        if not inspections.exists():
            continue

        # Check for mismatches
        actual_commodities = set(inspections.values_list('commodity', flat=True))

        # Remove None values
        actual_commodities = {c for c in actual_commodities if c}

        # If there are commodities that don't match expected
        wrong_commodities = actual_commodities - {expected_commodity}

        if wrong_commodities:
            mismatches.append({
                'client': client.name,
                'account_code': account_code,
                'expected': expected_commodity,
                'actual': list(actual_commodities),
                'wrong': list(wrong_commodities),
                'count': inspections.count()
            })

    # Report results
    print(f"{'='*100}")
    print(f"MISMATCH RESULTS")
    print(f"{'='*100}\n")

    if mismatches:
        print(f"Found {len(mismatches)} facilities with commodity mismatches:\n")

        for idx, mismatch in enumerate(mismatches, 1):
            print(f"{idx}. {mismatch['client']}")
            print(f"   Account Code: {mismatch['account_code']}")
            print(f"   Expected Commodity: {mismatch['expected']}")
            print(f"   Actual Commodities: {', '.join(mismatch['actual'])}")
            print(f"   Wrong Commodities: {', '.join(mismatch['wrong'])}")
            print(f"   Total Inspections: {mismatch['count']}")
            print()

        # Specific check for Festive
        festive = [m for m in mismatches if 'festive' in m['client'].lower()]
        if festive:
            print(f"{'='*100}")
            print(f"FESTIVE ANALYSIS")
            print(f"{'='*100}\n")
            for f in festive:
                print(f"Festive is registered as: {f['expected']} (based on {f['account_code']})")
                print(f"But inspected as: {', '.join(f['actual'])}")
                print(f"\nThis means:")
                if f['expected'] == 'RAW' and 'POULTRY' in f['actual']:
                    print("  - Festive account code says RAW meat facility")
                    print("  - But inspections are for POULTRY")
                    print("  - Either:")
                    print("    1. Account code is wrong (should be POULTRY)")
                    print("    2. Inspections are being assigned to wrong facility")
                    print("    3. Facility changed commodity type")
    else:
        print("No mismatches found - all facilities match their registered commodity type")

    print(f"\n{'='*100}\n")

    return mismatches


def analyze_festive_specifically():
    """Deep dive into Festive facility"""

    print(f"\n{'='*100}")
    print(f"FESTIVE FACILITY DEEP DIVE")
    print(f"{'='*100}\n")

    # Get Festive client
    festive_clients = Client.objects.filter(name__icontains='Festive')

    print(f"Found {festive_clients.count()} Festive client records:\n")

    for client in festive_clients:
        print(f"Client: {client.name}")
        print(f"Account Code: {client.internal_account_code}")

        # Parse account code
        account_code = client.internal_account_code or ''
        parts = account_code.split('-')
        if len(parts) >= 3:
            print(f"  Facility Type: {parts[0]} ({parts[0]} = Abattoir)")
            print(f"  Industry: {parts[1]}")
            print(f"  Commodity: {parts[2]} ({'RAW meat' if parts[2] == 'RAW' else parts[2]})")

        # Get inspections
        inspections = FoodSafetyAgencyInspection.objects.filter(
            Q(client_name__iexact=client.name) |
            Q(internal_account_code=client.internal_account_code)
        )

        print(f"\nInspections: {inspections.count()}")
        if inspections.exists():
            commodities = inspections.values('commodity').annotate(count=Count('id'))
            from django.db.models import Count
            commodities = inspections.values('commodity').annotate(count=Count('id'))

            for comm in commodities:
                print(f"  {comm['commodity']}: {comm['count']} inspections")

        print()


if __name__ == "__main__":
    print("\n" + "="*100)
    print("COMMODITY MISMATCH TEST")
    print("="*100)

    try:
        # Run general mismatch test
        mismatches = test_commodity_mismatches()

        # Run Festive-specific analysis
        analyze_festive_specifically()

        if mismatches:
            print(f"\nAction needed: Review {len(mismatches)} facilities with commodity mismatches")
        else:
            print(f"\nAll facilities pass commodity validation")

        sys.exit(0)

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
