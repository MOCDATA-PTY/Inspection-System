#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix duplicate inspections in the database
This script identifies and removes duplicate remote_ids, keeping only the most recent version
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
from django.db.models import Count, Max
from django.db import transaction

def fix_duplicates():
    """Remove duplicate inspections, keeping the most recent version of each"""
    print("=" * 80)
    print("FIX DUPLICATE INSPECTIONS")
    print("=" * 80)

    # Get current count
    total_before = FoodSafetyAgencyInspection.objects.count()
    print(f"\n📊 Current total: {total_before:,} inspections")

    # Find duplicates
    print("\n🔍 Finding duplicates...")
    duplicates = FoodSafetyAgencyInspection.objects.values('remote_id').annotate(
        count=Count('id'),
        max_id=Max('id')
    ).filter(count__gt=1).order_by('-count')

    if not duplicates.exists():
        print("\n✅ No duplicates found! Database is clean.")
        return

    total_duplicate_groups = duplicates.count()
    total_records_to_delete = sum(d['count'] - 1 for d in duplicates)

    print(f"\n❌ Found {total_duplicate_groups:,} remote_ids with duplicates")
    print(f"   Total duplicate records to delete: {total_records_to_delete:,}")
    print(f"   Expected count after cleanup: {total_before - total_records_to_delete:,}")

    # Show top 10 duplicates
    print("\n📋 Top 10 duplicate groups:")
    for i, dup in enumerate(duplicates[:10], 1):
        print(f"   {i:2}. Remote ID: {dup['remote_id']:<25} - {dup['count']} copies")

    # Ask for confirmation (skip if --force flag provided)
    force_mode = '--force' in sys.argv

    if not force_mode:
        print("\n" + "=" * 80)
        print("⚠️  WARNING: This will delete duplicate records!")
        print("=" * 80)
        try:
            response = input("\nProceed with deletion? (type 'yes' to confirm): ")
            if response.lower() != 'yes':
                print("\n❌ Cancelled. No changes made.")
                return
        except EOFError:
            print("\n⚠️  Running in non-interactive mode. Use --force flag to proceed.")
            print("   Example: python fix_duplicates.py --force")
            return
    else:
        print("\n⚠️  Force mode enabled - proceeding with deletion automatically...")

    # Delete duplicates (keep the one with highest ID - most recent)
    print("\n🗑️  Deleting duplicates...")
    deleted_count = 0

    with transaction.atomic():
        for dup in duplicates:
            remote_id = dup['remote_id']
            max_id = dup['max_id']

            # Delete all except the one with max_id (most recent)
            deleted = FoodSafetyAgencyInspection.objects.filter(
                remote_id=remote_id
            ).exclude(
                id=max_id
            ).delete()

            deleted_count += deleted[0]

            # Progress indicator
            if deleted_count % 100 == 0:
                print(f"   Deleted {deleted_count:,} / {total_records_to_delete:,} duplicates...")

    # Final count
    total_after = FoodSafetyAgencyInspection.objects.count()

    print("\n" + "=" * 80)
    print("✅ CLEANUP COMPLETE")
    print("=" * 80)
    print(f"\nBefore: {total_before:,} inspections")
    print(f"Deleted: {deleted_count:,} duplicates")
    print(f"After: {total_after:,} inspections")
    print(f"\n✅ Database is now clean - each remote_id appears exactly once")

    # Verify no duplicates remain
    remaining_dups = FoodSafetyAgencyInspection.objects.values('remote_id').annotate(
        count=Count('id')
    ).filter(count__gt=1).count()

    if remaining_dups == 0:
        print("\n✅ Verification passed: No duplicates remain")
    else:
        print(f"\n⚠️  Warning: {remaining_dups} duplicates still found - may need another cleanup pass")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        fix_duplicates()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
