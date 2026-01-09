"""
Map all relationships for PoultryEggInspectionRecords - FIXED VERSION
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import SQLServerConnection

print("=" * 80)
print("MAPPING EGG INSPECTION RELATIONSHIPS")
print("=" * 80)

sql_conn = SQLServerConnection()
if not sql_conn.connect():
    print("[ERROR] Failed to connect to SQL Server")
    exit(1)

print("\n[OK] Connected to SQL Server (AFS database)")
cursor = sql_conn.connection.cursor()

# First, get Clients table column names
print("\n" + "=" * 80)
print("STEP 1: Clients Table Structure")
print("=" * 80)

cursor.execute("""
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'Clients'
    ORDER BY ORDINAL_POSITION
""")

client_columns = cursor.fetchall()
print("\n[FOUND] Clients table columns:")
for (col_name,) in client_columns:
    print(f"  - {col_name}")

# Sample client data
cursor.execute("SELECT TOP 5 * FROM Clients")
clients = cursor.fetchall()
client_col_names = [col[0] for col in cursor.description]

print("\nSample client data:")
for client in clients:
    print(f"  ID {client[0]}: {dict(zip(client_col_names[:5], client[:5]))}")

# Check relationship between Clients and PoultryEggInspectionRecords
print("\n" + "=" * 80)
print("STEP 2: Client-Inspection Relationship")
print("=" * 80)

# Use correct column names from Clients table
cursor.execute("""
    SELECT TOP 10
        c.Id,
        c.Name,
        c.InternalAccountCode,
        COUNT(pe.Id) as EggInspectionCount
    FROM Clients c
    LEFT JOIN PoultryEggInspectionRecords pe ON c.Id = pe.ClientId
    GROUP BY c.Id, c.Name, c.InternalAccountCode
    HAVING COUNT(pe.Id) > 0
    ORDER BY COUNT(pe.Id) DESC
""")

top_clients = cursor.fetchall()

print("\nTop 10 clients by egg inspection count:")
for client_id, name, account_code, inspection_count in top_clients:
    acc_code = account_code or "N/A"
    print(f"  {client_id:5d}. {name:50s} ({acc_code:10s}) - {inspection_count:4d} inspections")

# Sample complete inspection
print("\n" + "=" * 80)
print("STEP 3: Sample Complete Inspection Record")
print("=" * 80)

cursor.execute("""
    SELECT TOP 1
        pe.Id,
        pe.DateOfInspection,
        c.Name as ClientName,
        pe.ClientBranch,
        pe.EggProducer,
        pe.BatchNumber,
        pe.BBDate,
        pe.SizeId,
        pe.GradeId,
        pe.AverageHaugh,
        pe.AverageWeight,
        pe.GeneralComments
    FROM PoultryEggInspectionRecords pe
    LEFT JOIN Clients c ON pe.ClientId = c.Id
    WHERE pe.EggProducer IS NOT NULL AND pe.EggProducer != ''
    ORDER BY pe.DateOfInspection DESC
""")

sample = cursor.fetchone()

if sample:
    print("\n[SAMPLE] Recent egg inspection:")
    print(f"  Inspection ID: {sample[0]}")
    print(f"  Date: {sample[1]}")
    print(f"  Client: {sample[2]}")
    print(f"  Branch: {sample[3]}")
    print(f"  Egg Producer: {sample[4]}")
    print(f"  Batch Number: {sample[5]}")
    print(f"  Best Before: {sample[6]}")
    print(f"  Size ID: {sample[7]}")
    print(f"  Grade ID: {sample[8]}")
    print(f"  Avg Haugh: {sample[9]}")
    print(f"  Avg Weight: {sample[10]}g")
    print(f"  Comments: {sample[11] or '(None)'}")

# Get quality checklist data for this inspection
if sample:
    inspection_id = sample[0]
    print(f"\n  Quality checks for inspection #{inspection_id}:")

    cursor.execute(f"""
        SELECT TOP 5
            SampleNumber,
            WeightGrams,
            HaughReadingmm,
            HaughValue
        FROM PoultryEggQualityCheckListEntryTypes
        WHERE InspectionRecordId = {inspection_id}
        ORDER BY SampleNumber
    """)

    quality_checks = cursor.fetchall()
    if quality_checks:
        print(f"    Found {len(quality_checks)} quality check entries:")
        for sample_num, weight, haugh_reading, haugh_value in quality_checks:
            print(f"      Sample #{sample_num}: Weight={weight}g, Haugh Reading={haugh_reading}mm, Haugh Value={haugh_value}")
    else:
        print("    (No quality check data)")

# Summary of products inspected
print("\n" + "=" * 80)
print("STEP 4: Products Inspected Summary")
print("=" * 80)

cursor.execute("""
    SELECT
        pe.EggProducer,
        pe.SizeId,
        pe.GradeId,
        COUNT(*) as InspectionCount,
        COUNT(DISTINCT pe.ClientId) as UniqueClients
    FROM PoultryEggInspectionRecords pe
    WHERE pe.EggProducer IS NOT NULL AND pe.EggProducer != ''
    GROUP BY pe.EggProducer, pe.SizeId, pe.GradeId
    HAVING COUNT(*) > 5
    ORDER BY COUNT(*) DESC
