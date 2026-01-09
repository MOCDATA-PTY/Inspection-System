"""
Show egg producers from PoultryEggInspectionRecords table
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import SQLServerConnection

print("=" * 80)
print("EGG PRODUCERS IN SQL SERVER")
print("=" * 80)

# Connect to SQL Server
sql_conn = SQLServerConnection()
if not sql_conn.connect():
    print("[ERROR] Failed to connect to SQL Server")
    exit(1)

print("\n[OK] Connected to SQL Server (AFS database)")

cursor = sql_conn.connection.cursor()

# Get total records
cursor.execute("SELECT COUNT(*) FROM PoultryEggInspectionRecords")
total_records = cursor.fetchone()[0]
print(f"\n[INFO] Total egg inspection records: {total_records:,}")

# Get distinct egg producers
print("\n" + "=" * 80)
print("DISTINCT EGG PRODUCERS")
print("=" * 80)

cursor.execute("""
    SELECT DISTINCT EggProducer
    FROM PoultryEggInspectionRecords
    WHERE EggProducer IS NOT NULL AND EggProducer != ''
    ORDER BY EggProducer
""")

producers = cursor.fetchall()

print(f"\n[FOUND] {len(producers)} distinct egg producers")

if producers:
    print("\nEgg Producer Names:")
    for i, (producer,) in enumerate(producers, 1):
        print(f"  {i:3d}. {producer}")

# Get count by producer
print("\n" + "=" * 80)
print("INSPECTION COUNT BY EGG PRODUCER")
print("=" * 80)

cursor.execute("""
    SELECT
        CASE
            WHEN EggProducer IS NULL OR EggProducer = '' THEN '(Empty/Blank)'
            ELSE EggProducer
        END as Producer,
        COUNT(*) as InspectionCount
    FROM PoultryEggInspectionRecords
    GROUP BY EggProducer
    ORDER BY COUNT(*) DESC
""")

producer_counts = cursor.fetchall()

print(f"\nTop egg producers by inspection count:")
for i, (producer, count) in enumerate(producer_counts[:20], 1):  # Show top 20
    print(f"  {i:3d}. {producer:50s} - {count:5d} inspections")

# Get producer ID information
print("\n" + "=" * 80)
print("PRODUCER ID ANALYSIS")
print("=" * 80)

cursor.execute("""
    SELECT
        ProducerId,
        EggProducer,
        COUNT(*) as InspectionCount
    FROM PoultryEggInspectionRecords
    WHERE ProducerId IS NOT NULL
    GROUP BY ProducerId, EggProducer
    ORDER BY COUNT(*) DESC
""")

producer_ids = cursor.fetchall()

print(f"\n[FOUND] {len(producer_ids)} producer ID entries")
print("\nTop producers by ID (with inspection counts):")
for i, (producer_id, egg_producer, count) in enumerate(producer_ids[:20], 1):
    producer_name = egg_producer if egg_producer else "(No name)"
    print(f"  {i:3d}. ProducerId {producer_id:5d}: {producer_name:40s} - {count:5d} inspections")

# Check if there's a separate Producers table
print("\n" + "=" * 80)
print("LOOKING FOR PRODUCERS LOOKUP TABLE")
print("=" * 80)

cursor.execute("""
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    AND TABLE_NAME LIKE '%Producer%'
    ORDER BY TABLE_NAME
""")

producer_tables = cursor.fetchall()

if producer_tables:
    print("\n[FOUND] Producer-related tables:")
    for (table_name,) in producer_tables:
        print(f"  - {table_name}")

        # Try to get row count
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"    Rows: {count:,}")

            # Sample first few rows
            cursor.execute(f"SELECT TOP 3 * FROM {table_name}")
            rows = cursor.fetchall()
            if rows and cursor.description:
                columns = [col[0] for col in cursor.description]
                print(f"    Columns: {', '.join(columns)}")
        except Exception as e:
            print(f"    Error: {e}")
else:
    print("\n[INFO] No separate producers table found")

sql_conn.disconnect()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
