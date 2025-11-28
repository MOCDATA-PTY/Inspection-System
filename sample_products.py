#!/usr/bin/env python
"""Pull 10 product samples from SQL Server tables"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

import pymssql
from django.conf import settings

print("=" * 120)
print("SQL SERVER PRODUCT SAMPLES - 10 rows from each table")
print("=" * 120)

# Connect to SQL Server
sql_config = settings.DATABASES.get('sql_server', {})
try:
    conn = pymssql.connect(
        server=sql_config.get('HOST'),
        port=int(sql_config.get('PORT', 1433)),
        user=sql_config.get('USER'),
        password=sql_config.get('PASSWORD'),
        database=sql_config.get('NAME'),
        timeout=10
    )
    print("\n[OK] Connected to SQL Server\n")
    cursor = conn.cursor()
except Exception as e:
    print(f"\n[ERROR] Failed to connect: {e}")
    exit(1)

# PMP Products
print("=" * 120)
print("PMP PRODUCTS (PMPInspectedProductRecordTypes)")
print("=" * 120)
print(f"{'Id':<8} {'InspectionId':<15} {'ClientId':<10} {'PMPItemDetails (Product Name)':<50}")
print("-" * 120)

query = """
SELECT TOP 10 Id, InspectionId, ClientId, PMPItemDetails
FROM PMPInspectedProductRecordTypes
WHERE PMPItemDetails IS NOT NULL AND PMPItemDetails != ''
ORDER BY Id DESC
"""
cursor.execute(query)
for row in cursor.fetchall():
    print(f"{row[0]:<8} {row[1]:<15} {row[2]:<10} {row[3]:<50}")

# Raw Products
print("\n" + "=" * 120)
print("RAW PRODUCTS (RawRMPInspectedProductRecordTypes)")
print("=" * 120)
print(f"{'Id':<8} {'InspectionId':<15} {'ClientId':<10} {'NewProductItemDetails (Product Name)':<50}")
print("-" * 120)

query = """
SELECT TOP 10 Id, InspectionId, ClientId, NewProductItemDetails
FROM RawRMPInspectedProductRecordTypes
WHERE NewProductItemDetails IS NOT NULL AND NewProductItemDetails != ''
ORDER BY Id DESC
"""
cursor.execute(query)
for row in cursor.fetchall():
    print(f"{row[0]:<8} {row[1]:<15} {row[2]:<10} {row[3]:<50}")

# Poultry Grading
print("\n" + "=" * 120)
print("POULTRY GRADING (PoultryGradingInspectionRecordTypes)")
print("=" * 120)
print(f"{'Id':<8} {'ClientId':<10} {'NewClientName':<30} {'DateOfInspection':<20} {'ProductName':<30}")
print("-" * 120)

query = """
SELECT TOP 10 Id, ClientId, NewClientName, DateOfInspection, ProductName
FROM PoultryGradingInspectionRecordTypes
WHERE ProductName IS NOT NULL AND ProductName != ''
ORDER BY Id DESC
"""
cursor.execute(query)
for row in cursor.fetchall():
    client_name = (row[2] or 'NULL')[:30]
    date = str(row[3])[:20] if row[3] else 'NULL'
    product = (row[4] or 'NULL')[:30]
    print(f"{row[0]:<8} {row[1]:<10} {client_name:<30} {date:<20} {product:<30}")

# Poultry Label
print("\n" + "=" * 120)
print("POULTRY LABEL (PoultryLabelInspectionChecklistRecords)")
print("=" * 120)
print(f"{'Id':<8} {'ClientId':<10} {'NewClientName':<30} {'DateOfInspection':<20} {'ProductName':<30}")
print("-" * 120)

query = """
SELECT TOP 10 Id, ClientId, NewClientName, DateOfInspection, ProductName
FROM PoultryLabelInspectionChecklistRecords
WHERE ProductName IS NOT NULL AND ProductName != ''
ORDER BY Id DESC
"""
cursor.execute(query)
for row in cursor.fetchall():
    client_name = (row[2] or 'NULL')[:30]
    date = str(row[3])[:20] if row[3] else 'NULL'
    product = (row[4] or 'NULL')[:30]
    print(f"{row[0]:<8} {row[1]:<10} {client_name:<30} {date:<20} {product:<30}")

# Poultry QUID
print("\n" + "=" * 120)
print("POULTRY QUID (PoultryQuidInspectionRecordTypes)")
print("=" * 120)
print(f"{'Id':<8} {'ClientId':<10} {'NewClientName':<30} {'DateOfInspection':<20} {'ProductName':<30}")
print("-" * 120)

query = """
SELECT TOP 10 Id, ClientId, NewClientName, DateOfInspection, ProductName
FROM PoultryQuidInspectionRecordTypes
WHERE ProductName IS NOT NULL AND ProductName != ''
ORDER BY Id DESC
"""
cursor.execute(query)
for row in cursor.fetchall():
    client_name = (row[2] or 'NULL')[:30]
    date = str(row[3])[:20] if row[3] else 'NULL'
    product = (row[4] or 'NULL')[:30]
    print(f"{row[0]:<8} {row[1]:<10} {client_name:<30} {date:<20} {product:<30}")

cursor.close()
conn.close()

print("\n" + "=" * 120)
print("DONE")
print("=" * 120)
