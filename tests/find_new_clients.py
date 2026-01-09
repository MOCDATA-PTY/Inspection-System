"""
Script to find all clients with "New" in their name and export to Excel
"""
import pyodbc
import pandas as pd
from datetime import datetime
import os

# SQL Server connection
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=102.67.140.12,1053;'
    'DATABASE=AFS;'
    'UID=FSAUser2;'
    'PWD=password;'
    'TrustServerCertificate=yes;'
)

def find_new_clients():
    """Find all clients with 'New' in their name"""
    try:
        print('Connecting to SQL Server...')
        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()

        print('Searching for clients starting with "New"...')

        # Query to get all client information
        query = """
            SELECT
                Id as ClientID,
                Name as ClientName,
                InternalAccountNumber,
                ContactName,
                ContactNumber,
                ContactEmail,
                PhysicalAddress,
                PostalAddress,
                VATNumber,
                CompanyRegistrationNumber,
                ContactNameForInspections,
                ContactNumberForInspections,
                ContactEmailForInspections,
                SiteName,
                IsActive,
                CreatedOn,
                ModifiedOn
            FROM [AFS].[dbo].[Clients]
            WHERE Name LIKE 'New%'
            ORDER BY Name
        """

        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()

        if not results:
            print('No clients found starting with "New"')
            cursor.close()
            conn.close()
            return None

        print(f'Found {len(results)} clients starting with "New"')

        # Convert to list of dictionaries
        clients_data = []
        for row in results:
            client_dict = {}
            for i, col in enumerate(columns):
                client_dict[col] = row[i]
            clients_data.append(client_dict)

        cursor.close()
        conn.close()

        return clients_data

    except Exception as e:
        print(f'ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return None

def export_to_excel(clients_data):
    """Export client data to Excel file"""
    if not clients_data:
        print('No data to export')
        return None

    # Create DataFrame
    df = pd.DataFrame(clients_data)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'clients_with_NEW_{timestamp}.xlsx'
    filepath = os.path.join(os.getcwd(), filename)

    print(f'\nExporting to Excel: {filename}')

    # Create Excel writer
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Clients with NEW', index=False)

        # Get the worksheet to format it
        worksheet = writer.sheets['Clients with NEW']

        # Auto-adjust column widths
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            ) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)

        # Format header row
        for cell in worksheet[1]:
            cell.font = cell.font.copy(bold=True)

    print(f'Excel file created successfully: {filepath}')
    print(f'\nSummary:')
    print(f'  Total clients: {len(df)}')
    print(f'  Active clients: {df["IsActive"].sum() if "IsActive" in df.columns else "N/A"}')

    return filepath

def main():
    print('='*60)
    print('FINDING CLIENTS STARTING WITH "NEW"')
    print('='*60)
    print()

    # Find clients
    clients_data = find_new_clients()

    if clients_data:
        # Display preview
        print('\nPreview of clients found:')
        print('-'*60)
        for i, client in enumerate(clients_data[:10], 1):
            print(f'{i}. {client.get("ClientName", "N/A")}')
            print(f'   Account: {client.get("InternalAccountNumber", "N/A")}')
            print(f'   Active: {client.get("IsActive", "N/A")}')

        if len(clients_data) > 10:
            print(f'   ... and {len(clients_data) - 10} more')
        print()

        # Export to Excel
        filepath = export_to_excel(clients_data)

        if filepath:
            print('\n' + '='*60)
            print('EXPORT COMPLETE!')
            print('='*60)
            print(f'File saved to: {filepath}')
    else:
        print('No clients found or error occurred')

if __name__ == '__main__':
    main()
