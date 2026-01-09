#!/usr/bin/env python3
"""
Find all client name variations containing "Amans" and their PMP inspections
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

def find_all_amans_clients():
    """Find ALL client IDs that have 'Amans' anywhere in the name"""
    try:
        print('\n' + '='*80)
        print('FINDING ALL CLIENT VARIATIONS CONTAINING "AMANS"')
        print('='*80)

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        query = """
            SELECT
                Id,
                Name,
                InternalAccountNumber,
                IsActive
            FROM [AFS].[dbo].[Clients]
            WHERE Name LIKE '%Amans%'
            ORDER BY Name
        """

        cursor.execute(query)
        results = cursor.fetchall()

        client_ids = []
        if results:
            print(f'\nFound {len(results)} client name variations:')
            print('-'*80)
            for row in results:
                client_id, name, account, is_active = row
                print(f"\nClient ID: {client_id}")
                print(f"Name: {name}")
                print(f"Account: {account}")
                print(f"Active: {is_active}")
                client_ids.append(client_id)
        else:
            print('\nNo clients found with "Amans" in name')

        cursor.close()
        conn.close()

        return client_ids

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return []


def find_pmp_for_all_clients(client_ids):
    """Find all PMP inspections for all Amans client IDs in December"""
    try:
        print('\n' + '='*80)
        print(f'FINDING PMP INSPECTIONS FOR ALL AMANS CLIENTS IN DECEMBER')
        print('='*80)

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        # Build query with IN clause for multiple client IDs
        placeholders = ','.join('?' * len(client_ids))
        query = f"""
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
            WHERE pmp.ClientId IN ({placeholders})
                AND pmp.DateOfInspection >= '2025-12-01'
                AND pmp.DateOfInspection < '2026-01-01'
            ORDER BY pmp.DateOfInspection DESC, pmp.Id DESC
        """

        cursor.execute(query, client_ids)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        all_inspections = []
        if results:
            print(f'\nFound {len(results)} PMP inspections across all Amans clients:')
            print('-'*80)
            for row in results:
                data = dict(zip(columns, row))
                all_inspections.append(data)
                print(f"\nInspection ID: {data['Id']}")
                print(f"Date: {data['DateOfInspection']}")
                print(f"Client ID: {data['ClientId']}")
                print(f"Client Name: {data['ActualClientName']}")
                print(f"Product: {data['NewPMPItemDetails']}")
                print(f"Inspector ID: {data['InspectorId']}")
                print(f"IsSent: {data['IsSent']}")
        else:
            print(f'\nNo PMP inspections found for any Amans clients in December')

        cursor.close()
        conn.close()

        return all_inspections

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return []


def find_raw_for_all_clients(client_ids):
    """Find all RAW inspections for all Amans client IDs in December"""
    try:
        print('\n' + '='*80)
        print(f'FINDING RAW INSPECTIONS FOR ALL AMANS CLIENTS IN DECEMBER')
        print('='*80)

        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        # Build query with IN clause for multiple client IDs
        placeholders = ','.join('?' * len(client_ids))
        query = f"""
            SELECT
                raw.Id,
                raw.DateOfInspection,
                raw.ClientId,
                raw.NewClientName,
                raw.ProductItemId,
                raw.NewProductItemDetails,
                raw.IsSampleTaken,
                raw.InspectorId,
                c.Name as ActualClientName
            FROM [AFS].[dbo].[RawRMPDirectionRecordTypes] raw
            LEFT JOIN [AFS].[dbo].[Clients] c ON raw.ClientId = c.Id
            WHERE raw.ClientId IN ({placeholders})
                AND raw.DateOfInspection >= '2025-12-01'
                AND raw.DateOfInspection < '2026-01-01'
            ORDER BY raw.DateOfInspection DESC, raw.Id DESC
        """

        cursor.execute(query, client_ids)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        all_inspections = []
        if results:
            print(f'\nFound {len(results)} RAW inspections across all Amans clients:')
            print('-'*80)
            for row in results:
                data = dict(zip(columns, row))
                all_inspections.append(data)
                print(f"\nInspection ID: {data['Id']}")
                print(f"Date: {data['DateOfInspection']}")
                print(f"Client ID: {data['ClientId']}")
                print(f"Client Name: {data['ActualClientName']}")
                print(f"Product: {data['NewProductItemDetails']}")
                print(f"Sample Taken: {data['IsSampleTaken']}")
                print(f"Inspector ID: {data['InspectorId']}")
        else:
            print(f'\nNo RAW inspections found for any Amans clients in December')

        cursor.close()
        conn.close()

        return all_inspections

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return []


def export_to_excel(pmp_inspections, raw_inspections):
    """Export all Amans inspections to Excel"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'Amans_All_Inspections_December_{timestamp}.xlsx'

        print(f'\n\nExporting to Excel: {filename}')

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            if pmp_inspections:
                df_pmp = pd.DataFrame(pmp_inspections)
                df_pmp.to_excel(writer, sheet_name='PMP Inspections', index=False)
                print(f'  PMP sheet: {len(df_pmp)} records')

            if raw_inspections:
                df_raw = pd.DataFrame(raw_inspections)
                df_raw.to_excel(writer, sheet_name='RAW Inspections', index=False)
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
    print('AMANS CLIENT VARIATIONS AND INSPECTIONS SEARCH')
    print('='*80)

    # Step 1: Find all client IDs with "Amans" in name
    client_ids = find_all_amans_clients()

    if not client_ids:
        print('\nNo Amans clients found!')
        return

    print(f'\n\nTotal client IDs to search: {client_ids}')

    # Step 2: Find PMP inspections for all these client IDs
    pmp_inspections = find_pmp_for_all_clients(client_ids)

    # Step 3: Find RAW inspections for all these client IDs
    raw_inspections = find_raw_for_all_clients(client_ids)

    # Step 4: Export to Excel
    if pmp_inspections or raw_inspections:
        export_to_excel(pmp_inspections, raw_inspections)

    print('\n' + '='*80)
    print('SUMMARY')
    print('='*80)
    print(f'Total Amans client variations found: {len(client_ids)}')
    print(f'Total PMP inspections in December: {len(pmp_inspections)}')
    print(f'Total RAW inspections in December: {len(raw_inspections)}')
    print('='*80)


if __name__ == '__main__':
    main()
