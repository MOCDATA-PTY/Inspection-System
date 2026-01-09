#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify that inspections have been split correctly - one product per inspection
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

def verify_product_split():
    """Verify that each inspection has exactly one product"""
    print("=" * 80)
    print("INSPECTION PRODUCT SPLIT VERIFICATION")
    print("=" * 80)

    # Get total count
    total = FoodSafetyAgencyInspection.objects.count()
    print(f"\n📊 Total inspection records: {total:,}")

    # Check for comma-separated products (should be ZERO after split)
    inspections_with_commas = FoodSafetyAgencyInspection.objects.filter(
        product_name__contains=','
    ).count()

    print(f"\n🔍 Inspections with comma-separated products: {inspections_with_commas}")

    if inspections_with_commas > 0:
        print("   ❌ FAIL: Found inspections with multiple products!")
        print("   These need to be split into individual records.")

        # Show examples
        print("\n   Examples of multi-product inspections:")
        examples = FoodSafetyAgencyInspection.objects.filter(
            product_name__contains=','
        )[:5]

        for insp in examples:
            print(f"\n   Remote ID: {insp.remote_id}")
            print(f"   Client: {insp.client_name}")
            print(f"   Products: {insp.product_name}")
    else:
        print("   ✅ PASS: No multi-product inspections found!")

    # Check for split inspections (remote_id with underscore suffix)
    split_inspections = FoodSafetyAgencyInspection.objects.filter(
        remote_id__contains='_'
    ).count()

    print(f"\n📋 Split inspection records (with _1, _2, etc.): {split_inspections:,}")

    if split_inspections > 0:
        print("   ✅ Found split inspections!")

        # Show examples
        print("\n   Examples of split inspections:")
        examples = FoodSafetyAgencyInspection.objects.filter(
            remote_id__contains='_'
        ).order_by('remote_id')[:10]

        for insp in examples:
            print(f"\n   Remote ID: {insp.remote_id}")
            print(f"   Client: {insp.client_name}")
            print(f"   Product: {insp.product_name}")
            print(f"   Commodity: {insp.commodity}")

    # Show sample of regular inspections
    print("\n" + "=" * 80)
    print("SAMPLE INSPECTIONS (First 10)")
    print("=" * 80)

    sample = FoodSafetyAgencyInspection.objects.all()[:10]

    for idx, insp in enumerate(sample, 1):
        print(f"\n{idx}. Remote ID: {insp.remote_id}")
        print(f"   Client: {insp.client_name}")
        print(f"   Product: {insp.product_name}")
        print(f"   Date: {insp.date_of_inspection}")
        print(f"   Inspector: {insp.inspector_name}")

    # Final verdict
    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)

    if inspections_with_commas == 0:
        print("\n✅ SUCCESS: All inspections have exactly ONE product!")
        print("   Each product is now a separate inspection record.")
        print("   The product splitting is working correctly.")
    else:
        print("\n❌ ISSUE: Some inspections still have multiple products")
        print("   You need to run 'Sync Everything' to apply the split logic.")
        print("   After sync, each product will be a separate inspection record.")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    verify_product_split()
