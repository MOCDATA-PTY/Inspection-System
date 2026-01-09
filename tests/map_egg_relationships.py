"""
Map all relationships for PoultryEggInspectionRecords to find inspected products
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import SQLServerConnection

print("=" * 80)
print("MAPPING EGG INSPECTION RELATIONSHIPS")
print("=" * 80)

# Connect to SQL Server
sql_conn = SQLServerConnection()
if not sql_conn.connect():
    print("[ERROR] Failed to connect to SQL Server")
    exit(1)

print("\n[OK] Connected to SQL Server (AFS database)")
cursor = sql_conn.connection.cursor()

# Get foreign key relationships for PoultryEggInspectionRecords
print("\n" + "=" * 80)
print("STEP 1: Foreign Key Relationships")
print("=" * 80)

cursor.execute("""
    SELECT
        fk.name AS ForeignKeyName,
        OBJECT_NAME(fk.parent_object_id) AS TableName,
        COL_NAME(fc.parent_object_id, fc.parent_column_id) AS ColumnName,
        OBJECT_NAME(fk.referenced_object_id) AS ReferencedTable,
        COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS ReferencedColumn
    FROM sys.foreign_keys AS fk
    INNER JOIN sys.foreign_key_columns AS fc
        ON fk.object_id = fc.constraint_object_id
    WHERE OBJECT_NAME(fk.parent_object_id) = 'PoultryEggInspectionRecords'
    ORDER BY ColumnName
""")

foreign_keys = cursor.fetchall()

if foreign_keys:
    print("\n[FOUND] Foreign key relationships:")
    for fk_name, table, column, ref_table, ref_column in foreign_keys:
        print(f"\n  {column} → {ref_table}.{ref_column}")
        print(f"    FK Name: {fk_name}")
else:
    print("\n[INFO] No formal foreign keys defined")
    print("Will check based on column naming patterns (Id suffix)")

# Check potential relationships based on column names ending in 'Id'
print("\n" + "=" * 80)
print("STEP 2: Potential Relationships (Columns ending in 'Id')")
print("=" * 80)

cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'PoultryEggInspectionRecords'
    AND COLUMN_NAME LIKE '%Id'
    ORDER BY COLUMN_NAME
""")

id_columns = cursor.fetchall()

print("\n[FOUND] Columns that likely reference other tables:")
for col_name, data_type in id_columns:
    print(f"  - {col_name} ({data_type})")

# Now let's explore each relationship
relationships = {
    'ClientId': 'Clients',
    'ProducerId': 'PoultryEggProducerTypes',  # Guessing
    'InspectorId': 'Users/Inspectors',
    'InspectionLocationTypeId': 'InspectionLocations',
    'InspectionReasonTypeId': 'InspectionReasonTypes',
    'SizeId': 'EggSizeTypes',  # Guessing
    'GradeId': 'EggGradeTypes',  # Guessing
    'TraySizeId': 'TraySizeTypes',  # Guessing
    'ApprovedById': 'Users',
    'WeighingChecklistApprovedById': 'Users'
}

print("\n" + "=" * 80)
print("STEP 3: Exploring Related Tables")
print("=" * 80)

# Find all tables that might contain lookup data
cursor.execute("""
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    AND (
        TABLE_NAME LIKE '%Type%' OR
        TABLE_NAME LIKE '%Enum%' OR
        TABLE_NAME LIKE '%Size%' OR
        TABLE_NAME LIKE '%Grade%'
    )
    AND TABLE_NAME LIKE '%Egg%'
    ORDER BY TABLE_NAME
""")

lookup_tables = cursor.fetchall()

print("\n[FOUND] Egg-related lookup tables:")
for (table_name,) in lookup_tables:
    print(f"\n  TABLE: {table_name}")
    try:
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]

        # Get columns
        cursor.execute(f"SELECT TOP 1 * FROM {table_name}")
        cursor.fetchone()
        columns = [col[0] for col in cursor.description]

        print(f"    Rows: {count}")
        print(f"    Columns: {', '.join(columns)}")

        # Sample data
        if count > 0:
            cursor.execute(f"SELECT TOP 5 * FROM {table_name}")
            rows = cursor.fetchall()
            if rows:
                print(f"    Sample data:")
                for row in rows:
                    # Format row nicely
                    row_data = []
                    for col, val in zip(columns, row):
                        if col in ['Id', 'SizeId', 'GradeId']:
                            row_data.append(f"{col}={val}")
                        elif 'Description' in col or 'Name' in col:
                            row_data.append(f"{col}='{val}'")
                    if row_data:
                        print(f"      {', '.join(row_data[:3])}")
    except Exception as e:
        print(f"    Error: {e}")

