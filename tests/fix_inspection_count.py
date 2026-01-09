#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test and Fix Inspection Record Count Issue
Diagnoses and fixes duplicate/excess inspection records locally
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
from django.db.models import Count, Q
from datetime import datetime, timedelta
from collections import defaultdict


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def check_inspection_counts():
    """Check and analyze inspection record counts"""
    print_section("INSPECTION RECORD COUNT ANALYSIS")

    # Total count
    total = FoodSafetyAgencyInspection.objects.count()
    print(f"\n📊 TOTAL INSPECTIONS IN DATABASE: {total:,}")

    if total < 1000:
        print("   ✅ Count looks reasonable (< 1,000)")
    elif total < 10000:
        print("   ⚠️  Count is high (1,000 - 10,000)")
    else:
        print(f"   ❌ COUNT IS TOO HIGH ({total:,})! Expected much lower.")

    # Count by date ranges
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    sixty_days_ago = today - timedelta(days=60)
    ninety_days_ago = today - timedelta(days=90)

    last_30_days = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=thirty_days_ago
    ).count()

    last_60_days = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=sixty_days_ago
    ).count()

    last_90_days = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=ninety_days_ago
    ).count()

    print(f"\n📅 Date Range Breakdown:")
    print(f"   Last 30 days: {last_30_days:,}")
    print(f"   Last 60 days: {last_60_days:,}")
    print(f"   Last 90 days: {last_90_days:,}")

    return total


def check_duplicate_remote_ids():
    """Check for duplicate remote_id values"""
    print_section("DUPLICATE REMOTE_ID ANALYSIS")

    # Find duplicates
    duplicates = FoodSafetyAgencyInspection.objects.values('remote_id').annotate(
        count=Count('id')
    ).filter(count__gt=1).order_by('-count')

    duplicate_count = duplicates.count()

    if duplicate_count == 0:
        print("\n✅ No duplicate remote_ids found!")
        return 0, []

    print(f"\n❌ FOUND {duplicate_count:,} DUPLICATE REMOTE_IDs!")

    # Calculate total duplicate records
    total_duplicate_records = 0
    duplicate_list = []

    for dup in duplicates:
        extra_copies = dup['count'] - 1
        total_duplicate_records += extra_copies
        duplicate_list.append({
            'remote_id': dup['remote_id'],
            'count': dup['count'],
            'extra_copies': extra_copies
        })

    print(f"\n📊 Duplicate Statistics:")
    print(f"   Unique remote_ids with duplicates: {duplicate_count:,}")
    print(f"   Total duplicate records: {total_duplicate_records:,}")

    # Show top 10 worst offenders
    print(f"\n🔝 Top 10 Most Duplicated Remote IDs:")
    for i, dup in enumerate(duplicate_list[:10], 1):
        print(f"   {i:2}. Remote ID: {str(dup['remote_id']):<30} appears {dup['count']:,} times ({dup['extra_copies']:,} duplicates)")

    if duplicate_count > 10:
        print(f"\n   ... and {duplicate_count - 10:,} more duplicated remote_ids")

    return total_duplicate_records, duplicate_list


