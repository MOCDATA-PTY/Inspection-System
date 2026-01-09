"""
Fix commodity classifications in local SQLite database
Moves processed meat products from POULTRY/RAW to PMP where they belong
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db import transaction

print("=" * 80)
print("FIX COMMODITY CLASSIFICATIONS - LOCAL SQLITE DATABASE")
print("=" * 80)

# Define keywords that indicate processed meat products (should be in PMP)
processed_meat_keywords = [
    'wors', 'sausage', 'polony', 'vienna', 'russian', 'frankfurter',
    'bacon', 'ham', 'salami', 'biltong', 'droewors', 'processed',
    'boerewors', 'smoked', 'cured', 'cold meat', 'deli'
]

# Find misclassified products in POULTRY
print("\n1. Finding processed meat products in POULTRY category...")
print("-" * 80)

poultry_issues = []
for keyword in processed_meat_keywords:
    inspections = FoodSafetyAgencyInspection.objects.filter(
        commodity='POULTRY',
        product_name__icontains=keyword
    )
    if inspections.exists():
        poultry_issues.extend(list(inspections))

print(f"Found {len(poultry_issues)} POULTRY inspections that should be PMP")

if poultry_issues:
    print("\nExamples:")
    for insp in poultry_issues[:10]:
        print(f"  [{insp.unique_inspection_id}] {insp.client_name} - {insp.product_name}")

# Find misclassified products in RAW
print("\n2. Finding processed meat products in RAW category...")
print("-" * 80)

raw_issues = []
for keyword in processed_meat_keywords:
    inspections = FoodSafetyAgencyInspection.objects.filter(
        commodity='RAW',
        product_name__icontains=keyword
    )
    if inspections.exists():
        raw_issues.extend(list(inspections))

print(f"Found {len(raw_issues)} RAW inspections that should be PMP")

if raw_issues:
    print("\nExamples:")
    for insp in raw_issues[:10]:
        print(f"  [{insp.unique_inspection_id}] {insp.client_name} - {insp.product_name}")

# Calculate total
total_to_fix = len(poultry_issues) + len(raw_issues)

if total_to_fix == 0:
    print("\n[OK] No misclassified products found! Database is clean.")
    exit(0)

# Show summary before fixing
print("\n" + "=" * 80)
print("SUMMARY OF CHANGES TO BE MADE")
print("=" * 80)
print(f"POULTRY -> PMP: {len(poultry_issues)} inspections")
print(f"RAW -> PMP: {len(raw_issues)} inspections")
print(f"Total changes: {total_to_fix} inspections")

# Perform the fix
print("\n" + "=" * 80)
print("APPLYING FIXES")
print("=" * 80)

fixed_count = 0
errors = []

try:
    with transaction.atomic():
        # Fix POULTRY issues
        if poultry_issues:
            print(f"\nUpdating {len(poultry_issues)} POULTRY -> PMP...")
            for insp in poultry_issues:
                try:
                    old_id = insp.unique_inspection_id
                    insp.commodity = 'PMP'
                    insp.save()
                    new_id = insp.unique_inspection_id
                    fixed_count += 1
                    if fixed_count <= 10:  # Show first 10
                        print(f"  [OK] {old_id} -> {new_id}: {insp.product_name}")
                except Exception as e:
                    errors.append((insp.remote_id, insp.product_name, str(e)))

        # Fix RAW issues
        if raw_issues:
            print(f"\nUpdating {len(raw_issues)} RAW -> PMP...")
            for insp in raw_issues:
                try:
                    old_id = insp.unique_inspection_id
                    insp.commodity = 'PMP'
                    insp.save()
                    new_id = insp.unique_inspection_id
                    fixed_count += 1
                    if fixed_count <= 20 and fixed_count > 10:  # Show next 10
                        print(f"  [OK] {old_id} -> {new_id}: {insp.product_name}")
                except Exception as e:
                    errors.append((insp.remote_id, insp.product_name, str(e)))

        print(f"\n[SUCCESS] Fixed {fixed_count} inspections")

except Exception as e:
    print(f"\n[ERROR] Transaction failed: {e}")
    import traceback
    traceback.print_exc()

# Show errors if any
if errors:
    print("\n" + "=" * 80)
    print("ERRORS ENCOUNTERED")
    print("=" * 80)
    for remote_id, product, error in errors[:10]:
        print(f"  [{remote_id}] {product}: {error}")

# Verify the fix
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

# Check if any processed meats remain in POULTRY
remaining_poultry = 0
for keyword in processed_meat_keywords:
    count = FoodSafetyAgencyInspection.objects.filter(
        commodity='POULTRY',
        product_name__icontains=keyword
    ).count()
    remaining_poultry += count

# Check if any processed meats remain in RAW
remaining_raw = 0
for keyword in processed_meat_keywords:
    count = FoodSafetyAgencyInspection.objects.filter(
        commodity='RAW',
        product_name__icontains=keyword
    ).count()
    remaining_raw += count

print(f"Remaining processed meats in POULTRY: {remaining_poultry}")
print(f"Remaining processed meats in RAW: {remaining_raw}")

if remaining_poultry == 0 and remaining_raw == 0:
    print("\n[SUCCESS] All misclassified products have been fixed!")
else:
    print(f"\n[WARNING] {remaining_poultry + remaining_raw} products still misclassified")

# Show new PMP count
pmp_count = FoodSafetyAgencyInspection.objects.filter(commodity='PMP').count()
print(f"\nTotal PMP inspections now: {pmp_count}")

# Show specific fix for "Wors Garlic"
print("\n" + "=" * 80)
print("SPECIFIC FIX: Wors Garlic (Inspection 65713)")
print("=" * 80)

wors_garlic = FoodSafetyAgencyInspection.objects.filter(
    remote_id=65713,
    product_name__icontains='wors garlic'
).first()

if wors_garlic:
    print(f"Inspection: {wors_garlic.unique_inspection_id}")
    print(f"Client: {wors_garlic.client_name}")
    print(f"Product: {wors_garlic.product_name}")
    print(f"Commodity: {wors_garlic.commodity}")

    if wors_garlic.commodity == 'PMP':
        print("\n[OK] Successfully moved to PMP category!")
    else:
        print(f"\n[WARNING] Still in {wors_garlic.commodity} category")
else:
    print("[INFO] Inspection 65713 not found in database")

print("\n" + "=" * 80)
print("FIX COMPLETE")
print("=" * 80)
print(f"""
Summary:
- Fixed {fixed_count} inspections
- Moved processed meat products to PMP category
- Local SQLite database updated
- Production PostgreSQL database unchanged

The classification issues are now fixed in your local test database!
""")
