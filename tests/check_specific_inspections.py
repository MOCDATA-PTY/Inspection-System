#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check specific inspections to verify product names
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

print("=" * 80)
print("CHECKING SPECIFIC INSPECTIONS")
print("=" * 80)

# Check inspection 17082 (EGGS - no product name)
print("\n[1] Inspection 17082 - Kekkel en kraai Grootbrak (EGGS)")
print("-" * 80)

eggs_inspections = FoodSafetyAgencyInspection.objects.filter(
    remote_id__startswith='17082'
).order_by('remote_id')

if eggs_inspections.exists():
    print(f"Found {eggs_inspections.count()} inspection(s) with remote_id starting with 17082:\n")
    for insp in eggs_inspections:
        print(f"   Remote ID: {insp.remote_id}")
        print(f"   Client: {insp.client_name}")
        print(f"   Commodity: {insp.commodity}")
        print(f"   Product Name: {insp.product_name or '[EMPTY]'}")
        print(f"   Date: {insp.date_of_inspection}")
        print(f"   Inspector: {insp.inspector_name}")
        print()
else:
    print("   ❌ No inspection found with remote_id 17082")

# Check inspection 65201 (POULTRY - should be chicken product)
print("\n[2] Inspection 65201 - Kekkel en kraai Grootbrak (POULTRY)")
print("-" * 80)

poultry_inspections = FoodSafetyAgencyInspection.objects.filter(
    remote_id__startswith='65201'
).order_by('remote_id')

if poultry_inspections.exists():
    print(f"Found {poultry_inspections.count()} inspection(s) with remote_id starting with 65201:\n")
    for insp in poultry_inspections:
        print(f"   Remote ID: {insp.remote_id}")
        print(f"   Client: {insp.client_name}")
        print(f"   Commodity: {insp.commodity}")
        print(f"   Product Name: {insp.product_name or '[EMPTY]'}")
        print(f"   Date: {insp.date_of_inspection}")
        print(f"   Inspector: {insp.inspector_name}")

        # Verify it's a chicken product
        if insp.product_name:
            product_lower = insp.product_name.lower()
            is_chicken = any(word in product_lower for word in ['chicken', 'chick', 'poultry', 'russian'])
            if is_chicken:
                print(f"   ✅ Product appears to be chicken/poultry related")
            else:
                print(f"   ⚠️  Product does NOT appear to be chicken/poultry related")
        print()
else:
    print("   ❌ No inspection found with remote_id 65201")

# Check all Kekkel en kraai Grootbrak inspections
print("\n[3] All Recent Inspections for 'Kekkel en kraai Grootbrak'")
print("-" * 80)

all_kekkel = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains='Kekkel'
).order_by('-date_of_inspection', 'commodity')[:10]

if all_kekkel.exists():
    print(f"Found {all_kekkel.count()} recent inspection(s):\n")
    for insp in all_kekkel:
        print(f"   Remote ID: {insp.remote_id}")
        print(f"   Commodity: {insp.commodity}")
        print(f"   Product: {insp.product_name or '[EMPTY]'}")
        print(f"   Date: {insp.date_of_inspection}")
        print()
else:
    print("   ❌ No inspections found for Kekkel en kraai Grootbrak")

# Summary of empty product names
print("\n[4] Summary: Inspections with Empty Product Names")
print("-" * 80)

empty_products = FoodSafetyAgencyInspection.objects.filter(
    product_name__isnull=True
) | FoodSafetyAgencyInspection.objects.filter(
    product_name=''
)

empty_count = empty_products.count()
total_count = FoodSafetyAgencyInspection.objects.count()

print(f"Total inspections: {total_count:,}")
print(f"Inspections with empty product names: {empty_count:,}")
print(f"Percentage: {(empty_count/total_count*100) if total_count > 0 else 0:.2f}%")

if empty_count > 0:
    print(f"\nSample of inspections with empty product names:")
    for insp in empty_products[:5]:
        print(f"   Remote ID: {insp.remote_id} | Commodity: {insp.commodity} | Client: {insp.client_name}")

print("\n" + "=" * 80)
