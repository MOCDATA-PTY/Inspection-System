#!/usr/bin/env python3
"""
Check PMP table structure to find NewClientName field
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
import pymssql

print("="*80)
print("CHECKING PMP TABLE STRUCTURE")
print("="*80)

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
print("[OK] Connected to SQL Server\n")

# Check PMPInspectionRecordTypes table
print("[STEP 1] Checking PMPInspectionRecordTypes table columns...")
cursor.execute("""
    SELECT TOP 1 *
    FROM [AFS].[dbo].[PMPInspectionRecordTypes]
    WHERE DateOfInspection = '2024-12-03'
""")

row = cursor.fetchone()
if row:
    print("   Columns in PMPInspectionRecordTypes:")
    for key in row.keys():
        print(f"      - {key}: {row[key]}")

# Check PMPInspectedProductRecordTypes table
print("\n[STEP 2] Checking PMPInspectedProductRecordTypes table columns...")
cursor.execute("""
    SELECT TOP 1 *
    FROM [AFS].[dbo].[PMPInspectedProductRecordTypes] prod
    JOIN [AFS].[dbo].[PMPInspectionRecordTypes] rec ON prod.InspectionId = rec.Id
    WHERE rec.DateOfInspection = '2024-12-03'
""")

row = cursor.fetchone()
if row:
    print("   Columns in PMPInspectedProductRecordTypes:")
    for key in row.keys():
        print(f"      - {key}: {row[key]}")

# Now search for inspections with NewClientName containing "Amans"
print("\n[STEP 3] Searching for inspections with NewClientName containing 'Amans'...")
cursor.execute("""
    SELECT rec.Id, rec.DateOfInspection, rec.NewClientName,
           clt.Name as OfficialClientName, clt.Id as ClientId,
           prod.PMPItemDetails as ProductName
    FROM [AFS].[dbo].[PMPInspectionRecordTypes] rec
    JOIN [AFS].[dbo].[PMPInspectedProductRecordTypes] prod ON prod.InspectionId = rec.Id
    JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
    WHERE rec.DateOfInspection = '2024-12-03'
    AND rec.NewClientName LIKE '%Amans%'
""")

amans_rows = cursor.fetchall()
print(f"   Found {len(amans_rows)} PMP products with 'Amans' in NewClientName on Dec 3rd:")
for row in amans_rows:
    print(f"\n      Inspection ID: {row['Id']}")
    print(f"      Date: {row['DateOfInspection']}")
    print(f"      NewClientName (typed by inspector): {row['NewClientName']}")
    print(f"      Official Client Name: {row['OfficialClientName']}")
    print(f"      Client ID: {row['ClientId']}")
    print(f"      Product: {row['ProductName']}")

# Also check RAW table
print("\n[STEP 4] Checking RAW table for NewClientName...")
cursor.execute("""
    SELECT rec.Id, rec.DateOfInspection, rec.NewClientName,
           clt.Name as OfficialClientName, clt.Id as ClientId,
           prod.NewProductItemDetails as ProductName
    FROM [AFS].[dbo].[RawRMPInspectionRecordTypes] rec
    JOIN [AFS].[dbo].[RawRMPInspectedProductRecordTypes] prod ON prod.InspectionId = rec.Id
    JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
    WHERE rec.DateOfInspection = '2024-12-03'
    AND rec.NewClientName LIKE '%Amans%'
""")

raw_rows = cursor.fetchall()
print(f"   Found {len(raw_rows)} RAW products with 'Amans' in NewClientName on Dec 3rd:")
for row in raw_rows:
    print(f"\n      Inspection ID: {row['Id']}")
    print(f"      Date: {row['DateOfInspection']}")
    print(f"      NewClientName (typed by inspector): {row['NewClientName']}")
    print(f"      Official Client Name: {row['OfficialClientName']}")
    print(f"      Client ID: {row['ClientId']}")
    print(f"      Product: {row['ProductName']}")

cursor.close()
connection.close()

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
print("The FSA_INSPECTION_QUERY uses clt.Name (official client name)")
print("But inspectors type custom names in rec.NewClientName field")
print("We need to update the query to use NewClientName instead of clt.Name")
print("OR use NewClientName when it's available and fall back to clt.Name")
print("="*80)
