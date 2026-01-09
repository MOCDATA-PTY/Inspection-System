#!/usr/bin/env python3
"""
Search for PMP inspections with Chilli products on December 3, 2025
"""
import pyodbc
from datetime import datetime

# SQL Server connection
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=102.67.140.12,1053;'
    'DATABASE=AFS;'
    'UID=FSAUser2;'
    'PWD=password;'
    'TrustServerCertificate=yes;'
)

def search_chilli_products():
    """Search for PMP inspections with Chilli in product name"""
    try:
        print('\n' + '='*80)
        print('SEARCHING PMP INSPECTIONS WITH "CHILLI" IN PRODUCT NAME')
        print('='*80)

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        query = """
            SELECT
                pmp.Id,
                pmp.DateOfInspection,
                pmp.ClientId,
                pmp.NewClientName,
                pmp.PMPItemId,
                pmp.NewPMPItemDetails,
                pmp.IsSent,
                pmp.InspectorId,
                c.Name as ActualClientName
            FROM [AFS].[dbo].[PMPDirectionRecordTypes] pmp
            LEFT JOIN [AFS].[dbo].[Clients] c ON pmp.ClientId = c.Id
            WHERE pmp.NewPMPItemDetails LIKE '%Chilli%'
                AND pmp.DateOfInspection >= '2025-12-01'
            ORDER BY pmp.DateOfInspection DESC, pmp.Id DESC
        """

        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        if results:
            print(f'\nFound {len(results)} PMP inspections with Chilli products:')
            print('-'*80)
            for row in results:
                data = dict(zip(columns, row))
                print(f"\nInspection ID: {data['Id']}")
                print(f"Date: {data['DateOfInspection']}")
                print(f"Client ID: {data['ClientId']}")
                print(f"Client Name: {data['ActualClientName']}")
                print(f"Product: {data['NewPMPItemDetails']}")
                print(f"Inspector ID: {data['InspectorId']}")
                print(f"IsSent: {data['IsSent']}")
        else:
            print('\nNo PMP inspections found with Chilli products in December')

        cursor.close()
        conn.close()

        return results

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return None


def search_all_pmp_dec_3():
    """Search for ALL PMP inspections on December 3"""
    try:
        print('\n' + '='*80)
        print('SEARCHING ALL PMP INSPECTIONS ON DECEMBER 3, 2025')
        print('='*80)

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        query = """
            SELECT
                pmp.Id,
                pmp.DateOfInspection,
                pmp.ClientId,
                pmp.NewClientName,
                pmp.PMPItemId,
                pmp.NewPMPItemDetails,
                pmp.IsSent,
                pmp.InspectorId,
                c.Name as ActualClientName
            FROM [AFS].[dbo].[PMPDirectionRecordTypes] pmp
            LEFT JOIN [AFS].[dbo].[Clients] c ON pmp.ClientId = c.Id
            WHERE pmp.DateOfInspection >= '2025-12-03 00:00:00'
                AND pmp.DateOfInspection < '2025-12-04 00:00:00'
            ORDER BY pmp.Id DESC
        """

        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        if results:
            print(f'\nFound {len(results)} PMP inspections on December 3:')
            print('-'*80)
            for row in results:
                data = dict(zip(columns, row))
                print(f"\nInspection ID: {data['Id']}")
                print(f"Date: {data['DateOfInspection']}")
                print(f"Client ID: {data['ClientId']}")
                print(f"Client Name: {data['ActualClientName']}")
                print(f"Product: {data['NewPMPItemDetails']}")
                print(f"Inspector ID: {data['InspectorId']}")
                print(f"IsSent: {data['IsSent']}")
        else:
            print('\nNo PMP inspections found on December 3')

        cursor.close()
        conn.close()

        return results

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return None


def check_max_pmp_id():
    """Check what the maximum PMP inspection ID is"""
    try:
        print('\n' + '='*80)
        print('CHECKING MAXIMUM PMP INSPECTION ID IN DATABASE')
        print('='*80)

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        query = """
            SELECT TOP 10
                Id,
                DateOfInspection,
                ClientId,
                NewClientName,
                NewPMPItemDetails,
                IsSent
            FROM [AFS].[dbo].[PMPDirectionRecordTypes]
            ORDER BY Id DESC
        """

        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        if results:
            print(f'\nTop 10 most recent PMP inspection IDs:')
            print('-'*80)
            for row in results:
                data = dict(zip(columns, row))
                print(f"\nID: {data['Id']} | Date: {data['DateOfInspection']} | IsSent: {data['IsSent']}")
                print(f"  Client: {data['NewClientName']}")
                print(f"  Product: {data['NewPMPItemDetails']}")

        cursor.close()
        conn.close()

        return results

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return None


def main():
    print('\n' + '='*80)
    print('PMP CHILLI PRODUCT SEARCH')
    print('='*80)

    # Step 1: Check maximum IDs to see if 8696/8698 are even possible
    check_max_pmp_id()

    # Step 2: Search for Chilli products
    search_chilli_products()

    # Step 3: Search all PMP on December 3
    search_all_pmp_dec_3()

    print('\n' + '='*80)
    print('SEARCH COMPLETE')
    print('='*80)


if __name__ == '__main__':
    main()
