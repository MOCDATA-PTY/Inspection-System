#!/usr/bin/env python3
"""
Search for Amans POULTRY inspections in December
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

def search_poultry_amans():
    """Search POULTRY inspections where NewClientName contains 'Amans'"""
    try:
        print('\n' + '='*80)
        print('SEARCHING POULTRY INSPECTIONS FOR AMANS IN DECEMBER')
        print('='*80)

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        query = """
            SELECT
                poultry.Id,
                poultry.DateOfInspection,
                poultry.ClientId,
                poultry.NewClientName,
                poultry.ProductName,
                poultry.InspectorId,
                c.Name as ActualClientName
            FROM [AFS].[dbo].[PoultryDirectionRecordTypes] poultry
            LEFT JOIN [AFS].[dbo].[Clients] c ON poultry.ClientId = c.Id
            WHERE poultry.NewClientName LIKE '%Amans%'
                AND poultry.DateOfInspection >= '2025-12-01'
            ORDER BY poultry.DateOfInspection DESC, poultry.Id DESC
        """

        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        if results:
            print(f'\nFound {len(results)} POULTRY inspections:')
            print('-'*80)
            for row in results:
                data = dict(zip(columns, row))
                print(f"\nInspection ID: {data['Id']}")
                print(f"Date: {data['DateOfInspection']}")
                print(f"Client ID: {data['ClientId']}")
                print(f"NewClientName: {data['NewClientName']}")
                print(f"Official Client: {data['ActualClientName']}")
                print(f"Product: {data['ProductName']}")
                print(f"Inspector ID: {data['InspectorId']}")
        else:
            print('\nNo POULTRY inspections found with "Amans" in NewClientName')

        cursor.close()
        conn.close()

        return results

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return []


def search_all_dec3_inspector_177():
    """Search ALL inspections by Inspector 177 on December 3"""
    try:
        print('\n' + '='*80)
        print('SEARCHING ALL INSPECTIONS BY INSPECTOR 177 ON DEC 3')
        print('='*80)

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        print('\nPOULTRY:')
        print('-'*80)
        query = """
            SELECT
                Id,
                DateOfInspection,
                ClientId,
                NewClientName,
                ProductName
            FROM [AFS].[dbo].[PoultryDirectionRecordTypes]
            WHERE InspectorId = 177
                AND DateOfInspection >= '2025-12-03 00:00:00'
                AND DateOfInspection < '2025-12-04 00:00:00'
            ORDER BY DateOfInspection
        """
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"ID: {row[0]} | Time: {row[1]} | Client: {row[3]} | Product: {row[4]}")
        else:
            print("No POULTRY inspections")

        print('\nPMP:')
        print('-'*80)
        query = """
            SELECT
                Id,
                DateOfInspection,
                ClientId,
                NewClientName,
                NewPMPItemDetails
            FROM [AFS].[dbo].[PMPDirectionRecordTypes]
            WHERE InspectorId = 177
                AND DateOfInspection >= '2025-12-03 00:00:00'
                AND DateOfInspection < '2025-12-04 00:00:00'
            ORDER BY DateOfInspection
        """
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"ID: {row[0]} | Time: {row[1]} | Client: {row[3]} | Product: {row[4]}")
        else:
            print("No PMP inspections")

        print('\nRAW:')
        print('-'*80)
        query = """
            SELECT
                Id,
                DateOfInspection,
                ClientId,
                NewClientName,
                NewProductItemDetails
            FROM [AFS].[dbo].[RawRMPDirectionRecordTypes]
            WHERE InspectorId = 177
                AND DateOfInspection >= '2025-12-03 00:00:00'
                AND DateOfInspection < '2025-12-04 00:00:00'
            ORDER BY DateOfInspection
        """
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"ID: {row[0]} | Time: {row[1]} | Client: {row[3]} | Product: {row[4]}")
        else:
            print("No RAW inspections")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()


def main():
    print('\n' + '='*80)
    print('AMANS POULTRY INSPECTION SEARCH')
    print('='*80)

    # Search for Amans poultry inspections
    search_poultry_amans()

    # Show all inspections by inspector 177 on Dec 3
    search_all_dec3_inspector_177()

    print('\n' + '='*80)
    print('SEARCH COMPLETE')
    print('='*80)


if __name__ == '__main__':
    main()
