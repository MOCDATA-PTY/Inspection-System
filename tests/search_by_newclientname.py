#!/usr/bin/env python3
"""
Search inspections by NewClientName field (manually entered names)
"""
import pyodbc
import pandas as pd
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

def search_pmp_by_newclientname():
    """Search PMP inspections where NewClientName contains 'Amans'"""
    try:
        print('\n' + '='*80)
        print('SEARCHING PMP INSPECTIONS WHERE NewClientName CONTAINS "AMANS"')
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
            WHERE pmp.NewClientName LIKE '%Amans%'
                AND pmp.DateOfInspection >= '2025-12-01'
            ORDER BY pmp.DateOfInspection DESC, pmp.Id DESC
        """

        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        all_data = []
        if results:
            print(f'\nFound {len(results)} PMP inspections:')
            print('-'*80)
            for row in results:
                data = dict(zip(columns, row))
                all_data.append(data)
                print(f"\nInspection ID: {data['Id']}")
                print(f"Date: {data['DateOfInspection']}")
                print(f"Client ID: {data['ClientId']}")
                print(f"NewClientName (entered by inspector): {data['NewClientName']}")
                print(f"Official Client Name: {data['ActualClientName']}")
                print(f"Product: {data['NewPMPItemDetails']}")
                print(f"Inspector ID: {data['InspectorId']}")
                print(f"IsSent: {data['IsSent']}")
        else:
            print('\nNo PMP inspections found with "Amans" in NewClientName')

        cursor.close()
        conn.close()

        return all_data

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return []


def search_raw_by_newclientname():
    """Search RAW inspections where NewClientName contains 'Amans'"""
    try:
        print('\n' + '='*80)
        print('SEARCHING RAW INSPECTIONS WHERE NewClientName CONTAINS "AMANS"')
        print('='*80)

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        query = """
            SELECT
                raw.Id,
                raw.DateOfInspection,
                raw.ClientId,
                raw.NewClientName,
                raw.ProductItemId,
                raw.NewProductItemDetails,
                raw.InspectorId,
                c.Name as ActualClientName
            FROM [AFS].[dbo].[RawRMPDirectionRecordTypes] raw
            LEFT JOIN [AFS].[dbo].[Clients] c ON raw.ClientId = c.Id
            WHERE raw.NewClientName LIKE '%Amans%'
                AND raw.DateOfInspection >= '2025-12-01'
            ORDER BY raw.DateOfInspection DESC, raw.Id DESC
        """

        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        all_data = []
        if results:
            print(f'\nFound {len(results)} RAW inspections:')
            print('-'*80)
            for row in results:
                data = dict(zip(columns, row))
                all_data.append(data)
                print(f"\nInspection ID: {data['Id']}")
                print(f"Date: {data['DateOfInspection']}")
                print(f"Client ID: {data['ClientId']}")
                print(f"NewClientName (entered by inspector): {data['NewClientName']}")
                print(f"Official Client Name: {data['ActualClientName']}")
                print(f"Product: {data['NewProductItemDetails']}")
                print(f"Inspector ID: {data['InspectorId']}")
        else:
            print('\nNo RAW inspections found with "Amans" in NewClientName')

        cursor.close()
        conn.close()

        return all_data

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return []


def get_unique_newclientname_variations():
    """Get all unique NewClientName variations containing Amans"""
    try:
        print('\n' + '='*80)
        print('FINDING ALL UNIQUE NewClientName VARIATIONS CONTAINING "AMANS"')
        print('='*80)

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        # Check PMP
        query = """
            SELECT DISTINCT NewClientName, COUNT(*) as Count
            FROM [AFS].[dbo].[PMPDirectionRecordTypes]
            WHERE NewClientName LIKE '%Amans%'
            GROUP BY NewClientName
            ORDER BY Count DESC
        """
        cursor.execute(query)
        pmp_results = cursor.fetchall()

        # Check RAW
        query = """
            SELECT DISTINCT NewClientName, COUNT(*) as Count
            FROM [AFS].[dbo].[RawRMPDirectionRecordTypes]
            WHERE NewClientName LIKE '%Amans%'
            GROUP BY NewClientName
            ORDER BY Count DESC
        """
        cursor.execute(query)
        raw_results = cursor.fetchall()

        print('\nPMP NewClientName variations:')
        print('-'*80)
        for name, count in pmp_results:
            print(f"{count:4} inspections - '{name}'")

        print('\n\nRAW NewClientName variations:')
        print('-'*80)
        for name, count in raw_results:
            print(f"{count:4} inspections - '{name}'")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()


def export_to_excel(pmp_data, raw_data):
    """Export all Amans inspections to Excel"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'Amans_All_December_Inspections_{timestamp}.xlsx'

        print(f'\n\nExporting to Excel: {filename}')

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            if pmp_data:
                df_pmp = pd.DataFrame(pmp_data)
                df_pmp.to_excel(writer, sheet_name='PMP', index=False)
                print(f'  PMP sheet: {len(df_pmp)} records')

            if raw_data:
                df_raw = pd.DataFrame(raw_data)
                df_raw.to_excel(writer, sheet_name='RAW', index=False)
                print(f'  RAW sheet: {len(df_raw)} records')

        print(f'\nExcel file created: {filename}')
        return filename

    except Exception as e:
        print(f'ERROR creating Excel: {str(e)}')
        import traceback
        traceback.print_exc()
        return None


def main():
    print('\n' + '='*80)
    print('AMANS INSPECTION SEARCH BY NewClientName FIELD')
    print('='*80)

    # Step 1: Show all unique name variations
    get_unique_newclientname_variations()

    # Step 2: Get all PMP inspections
    pmp_data = search_pmp_by_newclientname()

    # Step 3: Get all RAW inspections
    raw_data = search_raw_by_newclientname()

    # Step 4: Export to Excel
    if pmp_data or raw_data:
        export_to_excel(pmp_data, raw_data)

    print('\n' + '='*80)
    print('SUMMARY')
    print('='*80)
    print(f'Total PMP inspections in December: {len(pmp_data)}')
    print(f'Total RAW inspections in December: {len(raw_data)}')
    print('='*80)


if __name__ == '__main__':
    main()
