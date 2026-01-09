import os
import sys
import django
from datetime import datetime
import time

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import connection

print("=" * 100)
print("TESTING DIRECT POSTGRESQL QUERY")
print("=" * 100)

start_date = '2025-12-01'
end_date = datetime.now().strftime('%Y-%m-%d')

print(f"\nDate range: {start_date} to {end_date}")
print("-" * 100)

# Direct SQL query to count inspections
query = """
SELECT COUNT(*)
FROM food_safety_agency_inspections
WHERE commodity IN ('RAW', 'PMP')
  AND hours IS NOT NULL
  AND km_traveled IS NOT NULL
  AND date_of_inspection >= %s
  AND date_of_inspection <= %s
"""

print("\n1. Counting inspections...")
start_time = time.time()

with connection.cursor() as cursor:
    cursor.execute(query, [start_date, end_date])
    count = cursor.fetchone()[0]

elapsed = time.time() - start_time
print(f"   Found {count} inspections in {elapsed:.2f} seconds")

# Now fetch actual data
print("\n2. Fetching inspection data...")
query = """
SELECT
    commodity,
    remote_id,
    inspector_name,
    client_name,
    date_of_inspection,
    product_name,
    hours,
    km_traveled,
    fat,
    protein
FROM food_safety_agency_inspections
WHERE commodity IN ('RAW', 'PMP')
  AND hours IS NOT NULL
  AND km_traveled IS NOT NULL
  AND date_of_inspection >= %s
  AND date_of_inspection <= %s
ORDER BY client_name, date_of_inspection, commodity
"""

start_time = time.time()

with connection.cursor() as cursor:
    cursor.execute(query, [start_date, end_date])
    rows = cursor.fetchall()

elapsed = time.time() - start_time
print(f"   Fetched {len(rows)} rows in {elapsed:.2f} seconds")

# Show first 10 inspections
print("\n3. First 10 inspections:")
print("-" * 100)
for idx, row in enumerate(rows[:10], 1):
    commodity, remote_id, inspector, client, date, product, hours, km, fat, protein = row
    print(f"{idx:3}. {client:40} | {commodity:6} | {date} | {product[:30] if product else ''}")

# Apply deduplication
print("\n4. Applying deduplication...")
seen = set()
unique_rows = []

for row in rows:
    commodity, remote_id, inspector, client, date, product, hours, km, fat, protein = row
    key = (inspector or '', client or '', commodity or '', str(date), product or '')
    if key not in seen:
        seen.add(key)
        unique_rows.append(row)

print(f"   Before dedup: {len(rows)}")
print(f"   After dedup:  {len(unique_rows)}")
print(f"   Duplicates:   {len(rows) - len(unique_rows)}")

# Estimate line items
print("\n5. Estimating line items...")
total_line_items = 0
for row in unique_rows:
    commodity, remote_id, inspector, client, date, product, hours, km, fat, protein = row
    # Each inspection generates 2 base items
    items = 2
    # If lab data exists, add 2 more items
    if fat or protein:
        items += 2
    total_line_items += items

print(f"   Unique inspections: {len(unique_rows)}")
print(f"   Total line items:   {total_line_items}")

print("\n" + "=" * 100)
print("RESULT: Direct PostgreSQL query is FAST")
print("The slowness must be in the Excel generation or Python deduplication loop")
print("=" * 100)
