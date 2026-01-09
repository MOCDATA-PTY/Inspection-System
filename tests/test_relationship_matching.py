#!/usr/bin/env python3
"""
Test relationship-based client name matching locally on SQLite
"""
import os
import sys
import django
import sqlite3
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
import pymssql

# FSA_INSPECTION_QUERY from data_views.py (simplified for testing)
FSA_INSPECTION_QUERY = """
SELECT 'POULTRY' as Commodity, DateOfInspection, InspectorId,
       IsDirectionPresentForthisInspection, NULL AS IsSampleTaken,
       [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].Id as Id,
       clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber,
       [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ProductName as ProductName
FROM AFS.dbo.PoultryLabelInspectionChecklistRecords
join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ClientId
where AFS.dbo.[PoultryLabelInspectionChecklistRecords].IsActive = 1
AND DateOfInspection >= '2024-12-01'
AND [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ProductName IS NOT NULL
AND [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ProductName != ''
UNION ALL
SELECT 'EGGS' as Commodity, DateOfInspection, InspectorId,
       IsDirectionPresentForInspection as IsDirectionPresentForthisInspection,
       NULL AS IsSampleTaken,
       [AFS].[dbo].[PoultryEggInspectionRecords].Id as Id,
       clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber,
       [AFS].[dbo].[PoultryEggInspectionRecords].EggProducer as ProductName
FROM [AFS].[dbo].[PoultryEggInspectionRecords]
join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].[PoultryEggInspectionRecords].ClientId
where AFS.dbo.[PoultryEggInspectionRecords].IsActive = 1
AND DateOfInspection >= '2024-12-01'
UNION ALL
SELECT 'RAW' as Commodity, DateOfInspection, InspectorId,
       IsDirectionPresentForthisInspection,
       CASE WHEN EXISTS (SELECT 1 FROM AFS.dbo.RawRMPInspectionLabSampleLinks WHERE RawRMPInspectionLabSampleLinks.InspectionId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id) THEN 1 ELSE 0 END AS IsSampleTaken,
       [AFS].[dbo].[RawRMPInspectionRecordTypes].Id as Id,
       COALESCE(prod.NewClientName, clt.Name) as Client, clt.InternalAccountNumber as InternalAccountNumber,
       prod.NewProductItemDetails as ProductName
FROM [AFS].[dbo].[RawRMPInspectionRecordTypes]
JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod on prod.InspectionId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id
join AFS.dbo.Clients clt on clt.Id = prod.ClientId
where AFS.dbo.[RawRMPInspectionRecordTypes].IsActive = 1
AND DateOfInspection >= '2024-12-01'
AND prod.NewProductItemDetails IS NOT NULL
AND prod.NewProductItemDetails != ''
UNION ALL
SELECT 'PMP' as Commodity, DateOfInspection, InspectorId,
       IsDirectionPresentForthisInspection,
       CASE WHEN EXISTS (SELECT 1 FROM AFS.dbo.PMPInspectionLabSampleLinks WHERE PMPInspectionLabSampleLinks.InspectionId = [AFS].[dbo].[PMPInspectionRecordTypes].Id) THEN 1 ELSE 0 END AS IsSampleTaken,
       [AFS].[dbo].[PMPInspectionRecordTypes].Id as Id,
       COALESCE(prod.NewClientName, clt.Name) as Client, clt.InternalAccountNumber as InternalAccountNumber,
       prod.PMPItemDetails as ProductName
FROM [AFS].[dbo].[PMPInspectionRecordTypes]
JOIN AFS.dbo.PMPInspectedProductRecordTypes prod on prod.InspectionId = [AFS].[dbo].[PMPInspectionRecordTypes].Id
join AFS.dbo.Clients clt on clt.Id = prod.ClientId
where AFS.dbo.[PMPInspectionRecordTypes].IsActive = 1
AND DateOfInspection >= '2024-12-01'
AND prod.PMPItemDetails IS NOT NULL
AND prod.PMPItemDetails != ''
ORDER BY DateOfInspection DESC, Commodity, Id
"""

print("="*80)
print("TESTING RELATIONSHIP-BASED CLIENT NAME MATCHING")
print("="*80)

# Connect to SQL Server
print("\n[STEP 1] Connecting to SQL Server...")
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
print("[OK] Connected to SQL Server")

# Fetch December inspections
print("\n[STEP 2] Fetching December inspections from SQL Server...")
cursor.execute(FSA_INSPECTION_QUERY)
sql_inspections = cursor.fetchall()
print(f"[DATA] Retrieved {len(sql_inspections)} inspections")

# Filter for Amans-related inspections on December 3rd
print("\n[STEP 3] Filtering for December 3rd inspections...")
dec_3_inspections = [
    insp for insp in sql_inspections
    if insp['DateOfInspection'] and insp['DateOfInspection'].date() == datetime(2024, 12, 3).date()
]
print(f"[DATA] Found {len(dec_3_inspections)} inspections on December 3rd")

# Show all unique client names on December 3rd
print("\n[STEP 4] Analyzing client names on December 3rd...")
unique_clients_dec3 = {}  # client_name -> list of inspections
for insp in dec_3_inspections:
    client = insp['Client']
    if client not in unique_clients_dec3:
        unique_clients_dec3[client] = []
    unique_clients_dec3[client].append(insp)

print(f"[DATA] Found {len(unique_clients_dec3)} unique client names on Dec 3rd:")
for client, inspections in unique_clients_dec3.items():
    commodities = {}
    for insp in inspections:
        commodity = insp['Commodity']
        if commodity not in commodities:
            commodities[commodity] = 0
        commodities[commodity] += 1

    commodity_str = ", ".join([f"{count} {comm}" for comm, count in commodities.items()])
    print(f"   - '{client}': {len(inspections)} products ({commodity_str})")

