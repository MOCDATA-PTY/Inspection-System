"""
Analyze POULTRY commodity for product names that don't belong
"""
import sqlite3
import os

LOCAL_DB = 'local_inspection_analysis.sqlite3'

if not os.path.exists(LOCAL_DB):
    print(f"ERROR: Database not found: {LOCAL_DB}")
    print("Please run create_local_db_and_analyze.py first")
    exit(1)

conn = sqlite3.connect(LOCAL_DB)
cursor = conn.cursor()

print("=" * 80)
print("POULTRY COMMODITY PRODUCT NAME ANALYSIS")
print("=" * 80)

# Get all unique POULTRY product names
cursor.execute('''
    SELECT DISTINCT product_name, COUNT(*) as count
    FROM inspections
    WHERE commodity = 'POULTRY'
    GROUP BY product_name
    ORDER BY count DESC
''')

all_poultry_products = cursor.fetchall()
print(f"\nTotal unique POULTRY products: {len(all_poultry_products)}")
print(f"Total POULTRY inspections: {sum(row[1] for row in all_poultry_products)}")

# Define keywords that SHOULD be in poultry
valid_poultry_keywords = [
    'chicken', 'poultry', 'wing', 'breast', 'thigh', 'drumstick', 'leg',
    'feet', 'foot', 'head', 'gizzard', 'liver', 'heart', 'neck',
    'whole bird', 'carcass', 'portions', 'braai pack', 'iqp', 'abalone'
]

# Define keywords that should NOT be in poultry
invalid_keywords = [
    'wors', 'sausage', 'polony', 'vienna', 'russian', 'frankfurter',
    'bacon', 'ham', 'salami', 'biltong', 'droewors', 'beef', 'pork',
    'mutton', 'lamb', 'boerewors', 'mince', 'patties', 'burger'
]

print("\n" + "=" * 80)
print("ANALYSIS: Products that DON'T belong in POULTRY category")
print("=" * 80)

misclassified = []

for product_name, count in all_poultry_products:
    product_lower = product_name.lower() if product_name else ''

    # Check if product contains invalid keywords
    has_invalid = any(keyword in product_lower for keyword in invalid_keywords)
    has_valid = any(keyword in product_lower for keyword in valid_poultry_keywords)

    if has_invalid:
        misclassified.append((product_name, count, 'INVALID_KEYWORD'))
    elif not has_valid and product_name and len(product_name) > 2:
        # Product doesn't contain any valid poultry keywords
        # (excluding very short names which might be codes)
        misclassified.append((product_name, count, 'NO_POULTRY_KEYWORD'))

if misclassified:
    print(f"\n[ERROR] Found {len(misclassified)} products that likely don't belong in POULTRY category")
    print(f"Total affected inspections: {sum(item[1] for item in misclassified)}")

    print("\n--- Products with INVALID keywords (sausages, beef, pork, etc.) ---")
    invalid_products = [item for item in misclassified if item[2] == 'INVALID_KEYWORD']

    if invalid_products:
        print(f"\n{'Product Name':<50} {'Count':<10} {'Issue':<30}")
        print("-" * 90)
        for product, count, reason in sorted(invalid_products, key=lambda x: x[1], reverse=True):
            # Identify which invalid keyword was found
            product_lower = product.lower()
            found_keywords = [kw for kw in invalid_keywords if kw in product_lower]
            issue = f"Contains: {', '.join(found_keywords)}"
            print(f"{product:<50} {count:<10} {issue:<30}")

    print("\n--- Products with NO poultry keywords (might be misclassified) ---")
    no_keyword_products = [item for item in misclassified if item[2] == 'NO_POULTRY_KEYWORD']

    if no_keyword_products:
        print(f"\n{'Product Name':<50} {'Count':<10}")
        print("-" * 60)
        for product, count, reason in sorted(no_keyword_products, key=lambda x: x[1], reverse=True)[:30]:
            print(f"{product:<50} {count:<10}")
else:
    print("\n[OK] All POULTRY products appear to be correctly classified")

# Show some examples of CORRECT poultry products
print("\n" + "=" * 80)
print("EXAMPLES OF CORRECTLY CLASSIFIED POULTRY PRODUCTS")
print("=" * 80)

cursor.execute('''
    SELECT DISTINCT product_name, COUNT(*) as count
    FROM inspections
    WHERE commodity = 'POULTRY'
    AND (
        LOWER(product_name) LIKE '%chicken%'
        OR LOWER(product_name) LIKE '%wing%'
        OR LOWER(product_name) LIKE '%breast%'
        OR LOWER(product_name) LIKE '%drumstick%'
        OR LOWER(product_name) LIKE '%feet%'
    )
    ORDER BY count DESC
    LIMIT 20
''')

print(f"\n{'Product Name':<50} {'Count':<10}")
print("-" * 60)
for product, count in cursor.fetchall():
    print(f"{product:<50} {count:<10}")

# Find which clients have the most misclassified products
if misclassified:
    print("\n" + "=" * 80)
    print("CLIENTS WITH MISCLASSIFIED POULTRY PRODUCTS")
    print("=" * 80)

    # Get list of misclassified product names
    misclassified_names = [item[0] for item in misclassified]

    # Build query with proper parameter placeholders
    placeholders = ','.join('?' * len(misclassified_names))

    cursor.execute(f'''
        SELECT client_name, product_name, COUNT(*) as count
        FROM inspections
        WHERE commodity = 'POULTRY'
        AND product_name IN ({placeholders})
        GROUP BY client_name, product_name
        ORDER BY count DESC
        LIMIT 30
    ''', misclassified_names)

    print(f"\n{'Client Name':<50} {'Product':<30} {'Count':<10}")
    print("-" * 90)
    for client, product, count in cursor.fetchall():
        print(f"{client:<50} {product:<30} {count:<10}")

# Recommendations
print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

if misclassified:
    total_affected = sum(item[1] for item in misclassified)
    invalid_count = len([item for item in misclassified if item[2] == 'INVALID_KEYWORD'])

    print(f"""
ISSUE FOUND: {total_affected} POULTRY inspections have incorrect products

1. PROCESSED MEAT PRODUCTS IN POULTRY CATEGORY (Priority: HIGH)
   - {invalid_count} products contain sausages, wors, polony, etc.
   - These should be in PMP (Processed Meat Products) category, NOT POULTRY
   - Examples: "Russian", "Polony", "Wors", "Boerewors"

   ACTION REQUIRED:
   - Update commodity from POULTRY to PMP for these inspections
   - Train inspectors that:
     * POULTRY = raw chicken products (wings, breasts, feet, etc.)
     * PMP = processed products (sausages, polony, hams, etc.)

2. UNCLEAR PRODUCTS (Priority: MEDIUM)
   - Some products don't contain clear poultry indicators
   - May need manual review to confirm if they're correct

3. DATA CLEANUP
   - Identify and reclassify affected inspections
   - Update inspection records in source database
   - Add validation to prevent future misclassification
""")
else:
    print("\n[OK] No issues found - all POULTRY products appear correctly classified")

conn.close()

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)