""")

products = cursor.fetchall()

print(f"\n[FOUND] {len(products)} distinct egg products (producer+size+grade combinations)")
print("\nTop egg products by inspection frequency:")
for i, (producer, size_id, grade_id, count, clients) in enumerate(products[:15], 1):
    print(f"  {i:2d}. {producer:40s} Size:{size_id} Grade:{grade_id} - {count:3d} inspections at {clients:3d} clients")

# Final relationship map
print("\n" + "=" * 80)
print("COMPLETE RELATIONSHIP MAP")
print("=" * 80)

print("""
MAIN TABLE: PoultryEggInspectionRecords (7,293 records)
│
├─ WHERE INSPECTED:
│  └─ ClientId → Clients.Id (5,000 clients)
│      ├─ Name (Client name)
│      ├─ InternalAccountCode
│      └─ ClientBranch (branch name in inspection record)
│
├─ WHAT WAS INSPECTED (Product):
│  ├─ EggProducer (producer name - text)
│  ├─ ProducerId (producer ID - numeric)
│  ├─ SizeId (egg size - 1=small, 2=medium, 3=large, etc.)
│  ├─ GradeId (egg grade - 1=A, 2=B, etc.)
│  ├─ BatchNumber (batch identifier)
│  └─ BBDate (best before date)
│
├─ QUALITY DETAILS:
│  └─ InspectionRecordId → PoultryEggQualityCheckListEntryTypes (246,355 quality checks)
│      ├─ SampleNumber
│      ├─ WeightGrams
│      ├─ HaughReadingmm (egg quality measure)
│      └─ HaughValue
│
├─ LABEL CHECKS:
│  ├─ PoultryEggInnerContainerLabelChecklistTypes (7,293 records)
│  │   └─ Dev1-Dev10 (deviations found)
│  ├─ PoultryEggOuterContainerLabelChecklistTypes (7,293 records)
│  │   └─ Dev1-Dev10 (deviations found)
│  └─ PoultryEggPackContainerLabellingDeviationTypes (7,293 records)
│
├─ PHOTOS:
│  └─ PoultryEggPhotoLinkRecordTypes (21,110 photos)
│      ├─ FileName (photo file)
│      └─ PhotoTypeId (1=Tray Labelling, 2=Quality, 3=Label/Pack)
│
├─ SIGNATURES:
│  └─ PoultryEggInspectionSignatureTypes (26,531 signatures)
│      ├─ FileName (signature image)
│      └─ SignatureTypeId (1=Inspector, 2=Client, 3=No Client, 4=New Client)
│
└─ WHO/WHEN/WHY:
   ├─ InspectorId (who inspected)
   ├─ DateOfInspection (when)
   ├─ InspectionReasonTypeId (why)
   ├─ InspectionLocationTypeId (type of location)
   └─ ApprovedById (who approved)
""")

print("\n[ANSWER] To find egg products inspected at specific places:")
print("\n  Query Example:")
print("""
  SELECT
      c.Name as ClientName,
      pe.ClientBranch,
      pe.EggProducer,
      pe.SizeId,
      pe.GradeId,
      pe.BatchNumber,
      pe.BBDate,
      pe.DateOfInspection
  FROM PoultryEggInspectionRecords pe
  JOIN Clients c ON pe.ClientId = c.Id
  WHERE c.Name LIKE '%Spar%'
    AND pe.EggProducer IS NOT NULL
  ORDER BY pe.DateOfInspection DESC
""")

print("\n  This shows:")
print("  - WHERE: Client name and branch")
print("  - WHAT: Egg producer, size, grade, batch")
print("  - WHEN: Inspection date, best before date")

sql_conn.disconnect()

print("\n" + "=" * 80)
print("MAPPING COMPLETE")
print("=" * 80)