# Check for quality checklist entries (these might contain product details)
print("\n" + "=" * 80)
print("STEP 4: Quality Checklist Entries (Product Details)")
print("=" * 80)

cursor.execute("""
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    AND TABLE_NAME LIKE '%PoultryEgg%'
    AND (TABLE_NAME LIKE '%Checklist%' OR TABLE_NAME LIKE '%Quality%')
    ORDER BY TABLE_NAME
""")

quality_tables = cursor.fetchall()

for (table_name,) in quality_tables:
    print(f"\n  TABLE: {table_name}")
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]

        cursor.execute(f"SELECT TOP 1 * FROM {table_name}")
        cursor.fetchone()
        columns = [col[0] for col in cursor.description]

        print(f"    Rows: {count}")
        print(f"    Columns: {', '.join(columns)}")
    except Exception as e:
        print(f"    Error: {e}")

# Check Clients table
print("\n" + "=" * 80)
print("STEP 5: Clients Table (Inspected Locations)")
print("=" * 80)

cursor.execute("SELECT COUNT(*) FROM Clients")
client_count = cursor.fetchone()[0]
print(f"\n[INFO] Total clients: {client_count:,}")

cursor.execute("""
    SELECT TOP 10
        c.Id,
        c.ClientName,
        c.InternalAccountCode,
        COUNT(pe.Id) as EggInspectionCount
    FROM Clients c
    LEFT JOIN PoultryEggInspectionRecords pe ON c.Id = pe.ClientId
    GROUP BY c.Id, c.ClientName, c.InternalAccountCode
    HAVING COUNT(pe.Id) > 0
    ORDER BY COUNT(pe.Id) DESC
""")

top_clients = cursor.fetchall()

print("\nTop 10 clients by egg inspection count:")
for client_id, name, account_code, inspection_count in top_clients:
    print(f"  {client_id:5d}. {name:50s} - {inspection_count:4d} inspections")

# Sample inspection with all related data
print("\n" + "=" * 80)
print("STEP 6: Sample Complete Inspection Record")
print("=" * 80)

cursor.execute("""
    SELECT TOP 1
        pe.Id,
        pe.DateOfInspection,
        c.ClientName,
        pe.ClientBranch,
        pe.EggProducer,
        pe.BatchNumber,
        pe.BBDate,
        pe.SizeId,
        pe.GradeId,
        pe.StartOfInspection,
        pe.EndOfInspection,
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
    print(f"  Duration: {sample[9]} to {sample[10]}")
    print(f"  Comments: {sample[11] or '(None)'}")

# Summary
print("\n" + "=" * 80)
print("RELATIONSHIP SUMMARY")
print("=" * 80)

print("\n[STRUCTURE] Egg Inspection Data Model:")
print("""
PoultryEggInspectionRecords (Main Table)
├── ClientId → Clients (WHERE the inspection happened)
│   └── ClientName, InternalAccountCode, ClientBranch
├── EggProducer (WHO produced the eggs - text field)
├── ProducerId (WHO produced - ID reference)
├── SizeId → Size lookup table (WHAT size eggs)
├── GradeId → Grade lookup table (WHAT grade eggs)
├── BatchNumber (WHICH batch)
├── BBDate (Best before date)
├── InspectorId (WHO inspected)
├── InspectionLocationTypeId (TYPE of location)
├── InspectionReasonTypeId (WHY inspected)
└── TraySizeId → Tray size lookup

Related Detail Tables:
├── PoultryEggQualityCheckListEntryTypes (Quality checks performed)
├── PoultryEggInnerContainerLabelChecklistTypes (Label checks)
├── PoultryEggOuterContainerLabelChecklistTypes (Outer label checks)
└── PoultryEggPhotoLinkRecordTypes (Photos)
""")

print("\n[ANSWER] To find products inspected:")
print("  1. Main product info: EggProducer, BatchNumber, SizeId, GradeId")
print("  2. Where inspected: Clients.ClientName, ClientBranch")
print("  3. Quality details: PoultryEggQualityCheckListEntryTypes")
print("  4. When: DateOfInspection, BBDate")

sql_conn.disconnect()

print("\n" + "=" * 80)
print("MAPPING COMPLETE")
print("=" * 80)
