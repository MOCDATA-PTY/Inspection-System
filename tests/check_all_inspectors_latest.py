#!/usr/bin/env python3
"""
Check All Inspectors - Latest Inspections
==========================================
Checks the latest inspection for each inspector in the database.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Max, Q
from datetime import datetime


def check_all_inspectors():
    """Check latest inspection for each inspector."""

    print(f"\n{'='*100}")
    print(f"ALL INSPECTORS - LATEST INSPECTION CHECK")
    print(f"{'='*100}\n")

    # Get all unique inspectors
    inspectors = FoodSafetyAgencyInspection.objects.values_list(
        'inspector_name', flat=True
    ).distinct().order_by('inspector_name')

    print(f"{'Inspector':<30} {'Latest (All)':<15} {'Latest (w/ Files)':<15} {'Latest (w/ Hours)':<15}")
    print("-" * 100)

    for inspector in inspectors:
        if not inspector or inspector == 'Unknown':
            continue

        # Latest inspection overall
        latest_all = FoodSafetyAgencyInspection.objects.filter(
            inspector_name=inspector
        ).order_by('-date_of_inspection').first()

        # Latest inspection with files (rfi_uploaded_by filled)
        latest_with_files = FoodSafetyAgencyInspection.objects.filter(
            inspector_name=inspector,
            rfi_uploaded_by__isnull=False
        ).order_by('-date_of_inspection').first()

        # Latest inspection with hours filled
        latest_with_hours = FoodSafetyAgencyInspection.objects.filter(
            inspector_name=inspector,
            hours__isnull=False
        ).order_by('-date_of_inspection').first()

        date_all = latest_all.date_of_inspection if latest_all else 'None'
        date_files = latest_with_files.date_of_inspection if latest_with_files else 'None'
        date_hours = latest_with_hours.date_of_inspection if latest_with_hours else 'None'

        print(f"{inspector:<30} {str(date_all):<15} {str(date_files):<15} {str(date_hours):<15}")

    # Now show recent inspections overall
    print(f"\n\n{'='*100}")
    print(f"RECENT INSPECTIONS (Last 20 - All inspectors)")
    print(f"{'='*100}\n")

    recent = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection', '-created_at')[:20]

    print(f"{'Date':<15} {'Inspector':<25} {'Client':<35} {'Has Files':<10}")
    print("-" * 100)

    for insp in recent:
        has_files = 'Yes' if insp.rfi_uploaded_by else 'No'
        client = (insp.client_name[:32] + '...') if len(insp.client_name) > 35 else insp.client_name
        inspector = (insp.inspector_name[:22] + '...') if len(insp.inspector_name) > 25 else insp.inspector_name
        print(f"{str(insp.date_of_inspection):<15} {inspector:<25} {client:<35} {has_files:<10}")

    # Check dashboard "recent inspections" query
    print(f"\n\n{'='*100}")
    print(f"DASHBOARD 'RECENT INSPECTIONS' (Top 5 by created_at)")
    print(f"{'='*100}\n")

    dashboard_recent = FoodSafetyAgencyInspection.objects.order_by('-created_at')[:5]

    for i, insp in enumerate(dashboard_recent, 1):
        print(f"{i}. {insp.inspector_name}")
        print(f"   Client: {insp.client_name}")
        print(f"   Date of Inspection: {insp.date_of_inspection}")
        print(f"   Created At: {insp.created_at}")
        print(f"   Has RFI: {'Yes' if insp.rfi_uploaded_by else 'No'}")
        print()

    # Check what the dashboard would show if filtered by rfi_uploaded_by
    print(f"\n\n{'='*100}")
    print(f"IF FILTERED BY 'HAS FILES' (rfi_uploaded_by is not null)")
    print(f"{'='*100}\n")

    filtered_recent = FoodSafetyAgencyInspection.objects.filter(
        rfi_uploaded_by__isnull=False
    ).order_by('-created_at')[:5]

    for i, insp in enumerate(filtered_recent, 1):
        print(f"{i}. {insp.inspector_name}")
        print(f"   Date: {insp.date_of_inspection}")
        print(f"   Client: {insp.client_name}")
        print(f"   RFI Uploaded By: {insp.rfi_uploaded_by}")
        print()

    print(f"\n{'='*100}")
    print(f"SUMMARY")
    print(f"{'='*100}")

    # Count recent inspections with vs without files
    from datetime import date, timedelta
    week_ago = date.today() - timedelta(days=7)

    recent_all_count = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=week_ago
    ).count()

    recent_with_files = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=week_ago,
        rfi_uploaded_by__isnull=False
    ).count()

    print(f"\nLast 7 days:")
    print(f"  Total inspections: {recent_all_count}")
    print(f"  With files uploaded: {recent_with_files}")
    print(f"  Without files: {recent_all_count - recent_with_files}")
    print()
    print("If dashboard filters by 'has files', recent inspections won't show!")
    print()


if __name__ == '__main__':
    check_all_inspectors()
