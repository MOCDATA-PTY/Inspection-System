#!/usr/bin/env python3
"""
Find Latest Inspection by Inspector
=====================================
Finds the most recent inspection by a specific inspector.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Q


def find_latest_inspection(inspector_name_search):
    """Find the latest inspection by inspector name (partial match)."""

    print(f"\n{'='*80}")
    print(f"SEARCHING FOR INSPECTOR: {inspector_name_search}")
    print(f"{'='*80}\n")

    # Search for inspector (case insensitive, partial match)
    inspections = FoodSafetyAgencyInspection.objects.filter(
        Q(inspector_name__icontains=inspector_name_search)
    ).order_by('-date_of_inspection', '-created_at')

    total_count = inspections.count()

    if total_count == 0:
        print(f"[NOT FOUND] No inspections found for inspector: {inspector_name_search}")
        print("\nTrying to find similar inspector names...")

        # Show all unique inspector names
        all_inspectors = FoodSafetyAgencyInspection.objects.values_list(
            'inspector_name', flat=True
        ).distinct().order_by('inspector_name')

        print("\nAll inspectors in database:")
        for name in all_inspectors:
            if name:
                print(f"  - {name}")

        return None

    print(f"[FOUND] {total_count} inspection(s) by {inspector_name_search}")
    print()

    # Get the latest inspection
    latest = inspections.first()

    print(f"{'='*80}")
    print(f"LATEST INSPECTION")
    print(f"{'='*80}")
    print(f"Inspector Name: {latest.inspector_name}")
    print(f"Client Name: {latest.client_name}")
    print(f"Date of Inspection: {latest.date_of_inspection}")
    print(f"Commodity: {latest.commodity or 'N/A'}")
    print(f"Product Name: {latest.product_name or 'N/A'}")
    print(f"Product Class: {latest.product_class or 'N/A'}")
    print(f"Created At: {latest.created_at}")
    print()

    # Show compliance/file status
    print(f"Status:")
    print(f"  - Hours: {latest.hours or 'N/A'}")
    print(f"  - KM Traveled: {latest.km_traveled or 'N/A'}")
    print(f"  - Lab Tests: Fat={latest.fat}, Protein={latest.protein}, Calcium={latest.calcium}, DNA={latest.dna}")
    print()

    # Show recent 5 inspections
    if total_count > 1:
        print(f"{'='*80}")
        print(f"RECENT INSPECTIONS (Last 5)")
        print(f"{'='*80}")

        for i, inspection in enumerate(inspections[:5], 1):
            print(f"\n{i}. {inspection.date_of_inspection} - {inspection.client_name}")
            print(f"   Commodity: {inspection.commodity or 'N/A'}")
            print(f"   Product: {inspection.product_name or 'N/A'}")
            print(f"   Hours: {inspection.hours or 'N/A'}, KM: {inspection.km_traveled or 'N/A'}")

    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total inspections by {latest.inspector_name}: {total_count}")
    print(f"Latest inspection date: {latest.date_of_inspection}")
    print(f"Latest client: {latest.client_name}")
    print(f"{'='*80}\n")

    return latest


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Find latest inspection by inspector name',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find Neisa's latest inspection
  python find_inspector_latest.py --inspector Neisa

  # Find all inspections by an inspector
  python find_inspector_latest.py --inspector "John Smith"
        """
    )

    parser.add_argument(
        '--inspector',
        type=str,
        required=True,
        help='Inspector name (partial match supported)'
    )

    args = parser.parse_args()

    find_latest_inspection(args.inspector)

    return 0


if __name__ == '__main__':
    sys.exit(main())
