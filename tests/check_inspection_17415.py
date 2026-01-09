"""
Check inspection 17415 (EGGS) to see why product_name is missing
"""
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 80)
print("INVESTIGATING INSPECTION 17415 (EGGS) - MISSING PRODUCT NAME")
print("=" * 80)
print()

# Find the inspection by remote_id and commodity
inspection = FoodSafetyAgencyInspection.objects.filter(
    commodity='EGGS',
    remote_id=17415
).first()

if not inspection:
    print("[ERROR] Inspection EGGS-17415 not found in database!")
    print("\nSearching for any inspection with remote_id 17415...")
    all_17415 = FoodSafetyAgencyInspection.objects.filter(remote_id=17415)
    print(f"Found {all_17415.count()} inspections with remote_id 17415:")
    for insp in all_17415:
        print(f"  - {insp.unique_inspection_id}: {insp.commodity}")
else:
    print(f"Found: {inspection.unique_inspection_id}")
    print()

    # Display all fields
    print("FULL INSPECTION DETAILS:")
    print("-" * 80)
    print(f"Database ID: {inspection.id}")
    print(f"Unique ID: {inspection.unique_inspection_id}")
    print(f"Remote ID: {inspection.remote_id}")
    print(f"Commodity: {inspection.commodity}")
    print()

    print("CLIENT & LOCATION:")
    print(f"Client Name: '{inspection.client_name}'")
    print(f"Internal Account Code: '{inspection.internal_account_code}'")
    print()

    print("INSPECTOR:")
    print(f"Inspector ID: {inspection.inspector_id}")
    print(f"Inspector Name: '{inspection.inspector_name}'")
    print()

    print("INSPECTION DATE & TIME:")
    print(f"Date of Inspection: {inspection.date_of_inspection}")
    print(f"Start Time: {inspection.start_of_inspection}")
    print(f"End Time: {inspection.end_of_inspection}")
    print()

    print("PRODUCT INFORMATION:")
    print(f"Product Name: '{inspection.product_name}' (Length: {len(inspection.product_name) if inspection.product_name else 0})")
    print(f"Product Class: '{inspection.product_class}' (Length: {len(inspection.product_class) if inspection.product_class else 0})")

    if inspection.product_name is None:
        print("  [ISSUE] product_name is NULL")
    elif inspection.product_name == "":
        print("  [ISSUE] product_name is empty string")
    else:
        print(f"  [INFO] product_name has value: '{inspection.product_name}'")
    print()

    print("SAMPLE INFO:")
    print(f"Sample Taken: {inspection.is_sample_taken}")
    print(f"Bought Sample: {inspection.bought_sample}")
    print()

    print("TESTING:")
    print(f"Fat: {inspection.fat}")
    print(f"Protein: {inspection.protein}")
    print(f"Calcium: {inspection.calcium}")
    print(f"DNA: {inspection.dna}")
    print(f"Needs Retest: {inspection.needs_retest}")
    print()

    print("TIMESTAMPS:")
    print(f"Created At: {inspection.created_at}")
    print(f"Updated At: {inspection.updated_at}")
    print()

    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    if not inspection.product_name:
        print("\n[ROOT CAUSE] Product name is missing from SQL Server data")
        print("\nPossible reasons:")
        print("1. The inspection was created in the mobile app but product name wasn't entered")
        print("2. The SQL Server EGGS table doesn't have a product name column")
        print("3. The product name column exists but is NULL for this record")
        print("4. The sync process isn't correctly mapping the product name field")
        print()
        print("RECOMMENDATION:")
        print("- Check the SQL Server EGGS table structure")
        print("- Verify if remote_id 17415 has a product name in SQL Server")
        print("- Check if other EGGS inspections have product names")
    else:
        print(f"\n[INFO] Product name exists: '{inspection.product_name}'")

    print()

    # Check other EGGS inspections for Test1
    print("=" * 80)
    print("OTHER EGGS INSPECTIONS FOR TEST1")
    print("=" * 80)

    other_eggs = FoodSafetyAgencyInspection.objects.filter(
        commodity='EGGS',
        client_name='Test1'
    ).order_by('-date_of_inspection')[:10]

    print(f"\nFound {other_eggs.count()} EGGS inspections for Test1:")
    for insp in other_eggs:
        product = insp.product_name if insp.product_name else "[EMPTY]"
        print(f"  {insp.unique_inspection_id} | {insp.date_of_inspection} | Product: {product}")

print()
print("=" * 80)
