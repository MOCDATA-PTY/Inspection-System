"""
Find the SQL Server table that contains egg product names
"""
import pymssql
from django.conf import settings
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# Get SQL Server config
sql_config = settings.DATABASES.get('sql_server', {})

print("="*80)
print("SEARCHING FOR EGG PRODUCT TABLES IN SQL SERVER")
print("="*80)

try:
    # Connect to SQL Server
    conn = pymssql.connect(
        server=sql_config.get('HOST'),
        port=int(sql_config.get('PORT', 1433)),
        user=sql_config.get('USER'),
        password=sql_config.get('PASSWORD'),
        database=sql_config.get('NAME'),
        timeout=30
    )

    cursor = conn.cursor()

    print("\n1. FINDING ALL TABLES WITH 'EGG' IN THE NAME")
    print("-"*80)

    # Get all table names
    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        AND (TABLE_NAME LIKE '%Egg%' OR TABLE_NAME LIKE '%EGG%')
        ORDER BY TABLE_NAME
    """)

    egg_tables = cursor.fetchall()

    if egg_tables:
        print(f"Found {len(egg_tables)} tables with 'Egg' in the name:\n")
        for table in egg_tables:
            print(f"  - {table[0]}")
    else:
        print("  No tables found with 'Egg' in name")

    print("\n2. SEARCHING FOR TABLES WITH PRODUCT/INSPECTION PATTERN")
    print("-"*80)

    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        AND TABLE_NAME LIKE '%Inspection%'
        ORDER BY TABLE_NAME
    """)

    inspection_tables = cursor.fetchall()
    print(f"Found {len(inspection_tables)} tables with 'Inspection' in name:\n")
    for table in inspection_tables:
        table_name = table[0]
        print(f"\n  Table: {table_name}")

        # Get column names
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name}'
            AND (COLUMN_NAME LIKE '%Product%' OR COLUMN_NAME LIKE '%Name%' OR COLUMN_NAME LIKE '%Item%')
            ORDER BY ORDINAL_POSITION
        """)

        columns = cursor.fetchall()
        if columns:
            print(f"    Relevant columns:")
            for col in columns:
                print(f"      - {col[0]} ({col[1]})")

    print("\n3. CHECKING IF EGG DATA EXISTS IN KNOWN TABLES")
    print("-"*80)

    # Get a sample egg inspection ID
    from main.models import FoodSafetyAgencyInspection
    sample_egg = FoodSafetyAgencyInspection.objects.filter(
        commodity__iexact='EGGS'
    ).first()

    if sample_egg:
        print(f"\nUsing sample egg inspection ID: {sample_egg.remote_id}")
        print(f"Client: {sample_egg.client_name}")
        print(f"Date: {sample_egg.date_of_inspection}")

        # Check each egg table for this inspection
        if egg_tables:
            for table in egg_tables:
                table_name = table[0]
                print(f"\n  Checking {table_name}...")

                try:
                    # Try to find records with this inspection ID
                    cursor.execute(f"SELECT TOP 5 * FROM {table_name} WHERE InspectionId = %s", (sample_egg.remote_id,))
                    results = cursor.fetchall()

                    if results:
                        print(f"    ✅ Found {len(results)} record(s)!")

                        # Get column names
                        cursor.execute(f"""
                            SELECT COLUMN_NAME
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_NAME = '{table_name}'
                            ORDER BY ORDINAL_POSITION
                        """)
                        col_names = [col[0] for col in cursor.fetchall()]

                        print(f"    Columns: {', '.join(col_names)}")
                        print(f"    Sample record:")
                        for i, col_name in enumerate(col_names):
                            if i < len(results[0]):
                                print(f"      {col_name}: {results[0][i]}")
                    else:
                        print(f"    No records found for this inspection ID")

                except Exception as e:
                    print(f"    Error querying {table_name}: {e}")

        # Also check if the inspection ID exists in the main table
        print(f"\n4. CHECKING MAIN INSPECTION RECORD")
        print("-"*80)

        for table_name in ['EggInspectionRecordTypes', 'EggsInspectionRecordTypes', 'InspectionRecordTypes']:
            try:
                cursor.execute(f"SELECT TOP 1 * FROM {table_name} WHERE Id = %s", (sample_egg.remote_id,))
                result = cursor.fetchone()
                if result:
                    print(f"\n  ✅ Found in {table_name}!")

                    # Get columns
                    cursor.execute(f"""
                        SELECT COLUMN_NAME
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = '{table_name}'
                        ORDER BY ORDINAL_POSITION
                    """)
                    col_names = [col[0] for col in cursor.fetchall()]

                    print(f"  Columns: {', '.join(col_names)}")
                    print(f"  Record data:")
                    for i, col_name in enumerate(col_names):
                        if i < len(result):
                            val = result[i]
                            # Only show non-null values for brevity
                            if val is not None:
                                print(f"    {col_name}: {val}")
                else:
                    print(f"  Not found in {table_name}")
            except Exception as e:
                print(f"  Table {table_name} does not exist or error: {e}")

    print("\n" + "="*80)
    print("SEARCH COMPLETE")
    print("="*80)

    conn.close()

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
