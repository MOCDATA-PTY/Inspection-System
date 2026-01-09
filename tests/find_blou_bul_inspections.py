"""Find Blou Bul Meat Market inspections 65711-65713"""
import sys
import os
import django
import pymssql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 80)
print("CHECKING BLOU BUL MEAT MARKET INSPECTIONS 65711-65713")
print("=" * 80)
print()

print("1. POSTGRESQL DATABASE:")
print("-" * 80)
for insp_id in [65711, 65712, 65713]:
    i = FoodSafetyAgencyInspection.objects.filter(remote_id=insp_id).first()
    if i:
        print(f"{insp_id}: {i.commodity} / {i.product_name}")
        print(f"  Client: {i.client_name}")
        print(f"  Date: {i.date_of_inspection}")
    else:
        print(f"{insp_id}: NOT FOUND")
print()

print("2. SQL SERVER DATABASE:")
print("-" * 80)

conn = pymssql.connect(
    server='102.67.140.12',
    port=1053,
    user='FSAUser2',
    password='password',
    database='AFS',
    timeout=30
)

cursor = conn.cursor(as_dict=True)

# Check all poultry tables
poultry_tables = [
    'PoultryQuidInspectionRecordTypes',
    'PoultryGradingInspectionRecordTypes',
    'PoultryLabelInspectionChecklistRecords',
    'PoultryInspectionRecordTypes'
]

for insp_id in [65711, 65712, 65713]:
    print(f"\nInspection {insp_id}:")
    found = False

    for table in poultry_tables:
        try:
            cursor.execute(f"""
                SELECT '{table}' as TableName, Id, ProductName, DateOfInspection, IsActive
                FROM {table}
                WHERE Id = {insp_id}
            """)
            result = cursor.fetchone()

            if result:
                print(f"  FOUND in {table}")
                print(f"    Product: {result['ProductName']}")
                print(f"    Date: {result['DateOfInspection']}")
                print(f"    Active: {result['IsActive']}")
                print(f"    ** This table maps to POULTRY commodity **")
                if 'wors' in result['ProductName'].lower() or 'bites' in result['ProductName'].lower():
                    print(f"    *** WRONG TABLE! This is a meat product, should be in PMP table ***")
                found = True
                break
        except Exception as e:
            continue

    if not found:
        print(f"  NOT FOUND in any poultry table")

conn.close()

print()
print("=" * 80)
print("CONCLUSION:")
print("=" * 80)
print("These inspections ARE in poultry tables in SQL Server,")
print("which is why they're showing as POULTRY commodity.")
print()
print("But 'Chilli Bites' and 'Wors Garlic' are meat products")
print("and should be in PMP tables, not poultry tables!")
print()
print("This is a DATA ENTRY ERROR in SQL Server.")
