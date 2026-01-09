#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick inspection count check"""
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

print("=" * 60)
print("QUICK INSPECTION COUNT CHECK")
print("=" * 60)

try:
    # Total count
    total = FoodSafetyAgencyInspection.objects.count()
    print(f"\n📊 TOTAL INSPECTIONS: {total:,}")

    # Split inspections (with _)
    split = FoodSafetyAgencyInspection.objects.filter(remote_id__contains='_').count()
    print(f"   - Split inspections (with _1, _2): {split:,}")

    # Base inspections (without _)
    base = FoodSafetyAgencyInspection.objects.exclude(remote_id__contains='_').count()
    print(f"   - Base inspections (no _): {base:,}")

    # Multi-product (with comma)
    multi = FoodSafetyAgencyInspection.objects.filter(product_name__contains=',').count()
    print(f"   - Multi-product (comma-separated): {multi:,}")

    print(f"\n✅ Check: {base} + {split} = {base + split} (should equal {total})")

    if multi > 0:
        print(f"\n⚠️  WARNING: {multi} inspections still have comma-separated products!")
        print("   These need to be split. Run 'Sync Everything' to fix.")
    else:
        print("\n✅ All products are properly separated!")

    # Show a few examples
    print("\n" + "=" * 60)
    print("SAMPLE INSPECTIONS (First 5)")
    print("=" * 60)

    samples = FoodSafetyAgencyInspection.objects.all()[:5]
    for i, insp in enumerate(samples, 1):
        print(f"\n{i}. Remote ID: {insp.remote_id}")
        print(f"   Product: {insp.product_name}")
        print(f"   Client: {insp.client_name}")

    print("\n" + "=" * 60)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
