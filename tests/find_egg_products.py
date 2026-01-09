"""
Find specific egg products by EggProducer and Size
- Pnp Extra Large Eggs
- Weldhagen Jumbo Eggs
- Nulaid Large Eggs(30)
"""

import pymssql

SQL_SERVER_CONFIG = {
    'HOST': '102.67.140.12',
    'PORT': 1053,
    'USER': 'FSAUser2',
    'PASSWORD': 'password',
    'DATABASE': 'AFS'
}

SIZE_MAP = {
    1: 'Jumbo',
    2: 'Extra Large',
    3: 'Large',
    4: 'Medium',
    5: 'Small',
    6: 'Peewee'
}

GRADE_MAP = {
    1: 'Grade A',
    2: 'Grade B',
    3: 'Grade C'
}

def find_egg_products():
    print("Searching for egg products in PoultryEggInspectionRecords...\n")

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

        # Search for Pnp eggs
        print("="*60)
        print("SEARCHING FOR PNP EGG PRODUCTS:")
        print("="*60)
        cursor.execute("""
            SELECT Id, EggProducer, SizeId, GradeId, DateOfInspection, ClientBranch
            FROM PoultryEggInspectionRecords
            WHERE EggProducer LIKE '%pnp%'
            OR EggProducer LIKE '%PnP%'
            OR EggProducer LIKE '%PNP%'
        """)
        pnp_results = cursor.fetchall()

        if pnp_results:
            for row in pnp_results:
                inspection_id, producer, size_id, grade_id, date, branch = row
                size_name = SIZE_MAP.get(size_id, f'Unknown Size {size_id}')
                grade_name = GRADE_MAP.get(grade_id, f'Unknown Grade {grade_id}')
                product_name = f'{producer} {size_name} {grade_name} Eggs'
                print(f"  ID: {inspection_id}")
                print(f"  Product: {product_name}")
                print(f"  Date: {date}")
                print(f"  Branch: {branch}")
                print()
        else:
            print("  No PnP egg products found\n")

        # Search for Weldhagen eggs
        print("="*60)
        print("SEARCHING FOR WELDHAGEN EGG PRODUCTS:")
        print("="*60)
        cursor.execute("""
            SELECT Id, EggProducer, SizeId, GradeId, DateOfInspection, ClientBranch
            FROM PoultryEggInspectionRecords
            WHERE EggProducer LIKE '%weldhagen%'
            OR EggProducer LIKE '%Weldhagen%'
        """)
        weldhagen_results = cursor.fetchall()

        if weldhagen_results:
            for row in weldhagen_results:
                inspection_id, producer, size_id, grade_id, date, branch = row
                size_name = SIZE_MAP.get(size_id, f'Unknown Size {size_id}')
                grade_name = GRADE_MAP.get(grade_id, f'Unknown Grade {grade_id}')
                product_name = f'{producer} {size_name} {grade_name} Eggs'
                print(f"  ID: {inspection_id}")
                print(f"  Product: {product_name}")
                print(f"  Date: {date}")
                print(f"  Branch: {branch}")
                print()
        else:
            print("  No Weldhagen egg products found\n")

        # Search for Nulaid eggs
        print("="*60)
        print("SEARCHING FOR NULAID EGG PRODUCTS:")
        print("="*60)
        cursor.execute("""
            SELECT Id, EggProducer, SizeId, GradeId, DateOfInspection, ClientBranch
            FROM PoultryEggInspectionRecords
            WHERE EggProducer LIKE '%nulaid%'
            OR EggProducer LIKE '%Nulaid%'
        """)
        nulaid_results = cursor.fetchall()

        if nulaid_results:
            for row in nulaid_results:
                inspection_id, producer, size_id, grade_id, date, branch = row
                size_name = SIZE_MAP.get(size_id, f'Unknown Size {size_id}')
                grade_name = GRADE_MAP.get(grade_id, f'Unknown Grade {grade_id}')
                product_name = f'{producer} {size_name} {grade_name} Eggs'
                print(f"  ID: {inspection_id}")
                print(f"  Product: {product_name}")
                print(f"  Date: {date}")
                print(f"  Branch: {branch}")
                print()
        else:
            print("  No Nulaid egg products found\n")

        # Show all unique egg producers
        print("="*60)
        print("ALL UNIQUE EGG PRODUCERS IN DATABASE:")
        print("="*60)
        cursor.execute("""
            SELECT DISTINCT EggProducer, COUNT(*) as Count
            FROM PoultryEggInspectionRecords
            WHERE EggProducer IS NOT NULL AND EggProducer != ''
            GROUP BY EggProducer
            ORDER BY EggProducer
        """)
        all_producers = cursor.fetchall()

        if all_producers:
            for producer, count in all_producers:
                print(f"  {producer} ({count} records)")
        else:
            print("  No egg producers found in database")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    find_egg_products()
