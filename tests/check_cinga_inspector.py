#!/usr/bin/env python3
"""
Check inspector ID for CINGA NGONGO and their inspections
"""
import pyodbc

# SQL Server connection
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=102.67.140.12,1053;'
    'DATABASE=AFS;'
    'UID=FSAUser2;'
    'PWD=password;'
    'TrustServerCertificate=yes;'
)

def find_inspector_id():
    """Find CINGA NGONGO's inspector ID from Django database"""
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    django.setup()

    from main.models import Inspector

    try:
        inspector = Inspector.objects.filter(name__icontains='CINGA').first()
        if inspector:
            print(f"\nFound in Django: {inspector.name} (ID: {inspector.inspector_id})")
            return inspector.inspector_id
        else:
            print("\nCINGA not found in Django database")
            return None
    except Exception as e:
        print(f"Error querying Django: {e}")
        return None


def check_cinga_inspections_dec_3(inspector_id):
    """Check all inspections by CINGA on December 3"""
    try:
        print('\n' + '='*80)
        print(f'CHECKING ALL INSPECTIONS BY INSPECTOR ID {inspector_id} ON DEC 3')
        print('='*80)

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        # Check RAW inspections
        print('\nRAW Inspections:')
        print('-'*80)
        query = """
            SELECT
                Id,
                DateOfInspection,
                ClientId,
                NewClientName,
                NewProductItemDetails,
                IsSampleTaken
            FROM [AFS].[dbo].[RawRMPDirectionRecordTypes]
            WHERE InspectorId = ?
                AND DateOfInspection >= '2025-12-03 00:00:00'
                AND DateOfInspection < '2025-12-04 00:00:00'
            ORDER BY DateOfInspection
        """
        cursor.execute(query, inspector_id)
        results = cursor.fetchall()

        if results:
            for row in results:
                print(f"\nID: {row[0]} | Time: {row[1]}")
                print(f"  Client: {row[3]}")
                print(f"  Product: {row[4]}")
                print(f"  Sample: {row[5]}")
        else:
            print("No RAW inspections found")

        # Check PMP inspections
        print('\n\nPMP Inspections:')
        print('-'*80)
        query = """
            SELECT
                Id,
                DateOfInspection,
                ClientId,
                NewClientName,
                NewPMPItemDetails
            FROM [AFS].[dbo].[PMPDirectionRecordTypes]
            WHERE InspectorId = ?
                AND DateOfInspection >= '2025-12-03 00:00:00'
                AND DateOfInspection < '2025-12-04 00:00:00'
            ORDER BY DateOfInspection
        """
        cursor.execute(query, inspector_id)
        results = cursor.fetchall()

        if results:
            for row in results:
                print(f"\nID: {row[0]} | Time: {row[1]}")
                print(f"  Client: {row[3]}")
                print(f"  Product: {row[4]}")
        else:
            print("No PMP inspections found")

        # Check EGGS inspections
        print('\n\nEGGS Inspections:')
        print('-'*80)
        query = """
            SELECT
                Id,
                DateOfInspection,
                ClientId,
                ClientBranch,
                EggProducer
            FROM [AFS].[dbo].[PoultryEggDirections]
            WHERE InspectorId = ?
                AND DateOfInspection >= '2025-12-03 00:00:00'
                AND DateOfInspection < '2025-12-04 00:00:00'
            ORDER BY DateOfInspection
        """
        cursor.execute(query, inspector_id)
        results = cursor.fetchall()

        if results:
            for row in results:
                print(f"\nID: {row[0]} | Time: {row[1]}")
                print(f"  Client: {row[3]}")
                print(f"  Producer: {row[4]}")
        else:
            print("No EGGS inspections found")

        # Check POULTRY inspections
        print('\n\nPOULTRY Inspections:')
        print('-'*80)
        query = """
            SELECT
                Id,
                DateOfInspection,
                ClientId,
                NewClientName,
                ProductName
            FROM [AFS].[dbo].[PoultryDirectionRecordTypes]
            WHERE InspectorId = ?
                AND DateOfInspection >= '2025-12-03 00:00:00'
                AND DateOfInspection < '2025-12-04 00:00:00'
            ORDER BY DateOfInspection
        """
        cursor.execute(query, inspector_id)
        results = cursor.fetchall()

        if results:
            for row in results:
                print(f"\nID: {row[0]} | Time: {row[1]}")
                print(f"  Client: {row[3]}")
                print(f"  Product: {row[4]}")
        else:
            print("No POULTRY inspections found")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()


def main():
    print('\n' + '='*80)
    print('CINGA NGONGO INSPECTION CHECK')
    print('='*80)

    # Find CINGA's inspector ID
    inspector_id = find_inspector_id()

    if inspector_id:
        # Check all their inspections on Dec 3
        check_cinga_inspections_dec_3(inspector_id)
    else:
        print("\nCould not find CINGA's inspector ID")

    print('\n' + '='*80)
    print('CHECK COMPLETE')
    print('='*80)


if __name__ == '__main__':
    main()
