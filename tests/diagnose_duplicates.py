import os
import sys
import django
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 100)
print("DIAGNOSING DUPLICATE LINE ITEMS")
print("=" * 100)

# Check specific cases that have duplicates in the export

# 1. Amans meat & deli (2 products but each appearing twice)
print("\n1. Amans meat & deli on 03/12/2025:")
print("-" * 100)
amans = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains='Amans meat',
    date_of_inspection=datetime(2025, 12, 3).date(),
    commodity='RAW'
).order_by('product_name', 'remote_id')

print(f"Found {amans.count()} RAW inspections:")
for idx, insp in enumerate(amans, 1):
    key = (insp.inspector_name or '', insp.client_name or '', insp.commodity or '',
           str(insp.date_of_inspection), insp.product_name or '')
    print(f"  {idx}. ID={insp.remote_id} | Product='{insp.product_name}' | Inspector='{insp.inspector_name}'")
    print(f"      Unique Key: {key}")

# 2. Boxer Superstore Botshabelo (MASSIVE duplicates - 8 PMP, 6 RAW)
print("\n2. Boxer Superstore Botshabelo on 02/12/2025:")
print("-" * 100)
boxer = FoodSafetyAgencyInspection.objects.filter(
    client_name='Boxer Superstore Botshabelo',
    date_of_inspection=datetime(2025, 12, 2).date()
).order_by('commodity', 'product_name', 'remote_id')

print(f"Found {boxer.count()} total inspections:")

pmp = [i for i in boxer if i.commodity == 'PMP']
raw = [i for i in boxer if i.commodity == 'RAW']

print(f"\nPMP Inspections ({len(pmp)}):")
for idx, insp in enumerate(pmp, 1):
    key = (insp.inspector_name or '', insp.client_name or '', insp.commodity or '',
           str(insp.date_of_inspection), insp.product_name or '')
    print(f"  {idx}. ID={insp.remote_id} | Product='{insp.product_name}'")

print(f"\nRAW Inspections ({len(raw)}):")
for idx, insp in enumerate(raw, 1):
    key = (insp.inspector_name or '', insp.client_name or '', insp.commodity or '',
           str(insp.date_of_inspection), insp.product_name or '')
    print(f"  {idx}. ID={insp.remote_id} | Product='{insp.product_name}'")

# 3. Check if deduplication key would catch these
print("\n" + "=" * 100)
print("CHECKING DEDUPLICATION KEYS")
print("=" * 100)

# Apply deduplication logic to Boxer Superstore Botshabelo
seen = set()
unique = []
duplicates = []

for insp in boxer:
    key = (insp.inspector_name or '', insp.client_name or '', insp.commodity or '',
           str(insp.date_of_inspection), insp.product_name or '')
    if key in seen:
        duplicates.append((insp, key))
    else:
        seen.add(key)
        unique.append(insp)

print(f"\nBoxer Superstore Botshabelo deduplication results:")
print(f"  Total inspections:  {boxer.count()}")
print(f"  Unique inspections: {len(unique)}")
print(f"  Duplicates found:   {len(duplicates)}")

if duplicates:
    print(f"\n  Duplicate details:")
    for insp, key in duplicates[:5]:
        print(f"    - ID={insp.remote_id} | {insp.commodity} | {insp.product_name}")
        print(f"      Key: {key}")

print("\n" + "=" * 100)
