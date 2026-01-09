#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-fix duplicate inspection records
Removes duplicates automatically, keeping the most recent record for each remote_id
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
from datetime import datetime

print("=" * 80)
print("AUTO-FIX DUPLICATE INSPECTION RECORDS")
print("=" * 80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Get initial count
initial_count = FoodSafetyAgencyInspection.objects.count()
print(f"Initial inspection count: {initial_count:,}")

# Find duplicates
duplicates = FoodSafetyAgencyInspection.objects.values('remote_id').annotate(
    count=Count('id')
).filter(count__gt=1).order_by('-count')

duplicate_count = duplicates.count()

if duplicate_count == 0:
    print("\n✅ No duplicates found! Database is clean.")
    sys.exit(0)

print(f"Found {duplicate_count:,} remote_ids with duplicates\n")

# Calculate expected deletions
total_to_delete = sum(dup['count'] - 1 for dup in duplicates)
print(f"Will delete {total_to_delete:,} duplicate records")
print(f"Expected final count: {initial_count - total_to_delete:,}\n")

# Fix duplicates
print("Removing duplicates (keeping most recent record for each remote_id)...")
deleted_count = 0

for i, dup in enumerate(duplicates, 1):
    remote_id = dup['remote_id']

    # Get all records with this remote_id, ordered by creation date
    records = FoodSafetyAgencyInspection.objects.filter(
        remote_id=remote_id
    ).order_by('-created_at', '-id')

    # Keep the first (most recent), delete the rest
    records_to_delete = list(records[1:])

    for record in records_to_delete:
        record.delete()
        deleted_count += 1

    if i % 100 == 0:
        print(f"  Processed {i:,}/{duplicate_count:,} duplicated remote_ids...")

print(f"\n✅ Deleted {deleted_count:,} duplicate records")

# Get final count
final_count = FoodSafetyAgencyInspection.objects.count()
print(f"\nFinal inspection count: {final_count:,}")

# Verify no duplicates remain
remaining_duplicates = FoodSafetyAgencyInspection.objects.values('remote_id').annotate(
    count=Count('id')
).filter(count__gt=1).count()

if remaining_duplicates == 0:
    print("✅ No remaining duplicates - database is clean!")
else:
    print(f"⚠️  Warning: Still have {remaining_duplicates:,} duplicate remote_ids")

print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
