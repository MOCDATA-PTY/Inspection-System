#!/usr/bin/env python3
"""
Test Shipment List Query
=========================
Tests what the shipment_list view actually returns after filter removal.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Count, Max, Min, Q
from datetime import datetime as dt


def test_shipment_list_query():
    """Test the exact query used in shipment_list view."""

    print(f"\n{'='*100}")
    print(f"TESTING SHIPMENT_LIST QUERY (After Filter Removal)")
    print(f"{'='*100}\n")

    # Replicate the exact query from shipment_list view
    inspections = FoodSafetyAgencyInspection.objects.all()

    # Filter by date (Oct 1, 2025 onwards) - same as shipment_list
    october_2025_start = dt(2025, 10, 1).date()
    inspections = inspections.filter(date_of_inspection__gte=october_2025_start)

    print(f"Total inspections from Oct 1, 2025: {inspections.count()}")

    # Create groups (same as shipment_list)
    groups_queryset = inspections.values(
        'client_name',
        'date_of_inspection'
    ).annotate(
        inspection_count=Count('id'),
        latest_inspection_id=Max('id'),
        earliest_inspection_id=Min('id'),
        has_sent_inspections=Count('id', filter=Q(is_sent=True)),
        has_unsent_inspections=Count('id', filter=Q(is_sent=False)),
        has_rfi_inspections=Count('id', filter=Q(rfi_uploaded_by__isnull=False)),
        has_no_rfi_inspections=Count('id', filter=Q(rfi_uploaded_by__isnull=True)),
    ).order_by('-date_of_inspection', 'client_name')

    # NO FILTERS APPLIED (this is the key - filters should be removed)

    total_groups = groups_queryset.count()
    print(f"Total groups (client/date combinations): {total_groups}")

    # Show first 20 groups
    print(f"\n{'='*100}")
    print(f"FIRST 20 GROUPS (Should include Nov 26-27)")
    print(f"{'='*100}\n")

    print(f"{'Date':<15} {'Client':<50} {'Count':<8} {'Has RFI':<10}")
    print("-" * 100)

    for group in groups_queryset[:20]:
        client = (group['client_name'][:47] + '...') if len(group['client_name']) > 50 else group['client_name']
        has_rfi = 'Yes' if group['has_rfi_inspections'] > 0 else 'No'
        print(f"{str(group['date_of_inspection']):<15} {client:<50} {group['inspection_count']:<8} {has_rfi:<10}")

    # Check for Nelisa specifically
    print(f"\n\n{'='*100}")
    print(f"NELISA'S LATEST INSPECTIONS IN GROUPS")
    print(f"{'='*100}\n")

    nelisa_inspections = inspections.filter(inspector_name__icontains='Nelisa')
    print(f"Nelisa total inspections: {nelisa_inspections.count()}")

    nelisa_groups = nelisa_inspections.values(
        'client_name',
        'date_of_inspection'
    ).annotate(
        inspection_count=Count('id'),
        has_rfi=Count('id', filter=Q(rfi_uploaded_by__isnull=False)),
    ).order_by('-date_of_inspection')[:10]

    print(f"\nNelisa's last 10 client/date groups:")
    for group in nelisa_groups:
        print(f"  {group['date_of_inspection']} - {group['client_name']} ({group['inspection_count']} inspections, RFI: {group['has_rfi'] > 0})")

    # Check if filters are somehow still being applied
    print(f"\n\n{'='*100}")
    print(f"CHECKING FOR HIDDEN FILTERS")
    print(f"{'='*100}\n")

    # Test with RFI filter (should NOT be in code anymore)
    groups_with_rfi = groups_queryset.filter(has_rfi_inspections__gt=0)
    print(f"Groups WITH RFI: {groups_with_rfi.count()}")
    print(f"Groups WITHOUT RFI: {total_groups - groups_with_rfi.count()}")

    # Show date range
    latest_date = groups_queryset.first()['date_of_inspection'] if groups_queryset.exists() else None
    print(f"\nLatest date in groups: {latest_date}")

    print(f"\n{'='*100}")
    print(f"CONCLUSION")
    print(f"{'='*100}")
    print(f"If latest date is Nov 26-27: Filter removal WORKED")
    print(f"If latest date is Nov 11-17: Filters still active OR cache issue")
    print()


if __name__ == '__main__':
    test_shipment_list_query()