def check_base_split_collisions():
    """Check if both base and split versions of inspections exist"""
    print_section("BASE + SPLIT VERSION COLLISION CHECK")

    # Get all split inspections (remote_id contains underscore)
    split_inspections = FoodSafetyAgencyInspection.objects.filter(
        remote_id__contains='_'
    )
    split_count = split_inspections.count()

    print(f"\n📋 Split inspections (with '_' in remote_id): {split_count:,}")

    if split_count == 0:
        print("   ℹ️  No split inspections found")
        return 0, []

    # Extract base IDs from split inspections
    base_ids_from_splits = set()
    for insp in split_inspections.values_list('remote_id', flat=True):
        if insp and '_' in str(insp):
            # Get base ID (everything before the last underscore)
            base_id = str(insp).rsplit('_', 1)[0]
            base_ids_from_splits.add(base_id)

    print(f"   Unique base IDs extracted from splits: {len(base_ids_from_splits):,}")

    # Check how many base IDs still exist as separate records
    collisions = []
    collision_count = 0

    for base_id in base_ids_from_splits:
        base_records = FoodSafetyAgencyInspection.objects.filter(remote_id=base_id)
        if base_records.exists():
            split_records = FoodSafetyAgencyInspection.objects.filter(
                remote_id__startswith=f"{base_id}_"
            )
            collisions.append({
                'base_id': base_id,
                'base_count': base_records.count(),
                'split_count': split_records.count(),
                'total_collision_records': base_records.count()
            })
            collision_count += base_records.count()

    if collisions:
        print(f"\n❌ FOUND {len(collisions):,} BASE IDs WITH COLLISIONS!")
        print(f"   Total collision records: {collision_count:,}")
        print("\n🔝 Top 10 Collisions:")

        for i, col in enumerate(collisions[:10], 1):
            print(f"   {i:2}. Base ID: {col['base_id']}")
            print(f"       Base records: {col['base_count']}, Split versions: {col['split_count']}")

        if len(collisions) > 10:
            print(f"\n   ... and {len(collisions) - 10:,} more collisions")
    else:
        print("\n✅ No collisions found - split inspections properly replaced bases")

    return collision_count, collisions


def check_multi_product_inspections():
    """Check for inspections with comma-separated products"""
    print_section("MULTI-PRODUCT INSPECTION CHECK")

    multi_product = FoodSafetyAgencyInspection.objects.filter(
        product_name__contains=','
    )

    count = multi_product.count()
    print(f"\n📦 Inspections with comma-separated products: {count:,}")

    if count > 0:
        print("   ⚠️  These should be split into individual records!")
        print("\n   Sample multi-product inspections:")
        for i, insp in enumerate(multi_product[:5], 1):
            print(f"   {i}. Remote ID: {insp.remote_id}")
            print(f"      Products: {insp.product_name}")
            print(f"      Date: {insp.date_of_inspection}")
    else:
        print("   ✅ All inspections have single products")

    return count


