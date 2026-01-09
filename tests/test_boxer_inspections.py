"""
Test script to check ONLY Boxer Superstore Sibasa inspections on 03/12/2025
Inspection IDs: 6596, 6597, 17125, 8684
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

import pymssql
from django.conf import settings
from main.views.data_views import FSA_INSPECTION_QUERY

print("=" * 100)
print("TESTING BOXER SUPERSTORE SIBASA INSPECTIONS - 03/12/2025")
print("=" * 100)

# Connect to SQL Server
sql_server_config = settings.DATABASES.get('sql_server', {})
connection = pymssql.connect(
    server=sql_server_config.get('HOST'),
    port=int(sql_server_config.get('PORT', 1433)),
    user=sql_server_config.get('USER'),
    password=sql_server_config.get('PASSWORD'),
    database=sql_server_config.get('NAME'),
    timeout=30
)
cursor = connection.cursor(as_dict=True)

# Test inspection IDs
test_ids = [6596, 6597, 17125, 8684]

print("\n1. CHECKING RAW SQL SERVER DATA (Direct Table Queries)")
print("=" * 100)

# Check each table directly
tables_to_check = [
    ('PoultryQuidInspectionRecordTypes', 'ProductName'),
    ('PoultryGradingInspectionRecordTypes', 'ProductName'),
    ('PoultryLabelInspectionChecklistRecords', 'ProductName'),
    ('PoultryEggInspectionRecords', 'EggProducer'),
    ('PMPInspectionRecordTypes', None),  # No ProductName in main table
    ('RawRMPInspectionRecordTypes', None),  # No ProductName in main table
]

for table, product_col in tables_to_check:
    print(f"\n{table}:")
    for test_id in test_ids:
        try:
            if product_col:
                query = f"SELECT Id, DateOfInspection, {product_col} FROM AFS.dbo.{table} WHERE Id = {test_id}"
            else:
                query = f"SELECT Id, DateOfInspection FROM AFS.dbo.{table} WHERE Id = {test_id}"

            cursor.execute(query)
            row = cursor.fetchone()

            if row:
                if product_col:
                    print(f"  Id {test_id}: {product_col} = '{row[product_col]}'")
                else:
                    print(f"  Id {test_id}: FOUND (no product in main table)")
            else:
                print(f"  Id {test_id}: NOT FOUND")
        except Exception as e:
            print(f"  Id {test_id}: ERROR - {e}")

# Check product tables for PMP and RMP
print(f"\nPMPInspectedProductRecordTypes (products for PMP inspections):")
for test_id in test_ids:
    try:
        query = f"""
            SELECT InspectionId, PMPItemDetails
            FROM AFS.dbo.PMPInspectedProductRecordTypes
            WHERE InspectionId = {test_id}
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            products = [row['PMPItemDetails'] for row in rows]
            print(f"  InspectionId {test_id}: {len(products)} products = {products}")
        else:
            print(f"  InspectionId {test_id}: NOT FOUND")
    except Exception as e:
        print(f"  InspectionId {test_id}: ERROR - {e}")

print(f"\nRawRMPInspectedProductRecordTypes (products for RMP inspections):")
for test_id in test_ids:
    try:
        query = f"""
            SELECT InspectionId, NewProductItemDetails
            FROM AFS.dbo.RawRMPInspectedProductRecordTypes
            WHERE InspectionId = {test_id}
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            products = [row['NewProductItemDetails'] for row in rows]
            print(f"  InspectionId {test_id}: {len(products)} products = {products}")
        else:
            print(f"  InspectionId {test_id}: NOT FOUND")
    except Exception as e:
        print(f"  InspectionId {test_id}: ERROR - {e}")

print("\n" + "=" * 100)
print("\n2. CHECKING FSA_INSPECTION_QUERY RESULTS (What Our Code Sees)")
print("=" * 100)

# Execute the full query
cursor.execute(FSA_INSPECTION_QUERY)
all_results = cursor.fetchall()

# Filter for our test IDs
boxer_results = [r for r in all_results if r.get('Id') in test_ids]

print(f"\nTotal rows in FSA_INSPECTION_QUERY: {len(all_results)}")
print(f"Rows for test inspection IDs: {len(boxer_results)}")

for result in sorted(boxer_results, key=lambda x: x.get('Id')):
    print(f"\n{'=' * 80}")
    print(f"Inspection ID: {result.get('Id')}")
    print(f"Commodity: {result.get('Commodity')}")
    print(f"Client: {result.get('Client')}")
    print(f"AccountNumber: {result.get('InternalAccountNumber')}")
    print(f"DateOfInspection: {result.get('DateOfInspection')}")
    print(f"ProductName: '{result.get('ProductName')}'")
    print(f"{'=' * 80}")

print("\n" + "=" * 100)
print("\n3. ANALYSIS")
print("=" * 100)

# Count by ID
from collections import Counter
id_counts = Counter(r.get('Id') for r in boxer_results)

print(f"\nInspection ID occurrences in query results:")
for test_id, count in sorted(id_counts.items()):
    print(f"  Id {test_id}: appears {count} time(s)")
    if count > 1:
        print(f"    ❌ DUPLICATE! Same ID appears multiple times in query")
        commodities = [r.get('Commodity') for r in boxer_results if r.get('Id') == test_id]
        print(f"    Commodities: {commodities}")

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)

print(f"""
Expected from user's screenshot:
- 6596: POULTRY_LABEL with "Dhanya wors, Fresh Chicken Whole, game Biltong"
- 6597: POULTRY_LABEL with "Boxer Boerewors, Cooked Salami, Fresh Chicken Gizzards"
- 17125: EGGS with "Medium Grade A Eggs"
- 8684: PMP with (product name cut off in screenshot)

What FSA_INSPECTION_QUERY returns:
- Check the results above to see if they match
""")

cursor.close()
connection.close()
print("\n" + "=" * 100)
