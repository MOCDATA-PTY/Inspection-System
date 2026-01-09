import os
import sys
import django
from datetime import datetime
from collections import defaultdict

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 100)
print("EXPORT ANALYSIS - WHY SO MANY INSPECTIONS?")
print("=" * 100)

# Fetch inspections (same as export)
start = datetime(2025, 12, 1).date()
end = datetime(2025, 12, 10).date()

inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__in=['RAW', 'PMP'],
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=start,
    date_of_inspection__lte=end
).order_by('date_of_inspection', 'client_name', 'commodity')

# Apply deduplication
seen = set()
unique_inspections = []

for insp in inspections:
    key = (insp.inspector_name or '', insp.client_name or '', insp.commodity or '',
           str(insp.date_of_inspection), insp.product_name or '')
    if key not in seen:
        seen.add(key)
        unique_inspections.append(insp)

print(f"\nDate range: {start} to {end}")
print(f"Total unique inspections: {len(unique_inspections)}")
print("\n" + "=" * 100)

# 1. BREAKDOWN BY DATE
print("\n1. INSPECTIONS BY DATE")
print("-" * 100)
by_date = defaultdict(list)
for insp in unique_inspections:
    by_date[insp.date_of_inspection].append(insp)

for date in sorted(by_date.keys()):
    count = len(by_date[date])
    print(f"{date}: {count:3} inspections")

# 2. BREAKDOWN BY CLIENT (clients with most inspections)
print("\n" + "=" * 100)
print("\n2. TOP 20 CLIENTS WITH MOST INSPECTIONS")
print("-" * 100)
by_client = defaultdict(list)
for insp in unique_inspections:
    by_client[insp.client_name].append(insp)

top_clients = sorted(by_client.items(), key=lambda x: len(x[1]), reverse=True)[:20]
for client, insps in top_clients:
    print(f"{client:50} {len(insps):3} inspections")

# 3. CLIENTS WITH MULTIPLE INSPECTIONS ON SAME DATE
print("\n" + "=" * 100)
print("\n3. CLIENTS WITH MULTIPLE INSPECTIONS ON SAME DATE")
print("-" * 100)
client_date_groups = defaultdict(lambda: defaultdict(list))

for insp in unique_inspections:
    client_date_groups[insp.client_name][insp.date_of_inspection].append(insp)

multiple_same_date = []
for client, dates in client_date_groups.items():
    for date, insps in dates.items():
        if len(insps) > 1:
            multiple_same_date.append((client, date, insps))

# Sort by number of inspections on same date
multiple_same_date.sort(key=lambda x: len(x[2]), reverse=True)

print(f"\nFound {len(multiple_same_date)} cases where a client has multiple inspections on the same date")
print("\nTop 10 cases:")
for idx, (client, date, insps) in enumerate(multiple_same_date[:10], 1):
    print(f"\n{idx}. {client} on {date} - {len(insps)} inspections:")
    for insp in insps:
        print(f"   - {insp.commodity:6} | {insp.product_name:40} | Inspector: {insp.inspector_name}")

# 4. EXPLAIN WHY MULTIPLE INSPECTIONS ARE VALID
print("\n" + "=" * 100)
print("\n4. WHY ARE THERE MULTIPLE INSPECTIONS?")
print("-" * 100)
print("""
Multiple inspections at the same client on the same date are VALID when:

1. DIFFERENT PRODUCTS inspected
   - Example: Blou Bul Meat Market had 3 RAW inspections:
     * Mnandi Braaiwors
     * Boerewors
     * Choice Braaiwors
   - Each product requires separate testing and generates separate line items
   - Each product is billed separately

2. DIFFERENT COMMODITIES
   - Example: A client might have both RAW and PMP inspections on same day:
     * RAW: Beef Braaiwors
     * PMP: Smoked Russians
   - Different commodity types require different testing protocols

3. MULTIPLE INSPECTORS
   - Sometimes multiple inspectors visit the same client on the same day
   - Each inspection is logged separately

THIS IS CORRECT BEHAVIOR. Each inspection represents a billable service.
The deduplication ONLY removes true duplicates (same inspector, client, commodity,
date, AND product).
""")

# 5. LINE ITEMS BREAKDOWN
print("\n" + "=" * 100)
print("\n5. LINE ITEMS BREAKDOWN")
print("-" * 100)

total_line_items = 0
raw_count = 0
pmp_count = 0
with_lab = 0
without_lab = 0

for insp in unique_inspections:
    if insp.commodity == 'RAW':
        raw_count += 1
        # RAW generates 2 base items (050, 051) + optional lab items (052, 053)
        items = 2
        if insp.fat or insp.protein:
            items += 2
            with_lab += 1
        else:
            without_lab += 1
        total_line_items += items
    elif insp.commodity == 'PMP':
        pmp_count += 1
        # PMP generates 2 base items (060, 061) + optional lab items (062, 064)
        items = 2
        if insp.fat or insp.protein:
            items += 2
            with_lab += 1
        else:
            without_lab += 1
        total_line_items += items

print(f"Total inspections:          {len(unique_inspections)}")
print(f"  - RAW:                    {raw_count}")
print(f"  - PMP:                    {pmp_count}")
print(f"\nInspections with lab data:  {with_lab}")
print(f"Inspections without lab:    {without_lab}")
print(f"\nEstimated total line items: {total_line_items}")
print(f"  (Each inspection = 2-4 line items depending on lab samples)")

print("\n" + "=" * 100)
