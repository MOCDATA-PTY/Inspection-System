#!/usr/bin/env python3
"""
Check Dashboard Data vs Database
==================================
Compares what the dashboard shows vs what's actually in the database.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db import models


def check_dashboard_data():
    """Check what data the dashboard would show."""

    print(f"\n{'='*80}")
    print(f"DASHBOARD DATA CHECK")
    print(f"{'='*80}\n")

    # Dashboard query for recent inspections (line 4439)
    print("[1] Recent Inspections (as shown on dashboard):")
    print("-" * 80)
    recent_inspections = FoodSafetyAgencyInspection.objects.order_by('-created_at')[:5]

    for i, insp in enumerate(recent_inspections, 1):
        print(f"{i}. Inspector: {insp.inspector_name}")
        print(f"   Client: {insp.client_name}")
        print(f"   Date of Inspection: {insp.date_of_inspection}")
        print(f"   Created At: {insp.created_at}")
        print()

    # Dashboard query for inspector stats (line 4442)
    print("\n[2] Top Inspectors by Count (as shown on dashboard):")
    print("-" * 80)
    inspector_stats = FoodSafetyAgencyInspection.objects.values('inspector_name').annotate(
        count=models.Count('id')
    ).order_by('-count')[:5]

    for i, stat in enumerate(inspector_stats, 1):
        print(f"{i}. {stat['inspector_name']}: {stat['count']} inspections")

    # Now check Nelisa specifically
    print(f"\n\n[3] NELISA NTOYAPHI - Detailed Check:")
    print("-" * 80)

    nelisa_all = FoodSafetyAgencyInspection.objects.filter(
        inspector_name__icontains='Nelisa'
    ).order_by('-date_of_inspection')[:10]

    print(f"Total inspections: {FoodSafetyAgencyInspection.objects.filter(inspector_name__icontains='Nelisa').count()}")
    print(f"\nLast 10 inspections by date_of_inspection:")
    for i, insp in enumerate(nelisa_all, 1):
        print(f"{i}. Date: {insp.date_of_inspection}, Client: {insp.client_name}")
        print(f"   Created at: {insp.created_at}")
        print(f"   Commodity: {insp.commodity}, Product: {insp.product_name}")

    # Check by created_at
    print(f"\n\nLast 10 inspections by created_at:")
    nelisa_by_created = FoodSafetyAgencyInspection.objects.filter(
        inspector_name__icontains='Nelisa'
    ).order_by('-created_at')[:10]

    for i, insp in enumerate(nelisa_by_created, 1):
        print(f"{i}. Created: {insp.created_at}, Date: {insp.date_of_inspection}")
        print(f"   Client: {insp.client_name}")

    # Check for November inspections specifically
    print(f"\n\n[4] November 2025 Inspections for Nelisa:")
    print("-" * 80)

    from datetime import datetime
    november_inspections = FoodSafetyAgencyInspection.objects.filter(
        inspector_name__icontains='Nelisa',
        date_of_inspection__year=2025,
        date_of_inspection__month=11
    ).order_by('-date_of_inspection')

    print(f"Total November 2025 inspections: {november_inspections.count()}")

    # Group by date
    from collections import defaultdict
    by_date = defaultdict(int)
    for insp in november_inspections:
        by_date[insp.date_of_inspection] += 1

    print("\nInspections by date:")
    for date in sorted(by_date.keys(), reverse=True):
        print(f"  {date}: {by_date[date]} inspections")

    print(f"\n{'='*80}")
    print(f"END OF REPORT")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    check_dashboard_data()
