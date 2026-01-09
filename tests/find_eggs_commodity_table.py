"""
Find the eggs commodity table in SQL Server database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import SQLServerConnection

print("=" * 80)
print("SEARCHING FOR EGGS COMMODITY TABLE")
print("=" * 80)

# Connect to SQL Server
sql_conn = SQLServerConnection()
if not sql_conn.connect():
    print("[ERROR] Failed to connect to SQL Server")
    exit(1)

print("\n[OK] Connected to SQL Server (AFS database)")

cursor = sql_conn.connection.cursor()

print("\n" + "=" * 80)
print("STEP 1: List all tables in database")
print("=" * 80)

# Get all tables
cursor.execute("""
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_NAME
""")

all_tables = cursor.fetchall()
print(f"\n[FOUND] {len(all_tables)} tables in AFS database")

# Filter for tables that might contain commodity/product/eggs data
commodity_tables = [table[0] for table in all_tables if any(keyword in table[0].lower() for keyword in ['commodity', 'product', 'egg', 'item', 'goods'])]

print(f"\n[FILTERED] Tables that might contain commodity/product data:")
for table in commodity_tables:
    print(f"  - {table}")

# Also show ALL tables to be thorough
print(f"\n[ALL TABLES] Complete list:")
for i, table in enumerate(all_tables, 1):
    print(f"  {i:3d}. {table[0]}")

print("\n" + "=" * 80)
print("STEP 2: Search for 'Eggs' or 'Commodity' in table names")
print("=" * 80)

eggs_related = [table[0] for table in all_tables if 'egg' in table[0].lower()]
commodity_related = [table[0] for table in all_tables if 'commodity' in table[0].lower() or 'commod' in table[0].lower()]

if eggs_related:
    print(f"\n[EGGS] Tables with 'egg' in name:")
    for table in eggs_related:
        print(f"  - {table}")
else:
    print("\n[EGGS] No tables found with 'egg' in name")

if commodity_related:
    print(f"\n[COMMODITY] Tables with 'commodity' in name:")
    for table in commodity_related:
        print(f"  - {table}")
else:
    print("\n[COMMODITY] No tables found with 'commodity' in name")

print("\n" + "=" * 80)
print("STEP 3: Check common table names")
print("=" * 80)

# Check common table names
common_names = ['Commodities', 'Products', 'Items', 'Eggs', 'EggProducts', 'CommodityTypes', 'ProductTypes']

print(f"\n[CHECKING] Common commodity table names:")
for name in common_names:
    exists = any(table[0].lower() == name.lower() for table in all_tables)
    status = "✓ EXISTS" if exists else "✗ Not found"
    print(f"  - {name}: {status}")

print("\n" + "=" * 80)
print("STEP 4: Sample data from likely tables")
print("=" * 80)

# If we found commodity tables, sample their data
if commodity_tables:
    for table_name in commodity_tables[:5]:  # Sample first 5 tables max
        print(f"\n[TABLE] {table_name}")
        try:
            cursor.execute(f"SELECT TOP 5 * FROM {table_name}")
            rows = cursor.fetchall()

            if rows:
                # Get column names
                columns = [column[0] for column in cursor.description]
                print(f"  Columns: {', '.join(columns)}")
                print(f"  Sample rows ({len(rows)}):")
                for row in rows:
                    print(f"    {row}")
            else:
                print("  (Empty table)")
        except Exception as e:
            print(f"  Error: {e}")

sql_conn.disconnect()

print("\n" + "=" * 80)
print("SEARCH COMPLETE")
print("=" * 80)
