#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check for duplicate inspections after sync
Run this on the server to diagnose the 11,768 inspection count issue
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
from datetime import datetime, timedelta

def check_duplicates():
    """Check for duplicate inspections and diagnose the count issue"""
    print("=" * 80)
    print("DUPLICATE INSPECTION DIAGNOSTICS")
    print("=" * 80)

    # Total count
    total = FoodSafetyAgencyInspection.objects.count()
    print(f"\n📊 TOTAL INSPECTIONS IN DATABASE: {total:,}")

    # Count by date range
    oct_start = datetime(2024, 10, 1).date()
    nov_end = datetime(2024, 11, 30).date()
    oct_nov_count = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=oct_start,
        date_of_inspection__lte=nov_end
    ).count()

    print(f"\n📅 October-November 2024: {oct_nov_count:,} inspections")

    # Check for split inspections
    split_count = FoodSafetyAgencyInspection.objects.filter(
        remote_id__contains='_'
    ).count()
    base_count = FoodSafetyAgencyInspection.objects.exclude(
        remote_id__contains='_'
    ).count()

    print(f"\n📋 Split Analysis:")
    print(f"   - Base inspections (no _): {base_count:,}")
    print(f"   - Split inspections (with _): {split_count:,}")
    print(f"   - Total: {base_count + split_count:,}")

    # Check for duplicate remote_ids
    print("\n" + "=" * 80)
    print("DUPLICATE REMOTE_ID CHECK")
    print("=" * 80)

    duplicates = FoodSafetyAgencyInspection.objects.values('remote_id').annotate(
        count=Count('remote_id')
    ).filter(count__gt=1).order_by('-count')

    if duplicates.exists():
        print(f"\n❌ FOUND {duplicates.count():,} DUPLICATE REMOTE IDs!")
        print("\nTop 20 duplicates:")
        for i, dup in enumerate(duplicates[:20], 1):
            print(f"{i:3}. Remote ID: {dup['remote_id']:<20} - Appears {dup['count']} times")

        if duplicates.count() > 20:
            print(f"\n... and {duplicates.count() - 20:,} more duplicates")

        # Calculate total duplicate records
        total_dup_records = sum(d['count'] - 1 for d in duplicates)
        print(f"\n⚠️  Total duplicate records: {total_dup_records:,}")
        print(f"   If we remove duplicates, we'd have: {total - total_dup_records:,} unique inspections")
    else:
        print("\n✅ No duplicate remote_ids found")

    # Check if base and split versions both exist
    print("\n" + "=" * 80)
    print("BASE + SPLIT COLLISION CHECK")
    print("=" * 80)

    # Get all split inspection base IDs
    split_inspections = FoodSafetyAgencyInspection.objects.filter(
        remote_id__contains='_'
    ).values_list('remote_id', flat=True)

    base_ids_from_split = set()
    for split_id in split_inspections:
        # Extract base ID (everything before the first underscore)
        if '_' in split_id:
            base_id = split_id.rsplit('_', 1)[0]
            base_ids_from_split.add(base_id)

    # Check how many of these base IDs still exist as separate records
    collisions = 0
    collision_examples = []

    for base_id in list(base_ids_from_split)[:100]:  # Check first 100
        if FoodSafetyAgencyInspection.objects.filter(remote_id=base_id).exists():
            collisions += 1
            if len(collision_examples) < 5:
                collision_examples.append(base_id)

    if collisions > 0:
        print(f"\n❌ FOUND COLLISIONS: {collisions} base IDs exist alongside their split versions!")
        print("\nExamples:")
        for base_id in collision_examples:
            base_rec = FoodSafetyAgencyInspection.objects.filter(remote_id=base_id).first()
            split_recs = FoodSafetyAgencyInspection.objects.filter(remote_id__startswith=f"{base_id}_")
            print(f"\n   Base: {base_id}")
            if base_rec:
                print(f"      Product: {base_rec.product_name}")
            print(f"   Split versions: {split_recs.count()}")
            for split in split_recs[:3]:
                print(f"      {split.remote_id}: {split.product_name}")

        print(f"\n⚠️  This means both the original AND split versions exist!")
        print(f"   This would cause: {collisions} + {split_count} = {collisions + split_count:,} extra records")
    else:
        print("\n✅ No collisions found - split inspections properly replaced base versions")

    # Check for multi-product inspections that still need splitting
    multi_product = FoodSafetyAgencyInspection.objects.filter(
        product_name__contains=','
    ).count()

    print("\n" + "=" * 80)
    print("MULTI-PRODUCT CHECK")
    print("=" * 80)
    print(f"\n📦 Inspections with comma-separated products: {multi_product:,}")

    if multi_product > 0:
        print("\n   ⚠️  These still need to be split!")
        samples = FoodSafetyAgencyInspection.objects.filter(
            product_name__contains=','
        )[:5]
        for insp in samples:
            print(f"\n   Remote ID: {insp.remote_id}")
            print(f"   Products: {insp.product_name}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY & DIAGNOSIS")
    print("=" * 80)
    print(f"\nTotal inspections: {total:,}")
    print(f"October-November 2024: {oct_nov_count:,}")

    if duplicates.exists():
        total_dup_records = sum(d['count'] - 1 for d in duplicates)
        print(f"\n❌ PROBLEM: {duplicates.count():,} remote_ids appear multiple times")
        print(f"   Total duplicate records: {total_dup_records:,}")
        print(f"   Expected count (without duplicates): {total - total_dup_records:,}")
        print("\n🔧 RECOMMENDED ACTION:")
        print("   1. The sync is creating duplicates")
        print("   2. You may need to clear duplicates before the next sync")
        print("   3. Check if the sync is running multiple times simultaneously")
    elif collisions > 0:
        print(f"\n❌ PROBLEM: Both base and split versions exist for {collisions} inspections")
        print(f"   This is why the count is double what it should be")
        print("\n🔧 RECOMMENDED ACTION:")
        print("   The product splitting didn't delete the base records properly")
        print("   Need to fix the sync logic to delete base before creating splits")
    elif split_count > 0 and multi_product == 0:
        print("\n✅ Product splitting appears to have worked correctly")
        print(f"   All {split_count:,} split inspections are properly separated")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        check_duplicates()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
