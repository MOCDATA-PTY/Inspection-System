#!/usr/bin/env python3
"""
Check Sent Status of Recent Inspections
=========================================
Checks if recent Nov 26-27 inspections are marked as sent or not.
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


def check_sent_status():
    """Check sent status of recent Nelisa inspections."""

    print(f"\n{'='*100}")
    print(f"CHECKING SENT STATUS")
    print(f"{'='*100}\n")

    # Check Nov 26 inspections for Nelisa
    nov_26 = FoodSafetyAgencyInspection.objects.filter(
        inspector_name__icontains='Nelisa',
        date_of_inspection=date(2025, 11, 26)
    )

    print(f"Nelisa Nov 26 inspections: {nov_26.count()}")
    print(f"\nBreakdown:")
    sent_count = nov_26.filter(is_sent=True).count()
    not_sent_count = nov_26.filter(is_sent=False).count()

    print(f"  Sent: {sent_count}")
    print(f"  Not Sent: {not_sent_count}")

    print(f"\nDetails:")
    for insp in nov_26:
        sent_status = "SENT" if insp.is_sent else "NOT SENT"
        print(f"  {insp.client_name} - {sent_status}")

    # Check Nov 11 inspections for comparison
    print(f"\n\nNov 11 inspections (for comparison):")
    nov_11 = FoodSafetyAgencyInspection.objects.filter(
        inspector_name__icontains='Nelisa',
        date_of_inspection=date(2025, 11, 11)
    )

    print(f"Total: {nov_11.count()}")
    sent_count_11 = nov_11.filter(is_sent=True).count()
    not_sent_count_11 = nov_11.filter(is_sent=False).count()

    print(f"  Sent: {sent_count_11}")
    print(f"  Not Sent: {not_sent_count_11}")

    print(f"\n{'='*100}")
    print(f"CONCLUSION")
    print(f"{'='*100}")

    if not_sent_count > 0:
        print(f"\nNov 26 has {not_sent_count} NOT SENT inspections")
        print(f"They SHOULD show up with 'Sent Status: Not Sent' filter")
        print(f"\nIf they don't show: It's a cache or pagination issue")
    else:
        print(f"\nAll Nov 26 inspections are marked as SENT")
        print(f"That's why they don't show with 'Sent Status: Not Sent' filter!")
        print(f"\nFix: Clear the 'Sent Status' filter to see them")
    print()


if __name__ == '__main__':
    check_sent_status()
