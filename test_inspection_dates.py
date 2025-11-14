#!/usr/bin/env python3
"""
Test script to verify inspections are only from October 2025 onwards
"""

import os
import django
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

if __name__ == '__main__':
    print("=" * 80)
    print("INSPECTION DATE FILTER TEST")
    print("=" * 80)
    print()

    # Get all inspections
    all_inspections = FoodSafetyAgencyInspection.objects.all()
    total_count = all_inspections.count()

    print(f"Total inspections in database: {total_count}")
    print()

    # Check date range
    if total_count > 0:
        earliest = all_inspections.order_by('date_of_inspection').first()
        latest = all_inspections.order_by('-date_of_inspection').first()

        print(f"Earliest inspection date: {earliest.date_of_inspection}")
        print(f"Latest inspection date: {latest.date_of_inspection}")
        print()

        # Check if any inspections are before October 1, 2025
        october_2025 = datetime(2025, 10, 1).date()
        before_october = all_inspections.filter(date_of_inspection__lt=october_2025)
        before_count = before_october.count()

        print("=" * 80)
        print("FILTER CHECK: October 1, 2025 onwards")
        print("=" * 80)
        print()

        if before_count > 0:
            print(f"[WARNING] Found {before_count} inspections BEFORE October 1, 2025")
            print()
            print("Sample of old inspections:")
            for insp in before_october[:5]:
                print(f"  - {insp.date_of_inspection} - {insp.client_name}")
            print()
            print("[ACTION NEEDED] These will be filtered out in the view")
        else:
            print(f"[OK] All {total_count} inspections are from October 1, 2025 onwards!")
            print()
            print("Date range:")
            print(f"  From: {earliest.date_of_inspection}")
            print(f"  To: {latest.date_of_inspection}")

        print()

        # Count inspections by month for October 2025 onwards
        from_october = all_inspections.filter(date_of_inspection__gte=october_2025)
        print("=" * 80)
        print("INSPECTIONS BY MONTH (October 2025 onwards)")
        print("=" * 80)
        print()

        months = {}
        for insp in from_october:
            month_key = insp.date_of_inspection.strftime('%B %Y')
            months[month_key] = months.get(month_key, 0) + 1

        for month in sorted(months.keys()):
            print(f"  {month}: {months[month]} inspections")

        print()
        print(f"Total from October 2025 onwards: {from_october.count()}")

    else:
        print("No inspections found in database")

    print()
    print("=" * 80)
