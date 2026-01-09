import os
import sys
import django
import pymssql

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from datetime import datetime, timedelta
from django.conf import settings

print("Checking SQL Server for testing categories...")
print("=" * 80)

try:
    # Get SQL Server config from Django settings
    sql_config = settings.DATABASES['sql_server']

    # Connect to SQL Server
    conn = pymssql.connect(
        server=sql_config['HOST'],
        port=sql_config['PORT'],
        user=sql_config['USER'],
        password=sql_config['PASSWORD'],
        database=sql_config['NAME']
    )
    cursor = conn.cursor(as_dict=True)

    # Check for category testing table
    print("\nChecking for category/testing related tables:")
    print("-" * 80)
    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        AND (TABLE_NAME LIKE '%category%' OR TABLE_NAME LIKE '%test%' OR TABLE_NAME LIKE '%sample%')
        ORDER BY TABLE_NAME
    """)

    tables = cursor.fetchall()
    if tables:
        print("Found related tables:")
        for table in tables:
            print(f"  - {table['TABLE_NAME']}")
    else:
        print("No category/testing tables found")

    # Check inspections with CategoryTestingId
    print("\n" + "=" * 80)
    print("Checking inspections with CategoryTestingId set:")
    print("=" * 80)

    cursor.execute("""
        SELECT TOP 10
            InspectionId,
            DateOfInspection,
            CategoryTestingId,
            LabSampleSize,
            IsCalcuimContentTestRequired
        FROM tblFSAInspection
        WHERE CategoryTestingId IS NOT NULL
        ORDER BY DateOfInspection DESC
    """)

    inspections = cursor.fetchall()

    if inspections:
        print(f"\nFound {len(inspections)} inspections with CategoryTestingId:")
        for insp in inspections:
            print(f"  ID: {insp['InspectionId']}, Date: {insp['DateOfInspection']}, CategoryTestingId: {insp['CategoryTestingId']}, SampleSize: {insp['LabSampleSize']}, Calcium: {insp['IsCalcuimContentTestRequired']}")
    else:
        print("No inspections found with CategoryTestingId set")

    # Check for any tables that might have test type information
    print("\n" + "=" * 80)
    print("Looking for test type/category definitions:")
    print("=" * 80)

    # Try common table names
    for table_name in ['tblCategoryTesting', 'tblTestCategory', 'tblSampleType', 'CategoryTesting', 'TestType']:
        try:
            cursor.execute(f"SELECT TOP 10 * FROM {table_name}")
            rows = cursor.fetchall()
            if rows:
                print(f"\nFound table: {table_name}")
                print(f"First row keys: {list(rows[0].keys())}")
                for row in rows[:5]:
                    print(f"  {row}")
        except:
            pass  # Table doesn't exist

    conn.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
