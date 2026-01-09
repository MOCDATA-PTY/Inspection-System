"""
Populate product names for existing egg inspections
This fixes the issue where egg inspections have NULL product names
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from main.utils.sql_server_utils import SQLServerConnection

print("="*80)
print("POPULATING EGG PRODUCT NAMES")
print("="*80)

# Get all egg inspections without product names
egg_inspections = FoodSafetyAgencyInspection.objects.filter(
    commodity__iexact='EGGS',
    product_name__isnull=True
)

total_eggs = egg_inspections.count()
print(f"\nFound {total_eggs} egg inspections without product names")

if total_eggs == 0:
    print("All egg inspections already have product names!")
    exit(0)

# Connect to SQL Server
sql_conn = SQLServerConnection()
if not sql_conn.connect():
    print("ERROR: Failed to connect to SQL Server")
    exit(1)

cursor = sql_conn.connection.cursor()

# Size and Grade mappings
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

print("\nProcessing egg inspections...")
print("-"*80)

updated_count = 0
failed_count = 0
skipped_count = 0

for i, inspection in enumerate(egg_inspections, 1):
    try:
        # Extract the base inspection ID (remove _1, _2, etc. suffix if present)
        remote_id = str(inspection.remote_id)
        base_id = remote_id.split('_')[0] if '_' in remote_id else remote_id

        # Query SQL Server for Size and Grade
        query = """
            SELECT SizeId, GradeId
            FROM PoultryEggInspectionRecords
            WHERE Id = %s
        """
        cursor.execute(query, (int(base_id),))
        result = cursor.fetchone()

        if result:
            size_id, grade_id = result

            if size_id and grade_id:
                # Generate product name
                size_name = SIZE_MAP.get(size_id, f'Size {size_id}')
                grade_name = GRADE_MAP.get(grade_id, f'Grade {grade_id}')
                product_name = f'{size_name} {grade_name} Eggs'

                # Update the inspection
                inspection.product_name = product_name
                inspection.save(update_fields=['product_name'])

                updated_count += 1

                # Progress indicator
                if i % 50 == 0:
                    print(f"Progress: {i}/{total_eggs} ({(i/total_eggs*100):.1f}%) - Updated: {updated_count}")
            else:
                skipped_count += 1
                if i <= 10:  # Show first 10 skipped
                    print(f"  Skipped ID {remote_id}: Missing Size or Grade")
        else:
            failed_count += 1
            if i <= 10:  # Show first 10 failures
                print(f"  Failed ID {remote_id}: Not found in SQL Server")

    except Exception as e:
        failed_count += 1
        if i <= 10:  # Show first 10 errors
            print(f"  Error for ID {inspection.remote_id}: {e}")

sql_conn.disconnect()

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total egg inspections processed: {total_eggs}")
print(f"Successfully updated: {updated_count}")
print(f"Skipped (missing size/grade): {skipped_count}")
print(f"Failed (not found or error): {failed_count}")
print(f"\nSuccess rate: {(updated_count/total_eggs*100):.1f}%")
print("="*80)

# Verify the update
updated_eggs = FoodSafetyAgencyInspection.objects.filter(
    commodity__iexact='EGGS',
    product_name__isnull=False
).exclude(product_name='')

print(f"\n✅ Verification: {updated_eggs.count()} egg inspections now have product names")

# Show sample
print("\nSample updated eggs:")
for egg in updated_eggs[:10]:
    print(f"  ID {egg.remote_id}: {egg.product_name}")
