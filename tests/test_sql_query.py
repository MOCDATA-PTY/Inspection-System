"""
Test SQL Server query to find the exact error
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
import pymssql

def test_sql_query():
    """Test the SQL Server query to find issues"""
    try:
        print("=" * 80)
        print("Testing SQL Server Connection and Query")
        print("=" * 80)

        # Get SQL Server config
        sql_server_config = settings.DATABASES.get('sql_server', {})

        print(f"\n[1] Connecting to SQL Server...")
        print(f"    Server: {sql_server_config.get('HOST')}:{sql_server_config.get('PORT', 1433)}")
        print(f"    Database: {sql_server_config.get('NAME')}")

        connection = pymssql.connect(
            server=sql_server_config.get('HOST'),
            port=int(sql_server_config.get('PORT', 1433)),
            user=sql_server_config.get('USER'),
            password=sql_server_config.get('PASSWORD'),
            database=sql_server_config.get('NAME'),
            timeout=30
        )
        cursor = connection.cursor(as_dict=True)
        print("    ✓ Connected successfully!")

        # Test if the sample link tables exist
        print(f"\n[2] Checking if sample link tables exist...")

        tables_to_check = [
            'RawRmpInspectionsLabSampleLinks',
            'PMPInspectionLabSampleLinks'
        ]

        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT TOP 1 * FROM AFS.dbo.{table}")
                result = cursor.fetchone()
                print(f"    ✓ Table '{table}' exists")
                if result:
                    print(f"      Columns: {list(result.keys())}")
            except Exception as e:
                print(f"    ✗ Table '{table}' NOT FOUND or error: {e}")

        # Try a simplified RAW query first
        print(f"\n[3] Testing simplified RAW query...")
        simple_raw_query = '''
            SELECT TOP 5
                'RAW' as Commodity,
                DateOfInspection,
                [AFS].[dbo].[RawRMPInspectionRecordTypes].Id as Id,
                clt.Name as Client
            FROM [AFS].[dbo].[RawRMPInspectionRecordTypes]
            JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod
                on prod.InspectionId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id
            JOIN AFS.dbo.Clients clt
                on clt.Id = prod.ClientId
            WHERE AFS.dbo.[RawRMPInspectionRecordTypes].IsActive = 1
                AND DateOfInspection >= '2025-10-01'
                AND DateOfInspection < '2026-04-01'
        '''

        try:
            cursor.execute(simple_raw_query)
            results = cursor.fetchall()
            print(f"    ✓ Simple RAW query works! Got {len(results)} results")
        except Exception as e:
            print(f"    ✗ Simple RAW query failed: {e}")
            return False

        # Now test with the sample link EXISTS clause
        print(f"\n[4] Testing RAW query with sample link check...")
        raw_with_sample_query = '''
            SELECT TOP 5
                'RAW' as Commodity,
                DateOfInspection,
                CASE WHEN EXISTS (
                    SELECT 1 FROM AFS.dbo.RawRmpInspectionsLabSampleLinks
                    WHERE RawRmpInspectionsLabSampleLinks.RawRMPInspectionRecordId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id
                ) THEN 1 ELSE 0 END AS IsSampleTaken,
                [AFS].[dbo].[RawRMPInspectionRecordTypes].Id as Id,
                clt.Name as Client
            FROM [AFS].[dbo].[RawRMPInspectionRecordTypes]
            JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod
                on prod.InspectionId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id
            JOIN AFS.dbo.Clients clt
                on clt.Id = prod.ClientId
            WHERE AFS.dbo.[RawRMPInspectionRecordTypes].IsActive = 1
                AND DateOfInspection >= '2025-10-01'
                AND DateOfInspection < '2026-04-01'
        '''

        try:
            cursor.execute(raw_with_sample_query)
            results = cursor.fetchall()
            print(f"    ✓ RAW query with sample check works! Got {len(results)} results")
            if results:
                print(f"      Sample result: {results[0]}")
        except Exception as e:
            print(f"    ✗ RAW query with sample check failed: {e}")
            print(f"\n    Trying alternative table names...")

            # Try alternative table names
            alternatives = [
                'RawRMPInspectionLabSampleLinks',
                'RawInspectionsLabSampleLinks',
                'RawRmpLabSampleLinks',
                'RawLabSampleLinks'
            ]

            for alt_table in alternatives:
                try:
                    alt_query = raw_with_sample_query.replace('RawRmpInspectionsLabSampleLinks', alt_table)
                    cursor.execute(alt_query)
                    results = cursor.fetchall()
                    print(f"    ✓ Found working table name: '{alt_table}'")
                    return alt_table
                except:
                    print(f"    ✗ '{alt_table}' doesn't work")

            return False

        # Test PMP query
        print(f"\n[5] Testing PMP query with sample link check...")
        pmp_with_sample_query = '''
            SELECT TOP 5
                'PMP' as Commodity,
                DateOfInspection,
                CASE WHEN EXISTS (
                    SELECT 1 FROM AFS.dbo.PMPInspectionLabSampleLinks
                    WHERE PMPInspectionLabSampleLinks.PMPInspectionRecordId = [AFS].[dbo].[PMPInspectionRecordTypes].Id
                ) THEN 1 ELSE 0 END AS IsSampleTaken,
                [AFS].[dbo].[PMPInspectionRecordTypes].Id as Id,
                clt.Name as Client
            FROM [AFS].[dbo].[PMPInspectionRecordTypes]
            JOIN AFS.dbo.PMPInspectedProductRecordTypes prod
                on prod.InspectionId = [AFS].[dbo].[PMPInspectionRecordTypes].Id
            JOIN AFS.dbo.Clients clt
                on clt.Id = prod.ClientId
            WHERE AFS.dbo.[PMPInspectionRecordTypes].IsActive = 1
                AND DateOfInspection >= '2025-10-01'
                AND DateOfInspection < '2026-04-01'
        '''

        try:
            cursor.execute(pmp_with_sample_query)
            results = cursor.fetchall()
            print(f"    ✓ PMP query with sample check works! Got {len(results)} results")
            if results:
                print(f"      Sample result: {results[0]}")
        except Exception as e:
            print(f"    ✗ PMP query with sample check failed: {e}")
            print(f"\n    Trying alternative table names...")

            # Try alternative table names
            alternatives = [
                'PMPInspectionLabSamples',
                'PMPLabSampleLinks',
                'PMPLabSamples',
                'PMPSampleLinks'
            ]

            for alt_table in alternatives:
                try:
                    alt_query = pmp_with_sample_query.replace('PMPInspectionLabSampleLinks', alt_table)
                    cursor.execute(alt_query)
                    results = cursor.fetchall()
                    print(f"    ✓ Found working table name: '{alt_table}'")
                    return alt_table
                except:
                    print(f"    ✗ '{alt_table}' doesn't work")

            return False

        print(f"\n" + "=" * 80)
        print("✓ All tests passed! The query should work.")
        print("=" * 80)

        connection.close()
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_sql_query()
