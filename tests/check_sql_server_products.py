#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check SQL Server directly for product names of specific inspections
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

from django.conf import settings
import pymssql

print("=" * 80)
print("CHECKING SQL SERVER FOR PRODUCT NAMES")
print("=" * 80)

# Connect to SQL Server
sql_server_config = settings.DATABASES.get('sql_server', {})

print(f"\n📡 Connecting to SQL Server...")
print(f"   Server: {sql_server_config.get('HOST')}:{sql_server_config.get('PORT', 1433)}")
print(f"   Database: {sql_server_config.get('NAME')}\n")

try:
    connection = pymssql.connect(
        server=sql_server_config.get('HOST'),
        port=int(sql_server_config.get('PORT', 1433)),
        user=sql_server_config.get('USER'),
        password=sql_server_config.get('PASSWORD'),
        database=sql_server_config.get('NAME'),
        timeout=30
    )
    cursor = connection.cursor(as_dict=True)
    print("✅ Connected!\n")

    # Check specific inspections
    inspection_ids = [17082, 65201, 6520]

    for inspection_id in inspection_ids:
        print(f"[Inspection {inspection_id}]")
        print("-" * 80)

        # Get basic inspection info
        cursor.execute("""
            SELECT
                Id,
                Commodity,
                DateOfInspection,
                InternalAccountNumber
            FROM FSAInspections
            WHERE Id = %s
        """, (inspection_id,))

        inspection = cursor.fetchone()

        if inspection:
            print(f"   ✅ Found in SQL Server")
            print(f"   Commodity: {inspection.get('Commodity')}")
            print(f"   Date: {inspection.get('DateOfInspection')}")
            print(f"   Account Code: {inspection.get('InternalAccountNumber')}")

            # Get products for this inspection
            cursor.execute("""
                SELECT
                    ProductName
                FROM FSAInspectionProducts
                WHERE InspectionId = %s
                ORDER BY ProductName
            """, (inspection_id,))

            products = cursor.fetchall()

            if products:
                print(f"   Products found: {len(products)}")
                for i, prod in enumerate(products, 1):
                    print(f"      {i}. {prod.get('ProductName')}")
            else:
                print(f"   ❌ NO PRODUCTS FOUND in FSAInspectionProducts table")
                print(f"   → This inspection has no products in SQL Server!")

        else:
            print(f"   ❌ NOT FOUND in SQL Server")

        print()

    # Check how many inspections have no products
    print("\n" + "=" * 80)
    print("OVERALL STATISTICS")
    print("=" * 80)

    cursor.execute("""
        SELECT COUNT(DISTINCT i.Id) as TotalInspections
        FROM FSAInspections i
    """)
    total = cursor.fetchone()['TotalInspections']

    cursor.execute("""
        SELECT COUNT(DISTINCT i.Id) as InspectionsWithProducts
        FROM FSAInspections i
        INNER JOIN FSAInspectionProducts p ON i.Id = p.InspectionId
    """)
    with_products = cursor.fetchone()['InspectionsWithProducts']

    without_products = total - with_products

    print(f"\nTotal inspections in SQL Server: {total:,}")
    print(f"Inspections WITH products: {with_products:,} ({(with_products/total*100) if total > 0 else 0:.2f}%)")
    print(f"Inspections WITHOUT products: {without_products:,} ({(without_products/total*100) if total > 0 else 0:.2f}%)")

    cursor.close()
    connection.close()

    print("\n" + "=" * 80)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
