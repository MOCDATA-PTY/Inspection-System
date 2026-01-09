"""
Test script to verify egg product names are correctly generated for inspections
Tests that EggProducer + SizeId properly creates product names like:
- PnP Extra Large Eggs
- Weldhagen Jumbo Eggs
- Nulaid Large Eggs
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings before importing any Django code
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import fetch_product_names_for_inspection
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

def test_egg_product_names():
    """Test that egg product names are correctly generated"""

    print("="*80)
    print("TESTING EGG PRODUCT NAME GENERATION")
    print("="*80)
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

        # Test 1: Get a PnP egg inspection
        print("-" * 80)
        print("TEST 1: PnP Extra Large Eggs")
        print("-" * 80)

        cursor.execute("""
            SELECT TOP 1 Id, EggProducer, SizeId, GradeId, DateOfInspection
            FROM PoultryEggInspectionRecords
            WHERE EggProducer LIKE '%pnp%'
            AND SizeId = 2  -- Extra Large
        """)

        result = cursor.fetchone()
        if result:
            inspection_id, producer, size_id, grade_id, date = result
            expected_product = f"{producer} {SIZE_MAP[size_id]} Eggs"

            print(f"Inspection ID: {inspection_id}")
            print(f"EggProducer: {producer}")
            print(f"Size: {SIZE_MAP[size_id]} (ID: {size_id})")
            print(f"Grade: {GRADE_MAP[grade_id]} (ID: {grade_id})")
            print(f"Date: {date}")
            print(f"Expected Product Name: {expected_product}")

            # Fetch using the utility function
            fetched_products = fetch_product_names_for_inspection(inspection_id)
            print(f"Fetched Product Names: {fetched_products}")

            if expected_product in fetched_products:
                print("[PASS] TEST PASSED: Product name matches!")
            else:
                print("[FAIL] TEST FAILED: Product name does not match!")
            print()
        else:
            print("No PnP Extra Large eggs found in database")
            print()

        # Test 2: Get a Weldhagen egg inspection
        print("-" * 80)
        print("TEST 2: Weldhagen Eggs")
        print("-" * 80)

        cursor.execute("""
            SELECT TOP 1 Id, EggProducer, SizeId, GradeId, DateOfInspection
            FROM PoultryEggInspectionRecords
            WHERE EggProducer LIKE '%weldhagen%'
        """)

        result = cursor.fetchone()
        if result:
            inspection_id, producer, size_id, grade_id, date = result
            expected_product = f"{producer} {SIZE_MAP[size_id]} Eggs"

            print(f"Inspection ID: {inspection_id}")
            print(f"EggProducer: {producer}")
            print(f"Size: {SIZE_MAP[size_id]} (ID: {size_id})")
            print(f"Grade: {GRADE_MAP[grade_id]} (ID: {grade_id})")
            print(f"Date: {date}")
            print(f"Expected Product Name: {expected_product}")

            # Fetch using the utility function
            fetched_products = fetch_product_names_for_inspection(inspection_id)
            print(f"Fetched Product Names: {fetched_products}")

            if expected_product in fetched_products:
                print("[PASS] TEST PASSED: Product name matches!")
            else:
                print("[FAIL] TEST FAILED: Product name does not match!")
            print()
        else:
            print("No Weldhagen eggs found in database")
            print()

        # Test 3: Get a Nulaid Large egg inspection
        print("-" * 80)
        print("TEST 3: Nulaid Large Eggs")
        print("-" * 80)

        cursor.execute("""
            SELECT TOP 1 Id, EggProducer, SizeId, GradeId, DateOfInspection
            FROM PoultryEggInspectionRecords
            WHERE EggProducer LIKE '%nulaid%'
            AND SizeId = 3  -- Large
        """)

        result = cursor.fetchone()
        if result:
            inspection_id, producer, size_id, grade_id, date = result
            expected_product = f"{producer} {SIZE_MAP[size_id]} Eggs"

            print(f"Inspection ID: {inspection_id}")
            print(f"EggProducer: {producer}")
            print(f"Size: {SIZE_MAP[size_id]} (ID: {size_id})")
            print(f"Grade: {GRADE_MAP[grade_id]} (ID: {grade_id})")
            print(f"Date: {date}")
            print(f"Expected Product Name: {expected_product}")

            # Fetch using the utility function
            fetched_products = fetch_product_names_for_inspection(inspection_id)
            print(f"Fetched Product Names: {fetched_products}")

            if expected_product in fetched_products:
                print("[PASS] TEST PASSED: Product name matches!")
            else:
                print("[FAIL] TEST FAILED: Product name does not match!")
            print()
        else:
            print("No Nulaid Large eggs found in database")
            print()

        # Test 4: Get a Nulaid Extra Large egg inspection
        print("-" * 80)
        print("TEST 4: Nulaid Extra Large Eggs")
        print("-" * 80)

        cursor.execute("""
            SELECT TOP 1 Id, EggProducer, SizeId, GradeId, DateOfInspection
            FROM PoultryEggInspectionRecords
            WHERE EggProducer LIKE '%nulaid%'
            AND SizeId = 2  -- Extra Large
        """)

        result = cursor.fetchone()
        if result:
            inspection_id, producer, size_id, grade_id, date = result
            expected_product = f"{producer} {SIZE_MAP[size_id]} Eggs"

            print(f"Inspection ID: {inspection_id}")
            print(f"EggProducer: {producer}")
            print(f"Size: {SIZE_MAP[size_id]} (ID: {size_id})")
            print(f"Grade: {GRADE_MAP[grade_id]} (ID: {grade_id})")
            print(f"Date: {date}")
            print(f"Expected Product Name: {expected_product}")

            # Fetch using the utility function
            fetched_products = fetch_product_names_for_inspection(inspection_id)
            print(f"Fetched Product Names: {fetched_products}")

            if expected_product in fetched_products:
                print("[PASS] TEST PASSED: Product name matches!")
            else:
                print("[FAIL] TEST FAILED: Product name does not match!")
            print()
        else:
            print("No Nulaid Extra Large eggs found in database")
            print()

        # Test 5: Multiple inspections - Test different sizes
        print("-" * 80)
        print("TEST 5: Multiple PnP Egg Sizes")
        print("-" * 80)

        cursor.execute("""
            SELECT TOP 5 Id, EggProducer, SizeId, GradeId
            FROM PoultryEggInspectionRecords
            WHERE EggProducer LIKE '%pnp%'
            ORDER BY SizeId
        """)

        results = cursor.fetchall()
        passed_tests = 0
        failed_tests = 0

        for result in results:
            inspection_id, producer, size_id, grade_id = result
            expected_product = f"{producer} {SIZE_MAP.get(size_id, f'Size {size_id}')} Eggs"

            fetched_products = fetch_product_names_for_inspection(inspection_id)

            if expected_product in fetched_products:
                passed_tests += 1
                print(f"[PASS] ID {inspection_id}: {expected_product}")
            else:
                failed_tests += 1
                print(f"[FAIL] ID {inspection_id}: Expected '{expected_product}', Got {fetched_products}")

        print()
        print(f"Results: {passed_tests} passed, {failed_tests} failed")
        print()

        # Test 6: Edge case - Egg without producer name
        print("-" * 80)
        print("TEST 6: Egg Without Producer Name (Edge Case)")
        print("-" * 80)

        cursor.execute("""
            SELECT TOP 1 Id, EggProducer, SizeId, GradeId
            FROM PoultryEggInspectionRecords
            WHERE (EggProducer IS NULL OR EggProducer = '')
            AND SizeId IS NOT NULL
            AND GradeId IS NOT NULL
        """)

        result = cursor.fetchone()
        if result:
            inspection_id, producer, size_id, grade_id = result
            # When no producer, should fall back to Size + Grade
            expected_product = f"{SIZE_MAP[size_id]} {GRADE_MAP[grade_id]} Eggs"

            print(f"Inspection ID: {inspection_id}")
            print(f"EggProducer: {producer} (empty/null)")
            print(f"Size: {SIZE_MAP[size_id]} (ID: {size_id})")
            print(f"Grade: {GRADE_MAP[grade_id]} (ID: {grade_id})")
            print(f"Expected Product Name: {expected_product}")

            fetched_products = fetch_product_names_for_inspection(inspection_id)
            print(f"Fetched Product Names: {fetched_products}")

            if expected_product in fetched_products:
                print("[PASS] TEST PASSED: Fallback to Size + Grade works!")
            else:
                print("[FAIL] TEST FAILED: Fallback logic not working!")
            print()
        else:
            print("No eggs without producer name found")
            print()

        cursor.close()
        connection.close()

        print("="*80)
        print("TESTING COMPLETE")
        print("="*80)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_egg_product_names()
