#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check what's ACTUALLY in the database RIGHT NOW
"""
import os
import sys
import django

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("\n" + "="*80)
print("CHECK DATABASE RIGHT NOW")
print("="*80)

# Total inspections
total = FoodSafetyAgencyInspection.objects.count()
print(f"\n📊 Total inspections in database: {total}")

# Check by account code
account_code = "RE-IND-RAW-NA-0222"
by_code = FoodSafetyAgencyInspection.objects.filter(internal_account_code=account_code)
print(f"\n🔍 Inspections with account code '{account_code}': {by_code.count()}")

if by_code.exists():
    print(f"\n✅ FOUND! Sample:")
    for insp in by_code[:3]:
        print(f"\n   Inspection #{insp.id}:")
        print(f"   ├─ Client Name: {insp.client_name}")
        print(f"   ├─ Account Code: {insp.internal_account_code}")
        print(f"   └─ Date: {insp.date_of_inspection}")
else:
    print(f"\n❌ NOT FOUND by account code")

# Check by client name
by_name = FoodSafetyAgencyInspection.objects.filter(client_name__icontains="Ethans Butchery")
print(f"\n🔍 Inspections with 'Ethans Butchery' in name: {by_name.count()}")

if by_name.exists():
    print(f"\n✅ FOUND! Sample:")
    for insp in by_name[:3]:
        print(f"\n   Inspection #{insp.id}:")
        print(f"   ├─ Client Name: {insp.client_name}")
        print(f"   ├─ Account Code: {insp.internal_account_code}")
        print(f"   └─ Date: {insp.date_of_inspection}")
else:
    print(f"\n❌ NOT FOUND by name")

# Check by old name
by_old_name = FoodSafetyAgencyInspection.objects.filter(client_name__icontains="New Processed Meat Retailer")
print(f"\n🔍 Inspections with 'New Processed Meat Retailer' in name: {by_old_name.count()}")

if by_old_name.exists():
    print(f"\n⚠️ FOUND OLD NAME! Sample:")
    for insp in by_old_name[:3]:
        print(f"\n   Inspection #{insp.id}:")
        print(f"   ├─ Client Name: {insp.client_name}")
        print(f"   ├─ Account Code: {insp.internal_account_code or 'NONE'}")
        print(f"   └─ Date: {insp.date_of_inspection}")

# Check account codes stats
with_code = FoodSafetyAgencyInspection.objects.exclude(
    internal_account_code__isnull=True
).exclude(internal_account_code='').count()

print(f"\n📋 Account Code Statistics:")
print(f"   Total: {total}")
print(f"   With account codes: {with_code} ({(with_code/total*100) if total > 0 else 0:.1f}%)")
print(f"   Without: {total - with_code}")

# Show ALL unique client names with "Ethan" or "Retailer"
print(f"\n📋 All unique client names with 'Ethan' or 'Retailer':")
ethan_or_retailer = FoodSafetyAgencyInspection.objects.filter(
    client_name__iregex=r'(ethan|retailer)'
).values_list('client_name', flat=True).distinct()

for name in ethan_or_retailer[:10]:
    count = FoodSafetyAgencyInspection.objects.filter(client_name=name).count()
    print(f"   - '{name}' ({count} inspections)")

print("\n" + "="*80 + "\n")
