"""Test SQL Server query to find the exact error"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
import pymssql

def test_sql_query():
    try:
        print("="*80)
        print("Testing SQL Server Connection and Query")
        print("="*80)

        sql_server_config = settings.DATABASES.get('sql_server', {})

        print(f"\n[1] Connecting to SQL Server...")
        print(f"    Server: {sql_server_config.get('HOST')}:{sql_server_config.get('PORT', 1433)}")

        connection = pymssql.connect(
            server=sql_server_config.get('HOST'),
            port=int(sql_server_config.get('PORT', 1433)),
            user=sql_server_config.get('USER'),
            password=sql_server_config.get('PASSWORD'),
            database=sql_server_config.get('NAME'),
            timeout=30
        )
        cursor = connection.cursor(as_dict=True)
        print("    CONNECTED!")

        print(f"\n[2] Checking sample link tables...")

        # Check RAW sample table
        try:
            cursor.execute("SELECT TOP 1 * FROM AFS.dbo.RawRMPInspectionLabSampleLinks")
            result = cursor.fetchone()
            print(f"    RAW sample table EXISTS")
            if result:
                print(f"      Columns: {list(result.keys())}")
        except Exception as e:
            print(f"    RAW sample table ERROR: {e}")

        # Check PMP sample table
        try:
            cursor.execute("SELECT TOP 1 * FROM AFS.dbo.PMPInspectionLabSampleLinks")
            result = cursor.fetchone()
            print(f"    PMP sample table EXISTS")
            if result:
                print(f"      Columns: {list(result.keys())}")
        except Exception as e:
            print(f"    PMP sample table ERROR: {e}")

        print(f"\n[3] Testing RAW query with sample check...")
        raw_query = '''
            SELECT TOP 5
                'RAW' as Commodity,
                CASE WHEN EXISTS (
                    SELECT 1 FROM AFS.dbo.RawRMPInspectionLabSampleLinks
                    WHERE RawRMPInspectionLabSampleLinks.InspectionId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id
                ) THEN 1 ELSE 0 END AS IsSampleTaken,
                [AFS].[dbo].[RawRMPInspectionRecordTypes].Id as Id
            FROM [AFS].[dbo].[RawRMPInspectionRecordTypes]
            WHERE DateOfInspection >= '2025-10-01'
        '''

        cursor.execute(raw_query)
        results = cursor.fetchall()
        print(f"    RAW query OK! Got {len(results)} results")

        print(f"\n[4] Testing PMP query with sample check...")
        pmp_query = '''
            SELECT TOP 5
                'PMP' as Commodity,
                CASE WHEN EXISTS (
                    SELECT 1 FROM AFS.dbo.PMPInspectionLabSampleLinks
                    WHERE PMPInspectionLabSampleLinks.InspectionId = [AFS].[dbo].[PMPInspectionRecordTypes].Id
                ) THEN 1 ELSE 0 END AS IsSampleTaken,
                [AFS].[dbo].[PMPInspectionRecordTypes].Id as Id
            FROM [AFS].[dbo].[PMPInspectionRecordTypes]
            WHERE DateOfInspection >= '2025-10-01'
        '''

        cursor.execute(pmp_query)
        results = cursor.fetchall()
        print(f"    PMP query OK! Got {len(results)} results")

        print(f"\n" + "="*80)
        print("ALL TESTS PASSED!")
        print("="*80)

        connection.close()
        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_sql_query()
