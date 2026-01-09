"""
Check inspection 65713 to see where 'Wors Garlic' is coming from
"""

import pymssql

SQL_SERVER_CONFIG = {
    'HOST': '102.67.140.12',
    'PORT': 1053,
    'USER': 'FSAUser2',
    'PASSWORD': 'password',
    'DATABASE': 'AFS'
}

def check_inspection():
    print("Checking inspection 65713 for product sources...")
    print("="*80)

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

        # Check all possible tables for inspection ID 65713
        tables_to_check = [
            ('PMPInspectedProductRecordTypes', 'PMPItemDetails', 'InspectionId'),
            ('RawRMPInspectedProductRecordTypes', 'NewProductItemDetails', 'InspectionId'),
            ('PoultryGradingInspectionRecordTypes', 'ProductName', 'Id'),
            ('PoultryLabelInspectionChecklistRecords', 'ProductName', 'Id'),
            ('PoultryQuidInspectionRecordTypes', 'ProductName', 'Id'),
            ('PoultryInspectionRecordTypes', 'ProductName', 'Id'),
            ('PoultryEggInspectionRecords', 'EggProducer', 'Id'),
        ]

        for table_name, product_column, id_column in tables_to_check:
            try:
                query = f"""
                    SELECT {id_column}, {product_column}
                    FROM {table_name}
                    WHERE {id_column} = 65713
                """
                cursor.execute(query)
                results = cursor.fetchall()

                if results:
                    print(f"\nFOUND in {table_name}:")
                    for row in results:
                        print(f"  ID: {row[0]}")
                        print(f"  Product: {row[1]}")

            except Exception as e:
                print(f"\nError querying {table_name}: {e}")

        # Also check what table contains "Wors Garlic"
        print("\n" + "="*80)
        print("Searching for 'Wors Garlic' in all tables...")
        print("="*80)

        for table_name, product_column, id_column in tables_to_check:
            try:
                query = f"""
                    SELECT {id_column}, {product_column}
                    FROM {table_name}
                    WHERE {product_column} LIKE '%Wors%Garlic%'
                    OR {product_column} LIKE '%Garlic%Wors%'
                """
                cursor.execute(query)
                results = cursor.fetchall()

                if results:
                    print(f"\nFOUND 'Wors Garlic' in {table_name}:")
                    for row in results:
                        print(f"  ID: {row[0]}")
                        print(f"  Product: {row[1]}")

            except Exception as e:
                pass

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    check_inspection()
