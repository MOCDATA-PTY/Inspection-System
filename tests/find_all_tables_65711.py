"""Find inspection 65711-65713 in ALL SQL Server tables"""
import pymssql

conn = pymssql.connect(
    server='102.67.140.12',
    port=1053,
    user='FSAUser2',
    password='password',
    database='AFS',
    timeout=30
)

cursor = conn.cursor(as_dict=True)

print("Searching for inspections 65711-65713 in ALL tables:")
print("=" * 80)

tables_to_check = [
    ('PoultryQuidInspectionRecordTypes', 'ProductName', 'POULTRY'),
    ('PoultryGradingInspectionRecordTypes', 'ProductName', 'POULTRY'),
    ('PoultryLabelInspectionChecklistRecords', 'ProductName', 'POULTRY'),
    ('PoultryInspectionRecordTypes', 'ProductName', 'POULTRY'),
    ('PoultryEggInspectionRecords', 'EggProducer', 'EGGS'),
    ('PMPInspectionRecordTypes', None, 'PMP'),  # Products in separate table
    ('RawRMPInspectionRecordTypes', None, 'RAW'),  # Products in separate table
]

for insp_id in [65711, 65712, 65713]:
    print(f"\nInspection {insp_id}:")
    found = False

    for table, product_col, commodity in tables_to_check:
        try:
            if product_col:
                cursor.execute(f"""
                    SELECT Id, {product_col} as ProductName, DateOfInspection, IsActive
                    FROM {table}
                    WHERE Id = {insp_id}
                """)
            else:
                cursor.execute(f"""
                    SELECT Id, DateOfInspection, IsActive
                    FROM {table}
                    WHERE Id = {insp_id}
                """)

            result = cursor.fetchone()

            if result:
                print(f"  FOUND in {table} -> Maps to {commodity}")
                if 'ProductName' in result:
                    print(f"    Product: {result['ProductName']}")
                print(f"    Date: {result['DateOfInspection']}")
                print(f"    Active: {result['IsActive']}")

                # Check for products in separate tables
                if table == 'PMPInspectionRecordTypes':
                    cursor.execute(f"""
                        SELECT PMPItemDetails
                        FROM PMPInspectedProductRecordTypes
                        WHERE InspectionId = {insp_id}
                    """)
                    products = cursor.fetchall()
                    if products:
                        print(f"    Products:")
                        for p in products:
                            print(f"      - {p['PMPItemDetails']}")

                elif table == 'RawRMPInspectionRecordTypes':
                    cursor.execute(f"""
                        SELECT NewProductItemDetails
                        FROM RawRMPInspectedProductRecordTypes
                        WHERE InspectionId = {insp_id}
                    """)
                    products = cursor.fetchall()
                    if products:
                        print(f"    Products:")
                        for p in products:
                            print(f"      - {p['NewProductItemDetails']}")

                found = True
                break

        except Exception as e:
            continue

    if not found:
        print(f"  NOT FOUND in SQL Server")

conn.close()
