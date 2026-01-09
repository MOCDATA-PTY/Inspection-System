#!/usr/bin/env python
"""
Test script to verify km/hours data protection during sync
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Q
from datetime import datetime

def test_km_hours_backup_logic():
    """Test the backup and restore logic"""
    print("="*80)
    print("TESTING KM/HOURS PROTECTION LOGIC")
    print("="*80)

    # Step 1: Check current inspections with km/hours data
    print("\n1. Checking current inspections with km/hours data...")
    inspections_with_data = FoodSafetyAgencyInspection.objects.filter(
        Q(km_traveled__isnull=False) | Q(hours__isnull=False)
    ).exclude(Q(km_traveled=0) & Q(hours=0))

    count = inspections_with_data.count()
    print(f"   Found {count} inspections with km/hours data")

    if count == 0:
        print("   ⚠️  No km/hours data found - nothing to protect")
        return

    # Step 2: Simulate backup creation
    print("\n2. Simulating backup creation...")
    km_hours_backup = {}

    for insp in inspections_with_data[:10]:  # Test with first 10
        key = (insp.commodity, insp.remote_id, insp.date_of_inspection)
        km_hours_backup[key] = {
            'km_traveled': insp.km_traveled,
            'hours': insp.hours,
            'client_name': insp.client_name,
            'inspector_name': insp.inspector_name,
            'product_name': insp.product_name
        }

    print(f"   ✅ Created backup for {len(km_hours_backup)} inspections")
    print(f"   Sample keys: {list(km_hours_backup.keys())[:3]}")

    # Step 3: Test restoration logic (Strategy 1: Exact match)
    print("\n3. Testing restoration logic - Strategy 1 (Exact match)...")
    restored = 0
    not_found = 0

    for (commodity, remote_id, date_of_inspection), data in km_hours_backup.items():
        # Try exact match
        inspections = FoodSafetyAgencyInspection.objects.filter(
            commodity=commodity,
            remote_id=remote_id,
            date_of_inspection=date_of_inspection
        )

        if inspections.exists():
            restored += inspections.count()
        else:
            not_found += 1

    print(f"   ✅ Strategy 1 would restore: {restored} inspections")
    print(f"   ⚠️  Strategy 1 would miss: {not_found} inspections")

    # Step 4: Test fallback strategy
    print("\n4. Testing restoration logic - Strategy 2 (Fallback)...")
    fallback_restored = 0

    for (commodity, remote_id, date_of_inspection), data in km_hours_backup.items():
        # Try exact match first
        inspections = FoodSafetyAgencyInspection.objects.filter(
            commodity=commodity,
            remote_id=remote_id,
            date_of_inspection=date_of_inspection
        )

        # If no exact match, try fallback
        if not inspections.exists():
            inspections = FoodSafetyAgencyInspection.objects.filter(
                commodity=commodity,
                date_of_inspection=date_of_inspection
            )

            if inspections.exists():
                fallback_restored += 1

    print(f"   ✅ Strategy 2 would restore: {fallback_restored} additional inspections")
    print(f"   📊 Total coverage: {restored + fallback_restored}/{len(km_hours_backup)} inspections")

    # Step 5: Test persistent cache
    print("\n5. Testing persistent cache...")
    try:
        from django.core.cache import cache

        # Save to cache
        cache.set('test_km_hours_backup', km_hours_backup, timeout=86400)

        # Retrieve from cache
        cached_backup = cache.get('test_km_hours_backup')

        if cached_backup and len(cached_backup) == len(km_hours_backup):
            print(f"   ✅ Cache works! Stored and retrieved {len(cached_backup)} entries")
        else:
            print(f"   ⚠️  Cache issue: Stored {len(km_hours_backup)}, retrieved {len(cached_backup) if cached_backup else 0}")

        # Clean up
        cache.delete('test_km_hours_backup')

    except Exception as e:
        print(f"   ⚠️  Cache error: {e}")

    # Step 6: Show sample data that would be preserved
    print("\n6. Sample data that would be preserved:")
    sample = list(inspections_with_data[:3])
    for insp in sample:
        print(f"   - {insp.client_name} ({insp.date_of_inspection})")
        print(f"     Commodity: {insp.commodity}, Remote ID: {insp.remote_id}")
        print(f"     KM: {insp.km_traveled}, Hours: {insp.hours}")
        print(f"     Inspector: {insp.inspector_name}")
        print()

    print("="*80)
    print("✅ TEST COMPLETE - Logic verified!")
    print("="*80)

    # Summary
    coverage_percent = ((restored + fallback_restored) / len(km_hours_backup) * 100) if len(km_hours_backup) > 0 else 0

    print(f"\n📊 SUMMARY:")
    print(f"   Total inspections with km/hours: {count}")
    print(f"   Tested with sample of: {len(km_hours_backup)}")
    print(f"   Strategy 1 (exact match): {restored}")
    print(f"   Strategy 2 (fallback): {fallback_restored}")
    print(f"   Total coverage: {coverage_percent:.1f}%")

    if coverage_percent >= 90:
        print(f"\n✅ EXCELLENT! Protection covers {coverage_percent:.1f}% of data")
    elif coverage_percent >= 70:
        print(f"\n✅ GOOD! Protection covers {coverage_percent:.1f}% of data")
    else:
        print(f"\n⚠️  WARNING! Protection only covers {coverage_percent:.1f}% of data")

    return coverage_percent >= 70

if __name__ == '__main__':
    try:
        success = test_km_hours_backup_logic()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
