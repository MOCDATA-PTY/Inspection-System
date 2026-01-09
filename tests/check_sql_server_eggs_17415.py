"""
Check SQL Server directly for EGGS inspection 17415
to see if product name exists in the source database
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

import pyodbc
from django.conf import settings

def check_sql_server():
    print("=" * 80)
    print("CHECKING SQL SERVER FOR EGGS INSPECTION 17415")
    print("=" * 80)
    print()

    try:
        # Connect to SQL Server
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={settings.DATABASES['sqlserver']['HOST']};DATABASE={settings.DATABASES['sqlserver']['NAME']};UID={settings.DATABASES['sqlserver']['USER']};PWD={settings.DATABASES['sqlserver']['PASSWORD']};"

        conn = pyodbc.connect(connection_string, timeout=30)
        cursor = conn.cursor()

        print("[OK] Connected to SQL Server")
        print()

        # Query the EGGS table for inspection 17415
        query = """
        SELECT
            InspectionID,
            ProductName,
            ProductID,
            DateOfInspection,
            InspectorID,
            IsSampleTaken,
            BoughtSample,
            InternalAccountNumber
        FROM EGGS
        WHERE InspectionID = ?
        """

        print("Executing query for EGGS inspection 17415...")
        cursor.execute(query, 17415)

        row = cursor.fetchone()

        if not row:
            print("[ERROR] Inspection 17415 not found in SQL Server EGGS table!")
            print("\nSearching for recent Test1 EGGS inspections...")

            # Try to find Test1 inspections
            test_query = """
            SELECT TOP 5
                InspectionID,
                ProductName,
                DateOfInspection,
                InternalAccountNumber
            FROM EGGS
            WHERE InternalAccountNumber LIKE '%5042%'
            ORDER BY DateOfInspection DESC
            """

            cursor.execute(test_query)
            rows = cursor.fetchall()

            if rows:
                print(f"\nFound {len(rows)} recent EGGS inspections for account *5042:")
                for r in rows:
                    prod = r.ProductName if r.ProductName else "[NULL/EMPTY]"
                    print(f"  ID {r.InspectionID} | {r.DateOfInspection} | Product: {prod}")
        else:
            print("\n" + "=" * 80)
            print("SQL SERVER DATA FOR EGGS-17415")
            print("=" * 80)
            print()

            print(f"Inspection ID: {row.InspectionID}")
            print(f"Product Name: '{row.ProductName}' (Type: {type(row.ProductName).__name__})")

            if row.ProductName is None:
                print("  [ISSUE] ProductName is NULL in SQL Server")
            elif row.ProductName == "":
                print("  [ISSUE] ProductName is empty string in SQL Server")
            else:
                print(f"  [OK] ProductName has value: '{row.ProductName}'")

            print(f"Product ID: {row.ProductID}")
            print(f"Date of Inspection: {row.DateOfInspection}")
            print(f"Inspector ID: {row.InspectorID}")
            print(f"Sample Taken: {row.IsSampleTaken}")
            print(f"Bought Sample: {row.BoughtSample}")
            print(f"Internal Account Number: {row.InternalAccountNumber}")
            print()

            print("=" * 80)
            print("CONCLUSION")
            print("=" * 80)

            if not row.ProductName:
                print("\n[CONFIRMED] The product name is MISSING in the SQL Server source database.")
                print("\nThis means:")
                print("  - The inspector did NOT enter a product name when creating the inspection")
                print("  - The sync service correctly pulled the data (empty product name)")
                print("  - This is a DATA ENTRY ISSUE, not a sync issue")
                print()
                print("ACTION REQUIRED:")
                print("  - Inspector needs to update the inspection in the mobile app")
                print("  - Or manually update the product name in the Django admin panel")
            else:
                print(f"\n[FOUND] Product name exists in SQL Server: '{row.ProductName}'")
                print("\nThis means:")
                print("  - The data exists in SQL Server")
                print("  - But the sync didn't pull it correctly")
                print("  - This is a SYNC MAPPING ISSUE")
                print()
                print("ACTION REQUIRED:")
                print("  - Check the sync service's product name mapping for EGGS")
                print("  - Re-run the sync to pull the correct product name")

        conn.close()

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 80)

if __name__ == "__main__":
    check_sql_server()
