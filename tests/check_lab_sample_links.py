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

print("Checking Lab Sample Links tables...")
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

    # Find the correct inspection table name
    print("\nFinding inspection tables:")
    print("-" * 80)
    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        AND TABLE_NAME LIKE '%inspection%'
        ORDER BY TABLE_NAME
    """)

    tables = cursor.fetchall()
    if tables:
        print("Found inspection tables:")
        for table in tables:
            print(f"  - {table['TABLE_NAME']}")

    # Check PMPInspectionLabSampleLinks structure
    print("\n" + "=" * 80)
    print("PMPInspectionLabSampleLinks structure:")
    print("=" * 80)
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'PMPInspectionLabSampleLinks'
        ORDER BY ORDINAL_POSITION
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col['COLUMN_NAME']} ({col['DATA_TYPE']})")

    # Check recent PMP lab samples
    print("\n" + "=" * 80)
    print("Recent PMP Lab Samples:")
    print("=" * 80)
    cursor.execute("""
        SELECT TOP 20 *
        FROM PMPInspectionLabSampleLinks
        ORDER BY CreatedOn DESC
    """)
    pmp_samples = cursor.fetchall()
    if pmp_samples:
        print(f"\nFound {len(pmp_samples)} recent PMP lab samples:")
        for sample in pmp_samples[:10]:
            print(f"  InspectionId: {sample.get('InspectionId')}, LabId: {sample.get('LabId')}, Date: {sample.get('CreatedOn')}")
            print(f"    {sample}")
    else:
        print("No PMP lab samples found")

    # Check RawRMPInspectionLabSampleLinks structure
    print("\n" + "=" * 80)
    print("RawRMPInspectionLabSampleLinks structure:")
    print("=" * 80)
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'RawRMPInspectionLabSampleLinks'
        ORDER BY ORDINAL_POSITION
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col['COLUMN_NAME']} ({col['DATA_TYPE']})")

    # Check recent Raw lab samples
    print("\n" + "=" * 80)
    print("Recent RAW Lab Samples:")
    print("=" * 80)
    cursor.execute("""
        SELECT TOP 20 *
        FROM RawRMPInspectionLabSampleLinks
        ORDER BY CreatedOn DESC
    """)
    raw_samples = cursor.fetchall()
    if raw_samples:
        print(f"\nFound {len(raw_samples)} recent RAW lab samples:")
        for sample in raw_samples[:10]:
            print(f"  InspectionId: {sample.get('InspectionId')}, LabId: {sample.get('LabId')}, Date: {sample.get('CreatedOn')}")
            print(f"    {sample}")
    else:
        print("No RAW lab samples found")

    # Check for LabSampleType table
    print("\n" + "=" * 80)
    print("Looking for Lab Sample Type definitions:")
    print("=" * 80)
    try:
        cursor.execute("SELECT * FROM LabSampleTypes")
        sample_types = cursor.fetchall()
        if sample_types:
            print("\nLab Sample Types:")
            for st in sample_types:
                print(f"  {st}")
    except Exception as e:
        print(f"  LabSampleTypes table not found: {e}")

    # Try tblLabSampleTypes
    try:
        cursor.execute("SELECT * FROM tblLabSampleTypes")
        sample_types = cursor.fetchall()
        if sample_types:
            print("\ntblLabSampleTypes:")
            for st in sample_types:
                print(f"  {st}")
    except Exception as e:
        print(f"  tblLabSampleTypes table not found")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
