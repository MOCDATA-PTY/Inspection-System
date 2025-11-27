#!/usr/bin/env python3
"""
Compare Nelisa's Inspections
==============================
Compares Nov 11 vs Nov 26 inspections to find what's different.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import date


def compare_inspections():
    """Compare Nelisa's inspections from different dates."""

    print(f"\n{'='*80}")
    print(f"COMPARING NELISA'S INSPECTIONS")
    print(f"{'='*80}\n")

    # Get Nov 11 inspections
    nov_11 = FoodSafetyAgencyInspection.objects.filter(
        inspector_name__icontains='Nelisa',
        date_of_inspection=date(2025, 11, 11)
    )

    # Get Nov 26 inspections
    nov_26 = FoodSafetyAgencyInspection.objects.filter(
        inspector_name__icontains='Nelisa',
        date_of_inspection=date(2025, 11, 26)
    )

    print(f"Nov 11 inspections: {nov_11.count()}")
    print(f"Nov 26 inspections: {nov_26.count()}")
    print()

    # Compare first inspection from each date
    if nov_11.exists() and nov_26.exists():
        print("="*80)
        print("DETAILED COMPARISON - First inspection from each date")
        print("="*80)

        sample_11 = nov_11.first()
        sample_26 = nov_26.first()

        fields_to_check = [
            'client_name', 'commodity', 'product_name', 'product_class',
            'hours', 'km_traveled', 'fat', 'protein', 'calcium', 'dna',
            'bought_sample', 'sent_by', 'rfi_uploaded_by', 'invoice_uploaded_by',
            'created_at', 'updated_at', 'compliance_status', 'shipment_id'
        ]

        print(f"\n{'Field':<30} {'Nov 11':<30} {'Nov 26':<30}")
        print("-"*80)

        for field in fields_to_check:
            try:
                val_11 = getattr(sample_11, field, 'N/A')
                val_26 = getattr(sample_26, field, 'N/A')

                # Convert to string for display
                val_11_str = str(val_11)[:28] if val_11 is not None else 'None'
                val_26_str = str(val_26)[:28] if val_26 is not None else 'None'

                # Mark if different
                marker = " <-- DIFFERENT" if val_11 != val_26 else ""

                print(f"{field:<30} {val_11_str:<30} {val_26_str:<30}{marker}")
            except Exception as e:
                print(f"{field:<30} ERROR: {e}")

        # Check all Nov 26 inspections for common patterns
        print(f"\n\n{'='*80}")
        print(f"ALL NOV 26 INSPECTIONS - Field Analysis")
        print(f"{'='*80}\n")

        print("Checking which fields are filled:")

        nov_26_all = list(nov_26)

        # Count fields
        has_hours = sum(1 for i in nov_26_all if i.hours is not None)
        has_km = sum(1 for i in nov_26_all if i.km_traveled is not None)
        has_sent_by = sum(1 for i in nov_26_all if i.sent_by is not None)
        has_rfi = sum(1 for i in nov_26_all if i.rfi_uploaded_by is not None)
        has_invoice = sum(1 for i in nov_26_all if i.invoice_uploaded_by is not None)
        has_compliance = sum(1 for i in nov_26_all if getattr(i, 'compliance_status', None))
        has_shipment = sum(1 for i in nov_26_all if i.shipment_id is not None)

        total = len(nov_26_all)
        print(f"Hours filled: {has_hours}/{total}")
        print(f"KM traveled filled: {has_km}/{total}")
        print(f"Sent by filled: {has_sent_by}/{total}")
        print(f"RFI uploaded by: {has_rfi}/{total}")
        print(f"Invoice uploaded by: {has_invoice}/{total}")
        print(f"Compliance status: {has_compliance}/{total}")
        print(f"Shipment ID: {has_shipment}/{total}")

        # Show all Nov 26 inspections
        print(f"\n\nAll Nov 26 inspections details:")
        for i, insp in enumerate(nov_26_all, 1):
            print(f"\n{i}. {insp.client_name} - {insp.commodity}")
            print(f"   Product: {insp.product_name}")
            print(f"   Hours: {insp.hours}, KM: {insp.km_traveled}")
            print(f"   Sent by: {insp.sent_by}")
            print(f"   Created: {insp.created_at}")
            print(f"   Shipment ID: {insp.shipment_id}")

        # Compare with Nov 11 stats
        print(f"\n\n{'='*80}")
        print(f"NOV 11 INSPECTIONS - Field Analysis")
        print(f"{'='*80}\n")

        nov_11_all = list(nov_11)

        has_hours_11 = sum(1 for i in nov_11_all if i.hours is not None)
        has_km_11 = sum(1 for i in nov_11_all if i.km_traveled is not None)
        has_sent_by_11 = sum(1 for i in nov_11_all if i.sent_by is not None)
        has_shipment_11 = sum(1 for i in nov_11_all if i.shipment_id is not None)

        total_11 = len(nov_11_all)
        print(f"Hours filled: {has_hours_11}/{total_11}")
        print(f"KM traveled filled: {has_km_11}/{total_11}")
        print(f"Sent by filled: {has_sent_by_11}/{total_11}")
        print(f"Shipment ID: {has_shipment_11}/{total_11}")

    print(f"\n{'='*80}")
    print(f"CONCLUSION")
    print(f"{'='*80}")
    print("\nLikely cause: Check if the dashboard filters by:")
    print("  - sent_by field (if Nov 26 inspections don't have this)")
    print("  - shipment_id (if they're not linked to a shipment)")
    print("  - hours/km_traveled (if they're not filled in)")
    print("  - Some other required field")
    print()


if __name__ == '__main__':
    compare_inspections()
