"""
Test the OUTER APPLY query directly on SQL Server to see what it returns
This will show us if the problem is the query itself or Django processing
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/root/Inspection-System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
import pymssql

print("=" * 80)
print("TESTING QUERY DIRECTLY ON SQL SERVER")
print("=" * 80)

# Import the query
from main.views.data_views import FSA_INSPECTION_QUERY

# Connect to SQL Server
sql_server_config = settings.DATABASES.get('sql_server', {})

print(f"\nConnecting to SQL Server...")
print(f"  Host: {sql_server_config.get('HOST')}")
print(f"  Port: {sql_server_config.get('PORT', 1433)}")
print(f"  Database: {sql_server_config.get('NAME')}")

connection = pymssql.connect(
    server=sql_server_config.get('HOST'),
    port=int(sql_server_config.get('PORT', 1433)),
    user=sql_server_config.get('USER'),
    password=sql_server_config.get('PASSWORD'),
    database=sql_server_config.get('NAME'),
    timeout=30
)
cursor = connection.cursor(as_dict=True)
print("  ✓ Connected successfully")

print(f"\nExecuting FSA_INSPECTION_QUERY...")
cursor.execute(FSA_INSPECTION_QUERY)

rows = cursor.fetchall()
total_rows = len(rows)

print(f"\n{'='*80}")
print(f"QUERY RESULTS FROM SQL SERVER")
print(f"{'='*80}")
print(f"\nTotal rows returned: {total_rows:,}")

# Check for duplicate (commodity, remote_id) pairs
print(f"\nChecking for duplicates by (commodity, remote_id)...")

seen = {}
duplicates = {}

for row in rows:
    commodity = row.get('Commodity')
    remote_id = row.get('Id')
    key = (commodity, remote_id)

    if key in seen:
        if key not in duplicates:
            duplicates[key] = []
        duplicates[key].append(row)
    else:
        seen[key] = row

unique_count = len(seen)
duplicate_count = len(duplicates)

print(f"\nUnique (commodity, remote_id) pairs: {unique_count:,}")
print(f"Duplicate (commodity, remote_id) pairs: {duplicate_count:,}")

if duplicate_count > 0:
    print(f"\n❌ PROBLEM FOUND: SQL Server query is returning duplicates!")
    print(f"\nFirst 5 duplicates:")
    for i, (key, dup_rows) in enumerate(list(duplicates.items())[:5]):
        commodity, remote_id = key
        print(f"\n  {i+1}. {commodity}-{remote_id} appears {len(dup_rows) + 1} times:")
        # Show the first occurrence
        first = seen[key]
        print(f"      Product: {first.get('ProductName', 'N/A')}")
        print(f"      Client: {first.get('Client', 'N/A')}")
        print(f"      GPS: ({first.get('Latitude', 'N/A')}, {first.get('Longitude', 'N/A')})")

    print(f"\n❌ The OUTER APPLY is NOT preventing duplicates!")
    print(f"   There must be an issue with the query logic.")
else:
    print(f"\n✓ No duplicates found in SQL Server results")
    print(f"  The query is working correctly at the SQL Server level")

# Check for inspection with multiple products (expected behavior)
print(f"\n{'='*80}")
print(f"CHECKING PRODUCT DISTRIBUTION")
print(f"{'='*80}")

# Group by inspection ID only (not commodity + ID)
inspection_products = {}
for row in rows:
    # For inspections, we want to count by inspection ID alone
    # since one inspection can have multiple products
    commodity = row.get('Commodity')
    remote_id = row.get('Id')
    product = row.get('ProductName')

    insp_key = (commodity, remote_id)
    if insp_key not in inspection_products:
        inspection_products[insp_key] = []
    inspection_products[insp_key].append(product)

# Show inspections with multiple products
multi_product = {k: v for k, v in inspection_products.items() if len(v) > 1}

print(f"\nInspections with multiple products: {len(multi_product):,}")
print(f"  (This is EXPECTED - one inspection can check multiple products)")

if multi_product:
    print(f"\nTop 5 inspections by product count:")
    sorted_multi = sorted(multi_product.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    for (commodity, remote_id), products in sorted_multi:
        print(f"  {commodity}-{remote_id}: {len(products)} products")
        for p in products[:3]:  # Show first 3 products
            print(f"    - {p}")
        if len(products) > 3:
            print(f"    ... and {len(products) - 3} more")

print(f"\n{'='*80}")
print(f"CONCLUSION")
print(f"{'='*80}")

if duplicate_count > 0:
    print(f"\n❌ SQL Server is returning {total_rows:,} rows")
    print(f"❌ But only {unique_count:,} are unique (commodity, remote_id) pairs")
    print(f"❌ This means the OUTER APPLY is NOT working correctly")
    print(f"\nPossible causes:")
    print(f"  1. OUTER APPLY syntax issue with SQL Server version")
    print(f"  2. Query logic error")
    print(f"  3. Data issue in SQL Server tables")
else:
    print(f"\n✓ SQL Server is returning {total_rows:,} rows")
    print(f"✓ All {unique_count:,} are unique (commodity, remote_id) pairs")
    print(f"✓ The OUTER APPLY query is working correctly!")
    print(f"\nIf Django is creating 6k+ records, the issue is in Django processing,")
    print(f"not in the SQL Server query itself.")

print(f"{'='*80}")

connection.close()
