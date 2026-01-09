#!/usr/bin/env python3
"""
Test script to verify comment persistence for inspection groups
This script will:
1. Add a comment to the "Roots Butchery - Thabazimbi" inspection group (2025-10-30)
2. Retrieve the comment from the database
3. Verify it persists correctly
"""

import os
import django
import sys
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Max

def test_comment_persistence():
    print("=" * 80)
    print("COMMENT PERSISTENCE TEST")
    print("=" * 80)
    print()

    # Target inspection group
    client_name = "Roots Butchery - Thabazimbi"
    date_str = "2025-10-30"
    test_comment = f"Test comment added at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    print(f"Target Inspection Group:")
    print(f"   Client: {client_name}")
    print(f"   Date: {date_str}")
    print()

    # Step 1: Find all inspections for this group
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"ERROR: Invalid date format: {date_str}")
        return

    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name=client_name,
        date_of_inspection=date_obj
    )

    inspection_count = inspections.count()
    print(f"Step 1: Found {inspection_count} inspections in this group")

    if inspection_count == 0:
        print("ERROR: No inspections found for this group!")
        return

    # List all inspections
    print()
    print("Inspections in group:")
    for insp in inspections:
        print(f"   - ID {insp.id}: {insp.product_name} ({insp.commodity}) - Current comment: '{insp.comment or ''}'")
    print()

    # Step 2: Add comment to all inspections in the group
    print(f"Step 2: Adding comment to all {inspection_count} inspections...")
    print(f"   Comment text: '{test_comment}'")

    updated_count = inspections.update(comment=test_comment)
    print(f"   [SUCCESS] Updated {updated_count} inspections")
    print()

    # Step 3: Retrieve the comment using the same query as the view
    print("Step 3: Retrieving comment using groups queryset (same as view)...")

    # This mimics the query in core_views.py
    groups_queryset = FoodSafetyAgencyInspection.objects.filter(
        client_name=client_name,
        date_of_inspection=date_obj
    ).values(
        'client_name',
        'date_of_inspection'
    ).annotate(
        comment=Max('comment')  # This is the fix we added
    ).order_by('-date_of_inspection', 'client_name')

    if groups_queryset.exists():
        group = groups_queryset.first()
        retrieved_comment = group.get('comment', '')

        print(f"   Retrieved comment: '{retrieved_comment}'")
        print()

        # Step 4: Verify
        print("Step 4: Verification")
        if retrieved_comment == test_comment:
            print("   [SUCCESS] Comment matches what we saved!")
            print()
            print("   The comment persistence fix is working correctly.")
            print("   Comments will now persist after page refresh.")
        else:
            print("   [FAILURE] Comment does not match!")
            print(f"   Expected: '{test_comment}'")
            print(f"   Got: '{retrieved_comment}'")
    else:
        print("   [ERROR] Group query returned no results")

    print()
    print("=" * 80)
    print()

    # Step 5: Show current state of all inspections
    print("Step 5: Current state of all inspections in group:")
    inspections_refreshed = FoodSafetyAgencyInspection.objects.filter(
        client_name=client_name,
        date_of_inspection=date_obj
    )

    for insp in inspections_refreshed:
        print(f"   - ID {insp.id}: Comment = '{insp.comment}'")

    print()
    print("=" * 80)


if __name__ == '__main__':
    test_comment_persistence()
