"""
Show egg products inspected at different places - FINAL VERSION
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import SQLServerConnection

print("=" * 80)
print("EGG PRODUCTS INSPECTED AT DIFFERENT PLACES")
print("=" * 80)

sql_conn = SQLServerConnection()
if not sql_conn.connect():
    print("[ERROR] Failed to connect to SQL Server")
    exit(1)

print("\n[OK] Connected to SQL Server")
cursor = sql_conn.connection.cursor()

# Get top clients with egg inspections
print("\n" + "=" * 80)
print("TOP CLIENTS WITH EGG INSPECTIONS")
print("=" * 80)

cursor.execute("""
    SELECT TOP 20
        c.Id,
        c.Name,
        c.InternalAccountNumber,
        COUNT(pe.Id) as InspectionCount
    FROM Clients c
    JOIN PoultryEggInspectionRecords pe ON c.Id = pe.ClientId
    GROUP BY c.Id, c.Name, c.InternalAccountNumber
    ORDER BY COUNT(pe.Id) DESC
""")

top_clients = cursor.fetchall()

print(f"\nTop 20 clients by egg inspection count:")
for i, (client_id, name, account_num, count) in enumerate(top_clients, 1):
    acc = account_num or "N/A"
    print(f"  {i:2d}. {name:50s} (Acc:{acc:10s}) - {count:4d} inspections")

# Get products inspected at a specific client
print("\n" + "=" * 80)
print("SAMPLE: Products Inspected at Top Client")
print("=" * 80)

if top_clients:
    top_client_id = top_clients[0][0]
    top_client_name = top_clients[0][1]

    print(f"\nClient: {top_client_name} (ID: {top_client_id})")

    cursor.execute(f"""
        SELECT
            pe.ClientBranch,
            pe.EggProducer,
            pe.SizeId,
            pe.GradeId,
            pe.BatchNumber,
            pe.BBDate,
            pe.DateOfInspection,
            pe.AverageWeight,
            pe.GeneralComments
        FROM PoultryEggInspectionRecords pe
        WHERE pe.ClientId = {top_client_id}
        AND pe.EggProducer IS NOT NULL
        AND pe.EggProducer != ''
        ORDER BY pe.DateOfInspection DESC
    """)

    products = cursor.fetchall()

    if products:
        print(f"\nFound {len(products)} egg products inspected:")
        for i, (branch, producer, size, grade, batch, bb_date, insp_date, avg_wt, comments) in enumerate(products[:10], 1):
            print(f"\n  {i}. Date: {insp_date}")
            print(f"     Branch: {branch or 'Main'}")
            print(f"     Producer: {producer}")
            print(f"     Size ID: {size}, Grade ID: {grade}")
            print(f"     Batch: {batch}, Best Before: {bb_date}")
            if avg_wt:
                print(f"     Avg Weight: {avg_wt}g")
            if comments:
                print(f"     Comments: {comments}")
    else:
        print("\n(No products with producer names)")

# Summary of all egg products
print("\n" + "=" * 80)
print("ALL EGG PRODUCTS SUMMARY")
print("=" * 80)

cursor.execute("""
    SELECT
        pe.EggProducer,
        COUNT(*) as TotalInspections,
        COUNT(DISTINCT pe.ClientId) as UniqueClients,
        MIN(pe.DateOfInspection) as FirstInspection,
        MAX(pe.DateOfInspection) as LastInspection
    FROM PoultryEggInspectionRecords pe
    WHERE pe.EggProducer IS NOT NULL AND pe.EggProducer != ''
    GROUP BY pe.EggProducer
    HAVING COUNT(*) > 3
    ORDER BY COUNT(*) DESC
""")

all_products = cursor.fetchall()

print(f"\n[FOUND] {len(all_products)} egg producers with 4+ inspections")
print("\nTop egg producers:")
for i, (producer, inspections, clients, first, last) in enumerate(all_products[:15], 1):
    print(f"  {i:2d}. {producer:40s}")
    print(f"      Inspections: {inspections:3d} | Clients: {clients:3d} | Period: {first.date()} to {last.date()}")

# Complete relationship structure
print("\n" + "=" * 80)
print("DATABASE STRUCTURE FOR EGG INSPECTIONS")
print("=" * 80)

print("""
PoultryEggInspectionRecords
├─ ClientId → Clients.Id
│   └─ Name (e.g., "Spar", "Pick n Pay")
├─ ClientBranch (e.g., "Knysna", "Somerset West")
├─ EggProducer (e.g., "Windmeul", "Nulaid", "Quantum Foods")
├─ SizeId (1=?, 2=?, 3=?, 4=Large, etc.)
├─ GradeId (1=A?, 2=B?, etc.)
├─ BatchNumber (batch identifier)
├─ BBDate (best before date)
├─ DateOfInspection (when inspected)
├─ AverageWeight (grams)
└─ InspectionRecordId → PoultryEggQualityCheckListEntryTypes
    ├─ SampleNumber
    ├─ WeightGrams
    ├─ HaughReadingmm (quality measure)
    └─ HaughValue

To find products inspected at a specific place:
1. Find client by name: SELECT Id FROM Clients WHERE Name LIKE '%searchterm%'
2. Get their inspections: SELECT * FROM PoultryEggInspectionRecords WHERE ClientId = ?
3. Product details: EggProducer, SizeId, GradeId, BatchNumber, BBDate
""")

print("\n[KEY TABLES]:")
print("  - Clients (5,000) - WHERE inspections happen")
print("  - PoultryEggInspectionRecords (7,293) - WHAT was inspected")
print("  - PoultryEggQualityCheckListEntryTypes (246,355) - Quality details")
print("  - PoultryEggPhotoLinkRecordTypes (21,110) - Photos")
print("  - PoultryEggInspectionSignatureTypes (26,531) - Signatures")

sql_conn.disconnect()

print("\n" + "=" * 80)
print("COMPLETE - Egg products and inspection locations mapped!")
print("=" * 80)
