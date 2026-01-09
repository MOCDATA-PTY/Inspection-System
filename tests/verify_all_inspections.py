"""
Verify all inspections in local database against SQL Server
Find any cases where commodity or product names are incorrect
"""

import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
import pymssql

SQL_SERVER_CONFIG = {
    'HOST': '102.67.140.12',
    'PORT': 1053,
    'USER': 'FSAUser2',
    'PASSWORD': 'password',
    'DATABASE': 'AFS'
}

def verify_inspections():
    """Verify all local inspections against SQL Server."""

    print("=" * 80)
    print("VERIFICATION: Checking all local inspections against SQL Server")
    print("=" * 80)
    print()

    # Get all inspections from local database
    local_inspections = FoodSafetyAgencyInspection.objects.all().order_by('remote_id')
    total_count = local_inspections.count()

    print(f"Found {total_count:,} inspections in local database")
    print()

    # Connect to SQL Server
    try:
        connection = pymssql.connect(
            server=SQL_SERVER_CONFIG['HOST'],
            port=int(SQL_SERVER_CONFIG['PORT']),
            user=SQL_SERVER_CONFIG['USER'],
            password=SQL_SERVER_CONFIG['PASSWORD'],
            database=SQL_SERVER_CONFIG['DATABASE'],
            timeout=30
        )
        cursor = connection.cursor(as_dict=True)
        print("Connected to SQL Server")
        print()

        # Track issues
        issues = {
            'not_found_in_sql_server': [],
            'wrong_commodity': [],
            'wrong_product': [],
            'poultry_with_meat_products': [],
        }

        checked = 0
        valid = 0

        print("Checking inspections...")
        print("-" * 80)

        for idx, local_insp in enumerate(local_inspections, 1):
            checked += 1
            remote_id = local_insp.remote_id
            local_commodity = local_insp.commodity
            local_product = local_insp.product_name

            # Show progress every 100 inspections
            if idx % 100 == 0:
                print(f"Progress: {idx}/{total_count} ({(idx/total_count)*100:.1f}%)")

            # Check if inspection exists in SQL Server
            found_in_sql = False
            sql_commodity = None
            sql_product = None

            # Check each table based on local commodity
            if local_commodity == 'POULTRY':
                # Check poultry tables
                cursor.execute("""
                    SELECT 'POULTRY' as Commodity, ProductName
                    FROM PoultryQuidInspectionRecordTypes
                    WHERE Id = %s AND IsActive = 1
                """, (remote_id,))
                result = cursor.fetchone()

                if not result:
                    cursor.execute("""
                        SELECT 'POULTRY' as Commodity, ProductName
                        FROM PoultryGradingInspectionRecordTypes
                        WHERE Id = %s AND IsActive = 1
                    """, (remote_id,))
                    result = cursor.fetchone()

                if not result:
                    cursor.execute("""
                        SELECT 'POULTRY' as Commodity, ProductName
                        FROM PoultryLabelInspectionChecklistRecords
                        WHERE Id = %s AND IsActive = 1
                    """, (remote_id,))
                    result = cursor.fetchone()

                if result:
                    found_in_sql = True
                    sql_commodity = result['Commodity']
                    sql_product = result['ProductName']

            elif local_commodity == 'EGGS':
                # Check egg table
                cursor.execute("""
                    SELECT 'EGGS' as Commodity, EggProducer as ProductName
                    FROM PoultryEggInspectionRecords
                    WHERE Id = %s AND IsActive = 1
                """, (remote_id,))
                result = cursor.fetchone()

                if result:
                    found_in_sql = True
                    sql_commodity = result['Commodity']
                    sql_product = result['ProductName']

            elif local_commodity == 'PMP':
                # Check PMP table
                cursor.execute("""
                    SELECT 'PMP' as Commodity, prod.PMPItemDetails as ProductName
                    FROM PMPInspectionRecordTypes main
                    JOIN PMPInspectedProductRecordTypes prod ON prod.InspectionId = main.Id
                    WHERE main.Id = %s AND main.IsActive = 1
                """, (remote_id,))
                result = cursor.fetchone()

                if result:
                    found_in_sql = True
                    sql_commodity = result['Commodity']
                    sql_product = result['ProductName']

            elif local_commodity == 'RAW':
                # Check RAW table
                cursor.execute("""
                    SELECT 'RAW' as Commodity, prod.NewProductItemDetails as ProductName
                    FROM RawRMPInspectionRecordTypes main
                    JOIN RawRMPInspectedProductRecordTypes prod ON prod.InspectionId = main.Id
                    WHERE main.Id = %s AND main.IsActive = 1
                """, (remote_id,))
                result = cursor.fetchone()

                if result:
                    found_in_sql = True
                    sql_commodity = result['Commodity']
                    sql_product = result['ProductName']

            # If not found in expected table, check ALL tables
            if not found_in_sql:
                # Maybe it's in a different commodity table?
                # Check PMP
                cursor.execute("""
                    SELECT 'PMP' as Commodity, prod.PMPItemDetails as ProductName
                    FROM PMPInspectionRecordTypes main
                    JOIN PMPInspectedProductRecordTypes prod ON prod.InspectionId = main.Id
                    WHERE main.Id = %s AND main.IsActive = 1
                """, (remote_id,))
                result = cursor.fetchone()

                if result:
                    found_in_sql = True
                    sql_commodity = result['Commodity']
                    sql_product = result['ProductName']
                    issues['wrong_commodity'].append({
                        'remote_id': remote_id,
                        'local_commodity': local_commodity,
                        'sql_commodity': sql_commodity,
                        'local_product': local_product,
                        'sql_product': sql_product,
                        'client': local_insp.client_name,
                        'date': local_insp.date_of_inspection
                    })
                    continue

                # Check RAW
                cursor.execute("""
                    SELECT 'RAW' as Commodity, prod.NewProductItemDetails as ProductName
                    FROM RawRMPInspectionRecordTypes main
                    JOIN RawRMPInspectedProductRecordTypes prod ON prod.InspectionId = main.Id
                    WHERE main.Id = %s AND main.IsActive = 1
                """, (remote_id,))
                result = cursor.fetchone()

                if result:
                    found_in_sql = True
                    sql_commodity = result['Commodity']
                    sql_product = result['ProductName']
                    issues['wrong_commodity'].append({
                        'remote_id': remote_id,
                        'local_commodity': local_commodity,
                        'sql_commodity': sql_commodity,
                        'local_product': local_product,
                        'sql_product': sql_product,
                        'client': local_insp.client_name,
                        'date': local_insp.date_of_inspection
                    })
                    continue

            # Check if found at all
            if not found_in_sql:
                issues['not_found_in_sql_server'].append({
                    'remote_id': remote_id,
                    'commodity': local_commodity,
                    'product': local_product,
                    'client': local_insp.client_name,
                    'date': local_insp.date_of_inspection
                })
            else:
                # Verify product name matches (if applicable)
                # Note: For eggs, we don't compare product names since they're generated
                if local_commodity != 'EGGS':
                    if sql_product and local_product and sql_product.strip() != local_product.strip():
                        issues['wrong_product'].append({
                            'remote_id': remote_id,
                            'commodity': local_commodity,
                            'local_product': local_product,
                            'sql_product': sql_product,
                            'client': local_insp.client_name,
                            'date': local_insp.date_of_inspection
                        })
                    else:
                        valid += 1
                else:
                    valid += 1

                # Special check: POULTRY commodity with meat-related products
                if local_commodity == 'POULTRY' and local_product:
                    meat_keywords = ['wors', 'sausage', 'boerewors', 'droewors', 'beef', 'pork', 'mutton']
                    if any(keyword in local_product.lower() for keyword in meat_keywords):
                        issues['poultry_with_meat_products'].append({
                            'remote_id': remote_id,
                            'product': local_product,
                            'client': local_insp.client_name,
                            'date': local_insp.date_of_inspection
                        })

        print()
        print("=" * 80)
        print("VERIFICATION RESULTS")
        print("=" * 80)
        print(f"Total inspections checked: {checked:,}")
        print(f"Valid inspections: {valid:,}")
        print()

        # Report issues
        if issues['not_found_in_sql_server']:
            print("=" * 80)
            print(f"NOT FOUND IN SQL SERVER: {len(issues['not_found_in_sql_server'])} inspections")
            print("=" * 80)
            for issue in issues['not_found_in_sql_server'][:10]:  # Show first 10
                print(f"  ID {issue['remote_id']}: {issue['client']} - {issue['date']}")
                print(f"    Commodity: {issue['commodity']}, Product: {issue['product']}")
            if len(issues['not_found_in_sql_server']) > 10:
                print(f"  ... and {len(issues['not_found_in_sql_server']) - 10} more")
            print()

        if issues['wrong_commodity']:
            print("=" * 80)
            print(f"WRONG COMMODITY: {len(issues['wrong_commodity'])} inspections")
            print("=" * 80)
            for issue in issues['wrong_commodity'][:10]:
                print(f"  ID {issue['remote_id']}: {issue['client']} - {issue['date']}")
                print(f"    Local: {issue['local_commodity']} / {issue['local_product']}")
                print(f"    SQL:   {issue['sql_commodity']} / {issue['sql_product']}")
            if len(issues['wrong_commodity']) > 10:
                print(f"  ... and {len(issues['wrong_commodity']) - 10} more")
            print()

        if issues['wrong_product']:
            print("=" * 80)
            print(f"WRONG PRODUCT NAME: {len(issues['wrong_product'])} inspections")
            print("=" * 80)
            for issue in issues['wrong_product'][:10]:
                print(f"  ID {issue['remote_id']}: {issue['client']} - {issue['date']}")
                print(f"    Local: {issue['local_product']}")
                print(f"    SQL:   {issue['sql_product']}")
            if len(issues['wrong_product']) > 10:
                print(f"  ... and {len(issues['wrong_product']) - 10} more")
            print()

        if issues['poultry_with_meat_products']:
            print("=" * 80)
            print(f"POULTRY WITH MEAT PRODUCTS: {len(issues['poultry_with_meat_products'])} inspections")
            print("=" * 80)
            for issue in issues['poultry_with_meat_products'][:10]:
                print(f"  ID {issue['remote_id']}: {issue['client']} - {issue['date']}")
                print(f"    Product: {issue['product']}")
            if len(issues['poultry_with_meat_products']) > 10:
                print(f"  ... and {len(issues['poultry_with_meat_products']) - 10} more")
            print()

        # Summary
        total_issues = (len(issues['not_found_in_sql_server']) +
                       len(issues['wrong_commodity']) +
                       len(issues['wrong_product']) +
                       len(issues['poultry_with_meat_products']))

        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        if total_issues == 0:
            print("All inspections are valid!")
        else:
            print(f"Found {total_issues} issues:")
            print(f"  - Not found in SQL Server: {len(issues['not_found_in_sql_server'])}")
            print(f"  - Wrong commodity: {len(issues['wrong_commodity'])}")
            print(f"  - Wrong product name: {len(issues['wrong_product'])}")
            print(f"  - Poultry with meat products: {len(issues['poultry_with_meat_products'])}")
            print()
            print("RECOMMENDATION: Run a fresh sync from Settings page to fix these issues.")
            print("The sync will delete all local data and pull fresh data from SQL Server.")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    verify_inspections()
