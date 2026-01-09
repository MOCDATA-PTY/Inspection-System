import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import datetime

print("=" * 80)
print("TESTING is_sample_taken LOGIC FOR BOXER NKOMO VILLAGE (05/12/2025)")
print("=" * 80)

# Query inspections for Boxer Nkomo Village on 05/12/2025
inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains='Nkomo',
    date_of_inspection__day=5,
    date_of_inspection__month=12,
    date_of_inspection__year=2025
).order_by('product_name')

print(f"\nFound {inspections.count()} inspections for Boxer Nkomo Village on 05/12/2025\n")

for insp in inspections:
    print(f"Product: {insp.product_name}")
    print(f"  Commodity: {insp.commodity}")
    print(f"  Date: {insp.date_of_inspection.strftime('%d/%m/%Y')}")
    print(f"  Fat: {insp.fat}")
    print(f"  Protein: {insp.protein}")
    print(f"  DNA: {insp.dna if hasattr(insp, 'dna') else 'N/A'}")
    print(f"  Calcium: {insp.calcium}")
    print(f"  is_sample_taken: {insp.is_sample_taken}")
    print(f"  bought_sample: {insp.bought_sample}")

    # Determine what test line items SHOULD be generated
    print(f"\n  TEST LINE ITEMS THAT SHOULD BE GENERATED:")

    product_type = 'RAW' if insp.commodity and 'RAW' in insp.commodity.upper() else 'PMP'
    test_items = []

    if product_type == 'PMP':
        if insp.fat and insp.is_sample_taken:
            test_items.append('PMP 062 (Fat Test)')
        if insp.protein and insp.is_sample_taken:
            test_items.append('PMP 064 (Protein Test)')
        if insp.calcium and insp.is_sample_taken:
            test_items.append('PMP 066 (Calcium Test)')
    else:  # RAW
        if insp.fat and insp.is_sample_taken:
            test_items.append('RAW 052 (Fat Test)')
        if insp.protein and insp.is_sample_taken:
            test_items.append('RAW 053 (Protein Test)')
        if insp.dna and insp.is_sample_taken:
            test_items.append('RAW 056 (DNA Test)')
        if insp.calcium and insp.is_sample_taken:
            test_items.append('RAW 057 (Calcium Test)')

    if insp.bought_sample:
        if product_type == 'PMP':
            test_items.append(f'PMP 067 (Samples Bought: R{insp.bought_sample})')
        else:
            test_items.append(f'RAW 058 (Samples Bought: R{insp.bought_sample})')

    if test_items:
        for item in test_items:
            print(f"    [YES] {item}")
    else:
        print(f"    [NO] NO TEST CHARGES (not sampled or no tests required)")

    print("\n" + "-" * 80 + "\n")

print("\n" + "=" * 80)
print("SUMMARY OF EXPECTED BEHAVIOR:")
print("=" * 80)
print("""
Based on the is_sample_taken logic:
- Test charges (RAW 052, 053, etc.) should ONLY appear for products where:
  1. The test parameter is TRUE (fat=TRUE, protein=TRUE, etc.)
  2. AND is_sample_taken is TRUE

If a product has fat=TRUE but is_sample_taken=FALSE or None:
  [NO] NO fat test charge should be generated

If the export is showing test charges for products with is_sample_taken=FALSE/None,
then the logic in generate_test_line_items() is NOT working correctly.

IMPORTANT: If is_sample_taken is None/NULL in the database, the logic will treat
it as FALSE and NOT generate test charges (which is correct behavior).
""")
print("=" * 80)
