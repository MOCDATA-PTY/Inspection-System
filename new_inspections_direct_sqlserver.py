#!/usr/bin/env python
"""
Script to fetch ALL inspections where client names START with "New"
DIRECTLY from SQL Server - bypassing local database filters
Displays: Remote ID, Client Name, Inspection Date, Account Code, and Commodity
"""

import pyodbc
from datetime import datetime
from collections import Counter

def main():
    print("=" * 110)
    print("INSPECTIONS FOR CLIENTS STARTING WITH 'NEW' - DIRECT FROM SQL SERVER (ALL TIME)")
    print("=" * 110)
    print(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # SQL Server connection details
    server = '102.67.140.12'
    port = '1053'
    database = 'AFS'
    username = 'FSAUser2'
    password = 'password'
    driver = 'ODBC Driver 17 for SQL Server'

    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server},{port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=yes;"
    )

    try:
        print("Connecting to SQL Server...")
        connection = pyodbc.connect(connection_string, timeout=30)
        cursor = connection.cursor()
        print("Connected successfully!\n")

        # Query ALL inspections (no date filter!) where client names START with "New"
        # This combines all commodity types (POULTRY, EGGS, RAW, PMP)
        query = '''
            SELECT 'POULTRY' as Commodity, DateOfInspection, PoultryQuidInspectionRecordTypes.Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber
            FROM AFS.dbo.PoultryQuidInspectionRecordTypes
            JOIN AFS.dbo.Clients clt ON clt.Id = PoultryQuidInspectionRecordTypes.ClientId
            WHERE PoultryQuidInspectionRecordTypes.IsActive = 1
            AND LOWER(clt.Name) LIKE LOWER(?)

            UNION ALL

            SELECT 'POULTRY' as Commodity, DateOfInspection, PoultryGradingInspectionRecordTypes.Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber
            FROM AFS.dbo.PoultryGradingInspectionRecordTypes
            JOIN AFS.dbo.Clients clt ON clt.Id = PoultryGradingInspectionRecordTypes.ClientId
            WHERE PoultryGradingInspectionRecordTypes.IsActive = 1
            AND LOWER(clt.Name) LIKE LOWER(?)

            UNION ALL

            SELECT 'POULTRY' as Commodity, DateOfInspection, PoultryLabelInspectionChecklistRecords.Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber
            FROM AFS.dbo.PoultryLabelInspectionChecklistRecords
            JOIN AFS.dbo.Clients clt ON clt.Id = PoultryLabelInspectionChecklistRecords.ClientId
            WHERE PoultryLabelInspectionChecklistRecords.IsActive = 1
            AND LOWER(clt.Name) LIKE LOWER(?)

            UNION ALL

            SELECT 'EGGS' as Commodity, DateOfInspection, PoultryEggInspectionRecords.Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber
            FROM AFS.dbo.PoultryEggInspectionRecords
            JOIN AFS.dbo.Clients clt ON clt.Id = PoultryEggInspectionRecords.ClientId
            WHERE PoultryEggInspectionRecords.IsActive = 1
            AND LOWER(clt.Name) LIKE LOWER(?)

            UNION ALL

            SELECT 'RAW' as Commodity, DateOfInspection, RawRMPInspectionRecordTypes.Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber
            FROM AFS.dbo.RawRMPInspectionRecordTypes
            JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod ON prod.InspectionId = RawRMPInspectionRecordTypes.Id
            JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
            WHERE RawRMPInspectionRecordTypes.IsActive = 1
            AND LOWER(clt.Name) LIKE LOWER(?)

            UNION ALL

            SELECT 'PMP' as Commodity, DateOfInspection, PMPInspectionRecordTypes.Id as Id, clt.Name as Client, clt.InternalAccountNumber as InternalAccountNumber
            FROM AFS.dbo.PMPInspectionRecordTypes
            JOIN AFS.dbo.PMPInspectedProductRecordTypes prod ON prod.InspectionId = PMPInspectionRecordTypes.Id
            JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
            WHERE PMPInspectionRecordTypes.IsActive = 1
            AND LOWER(clt.Name) LIKE LOWER(?)

            ORDER BY DateOfInspection DESC, Client
        '''

        print("Querying SQL Server for ALL inspections where client name STARTS with 'New'...")
        print("This may take a moment...\n")

        # Execute query with 6 parameters (one for each UNION ALL query)
        # Using 'New%' to match names that START with "New" (not contain)
        cursor.execute(query, ('New%', 'New%', 'New%', 'New%', 'New%', 'New%'))

        # Fetch all results
        raw_results = cursor.fetchall()

        # Convert to list of dictionaries
        inspection_data = []
        for row in raw_results:
            inspection_data.append({
                'commodity': row[0],
                'date_of_inspection': row[1],
                'remote_id': row[2],
                'client_name': row[3],
                'internal_account_code': row[4]
            })

        total_count = len(inspection_data)
        print(f"Total Inspections Found (SQL SERVER - ALL TIME): {total_count}")

        # Show date range
        if total_count > 0:
            dates = [row['date_of_inspection'] for row in inspection_data if row['date_of_inspection']]
            if dates:
                earliest = min(dates)
                latest = max(dates)
                if isinstance(earliest, str):
                    print(f"Date Range: {earliest} to {latest}")
                else:
                    print(f"Date Range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}")
        print()

        if total_count == 0:
            print("No inspections found with client names containing 'New'.")
            return

        # Save to file AND print to console
        output_filename = f"new_inspections_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(output_filename, 'w', encoding='utf-8') as f:
            # Write header to file
            f.write("=" * 110 + "\n")
            f.write("INSPECTIONS FOR CLIENTS STARTING WITH 'NEW' - DIRECT FROM SQL SERVER (ALL TIME)\n")
            f.write("=" * 110 + "\n")
            f.write(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Inspections Found: {total_count}\n")
            f.write(f"Date Range: {min([r['date_of_inspection'] for r in inspection_data if r['date_of_inspection']]).strftime('%Y-%m-%d')} to {max([r['date_of_inspection'] for r in inspection_data if r['date_of_inspection']]).strftime('%Y-%m-%d')}\n\n")

            # Write table header to file
            header = f"{'#':<6} {'Remote ID':<12} {'Client Name':<50} {'Inspection Date':<18} {'Account Code':<25} {'Commodity':<15}"
            f.write(header + "\n")
            f.write("-" * 130 + "\n")

            # Print table header to console
            print(f"{'#':<6} {'Remote ID':<12} {'Client Name':<35} {'Inspection Date':<18} {'Account Code':<20} {'Commodity':<15}")
            print("-" * 110)

            # Print each inspection to BOTH file and console
            for index, inspection in enumerate(inspection_data, 1):
                remote_id = str(inspection['remote_id']) if inspection['remote_id'] else "N/A"
                client_name = inspection['client_name'] or "N/A"

                # Handle date formatting
                date_val = inspection['date_of_inspection']
                if date_val:
                    if isinstance(date_val, str):
                        inspection_date = date_val
                    else:
                        inspection_date = date_val.strftime('%Y-%m-%d')
                else:
                    inspection_date = "N/A"

                account_code = inspection['internal_account_code'] or "N/A"
                commodity = inspection['commodity'] or "N/A"

                # Write full line to file (no truncation)
                file_line = f"{index:<6} {remote_id:<12} {client_name:<50} {inspection_date:<18} {account_code:<25} {commodity:<15}"
                f.write(file_line + "\n")

                # Print truncated version to console
                display_client_name = client_name
                if len(display_client_name) > 34:
                    display_client_name = display_client_name[:31] + "..."

                console_line = f"{index:<6} {remote_id:<12} {display_client_name:<35} {inspection_date:<18} {account_code:<20} {commodity:<15}"
                print(console_line)

            # Write bottom border and total to file
            f.write("-" * 130 + "\n")
            f.write(f"\n*** GRAND TOTAL: {total_count} INSPECTIONS ***\n\n")

        # Print bottom border and total to console
        print("-" * 110)
        print(f"\n*** GRAND TOTAL: {total_count} INSPECTIONS ***\n")
        print(f"\nFull report saved to: {output_filename}")

        # Summary statistics
        print("\n" + "=" * 110)
        print("SUMMARY STATISTICS")
        print("=" * 110)

        # Count by commodity
        commodity_list = [row['commodity'] or "Not Specified" for row in inspection_data]
        commodity_counts = Counter(commodity_list)
        print("\nInspections by Commodity:")
        for commodity_name, count in commodity_counts.most_common():
            print(f"  {commodity_name}: {count}")

        # Date range
        dates = [row['date_of_inspection'] for row in inspection_data if row['date_of_inspection']]
        if dates:
            earliest = min(dates)
            latest = max(dates)
            print(f"\nDate Range:")
            if isinstance(earliest, str):
                print(f"  Earliest: {earliest}")
                print(f"  Latest: {latest}")
            else:
                print(f"  Earliest: {earliest.strftime('%Y-%m-%d')}")
                print(f"  Latest: {latest.strftime('%Y-%m-%d')}")

        print("\n" + "=" * 110)

        # Close connection
        cursor.close()
        connection.close()
        print("\nQuery completed successfully!")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
