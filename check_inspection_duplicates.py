#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check for duplicate inspection records in the database
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter

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

from main.models import FoodSafetyAgencyInspection

def check_duplicates():
    """Check for duplicate inspection records"""

    print(f"\n{'='*100}")
    print(f"INSPECTION RECORDS ANALYSIS")
    print(f"{'='*100}\n")

    # Get all inspections
    all_inspections = FoodSafetyAgencyInspection.objects.all()
    total_count = all_inspections.count()

    print(f"Total Inspections: {total_count:,}")

    # Get date range
    if total_count > 0:
        earliest = all_inspections.order_by('date_of_inspection').first()
        latest = all_inspections.order_by('-date_of_inspection').first()
        print(f"Date Range: {earliest.date_of_inspection} to {latest.date_of_inspection}")

    print(f"\n{'='*100}")
    print(f"CHECKING FOR DUPLICATES")
    print(f"{'='*100}\n")

    # Check for duplicate remote_ids
    remote_ids = list(all_inspections.values_list('remote_id', flat=True))
    remote_id_counts = Counter(remote_ids)
    duplicates = {k: v for k, v in remote_id_counts.items() if v > 1}

    if duplicates:
        print(f"⚠️  Found {len(duplicates)} duplicate remote_ids:")
        print(f"   Total duplicate records: {sum(v - 1 for v in duplicates.values()):,}\n")

        # Show top 20 duplicates
        sorted_duplicates = sorted(duplicates.items(), key=lambda x: x[1], reverse=True)
        print(f"Top 20 Most Duplicated Remote IDs:")
        print(f"{'─'*100}")
        for idx, (remote_id, count) in enumerate(sorted_duplicates[:20], 1):
            print(f"{idx:3d}. Remote ID {remote_id}: {count} copies")

            # Show details of these duplicates
            dups = FoodSafetyAgencyInspection.objects.filter(remote_id=remote_id)
            for dup in dups[:3]:  # Show first 3
                print(f"     - {dup.client_name} | {dup.date_of_inspection} | Created: {dup.created_at if hasattr(dup, 'created_at') else 'N/A'}")
            if dups.count() > 3:
                print(f"     ... and {dups.count() - 3} more")
            print()
    else:
        print("✅ No duplicate remote_ids found")

    # Group by month
    print(f"\n{'='*100}")
    print(f"INSPECTIONS BY MONTH")
    print(f"{'='*100}\n")

    from django.db.models.functions import TruncMonth
    from django.db.models import Count

    monthly_counts = (
        all_inspections
        .annotate(month=TruncMonth('date_of_inspection'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('-month')
    )

    for entry in monthly_counts[:12]:  # Show last 12 months
        month_str = entry['month'].strftime('%Y-%m') if entry['month'] else 'Unknown'
        count = entry['count']
        print(f"{month_str}: {count:,} inspections")

    # Check for exact duplicates (same remote_id, client_name, date)
    print(f"\n{'='*100}")
    print(f"EXACT DUPLICATES (same remote_id, client, date)")
    print(f"{'='*100}\n")

    from django.db.models import Count

    exact_duplicates = (
        FoodSafetyAgencyInspection.objects
        .values('remote_id', 'client_name', 'date_of_inspection')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
        .order_by('-count')
    )

    if exact_duplicates.exists():
        print(f"⚠️  Found {exact_duplicates.count()} groups of exact duplicates")
        print(f"   Total duplicate records: {sum(d['count'] - 1 for d in exact_duplicates):,}\n")

        print(f"Top 20 Exact Duplicates:")
        print(f"{'─'*100}")
        for idx, dup in enumerate(exact_duplicates[:20], 1):
            print(f"{idx:3d}. Remote ID {dup['remote_id']} | {dup['client_name']} | {dup['date_of_inspection']} | {dup['count']} copies")
    else:
        print("✅ No exact duplicates found")

    print(f"\n{'='*100}")
    print(f"SUMMARY")
    print(f"{'='*100}\n")
    print(f"Total Inspections: {total_count:,}")
    if duplicates:
        unique_count = len(set(remote_ids))
        duplicate_records = total_count - unique_count
        print(f"Unique Remote IDs: {unique_count:,}")
        print(f"Duplicate Records: {duplicate_records:,}")
        print(f"Duplication Rate: {(duplicate_records / total_count * 100):.1f}%")
    else:
        print(f"All inspections are unique ✅")

    print(f"\n{'='*100}\n")


if __name__ == "__main__":
    try:
        check_duplicates()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
