#!/usr/bin/env python3
"""
Search for Amans PMP inspections by ID and client name patterns
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

def search_by_inspection_ids():
    """Search PMP inspections directly by IDs 8696 and 8698"""
    try:
        print('\n' + '='*80)
        print('SEARCHING PMP INSPECTIONS BY ID (8696, 8698)')
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
                c.Name as ActualClientName,
                c.InternalAccountNumber
            FROM [AFS].[dbo].[PMPDirectionRecordTypes] pmp
            LEFT JOIN [AFS].[dbo].[Clients] c ON pmp.ClientId = c.Id
            WHERE pmp.Id IN (8696, 8698)
            ORDER BY pmp.Id
        """

        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        if results:
            print(f'\nFound {len(results)} PMP inspections:')
            print('-'*80)
            for row in results:
                data = dict(zip(columns, row))
                print(f"\nInspection ID: {data['Id']}")
                print(f"Date: {data['DateOfInspection']}")
                print(f"Client ID: {data['ClientId']}")
                print(f"Client Name (from Clients table): {data['ActualClientName']}")
                print(f"Client Name (NewClientName field): {data['NewClientName']}")
                print(f"Product ID: {data['PMPItemId']}")
                print(f"Product Details: {data['NewPMPItemDetails']}")
                print(f"Inspector ID: {data['InspectorId']}")
                print(f"Is Sent: {data['IsSent']}")
        else:
            print('\nNo PMP inspections found with IDs 8696 or 8698')

        cursor.close()
        conn.close()

        return results

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return None


def search_clients_with_slash():
    """Search for clients with forward slash in name"""
    try:
        print('\n' + '='*80)
        print('SEARCHING CLIENTS WITH "/" IN NAME (COMBINED NAMES)')
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
            WHERE Name LIKE '%/%'
                AND (Name LIKE '%Amans%' OR Name LIKE '%Processed Meat%')
            ORDER BY Name
        """

        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        if results:
            print(f'\nFound {len(results)} clients with "/" in name:')
            print('-'*80)
            for row in results:
                data = dict(zip(columns, row))
                print(f"\nClient ID: {data['Id']}")
                print(f"Name: {data['Name']}")
                print(f"Account: {data['InternalAccountNumber']}")
                print(f"Active: {data['IsActive']}")
        else:
            print('\nNo clients found with "/" in name')

        cursor.close()
        conn.close()

        return results

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return None


def search_all_amans_related():
    """Search for all clients containing Amans"""
    try:
        print('\n' + '='*80)
        print('SEARCHING ALL CLIENTS CONTAINING "AMANS"')
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
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        if results:
            print(f'\nFound {len(results)} clients with "Amans" in name:')
            print('-'*80)
            for row in results:
                data = dict(zip(columns, row))
                print(f"\nClient ID: {data['Id']}")
                print(f"Name: {data['Name']}")
                print(f"Account: {data['InternalAccountNumber']}")
                print(f"Active: {data['IsActive']}")
        else:
            print('\nNo clients found with "Amans" in name')

        cursor.close()
        conn.close()

        return results

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return None


def search_pmp_for_client_id(client_id):
    """Search PMP inspections for a specific client ID in December"""
    try:
        print('\n' + '='*80)
        print(f'SEARCHING PMP INSPECTIONS FOR CLIENT ID {client_id} IN DECEMBER')
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
            WHERE pmp.ClientId = ?
                AND pmp.DateOfInspection >= '2025-12-01'
                AND pmp.DateOfInspection < '2026-01-01'
            ORDER BY pmp.DateOfInspection DESC, pmp.Id
        """

        cursor.execute(query, client_id)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        if results:
            print(f'\nFound {len(results)} PMP inspections:')
            print('-'*80)
            for row in results:
                data = dict(zip(columns, row))
                print(f"\nInspection ID: {data['Id']}")
                print(f"Date: {data['DateOfInspection']}")
                print(f"Client Name: {data['ActualClientName']}")
                print(f"Product ID: {data['PMPItemId']}")
                print(f"Product: {data['NewPMPItemDetails']}")
                print(f"Inspector ID: {data['InspectorId']}")
        else:
            print(f'\nNo PMP inspections found for client ID {client_id} in December')

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
    print('AMANS PMP INSPECTION SEARCH')
    print('='*80)

    # Step 1: Search by exact inspection IDs from screenshot
    inspection_results = search_by_inspection_ids()

    # Step 2: Search for clients with "/" (combined names)
    slash_clients = search_clients_with_slash()

    # Step 3: Search all Amans-related clients
    amans_clients = search_all_amans_related()

    # Step 4: If we found Amans-related clients, search their PMP inspections
    if amans_clients:
        for row in amans_clients:
            client_id = row[0]
            search_pmp_for_client_id(client_id)

    print('\n' + '='*80)
    print('SEARCH COMPLETE')
    print('='*80)


if __name__ == '__main__':
    main()