# Search for Amans-related names
print("\n[STEP 5] Searching for Amans-related inspections...")
amans_related = {}
for client, inspections in unique_clients_dec3.items():
    if 'amans' in client.lower():
        amans_related[client] = inspections
        print(f"   [FOUND] '{client}':")
        for insp in inspections:
            print(f"      - {insp['Commodity']} product ID {insp['Id']}: {insp['ProductName']}")

# Test relationship matching
print("\n[STEP 6] Testing relationship-based matching...")
print("   Checking all pairs of client names on December 3rd...")

client_names_dec3 = list(unique_clients_dec3.keys())
relationships = []

for i, name1 in enumerate(client_names_dec3):
    for name2 in client_names_dec3[i+1:]:
        name1_lower = name1.lower()
        name2_lower = name2.lower()

        if name2_lower in name1_lower:
            relationships.append({
                'variant': name1,
                'canonical': name2,
                'reason': f"'{name1}' contains '{name2}'"
            })
            print(f"\n   [MATCH] Found relationship:")
            print(f"      Variant: '{name1}'")
            print(f"      Canonical: '{name2}'")
            print(f"      Reason: {relationships[-1]['reason']}")
        elif name1_lower in name2_lower:
            relationships.append({
                'variant': name2,
                'canonical': name1,
                'reason': f"'{name2}' contains '{name1}'"
            })
            print(f"\n   [MATCH] Found relationship:")
            print(f"      Variant: '{name2}'")
            print(f"      Canonical: '{name1}'")
            print(f"      Reason: {relationships[-1]['reason']}")

print(f"\n[STATS] Found {len(relationships)} relationships on December 3rd")

# Create SQLite test database
print("\n[STEP 7] Creating test SQLite database...")
test_db = 'test_relationship_matching.sqlite3'
if os.path.exists(test_db):
    os.remove(test_db)

conn_sqlite = sqlite3.connect(test_db)
c_sqlite = conn_sqlite.cursor()

# Create table matching Django model structure
c_sqlite.execute('''
    CREATE TABLE inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        commodity TEXT,
        remote_id INTEGER,
        date_of_inspection TEXT,
        client_name TEXT,
        product_name TEXT,
        inspector_name TEXT,
        is_sample_taken INTEGER
    )
''')

print(f"[OK] Created test database: {test_db}")

# Insert December 3rd inspections into SQLite
print("\n[STEP 8] Inserting December 3rd inspections into test database...")
INSPECTOR_MAP = {
    177: 'CINGA NGONGO',
    # Add other inspectors as needed
}

for insp in dec_3_inspections:
    inspector_name = INSPECTOR_MAP.get(insp['InspectorId'], 'Unknown')
    c_sqlite.execute('''
        INSERT INTO inspections (commodity, remote_id, date_of_inspection, client_name, product_name, inspector_name, is_sample_taken)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        insp['Commodity'],
        insp['Id'],
        str(insp['DateOfInspection'].date()),
        insp['Client'],
        insp['ProductName'],
        inspector_name,
        1 if insp['IsSampleTaken'] else 0
    ))

conn_sqlite.commit()
inserted_count = c_sqlite.execute('SELECT COUNT(*) FROM inspections').fetchone()[0]
print(f"[OK] Inserted {inserted_count} inspections")

# Apply relationship matching to SQLite database
print("\n[STEP 9] Applying relationship matching to test database...")
if relationships:
    for rel in relationships:
        variant = rel['variant']
        canonical = rel['canonical']

        c_sqlite.execute('''
            UPDATE inspections SET client_name = ? WHERE client_name = ?
        ''', (canonical, variant))

        updated = c_sqlite.rowcount
        print(f"   Updated {updated} inspections: '{variant}' -> '{canonical}'")

    conn_sqlite.commit()
else:
    print("   [INFO] No relationships to apply")

# Show results
print("\n[STEP 10] Final results for Amans on December 3rd...")
c_sqlite.execute('''
    SELECT * FROM inspections
    WHERE date_of_inspection = '2024-12-03'
    AND LOWER(client_name) LIKE '%amans%'
    ORDER BY commodity, remote_id
''')

amans_results = c_sqlite.fetchall()
print(f"[RESULT] Found {len(amans_results)} products for Amans:")

for row in amans_results:
    print(f"\n   Product ID: {row[2]}")
    print(f"   Commodity: {row[1]}")
    print(f"   Client: {row[4]}")
    print(f"   Product: {row[5]}")
    print(f"   Sample Taken: {'Yes' if row[7] else 'No'}")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"SQL Server has {len(dec_3_inspections)} inspections on December 3rd")
print(f"Found {len(amans_related)} Amans-related client names in SQL Server")
print(f"Relationship matching found {len(relationships)} name relationships")
print(f"After matching, {len(amans_results)} products linked to Amans")

if len(amans_results) > 2:
    print("\n✅ SUCCESS: Found PMP products after relationship matching!")
else:
    print("\n❌ PROBLEM: Only found RAW products, PMP missing")
    print("\nLet's check what PMP inspections exist on Dec 3rd:")
    c_sqlite.execute('''
        SELECT * FROM inspections
        WHERE date_of_inspection = '2024-12-03'
        AND commodity = 'PMP'
        ORDER BY client_name
    ''')
    pmp_results = c_sqlite.fetchall()
    print(f"Found {len(pmp_results)} PMP inspections on Dec 3rd:")
    for row in pmp_results:
        print(f"   - Client: '{row[4]}', Product: {row[5]}")

# Cleanup
cursor.close()
connection.close()
conn_sqlite.close()

print(f"\n[INFO] Test database saved to: {test_db}")
print("="*80)
