#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check how inspection 6517 (Food Lover's Market - Lynnwood) is stored in the database
Expected products: Fresh whole chicken, Nyama choma Braaiwors, Sliced Salami
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

def check_inspection_6517():
    """Check how inspection 6517 is stored - should be 3 separate records"""
    print("=" * 80)
    print("INSPECTION 6517 - Food Lover's Market - Lynnwood")
    print("=" * 80)
    print("\nExpected products:")
    print("  1. Fresh whole chicken")
    print("  2. Nyama choma Braaiwors")
    print("  3. Sliced Salami")
    print("\n" + "=" * 80)

    # Check for base inspection (without underscore)
    base = FoodSafetyAgencyInspection.objects.filter(remote_id='6517').first()
    if base:
        print("\n❌ FOUND BASE INSPECTION (NOT SPLIT YET):")
        print(f"   Remote ID: {base.remote_id}")
        print(f"   Client: {base.client_name}")
        print(f"   Commodity: {base.commodity}")
        print(f"   Product Name: {base.product_name}")
        print(f"   Date: {base.date_of_inspection}")
        print(f"   Inspector: {base.inspector_name}")
        print("\n   ⚠️  This inspection has NOT been split yet!")
        print("   Run 'Sync Everything' to split it into individual products.")
    else:
        print("\n✅ No base inspection found (good - it should be split)")

    # Check for split inspections (with underscore)
    split_inspections = FoodSafetyAgencyInspection.objects.filter(
        remote_id__startswith='6517_'
    ).order_by('remote_id')

    if split_inspections.exists():
        print(f"\n✅ FOUND {split_inspections.count()} SPLIT INSPECTION(S):")
        print("=" * 80)

        for idx, insp in enumerate(split_inspections, 1):
            print(f"\nRecord #{idx}:")
            print(f"   Remote ID: {insp.remote_id}")
            print(f"   Client: {insp.client_name}")
            print(f"   Commodity: {insp.commodity}")
            print(f"   Product Name: {insp.product_name}")
            print(f"   Date: {insp.date_of_inspection}")
            print(f"   Inspector: {insp.inspector_name}")
            print(f"   Account Code: {insp.internal_account_code}")

        print("\n" + "=" * 80)
        print("VERDICT: ✅ Inspection has been SPLIT correctly!")
        print(f"Each of the {split_inspections.count()} products is now a separate inspection record.")
    else:
        print("\n❌ NO SPLIT INSPECTIONS FOUND")
        print("   Expected to find: 6517_1, 6517_2, 6517_3")
        print("   You need to run 'Sync Everything' to apply the split logic.")

    # Also check for any inspection with this client name
    print("\n" + "=" * 80)
    print("ALL INSPECTIONS FOR 'Food Lover's Market - Lynnwood':")
    print("=" * 80)

    all_foodlovers = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains="Food Lover's Market - Lynnwood"
    ).order_by('remote_id')

    if all_foodlovers.exists():
        print(f"\nFound {all_foodlovers.count()} total inspection(s) for this client:")
        for insp in all_foodlovers:
            print(f"\n   Remote ID: {insp.remote_id}")
            print(f"   Product: {insp.product_name}")
            print(f"   Date: {insp.date_of_inspection}")
    else:
        print("\n❌ No inspections found for this client in the database")
        print("   The sync may not have run yet, or the client name doesn't match")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    check_inspection_6517()
