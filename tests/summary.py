"""
Summary script to pull 50 inspections with product names from each SQL Server table
Shows which table each product name comes from
"""

import pymssql
from django.conf import settings
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def connect_to_sql_server():
    """Connect to SQL Server using pymssql"""
    sql_server_config = settings.DATABASES.get('sql_server', {})

    try:
        connection = pymssql.connect(
            server=sql_server_config.get('HOST'),
            port=int(sql_server_config.get('PORT', 1433)),
            user=sql_server_config.get('USER'),
            password=sql_server_config.get('PASSWORD'),
            database=sql_server_config.get('NAME'),
            timeout=10
        )
        return connection
    except Exception as e:
        print(f"Failed to connect to SQL Server: {e}")
        return None

def pull_inspections_summary():
    """Pull 50 inspections from each table and display product names"""

    print("=" * 100)
    print(" " * 35 + "INSPECTION PRODUCT NAMES SUMMARY")
    print("=" * 100)
    print()

    connection = connect_to_sql_server()

    if not connection:
        print("ERROR: Could not connect to SQL Server!")
        return

    try:
        cursor = connection.cursor()

        # =============================
        # TABLE 1: PMP Inspected Products
        # =============================
        print("TABLE 1: PMPInspectedProductRecordTypes")
        print("=" * 100)
        print("Field: PMPItemDetails")
        print("Description: PMP (Processed Meat Products) Inspection Records")
        print("-" * 100)

        pmp_query = """
            SELECT TOP 50
                InspectionId,
                PMPItemDetails
            FROM PMPInspectedProductRecordTypes
            WHERE PMPItemDetails IS NOT NULL AND PMPItemDetails != ''
            ORDER BY InspectionId DESC
        """

        try:
            cursor.execute(pmp_query)
            results = cursor.fetchall()

            if results:
                print(f"Found {len(results)} records")
                print()
                for idx, row in enumerate(results, 1):
                    inspection_id, product_name = row
                    print(f"{idx:3}. Inspection ID: {inspection_id:8} | Product: {product_name}")
            else:
                print("No records found in this table.")

            print()
        except Exception as e:
            print(f"Error querying table: {e}")
            print()

        print("=" * 100)
        print()

        # =============================
        # TABLE 2: Poultry Grading Inspections
        # =============================
        print("TABLE 2: PoultryGradingInspectionRecordTypes")
        print("=" * 100)
        print("Field: ProductName")
        print("Description: Poultry Grading Inspection Records")
        print("-" * 100)

        poultry_grading_query = """
            SELECT TOP 50
                Id,
                ProductName
            FROM PoultryGradingInspectionRecordTypes
            WHERE ProductName IS NOT NULL AND ProductName != ''
            ORDER BY Id DESC
        """

        try:
            cursor.execute(poultry_grading_query)
            results = cursor.fetchall()

            if results:
                print(f"Found {len(results)} records")
                print()
                for idx, row in enumerate(results, 1):
                    inspection_id, product_name = row
                    print(f"{idx:3}. Inspection ID: {inspection_id:8} | Product: {product_name}")
            else:
                print("No records found in this table.")

            print()
        except Exception as e:
            print(f"Error querying table: {e}")
            print()

        print("=" * 100)
        print()

        # =============================
        # TABLE 3: Poultry Label Inspection Checklist
        # =============================
        print("TABLE 3: PoultryLabelInspectionChecklistRecords")
        print("=" * 100)
        print("Field: ProductName")
        print("Description: Poultry Label Inspection Checklist")
        print("-" * 100)

        poultry_label_query = """
            SELECT TOP 50
                Id,
                ProductName
            FROM PoultryLabelInspectionChecklistRecords
            WHERE ProductName IS NOT NULL AND ProductName != ''
            ORDER BY Id DESC
        """

        try:
            cursor.execute(poultry_label_query)
            results = cursor.fetchall()

            if results:
                print(f"Found {len(results)} records")
                print()
                for idx, row in enumerate(results, 1):
                    inspection_id, product_name = row
                    print(f"{idx:3}. Inspection ID: {inspection_id:8} | Product: {product_name}")
            else:
                print("No records found in this table.")

            print()
        except Exception as e:
            print(f"Error querying table: {e}")
            print()

        print("=" * 100)
        print()

        # =============================
        # TABLE 4: Poultry QUID Inspections
        # =============================
        print("TABLE 4: PoultryQuidInspectionRecordTypes")
        print("=" * 100)
        print("Field: ProductName")
        print("Description: Poultry QUID Inspection Records")
        print("-" * 100)

        poultry_quid_query = """
            SELECT TOP 50
                Id,
                ProductName
            FROM PoultryQuidInspectionRecordTypes
            WHERE ProductName IS NOT NULL AND ProductName != ''
            ORDER BY Id DESC
        """

        try:
            cursor.execute(poultry_quid_query)
            results = cursor.fetchall()

            if results:
                print(f"Found {len(results)} records")
                print()
                for idx, row in enumerate(results, 1):
                    inspection_id, product_name = row
                    print(f"{idx:3}. Inspection ID: {inspection_id:8} | Product: {product_name}")
            else:
                print("No records found in this table.")

            print()
        except Exception as e:
            print(f"Error querying table: {e}")
            print()

        print("=" * 100)
        print()

        # =============================
        # TABLE 5: Poultry Inspections
        # =============================
        print("TABLE 5: PoultryInspectionRecordTypes")
        print("=" * 100)
        print("Field: ProductName")
        print("Description: General Poultry Inspection Records")
        print("-" * 100)

        poultry_inspection_query = """
            SELECT TOP 50
                Id,
                ProductName
            FROM PoultryInspectionRecordTypes
            WHERE ProductName IS NOT NULL AND ProductName != ''
            ORDER BY Id DESC
        """

        try:
            cursor.execute(poultry_inspection_query)
            results = cursor.fetchall()

            if results:
                print(f"Found {len(results)} records")
                print()
                for idx, row in enumerate(results, 1):
                    inspection_id, product_name = row
                    print(f"{idx:3}. Inspection ID: {inspection_id:8} | Product: {product_name}")
            else:
                print("No records found in this table.")

            print()
        except Exception as e:
            print(f"Error querying table: {e}")
            print()

        print("=" * 100)
        print()

        # =============================
        # TABLE 6: Raw RMP Inspected Products
        # =============================
        print("TABLE 6: RawRMPInspectedProductRecordTypes")
        print("=" * 100)
        print("Field: NewProductItemDetails")
        print("Description: Raw RMP (Red Meat Products) Inspection Records")
        print("-" * 100)

        raw_rmp_query = """
            SELECT TOP 50
                InspectionId,
                NewProductItemDetails
            FROM RawRMPInspectedProductRecordTypes
            WHERE NewProductItemDetails IS NOT NULL AND NewProductItemDetails != ''
            ORDER BY InspectionId DESC
        """

        try:
            cursor.execute(raw_rmp_query)
            results = cursor.fetchall()

            if results:
                print(f"Found {len(results)} records")
                print()
                for idx, row in enumerate(results, 1):
                    inspection_id, product_name = row
                    print(f"{idx:3}. Inspection ID: {inspection_id:8} | Product: {product_name}")
            else:
                print("No records found in this table.")

            print()
        except Exception as e:
            print(f"Error querying table: {e}")
            print()

        print("=" * 100)

    except Exception as e:
        print(f"Error during query execution: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if connection:
            connection.close()

    print()
    print("=" * 100)
    print(" " * 45 + "END OF SUMMARY")
    print("=" * 100)


if __name__ == "__main__":
    try:
        pull_inspections_summary()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