def fix_duplicate_remote_ids(duplicate_list, dry_run=True):
    """Fix duplicate remote_ids by keeping only the most recent record"""
    print_section("FIXING DUPLICATE REMOTE_IDS")

    if not duplicate_list:
        print("\n✅ No duplicates to fix!")
        return 0

    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made")
    else:
        print("\n⚠️  LIVE MODE - Records will be deleted!")
        response = input("\nAre you sure you want to delete duplicate records? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return 0

    deleted_count = 0

    print(f"\nProcessing {len(duplicate_list):,} duplicated remote_ids...")

    for i, dup_info in enumerate(duplicate_list, 1):
        remote_id = dup_info['remote_id']

        # Get all records with this remote_id
        records = FoodSafetyAgencyInspection.objects.filter(
            remote_id=remote_id
        ).order_by('-created_at', '-id')

        # Keep the first (most recent), delete the rest
        records_to_delete = list(records[1:])

        if dry_run:
            print(f"{i:4}. Remote ID {remote_id}: Would delete {len(records_to_delete)} duplicate(s)")
        else:
            for record in records_to_delete:
                record.delete()
                deleted_count += 1
            print(f"{i:4}. Remote ID {remote_id}: Deleted {len(records_to_delete)} duplicate(s)")

    if dry_run:
        print(f"\n📊 Would delete {sum(d['extra_copies'] for d in duplicate_list):,} duplicate records")
    else:
        print(f"\n✅ Deleted {deleted_count:,} duplicate records")

    return deleted_count


def fix_base_split_collisions(collisions, dry_run=True):
    """Fix collisions by removing base records that have split versions"""
    print_section("FIXING BASE + SPLIT COLLISIONS")

    if not collisions:
        print("\n✅ No collisions to fix!")
        return 0

    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made")
    else:
        print("\n⚠️  LIVE MODE - Base records will be deleted!")
        response = input("\nAre you sure you want to delete base records with split versions? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return 0

    deleted_count = 0

    print(f"\nProcessing {len(collisions):,} collisions...")

    for i, collision in enumerate(collisions, 1):
        base_id = collision['base_id']

        # Delete all base records (keep split versions)
        base_records = FoodSafetyAgencyInspection.objects.filter(remote_id=base_id)
        count = base_records.count()

        if dry_run:
            print(f"{i:4}. Base ID {base_id}: Would delete {count} base record(s)")
        else:
            base_records.delete()
            deleted_count += count
            print(f"{i:4}. Base ID {base_id}: Deleted {count} base record(s)")

    if dry_run:
        print(f"\n📊 Would delete {sum(c['base_count'] for c in collisions):,} base records")
    else:
        print(f"\n✅ Deleted {deleted_count:,} base records")

    return deleted_count


def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print("INSPECTION RECORD DIAGNOSTIC AND REPAIR TOOL")
    print("=" * 80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Phase 1: Diagnosis
    print("\n" + "🔍" * 40)
    print("PHASE 1: DIAGNOSIS")
    print("🔍" * 40)

    initial_count = check_inspection_counts()
    duplicate_records, duplicate_list = check_duplicate_remote_ids()
    collision_records, collisions = check_base_split_collisions()
    multi_product_count = check_multi_product_inspections()

    # Summary
    print_section("DIAGNOSIS SUMMARY")
    print(f"\n📊 Current State:")
    print(f"   Total inspections: {initial_count:,}")
    print(f"   Duplicate remote_ids: {duplicate_records:,} extra records")
    print(f"   Base+Split collisions: {collision_records:,} extra records")
    print(f"   Multi-product inspections: {multi_product_count:,}")

    total_excess = duplicate_records + collision_records
    expected_count = initial_count - total_excess

    print(f"\n📈 Expected Count After Cleanup:")
    print(f"   Current: {initial_count:,}")
    print(f"   Excess: {total_excess:,}")
    print(f"   Expected: {expected_count:,}")

    if total_excess == 0:
        print("\n✅ Database looks clean! No fixes needed.")
        return

    # Phase 2: Dry Run
    print("\n\n" + "🧪" * 40)
    print("PHASE 2: DRY RUN (Simulation)")
    print("🧪" * 40)

    fix_duplicate_remote_ids(duplicate_list, dry_run=True)
    fix_base_split_collisions(collisions, dry_run=True)

    # Phase 3: Ask for confirmation
    print_section("READY TO FIX")
    print(f"\n⚠️  This will delete {total_excess:,} excess records")
    print(f"   Database will go from {initial_count:,} to {expected_count:,} records")

    response = input("\nDo you want to proceed with the fixes? (yes/no): ")

    if response.lower() != 'yes':
        print("\n❌ Aborted. No changes made.")
        return

    # Phase 4: Execute fixes
    print("\n\n" + "🔧" * 40)
    print("PHASE 3: EXECUTING FIXES")
    print("🔧" * 40)

    deleted_duplicates = fix_duplicate_remote_ids(duplicate_list, dry_run=False)
    deleted_collisions = fix_base_split_collisions(collisions, dry_run=False)

    # Phase 5: Verification
    print("\n\n" + "✅" * 40)
    print("PHASE 4: VERIFICATION")
    print("✅" * 40)

    final_count = FoodSafetyAgencyInspection.objects.count()

    print_section("FINAL RESULTS")
    print(f"\n📊 Before: {initial_count:,} inspections")
    print(f"   Deleted: {deleted_duplicates + deleted_collisions:,} records")
    print(f"   After: {final_count:,} inspections")

    if final_count == expected_count:
        print(f"\n✅ SUCCESS! Count matches expected value ({expected_count:,})")
    else:
        print(f"\n⚠️  Warning: Final count ({final_count:,}) doesn't match expected ({expected_count:,})")

    # Final check for remaining duplicates
    remaining_duplicates = FoodSafetyAgencyInspection.objects.values('remote_id').annotate(
        count=Count('id')
    ).filter(count__gt=1).count()

    if remaining_duplicates == 0:
        print("✅ No remaining duplicates!")
    else:
        print(f"⚠️  Still have {remaining_duplicates:,} duplicate remote_ids")

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
