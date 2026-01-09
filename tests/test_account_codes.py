#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to pull account codes from SQL Server for latest 10 inspections
"""
import os
import sys
import pymssql

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("\n" + "="*80)
print("ACCOUNT CODE RETRIEVAL TEST")
print("="*80)
print("\nPulling account codes from SQL Server for latest 10 inspections\n")

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
            password='password'
        )
        print("✓ Connected to SQL Server successfully")
        print(f"  Server: 102.67.140.12:1053")
        print(f"  Database: AFS")
        return connection
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None

def get_latest_inspections_with_account_codes(connection):
    """Get latest 10 inspections with account codes"""
    print("\n" + "="*80)
    print("STEP 2: Retrieving Latest 10 Inspections with Account Codes")
    print("="*80)

    try:
        cursor = connection.cursor(as_dict=True)

        # First, let's check what columns exist in the table
        print("\nChecking available columns...")
        cursor.execute("""
            SELECT TOP 1 *
            FROM tblFoodSafetyAgencyInspection
        """)

        sample_row = cursor.fetchone()
        if sample_row:
            print(f"\n✓ Found {len(sample_row.keys())} columns in table")
            print("\nAvailable columns:")
            for idx, col in enumerate(sample_row.keys(), 1):
                print(f"  {idx:2d}. {col}")

        # Now let's try to get account codes
        # Common column names for account codes:
        # AccountCode, Account_Code, ClientCode, Client_Code, etc.

        print("\n" + "-"*80)
        print("Searching for account code columns...")
        print("-"*80)

        account_columns = [col for col in sample_row.keys()
                          if 'account' in col.lower() or 'code' in col.lower()]

        if account_columns:
            print(f"\n✓ Found {len(account_columns)} potential account code columns:")
            for col in account_columns:
                print(f"  - {col}")
        else:
            print("\n⚠️  No obvious account code columns found")
            print("  Will display all columns for latest 10 inspections")

        # Query latest 10 inspections
        print("\n" + "-"*80)
        print("Fetching latest 10 inspections...")
        print("-"*80)

        cursor.execute("""
            SELECT TOP 10
                RecordID,
                ClientName,
                DateOfInspection,
                InspectionNumber,
                *
            FROM tblFoodSafetyAgencyInspection
            ORDER BY DateOfInspection DESC
        """)

        inspections = cursor.fetchall()

        if not inspections:
            print("\n✗ No inspections found")
            return []

        print(f"\n✓ Retrieved {len(inspections)} inspections")
        print("\n" + "="*80)
        print("LATEST 10 INSPECTIONS WITH ACCOUNT CODES")
        print("="*80)

        for idx, insp in enumerate(inspections, 1):
            print(f"\n{'='*80}")
            print(f"INSPECTION #{idx}")
            print(f"{'='*80}")

            # Display key fields
            print(f"  RecordID:          {insp.get('RecordID', 'N/A')}")
            print(f"  Client Name:       {insp.get('ClientName', 'N/A')}")
            print(f"  Date:              {insp.get('DateOfInspection', 'N/A')}")
            print(f"  Inspection #:      {insp.get('InspectionNumber', 'N/A')}")

            # Display account code fields
            if account_columns:
                print(f"\n  Account Code Fields:")
                for col in account_columns:
                    value = insp.get(col, 'N/A')
                    print(f"    {col:30s}: {value}")

            # Display all fields (optional, can be commented out)
            print(f"\n  All Fields:")
            for key, value in insp.items():
                if key not in ['RecordID', 'ClientName', 'DateOfInspection', 'InspectionNumber']:
                    # Truncate long values
                    str_value = str(value) if value is not None else 'NULL'
                    if len(str_value) > 50:
                        str_value = str_value[:50] + '...'
                    print(f"    {key:30s}: {str_value}")

        return inspections

    except Exception as e:
        print(f"\n✗ Error retrieving inspections: {e}")
        import traceback
        traceback.print_exc()
        return []

def check_account_code_field():
    """Check specifically for account code field"""
    print("\n" + "="*80)
    print("STEP 3: Analyzing Account Code Field")
    print("="*80)

    try:
        connection = pymssql.connect(
            server='102.67.140.12',
            port=1053,
            database='AFS',
            user='FSAUser2',
            password='password'
        )

        cursor = connection.cursor(as_dict=True)

        # Get column information from information schema
        cursor.execute("""
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'tblFoodSafetyAgencyInspection'
            AND (
                COLUMN_NAME LIKE '%Account%'
                OR COLUMN_NAME LIKE '%Code%'
                OR COLUMN_NAME LIKE '%Client%'
            )
            ORDER BY COLUMN_NAME
        """)

        columns = cursor.fetchall()

        if columns:
            print(f"\n✓ Found {len(columns)} columns matching account/code/client:")
            print("\n" + "-"*80)
            print(f"{'Column Name':<40} {'Data Type':<15} {'Max Length':<12} {'Nullable'}")
            print("-"*80)

            for col in columns:
                col_name = col['COLUMN_NAME']
                data_type = col['DATA_TYPE']
                max_len = col['CHARACTER_MAXIMUM_LENGTH'] or 'N/A'
                nullable = col['IS_NULLABLE']
                print(f"{col_name:<40} {data_type:<15} {str(max_len):<12} {nullable}")
        else:
            print("\n⚠️  No matching columns found")

        connection.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

def get_specific_account_codes():
    """Try to get account codes using common column names"""
    print("\n" + "="*80)
    print("STEP 4: Testing Common Account Code Column Names")
    print("="*80)

    try:
        connection = pymssql.connect(
            server='102.67.140.12',
            port=1053,
            database='AFS',
            user='FSAUser2',
            password='password'
        )

        cursor = connection.cursor(as_dict=True)

        # Try different possible column names
        possible_columns = [
            'AccountCode',
            'Account_Code',
            'ClientCode',
            'Client_Code',
            'CustomerCode',
            'Customer_Code',
            'AccCode',
            'CustCode',
            'Code',
            'AccountNumber',
            'Account_Number',
            'ClientNumber',
            'Client_Number',
        ]

        print("\nTrying common account code column names...")
        print("-"*80)

        for col_name in possible_columns:
            try:
                query = f"""
                    SELECT TOP 5
                        ClientName,
                        DateOfInspection,
                        [{col_name}]
                    FROM tblFoodSafetyAgencyInspection
                    WHERE [{col_name}] IS NOT NULL
                    ORDER BY DateOfInspection DESC
                """

                cursor.execute(query)
                results = cursor.fetchall()

                if results:
                    print(f"\n✅ SUCCESS! Found column: {col_name}")
                    print(f"   Sample values:")
                    for idx, row in enumerate(results, 1):
                        print(f"   {idx}. {row['ClientName']:40s} | {col_name}: {row[col_name]}")
                    return col_name

            except Exception:
                # Column doesn't exist, continue
                pass

        print("\n⚠️  None of the common column names worked")
        print("   Account code might be named differently")

        connection.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

    return None

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

        # Step 2: Check for account code columns
        check_account_code_field()

        # Step 3: Try common column names
        account_col = get_specific_account_codes()

        # Step 4: Get latest inspections with all data
        inspections = get_latest_inspections_with_account_codes(connection)

        connection.close()

        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)

        print(f"\n✓ Successfully connected to SQL Server")
        print(f"✓ Retrieved {len(inspections)} inspections")

        if account_col:
            print(f"✓ Account code column found: {account_col}")
        else:
            print("⚠️  Account code column name needs verification")

        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("""
If account code column was found:
  1. Note the column name from the output above
  2. Use it in your sync process
  3. Update Django model if needed

If NOT found:
  1. Check the 'All Fields' section in inspection output
  2. Look for any column that might contain account codes
  3. May need to check with database administrator
  4. Column might be in a related table (JOIN required)
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
