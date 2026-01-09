"""
Check if wors/sausage products are appearing in POULTRY commodity
"""
import sqlite3
import os

LOCAL_DB = 'local_inspection_analysis.sqlite3'

if not os.path.exists(LOCAL_DB):
    print(f"ERROR: Database not found: {LOCAL_DB}")
    exit(1)

conn = sqlite3.connect(LOCAL_DB)
cursor = conn.cursor()

print("=" * 80)
print("CHECKING FOR WORS PRODUCTS IN POULTRY COMMODITY")
print("=" * 80)

# Check if any wors products exist in POULTRY
wors_keywords = ['wors', 'sausage', 'polony', 'vienna', 'russian', 'frankfurter']

for keyword in wors_keywords:
    cursor.execute('''
        SELECT remote_id, product_name, client_name, date_of_inspection
        FROM inspections
        WHERE commodity = 'POULTRY'
        AND LOWER(product_name) LIKE ?
        ORDER BY date_of_inspection DESC
    ''', (f'%{keyword}%',))

    results = cursor.fetchall()

    if results:
        print(f"\n[ERROR] Found {len(results)} POULTRY inspections with '{keyword}' in product name:")
        print(f"{'Inspection ID':<15} {'Product Name':<40} {'Client':<40} {'Date':<15}")
        print("-" * 110)
        for remote_id, product, client, date in results[:10]:  # Show first 10
            print(f"{remote_id:<15} {product:<40} {client:<40} {date:<15}")
        if len(results) > 10:
            print(f"... and {len(results) - 10} more")

# Summary by commodity
print("\n" + "=" * 80)
print("SUMMARY: Where are WORS products located?")
print("=" * 80)

for keyword in ['wors', 'boerewors', 'braaiwors']:
    print(f"\nSearching for '{keyword}':")

    for commodity in ['POULTRY', 'EGGS', 'PMP', 'RAW']:
        cursor.execute('''
            SELECT COUNT(*)
            FROM inspections
            WHERE commodity = ?
            AND LOWER(product_name) LIKE ?
        ''', (commodity, f'%{keyword}%'))

        count = cursor.fetchone()[0]
        if count > 0:
            print(f"  {commodity}: {count} inspections")

# Check specific product: "Deli Viennas" that we found earlier
print("\n" + "=" * 80)
print("CHECKING SPECIFIC PRODUCT: 'Deli Viennas'")
print("=" * 80)

cursor.execute('''
    SELECT commodity, remote_id, client_name, date_of_inspection
    FROM inspections
    WHERE product_name = 'Deli Viennas'
''')

for commodity, remote_id, client, date in cursor.fetchall():
    print(f"Inspection {remote_id}: Commodity={commodity}, Client={client}, Date={date}")
    print(f"  -> This SHOULD be in PMP, not {commodity}")

# Check if same inspection IDs appear in multiple commodities (shouldn't happen)
print("\n" + "=" * 80)
print("CHECKING FOR DUPLICATE INSPECTION IDs ACROSS COMMODITIES")
print("=" * 80)

cursor.execute('''
    SELECT remote_id, COUNT(DISTINCT commodity) as commodity_count,
           GROUP_CONCAT(DISTINCT commodity) as commodities
    FROM inspections
    GROUP BY remote_id
    HAVING commodity_count > 1
''')

duplicates = cursor.fetchall()
if duplicates:
    print(f"\n[ERROR] Found {len(duplicates)} inspection IDs that appear in multiple commodities!")
    print(f"{'Inspection ID':<15} {'Commodities':<30}")
    print("-" * 45)
    for remote_id, count, commodities in duplicates[:20]:
        print(f"{remote_id:<15} {commodities:<30}")
else:
    print("\n[OK] No inspection IDs appear in multiple commodities")

# Final summary
print("\n" + "=" * 80)
print("ANSWER TO YOUR QUESTION")
print("=" * 80)

cursor.execute('''
    SELECT commodity, COUNT(*) as count
    FROM inspections
    WHERE LOWER(product_name) LIKE '%wors%'
    GROUP BY commodity
''')

print("\nWhere are ALL 'wors' products currently located:")
for commodity, count in cursor.fetchall():
    print(f"  {commodity}: {count} inspections with 'wors' in product name")

conn.close()
