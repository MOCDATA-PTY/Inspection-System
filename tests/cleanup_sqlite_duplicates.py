"""
Clean up duplicate (commodity, remote_id) pairs in local SQLite database
This prepares the database for the unique_together constraint
"""
import sqlite3
import os

LOCAL_DB = 'local_inspection_analysis.sqlite3'

if not os.path.exists(LOCAL_DB):
    print(f"ERROR: Database not found: {LOCAL_DB}")
    print("Please run create_local_db_and_analyze.py first")
    exit(1)

conn = sqlite3.connect(LOCAL_DB)
cursor = conn.cursor()

print("=" * 80)
print("CLEANUP DUPLICATE (COMMODITY, REMOTE_ID) PAIRS IN SQLITE DATABASE")
print("=" * 80)

# Find all duplicate (commodity, remote_id) pairs
print("\nStep 1: Finding duplicate (commodity, remote_id) pairs...")
cursor.execute('''
    SELECT commodity, remote_id, COUNT(*) as count
    FROM inspections
    GROUP BY commodity, remote_id
    HAVING COUNT(*) > 1
    ORDER BY count DESC
''')

duplicates = cursor.fetchall()

if not duplicates:
    print("\n[OK] No duplicates found! Database is ready for unique_together constraint.")
    conn.close()
    exit(0)

print(f"\n[FOUND] {len(duplicates)} duplicate (commodity, remote_id) pairs")
print(f"\nTop 10 duplicates:")
print(f"{'Commodity':<15} {'Remote ID':<12} {'Count':<10}")
print("-" * 40)
for commodity, remote_id, count in duplicates[:10]:
    print(f"{commodity:<15} {remote_id:<12} {count:<10}")

total_duplicates_to_delete = sum(count - 1 for _, _, count in duplicates)
print(f"\nTotal records to delete: {total_duplicates_to_delete}")

# For each duplicate group, keep the one with highest id (most recent)
print("\nStep 2: Cleaning up duplicates (keeping most recent record)...")

deleted_count = 0
for commodity, remote_id, count in duplicates:
    # Get all IDs for this duplicate group, ordered by id DESC
    cursor.execute('''
        SELECT id, client_name, product_name, date_of_inspection
        FROM inspections
        WHERE commodity = ? AND remote_id = ?
        ORDER BY id DESC
    ''', (commodity, remote_id))

    records = cursor.fetchall()

    # Keep first (highest id), delete rest
    keep_id = records[0][0]
    delete_ids = [r[0] for r in records[1:]]

    if delete_ids:
        placeholders = ','.join('?' * len(delete_ids))
        cursor.execute(f'''
            DELETE FROM inspections
            WHERE id IN ({placeholders})
        ''', delete_ids)

        deleted_count += len(delete_ids)

        if deleted_count <= 10:  # Show first 10 deletions
            print(f"  [{commodity}-{remote_id}] Kept ID {keep_id}, deleted {len(delete_ids)} duplicates")

print(f"\n[OK] Deleted {deleted_count} duplicate records")

# Commit changes
conn.commit()

# Verify no duplicates remain
print("\nStep 3: Verifying cleanup...")
cursor.execute('''
    SELECT commodity, remote_id, COUNT(*) as count
    FROM inspections
    GROUP BY commodity, remote_id
    HAVING COUNT(*) > 1
''')

remaining_duplicates = cursor.fetchall()

if remaining_duplicates:
    print(f"\n[ERROR] Still found {len(remaining_duplicates)} duplicates after cleanup!")
    for commodity, remote_id, count in remaining_duplicates[:5]:
        print(f"  - {commodity}-{remote_id}: {count} copies")
else:
    print("\n[SUCCESS] No duplicates remain! Database is clean.")

# Show final statistics
cursor.execute('SELECT COUNT(*) FROM inspections')
total_records = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(DISTINCT commodity || "-" || remote_id) FROM inspections')
unique_pairs = cursor.fetchone()[0]

print("\nFinal Statistics:")
print(f"  Total records: {total_records}")
print(f"  Unique (commodity, remote_id) pairs: {unique_pairs}")
print(f"  Records deleted: {deleted_count}")

conn.close()

print("\n" + "=" * 80)
print("Cleanup complete! The database is ready for unique_together constraint.")
print("=" * 80)
