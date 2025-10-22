"""
Demo script to show how JOIN creates separate rows for each product
This demonstrates the OLD (CORRECT) way vs NEW (WRONG) way
"""

import pymssql
from django.conf import settings
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def demo_product_separation():
    """Demonstrate how JOIN creates separate rows for each product"""

    print("=" * 120)
    print(" " * 35 + "PRODUCT SEPARATION DEMONSTRATION")
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
            timeout=10
        )

        cursor = connection.cursor(as_dict=True)

        # =============================
        # OLD WAY (CORRECT) - Using JOIN
        # =============================
        print("OLD WAY (CORRECT) - Using JOIN to separate products")
        print("=" * 120)
        print()

        # Example: PMP Inspections with JOIN
        old_way_query = """
            SELECT TOP 20
                i.Id as InspectionId,
                i.DateOfInspection,
                clt.Name as ClientName,
                prod.PMPItemDetails as ProductName
            FROM [AFS].[dbo].[PMPInspectionRecordTypes] i
            JOIN AFS.dbo.PMPInspectedProductRecordTypes prod ON prod.InspectionId = i.Id
            JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
            WHERE i.IsActive = 1
            AND i.DateOfInspection >= '2025-10-01'
            AND prod.PMPItemDetails IS NOT NULL
            AND prod.PMPItemDetails != ''
            ORDER BY i.Id DESC, prod.PMPItemDetails
        """

        cursor.execute(old_way_query)
        old_results = cursor.fetchall()

        print("Query Result: Each product gets its OWN row")
        print("-" * 120)

        inspection_groups = {}
        for row in old_results:
            insp_id = row['InspectionId']
            if insp_id not in inspection_groups:
                inspection_groups[insp_id] = []
            inspection_groups[insp_id].append(row)

        for insp_id, rows in list(inspection_groups.items())[:5]:  # Show first 5 inspection groups
            print(f"\nInspection Group ID: {insp_id}")
            print(f"Date: {rows[0]['DateOfInspection']}")
            print(f"Client: {rows[0]['ClientName']}")
            print(f"Number of Products: {len(rows)}")
            print(f"Products:")
            for idx, row in enumerate(rows, 1):
                print(f"  {idx}. {row['ProductName']}")

        print()
        print(f"Total Rows Returned: {len(old_results)}")
        print(f"Total Unique Inspections: {len(inspection_groups)}")
        print()
        print("KEY POINT: If Inspection 8119 has 3 products, it returns 3 SEPARATE ROWS!")
        print()

        print("=" * 120)
        print()

        # =============================
        # NEW WAY (WRONG) - Without JOIN, then fetching products
        # =============================
        print("NEW WAY (WRONG) - Get inspections first, then fetch products separately")
        print("=" * 120)
        print()

        new_way_query = """
            SELECT TOP 10
                i.Id as InspectionId,
                i.DateOfInspection,
                i.InspectorId
            FROM [AFS].[dbo].[PMPInspectionRecordTypes] i
            WHERE i.IsActive = 1
            AND i.DateOfInspection >= '2025-10-01'
            ORDER BY i.Id DESC
        """

        cursor.execute(new_way_query)
        new_results = cursor.fetchall()

        print("Step 1: Get Inspections (no products yet)")
        print("-" * 120)
        for idx, row in enumerate(new_results[:3], 1):
            print(f"{idx}. Inspection ID: {row['InspectionId']} | Date: {row['DateOfInspection']}")
        print()

        print("Step 2: Fetch products for each inspection")
        print("-" * 120)

        for row in new_results[:3]:
            insp_id = row['InspectionId']

            # Fetch products for this inspection
            product_query = """
                SELECT PMPItemDetails
                FROM PMPInspectedProductRecordTypes
                WHERE InspectionId = %s
                AND PMPItemDetails IS NOT NULL
                AND PMPItemDetails != ''
            """
            cursor.execute(product_query, (insp_id,))
            products = cursor.fetchall()

            product_names = [p['PMPItemDetails'] for p in products]
            product_string = ', '.join(product_names)

            print(f"\nInspection ID: {insp_id}")
            print(f"Products as comma-separated: {product_string}")
            print(f"Number of products: {len(product_names)}")

        print()
        print(f"Total Rows Returned: {len(new_results)}")
        print()
        print("KEY POINT: If Inspection 8119 has 3 products, it returns 1 ROW with comma-separated products!")
        print()

        print("=" * 120)
        print()

        # =============================
        # COMPARISON
        # =============================
        print("COMPARISON")
        print("=" * 120)
        print()
        print("OLD WAY (CORRECT):")
        print("  - Uses JOIN in SQL query")
        print("  - One inspection with 3 products = 3 database rows")
        print("  - Each row has ONE product name")
        print("  - Result: 3 separate inspection records in Django")
        print()
        print("NEW WAY (WRONG):")
        print("  - Gets inspections without JOIN")
        print("  - Fetches products separately")
        print("  - One inspection with 3 products = 1 database row")
        print("  - All products combined as 'Product1, Product2, Product3'")
        print("  - Result: 1 inspection record with multiple products")
        print()
        print("SOLUTION:")
        print("  - Use the OLD WAY with JOIN")
        print("  - Each product becomes a separate inspection record")
        print("  - One inspection group can have multiple individual inspections")
        print()
        print("=" * 120)

        connection.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        demo_product_separation()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
