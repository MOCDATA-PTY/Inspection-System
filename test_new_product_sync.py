"""
Test the new product sync with JOIN query
This will show that one inspection with multiple products = multiple rows
"""

import pymssql
from django.conf import settings
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.views.data_views import FSA_INSPECTION_QUERY

def test_new_sync_query():
    """Test the new FSA_INSPECTION_QUERY to verify product separation"""

    print("=" * 120)
    print(" " * 40 + "TESTING NEW PRODUCT SYNC QUERY")
    print("=" * 120)
    print()

    sql_server_config = settings.DATABASES.get('sql_server', {})

    try:
        connection = pymssql.connect(
            server=sql_server_config.get('HOST'),
            port=int(sql_server_config.get('PORT', 1433)),
            user=sql_server_config.get('USER'),
            password=sql_server_config.get('PASSWORD'),
            database=sql_server_config.get('NAME'),
            timeout=30
        )

        cursor = connection.cursor(as_dict=True)

        print("Executing FSA_INSPECTION_QUERY (TOP 100 records)...")
        print("-" * 120)
        print()

        # Modify query to get only TOP 100 for testing
        test_query = FSA_INSPECTION_QUERY.replace("SELECT 'POULTRY'", "SELECT TOP 100 'POULTRY'", 1)

        cursor.execute(test_query)
        rows = cursor.fetchall()

        print(f"Total Rows Returned: {len(rows)}")
        print()

        # Group by inspection ID to see products
        inspection_groups = {}
        for row in rows:
            insp_id = row['Id']
            client = row['Client']
            commodity = row['Commodity']
            product = row['ProductName']
            date = row['DateOfInspection']

            key = (insp_id, client, date, commodity)
            if key not in inspection_groups:
                inspection_groups[key] = []
            inspection_groups[key].append(product)

        print("=" * 120)
        print("INSPECTION GROUPS (Showing first 20)")
        print("=" * 120)
        print()

        for idx, (key, products) in enumerate(list(inspection_groups.items())[:20], 1):
            insp_id, client, date, commodity = key
            print(f"{idx:3}. Inspection ID: {insp_id:6} | Client: {client[:40]:40} | Commodity: {commodity:8}")
            print(f"     Date: {date} | Products: {len(products)}")
            for pidx, product in enumerate(products, 1):
                print(f"       {pidx}. {product}")
            print()

        print("=" * 120)
        print("SUMMARY")
        print("=" * 120)
        print()
        print(f"Total rows returned: {len(rows)}")
        print(f"Unique inspection groups: {len(inspection_groups)}")
        print()

        # Find examples where one inspection has multiple products
        multi_product_inspections = [(key, prods) for key, prods in inspection_groups.items() if len(prods) > 1]

        if multi_product_inspections:
            print(f"Found {len(multi_product_inspections)} inspections with multiple products!")
            print()
            print("Examples of multi-product inspections:")
            print("-" * 120)
            for idx, (key, products) in enumerate(multi_product_inspections[:5], 1):
                insp_id, client, date, commodity = key
                print(f"\n{idx}. Inspection {insp_id} - {client} ({commodity}) on {date}")
                print(f"   Has {len(products)} products:")
                for pidx, product in enumerate(products, 1):
                    print(f"     {pidx}. {product}")
            print()
            print("✅ SUCCESS: Query correctly creates separate rows for each product!")
        else:
            print("✅ Each inspection has exactly ONE product (as expected with JOIN)")

        print()
        print("=" * 120)
        print("VERIFICATION")
        print("=" * 120)
        print()
        print("Expected Behavior:")
        print("  - Each row should have exactly ONE product name")
        print("  - If an inspection has 3 products, there should be 3 rows with the same InspectionId")
        print("  - NO comma-separated product lists")
        print()
        print("Actual Results:")
        print(f"  - Total rows: {len(rows)}")
        print(f"  - Unique inspections: {len(inspection_groups)}")
        print(f"  - Inspections with multiple rows (multiple products): {len(multi_product_inspections)}")
        print()

        if len(rows) > len(inspection_groups):
            print("✅ CORRECT: More rows than unique inspections (some inspections have multiple products)")
        elif len(rows) == len(inspection_groups):
            print("⚠️  Each inspection has only one product (might be correct, or products missing)")
        else:
            print("❌ ERROR: Something is wrong with the data")

        print()
        print("=" * 120)

        connection.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        test_new_sync_query()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
