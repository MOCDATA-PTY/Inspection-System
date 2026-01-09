"""
Sample data from eggs-related tables in SQL Server
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import SQLServerConnection

print("=" * 80)
print("SAMPLING EGGS-RELATED TABLES")
print("=" * 80)

# Connect to SQL Server
sql_conn = SQLServerConnection()
if not sql_conn.connect():
    print("[ERROR] Failed to connect to SQL Server")
    exit(1)

print("\n[OK] Connected to SQL Server (AFS database)")

cursor = sql_conn.connection.cursor()

# List of egg-related tables to sample
egg_tables = [
    'EggDirList',
    'PoultryEggInspectionRecords',
    'MobileProduceCommodityLinks',
    'PoultryProductTypes',
    'PMPProductItemTypes',
    'RawRMPProductItemTypes'
]

for table_name in egg_tables:
    print("\n" + "=" * 80)
    print(f"TABLE: {table_name}")
    print("=" * 80)

    try:
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Total rows: {count}")

        # Get column names
        cursor.execute(f"SELECT TOP 1 * FROM {table_name}")
        cursor.fetchone()  # Fetch to get description
        columns = [column[0] for column in cursor.description]
        print(f"\nColumns ({len(columns)}):")
        for i, col in enumerate(columns, 1):
            print(f"  {i:2d}. {col}")

        # Get sample data
        cursor.execute(f"SELECT TOP 5 * FROM {table_name}")
        rows = cursor.fetchall()

        if rows:
            print(f"\nSample data ({len(rows)} rows):")
            for i, row in enumerate(rows, 1):
                print(f"\n  Row {i}:")
                for col_name, value in zip(columns, row):
                    # Truncate long values
                    str_value = str(value)
                    if len(str_value) > 100:
                        str_value = str_value[:100] + "..."
                    print(f"    {col_name}: {str_value}")
        else:
            print("\n(No data)")

    except Exception as e:
        print(f"[ERROR] {e}")

sql_conn.disconnect()

print("\n" + "=" * 80)
print("SAMPLING COMPLETE")
print("=" * 80)
