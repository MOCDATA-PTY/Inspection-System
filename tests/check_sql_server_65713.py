"""
Check SQL Server for inspection 65713 to find the correct product and commodity
"""

import pymssql

SQL_SERVER_CONFIG = {
    'HOST': '102.67.140.12',
    'PORT': 1053,
    'USER': 'FSAUser2',
    'PASSWORD': 'password',
    'DATABASE': 'AFS'
}

def check_sql_server():
    print("=" * 80)
    print("CHECKING SQL SERVER FOR INSPECTION 65713")
    print("=" * 80)
    print()

    try:
        connection = pymssql.connect(
            server=SQL_SERVER_CONFIG['HOST'],
            port=int(SQL_SERVER_CONFIG['PORT']),
            user=SQL_SERVER_CONFIG['USER'],
            password=SQL_SERVER_CONFIG['PASSWORD'],
            database=SQL_SERVER_CONFIG['DATABASE'],
            timeout=30
        )

        cursor = connection.cursor()

        # Check ALL main inspection tables for ID 65713
        print("-" * 80)
        print("1. CHECKING PMPInspectionRecordTypes (Processed Meat Products)")
        print("-" * 80)
        try:
            cursor.execute("""
                SELECT *
                FROM PMPInspectionRecordTypes
                WHERE Id = 65713
            """)
            pmp_main = cursor.fetchone()
            if pmp_main:
                print(f"FOUND in PMPInspectionRecordTypes:")
                print(f"  Full record: {pmp_main}")
                print()

                # Get products for this inspection
                print("  Products for this PMP inspection:")
                cursor.execute("""
                    SELECT PMPItemDetails
                    FROM PMPInspectedProductRecordTypes
                    WHERE InspectionId = 65713
                """)
                pmp_products = cursor.fetchall()
                for idx, prod in enumerate(pmp_products, 1):
                    print(f"    {idx}. {prod[0]}")
            else:
                print("  NOT FOUND in PMPInspectionRecordTypes")
        except Exception as e:
            print(f"  ERROR querying PMPInspectionRecordTypes: {e}")
        print()

        # Check RMP (Raw Meat Products)
        print("-" * 80)
        print("2. CHECKING RawRMPInspectionRecordTypes (Raw Meat Products)")
        print("-" * 80)
        try:
            cursor.execute("""
                SELECT *
                FROM RawRMPInspectionRecordTypes
                WHERE Id = 65713
            """)
            rmp_main = cursor.fetchone()
            if rmp_main:
                print(f"FOUND in RawRMPInspectionRecordTypes:")
                print(f"  Full record: {rmp_main}")
                print()

                # Get products for this inspection
                print("  Products for this RMP inspection:")
                cursor.execute("""
                    SELECT NewProductItemDetails
                    FROM RawRMPInspectedProductRecordTypes
                    WHERE InspectionId = 65713
                """)
                rmp_products = cursor.fetchall()
                for idx, prod in enumerate(rmp_products, 1):
                    print(f"    {idx}. {prod[0]}")
            else:
                print("  NOT FOUND in RawRMPInspectionRecordTypes")
        except Exception as e:
            print(f"  ERROR querying RawRMPInspectionRecordTypes: {e}")
        print()

        # Check Poultry tables
        poultry_tables = [
            ('PoultryGradingInspectionRecordTypes', 'ProductName'),
            ('PoultryLabelInspectionChecklistRecords', 'ProductName'),
            ('PoultryQuidInspectionRecordTypes', 'ProductName'),
            ('PoultryInspectionRecordTypes', 'ProductName'),
        ]

        for table_name, product_column in poultry_tables:
            print("-" * 80)
            print(f"CHECKING {table_name}")
            print("-" * 80)
            try:
                cursor.execute(f"""
                    SELECT *
                    FROM {table_name}
                    WHERE Id = 65713
                """)
                result = cursor.fetchone()
                if result:
                    print(f"FOUND in {table_name}:")
                    print(f"  Full record: {result}")
                else:
                    print(f"  NOT FOUND in {table_name}")
            except Exception as e:
                print(f"  ERROR querying {table_name}: {e}")
            print()

        # Check Egg Products
        print("-" * 80)
        print("CHECKING PoultryEggInspectionRecords")
        print("-" * 80)
        try:
            cursor.execute("""
                SELECT *
                FROM PoultryEggInspectionRecords
                WHERE Id = 65713
            """)
            egg_inspection = cursor.fetchone()
            if egg_inspection:
                print(f"FOUND in PoultryEggInspectionRecords:")
                print(f"  Full record: {egg_inspection}")
            else:
                print("  NOT FOUND in PoultryEggInspectionRecords")
        except Exception as e:
            print(f"  ERROR querying PoultryEggInspectionRecords: {e}")
        print()

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_sql_server()
