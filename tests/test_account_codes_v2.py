#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to pull account codes from SQL Server for latest 10 inspections
Uses correct table names from the actual FSA database
"""
import os
import sys
import pymssql

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("\n" + "="*80)
print("ACCOUNT CODE RETRIEVAL TEST - V2")
print("="*80)
print("\nPulling account codes from SQL Server Clients table for latest 10 inspections\n")

def test_sql_connection():
    """Test SQL Server connection"""
    print("="*80)
    print("STEP 1: Testing SQL Server Connection")
    print("="*80)

    try:
        connection = pymssql.connect(
            server='102.67.140.12',
            port=1053,
            database='AFS',
            user='FSAUser2',
            password='password',
            timeout=30
        )
        print("✓ Connected to SQL Server successfully")
        print(f"  Server: 102.67.140.12:1053")
        print(f"  Database: AFS")
        return connection
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None

def check_clients_table(connection):
    """Check the Clients table for account code fields"""
    print("\n" + "="*80)
    print("STEP 2: Checking Clients Table Structure")
    print("="*80)

    try:
        cursor = connection.cursor(as_dict=True)

        # Check Clients table structure
        print("\nQuerying Clients table structure...")
        cursor.execute("""
            SELECT TOP 1 *
            FROM AFS.dbo.Clients
        """)

        sample_client = cursor.fetchone()
        if sample_client:
            print(f"\n✓ Found {len(sample_client.keys())} columns in Clients table")
            print("\nClients table columns:")
            print("-"*80)
            for idx, col in enumerate(sorted(sample_client.keys()), 1):
                value = sample_client[col]
                str_value = str(value) if value is not None else 'NULL'
                if len(str_value) > 50:
                    str_value = str_value[:50] + '...'
                print(f"  {idx:2d}. {col:30s}: {str_value}")

            # Highlight account-related columns
            account_cols = [col for col in sample_client.keys()
                           if 'account' in col.lower() or 'code' in col.lower() or 'number' in col.lower()]

            if account_cols:
                print("\n" + "-"*80)
                print("✓ Potential account code columns found:")
                for col in account_cols:
                    print(f"  - {col}: {sample_client[col]}")

        return True

    except Exception as e:
        print(f"\n✗ Error checking Clients table: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_latest_inspections_with_clients(connection):
    """Get latest 10 inspections with client info including account codes"""
    print("\n" + "="*80)
    print("STEP 3: Retrieving Latest 10 Inspections with Client Data")
    print("="*80)

    try:
        cursor = connection.cursor(as_dict=True)

        # Query latest inspections from POULTRY table with Clients data
        print("\nQuerying latest POULTRY inspections with client info...")
        cursor.execute("""
            SELECT TOP 10
                p.Id as InspectionId,
                p.DateOfInspection,
                p.InspectorId,
                p.ProductName,
                p.ClientId,
                c.Name as ClientName,
                c.*
            FROM AFS.dbo.PoultryQuidInspectionRecordTypes p
            JOIN AFS.dbo.Clients c ON c.Id = p.ClientId
            WHERE p.IsActive = 1
            ORDER BY p.DateOfInspection DESC
        """)

        inspections = cursor.fetchall()

        if not inspections:
            print("\n✗ No inspections found")
            return []

        print(f"\n✓ Retrieved {len(inspections)} inspections")
        print("\n" + "="*80)
        print("LATEST 10 INSPECTIONS WITH CLIENT/ACCOUNT DATA")
        print("="*80)

        for idx, insp in enumerate(inspections, 1):
            print(f"\n{'='*80}")
            print(f"INSPECTION #{idx}")
            print(f"{'='*80}")

            # Display inspection fields
            print(f"  Inspection ID:     {insp.get('InspectionId', 'N/A')}")
            print(f"  Date:              {insp.get('DateOfInspection', 'N/A')}")
            print(f"  Inspector ID:      {insp.get('InspectorId', 'N/A')}")
            print(f"  Product:           {insp.get('ProductName', 'N/A')}")

            # Display client fields
            print(f"\n  Client Information:")
            print(f"    Client ID:       {insp.get('ClientId', 'N/A')}")
            print(f"    Client Name:     {insp.get('ClientName', 'N/A')}")

            # Display all client fields that might be account codes
            print(f"\n  All Client Fields:")
            for key, value in insp.items():
                if key not in ['InspectionId', 'DateOfInspection', 'InspectorId', 'ProductName', 'ClientId', 'ClientName', 'Id', 'Name']:
                    str_value = str(value) if value is not None else 'NULL'
                    if len(str_value) > 60:
                        str_value = str_value[:60] + '...'
                    print(f"    {key:30s}: {str_value}")

        return inspections

    except Exception as e:
        print(f"\n✗ Error retrieving inspections: {e}")
        import traceback
        traceback.print_exc()
        return []

def search_account_code_in_clients(connection):
    """Search for account code specifically in Clients table"""
    print("\n" + "="*80)
    print("STEP 4: Searching for Account Codes in Clients Table")
    print("="*80)

    try:
        cursor = connection.cursor(as_dict=True)

        # Get column names from Clients table
        cursor.execute("""
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'Clients'
            AND TABLE_SCHEMA = 'dbo'
            ORDER BY ORDINAL_POSITION
        """)

        columns = cursor.fetchall()

        if columns:
            print(f"\n✓ Found {len(columns)} columns in Clients table")
            print("\nColumn List:")
            print("-"*80)
            print(f"{'Column Name':<40} {'Data Type':<15} {'Max Length'}")
            print("-"*80)

            account_related = []
            for col in columns:
                col_name = col['COLUMN_NAME']
                data_type = col['DATA_TYPE']
                max_len = col['CHARACTER_MAXIMUM_LENGTH'] or 'N/A'
                print(f"{col_name:<40} {data_type:<15} {str(max_len)}")

                # Check if column name suggests it's an account code
                if any(keyword in col_name.lower() for keyword in ['account', 'code', 'number', 'acc', 'ref']):
                    account_related.append(col_name)

            if account_related:
                print("\n" + "-"*80)
                print(f"✓ Found {len(account_related)} potential account code columns:")
                for col in account_related:
                    print(f"  - {col}")

                    # Try to get sample values
                    try:
                        cursor.execute(f"""
                            SELECT TOP 5
                                Name as ClientName,
                                [{col}]
                            FROM AFS.dbo.Clients
                            WHERE [{col}] IS NOT NULL
                        """)

                        samples = cursor.fetchall()
                        if samples:
                            print(f"    Sample values:")
                            for sample in samples:
                                print(f"      {sample['ClientName']:40s} | {col}: {sample[col]}")
                    except Exception as e:
                        print(f"    Could not retrieve samples: {e}")

        return True

    except Exception as e:
        print(f"\n✗ Error searching for account codes: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE ACCOUNT CODE TEST")
    print("="*80)

    try:
        # Step 1: Test connection
        connection = test_sql_connection()

        if not connection:
            print("\n✗ Cannot proceed without database connection")
            return

        # Step 2: Check Clients table structure
        check_clients_table(connection)

        # Step 3: Get latest inspections with client data
        inspections = get_latest_inspections_with_clients(connection)

        # Step 4: Search specifically for account codes
        search_account_code_in_clients(connection)

        connection.close()

        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)

        print(f"\n✓ Successfully connected to SQL Server")
        print(f"✓ Retrieved {len(inspections)} inspections with client data")
        print(f"✓ Analyzed Clients table structure")
        print(f"\n✓ Check the output above for:")
        print(f"  1. 'Potential account code columns' in Clients table")
        print(f"  2. 'All Client Fields' section in each inspection")
        print(f"  3. Sample values for account-related columns")

        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("""
Based on the output above:

1. Look for columns in Clients table that might be account codes:
   - Common names: AccountCode, Account_Code, Code, CustomerCode, etc.
   - Check the sample values to verify which column contains the account codes

2. Once identified, you can:
   - Add it to your Django model if needed
   - Include it in the sync process
   - Update FSA_INSPECTION_QUERY to include the account code

3. If no obvious column found:
   - Check the 'All Client Fields' section
   - May need to ask database administrator
   - Account code might be stored differently
        """)

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
