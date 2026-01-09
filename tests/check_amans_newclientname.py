#!/usr/bin/env python3
"""
Check what's in NewClientName for all PMP inspections on December 3rd
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
print("CHECKING NewClientName FOR ALL PMP INSPECTIONS ON DEC 3RD")
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

# Query all PMP inspections on Dec 3rd
print("[QUERY] Fetching all PMP inspections on December 3rd...")
cursor.execute("""
    SELECT
        rec.Id as InspectionId,
        rec.DateOfInspection,
        rec.InspectorId,
        prod.Id as ProductId,
        prod.ClientId,
        prod.NewClientName,
        clt.Name as OfficialClientName,
        prod.PMPItemDetails as ProductName,
        CASE WHEN EXISTS (SELECT 1 FROM AFS.dbo.PMPInspectionLabSampleLinks WHERE PMPInspectionLabSampleLinks.InspectionId = rec.Id) THEN 1 ELSE 0 END AS IsSampleTaken
    FROM [AFS].[dbo].[PMPInspectionRecordTypes] rec
    JOIN [AFS].[dbo].[PMPInspectedProductRecordTypes] prod ON prod.InspectionId = rec.Id
    JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
    WHERE rec.DateOfInspection = '2024-12-03'
    AND rec.IsActive = 1
    AND prod.PMPItemDetails IS NOT NULL
    AND prod.PMPItemDetails != ''
    ORDER BY prod.Id
""")

pmp_inspections = cursor.fetchall()
print(f"[DATA] Found {len(pmp_inspections)} PMP products on December 3rd\n")

print("="*80)
print("DETAILED LIST:")
print("="*80)

for idx, insp in enumerate(pmp_inspections, 1):
    print(f"\n[{idx}] Product ID: {insp['ProductId']}")
    print(f"    Inspection ID: {insp['InspectionId']}")
    print(f"    Client ID: {insp['ClientId']}")
    print(f"    Official Client Name (clt.Name): '{insp['OfficialClientName']}'")
    print(f"    NewClientName (prod.NewClientName): '{insp['NewClientName']}'")
    print(f"    Product: {insp['ProductName']}")
    print(f"    Sample Taken: {'Yes' if insp['IsSampleTaken'] else 'No'}")
    print(f"    COALESCE Result: '{insp['NewClientName'] if insp['NewClientName'] else insp['OfficialClientName']}'")

print("\n" + "="*80)
print("SEARCHING FOR 'AMANS'...")
print("="*80)

amans_found = []
for insp in pmp_inspections:
    newname = insp['NewClientName'] or ''
    officialname = insp['OfficialClientName'] or ''

    if 'amans' in newname.lower() or 'amans' in officialname.lower():
        amans_found.append(insp)

if amans_found:
    print(f"\n[FOUND] {len(amans_found)} PMP inspections containing 'Amans':")
    for insp in amans_found:
        print(f"\n   Product ID: {insp['ProductId']}")
        print(f"   NewClientName: '{insp['NewClientName']}'")
        print(f"   Official Name: '{insp['OfficialClientName']}'")
        print(f"   Product: {insp['ProductName']}")
else:
    print("\n[NOT FOUND] No PMP inspections containing 'Amans' on December 3rd")
    print("\nPossible reasons:")
    print("1. The Amans PMP inspection might be on a different date")
    print("2. The NewClientName might use a different spelling")
    print("3. The inspection might not be marked as Active")

# Also check RAW inspections for Amans
print("\n" + "="*80)
print("CHECKING RAW INSPECTIONS FOR 'AMANS'...")
print("="*80)

cursor.execute("""
    SELECT
        rec.Id as InspectionId,
        rec.DateOfInspection,
        prod.Id as ProductId,
        prod.NewClientName,
        clt.Name as OfficialClientName,
        prod.NewProductItemDetails as ProductName
    FROM [AFS].[dbo].[RawRMPInspectionRecordTypes] rec
    JOIN [AFS].[dbo].[RawRMPInspectedProductRecordTypes] prod ON prod.InspectionId = rec.Id
    JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
    WHERE rec.DateOfInspection = '2024-12-03'
    AND rec.IsActive = 1
    AND (LOWER(prod.NewClientName) LIKE '%amans%' OR LOWER(clt.Name) LIKE '%amans%')
""")

raw_amans = cursor.fetchall()
print(f"\n[DATA] Found {len(raw_amans)} RAW products with 'Amans' on December 3rd:")
for insp in raw_amans:
    print(f"\n   Product ID: {insp['ProductId']}")
    print(f"   NewClientName: '{insp['NewClientName']}'")
    print(f"   Official Name: '{insp['OfficialClientName']}'")
    print(f"   Product: {insp['ProductName']}")

cursor.close()
connection.close()

print("\n" + "="*80)
print("DONE")
print("="*80)
