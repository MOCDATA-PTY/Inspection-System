#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnose Django system and inspection count issues
"""
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Count

def diagnose_inspections():
    """Diagnose inspection count and data issues"""
    print("=" * 80)
    print("INSPECTION DATABASE DIAGNOSTICS")
    print("=" * 80)

    # Total count
    total = FoodSafetyAgencyInspection.objects.count()
    print(f"\n📊 TOTAL INSPECTIONS: {total:,}")

    # Count inspections with commas (multi-product - should be split)
    multi_product = FoodSafetyAgencyInspection.objects.filter(
        product_name__contains=','
    ).count()

    print(f"\n🔍 Multi-product inspections (with commas): {multi_product:,}")
    if multi_product > 0:
        print("   ⚠️  These should be split into individual records!")

    # Count split inspections (with underscore)
    split_inspections = FoodSafetyAgencyInspection.objects.filter(
        remote_id__contains='_'
    ).count()

    print(f"\n📋 Split inspections (with _1, _2, etc.): {split_inspections:,}")

    # Count base inspections (no underscore)
    base_inspections = FoodSafetyAgencyInspection.objects.exclude(
        remote_id__contains='_'
    ).count()

    print(f"\n📋 Base inspections (without underscore): {base_inspections:,}")

    # Check for duplicates by remote_id
    print("\n" + "=" * 80)
    print("DUPLICATE CHECK")
    print("=" * 80)

    duplicates = FoodSafetyAgencyInspection.objects.values('remote_id').annotate(
        count=Count('remote_id')
    ).filter(count__gt=1).order_by('-count')

    if duplicates.exists():
        print(f"\n❌ FOUND {duplicates.count()} DUPLICATE REMOTE IDs:")
        for dup in duplicates[:10]:
            print(f"   Remote ID: {dup['remote_id']} - Count: {dup['count']}")
        if duplicates.count() > 10:
            print(f"   ... and {duplicates.count() - 10} more")
    else:
        print("\n✅ No duplicate remote_ids found")

    # Check for None/empty product names
    print("\n" + "=" * 80)
    print("DATA QUALITY CHECK")
    print("=" * 80)

    no_product = FoodSafetyAgencyInspection.objects.filter(
        product_name__isnull=True
    ).count() + FoodSafetyAgencyInspection.objects.filter(
        product_name=''
    ).count() + FoodSafetyAgencyInspection.objects.filter(
        product_name='None'
    ).count()

    print(f"\n⚠️  Inspections with no product name: {no_product:,}")

    # Recent inspections sample
    print("\n" + "=" * 80)
    print("RECENT INSPECTIONS (Last 10)")
    print("=" * 80)

    recent = FoodSafetyAgencyInspection.objects.all().order_by('-id')[:10]

    for idx, insp in enumerate(recent, 1):
        print(f"\n{idx}. Remote ID: {insp.remote_id}")
        print(f"   Client: {insp.client_name}")
        print(f"   Product: {insp.product_name}")
        print(f"   Date: {insp.date_of_inspection}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal inspections: {total:,}")
    print(f"  - Base inspections (no split): {base_inspections:,}")
    print(f"  - Split inspections: {split_inspections:,}")
    print(f"  - Multi-product (needs split): {multi_product:,}")
    print(f"  - Missing product name: {no_product:,}")

    if multi_product > 0 and split_inspections > 0:
        print("\n⚠️  WARNING: You have BOTH multi-product AND split inspections!")
        print("   This suggests the sync ran partially or multiple times.")
        print("   Recommendation: Run 'Sync Everything' once more to complete the split.")
    elif multi_product > 0:
        print("\n⚠️  Multi-product inspections need to be split.")
        print("   Run 'Sync Everything' to split them.")
    elif split_inspections > 0:
        print("\n✅ All inspections have been split correctly!")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    diagnose_inspections()
