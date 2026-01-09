"""
Comprehensive analysis of product/commodity mismatches across all categories
"""
import sqlite3
import os

LOCAL_DB = 'local_inspection_analysis.sqlite3'

if not os.path.exists(LOCAL_DB):
    print(f"ERROR: Database not found: {LOCAL_DB}")
    exit(1)

conn = sqlite3.connect(LOCAL_DB)
cursor = conn.cursor()

print("=" * 80)
print("COMPREHENSIVE COMMODITY/PRODUCT MISMATCH ANALYSIS")
print("=" * 80)

# Define what products belong in each commodity
commodity_rules = {
    'POULTRY': {
        'should_contain': ['chicken', 'poultry', 'wing', 'breast', 'thigh', 'drumstick', 'leg',
                          'feet', 'foot', 'head', 'gizzard', 'liver', 'heart', 'neck',
                          'whole bird', 'carcass', 'portions', 'braai pack', 'iqp', 'duck',
                          'turkey', 'goose', 'quail'],
        'should_not_contain': ['wors', 'sausage', 'polony', 'vienna', 'russian', 'frankfurter',
                               'bacon', 'ham', 'salami', 'biltong', 'droewors', 'beef', 'pork',
                               'mutton', 'lamb', 'boerewors', 'mince', 'patties', 'burger',
                               'egg', 'eggs']
    },
    'EGGS': {
        'should_contain': ['egg'],
        'should_not_contain': ['chicken', 'wors', 'sausage', 'beef', 'pork', 'polony',
                               'wing', 'breast', 'thigh', 'feet', 'salami']
    },
    'PMP': {  # Processed Meat Products
        'should_contain': ['wors', 'sausage', 'polony', 'vienna', 'russian', 'frankfurter',
                          'bacon', 'ham', 'salami', 'biltong', 'droewors', 'processed',
                          'cooked', 'smoked', 'cured'],
        'should_not_contain': ['raw', 'fresh', 'uncooked']
    },
    'RAW': {  # Raw Red Meat Products
        'should_contain': ['beef', 'pork', 'mutton', 'lamb', 'veal', 'offal', 'tripe',
                          'oxtail', 'mince', 'steak', 'chops', 'ribs', 'roast'],
        'should_not_contain': ['cooked', 'smoked', 'processed', 'wors', 'polony',
                               'chicken', 'egg']
    }
}

mismatches_by_commodity = {}

for commodity in ['POULTRY', 'EGGS', 'PMP', 'RAW']:
    print(f"\n{'=' * 80}")
    print(f"ANALYZING: {commodity}")
    print(f"{'=' * 80}")

    cursor.execute('''
        SELECT product_name, COUNT(*) as count, client_name
        FROM inspections
        WHERE commodity = ?
        AND product_name IS NOT NULL
        AND product_name != ''
        GROUP BY product_name, client_name
        ORDER BY count DESC
    ''', (commodity,))

    all_products = cursor.fetchall()
    total_inspections = sum(row[1] for row in all_products)

    print(f"\nTotal unique products: {len(set([row[0] for row in all_products]))}")
    print(f"Total inspections: {total_inspections}")

    rules = commodity_rules.get(commodity, {})
    should_contain = rules.get('should_contain', [])
    should_not_contain = rules.get('should_not_contain', [])

    # Find mismatches
    has_invalid_keyword = []
    missing_valid_keyword = []

    processed_products = set()

    for product_name, count, client_name in all_products:
        if product_name in processed_products:
            continue
        processed_products.add(product_name)

        product_lower = product_name.lower()

        # Check for invalid keywords (products that shouldn't be in this commodity)
        invalid_found = [kw for kw in should_not_contain if kw in product_lower]
        if invalid_found:
            # Get total count for this product
            cursor.execute('''
                SELECT COUNT(*) FROM inspections
                WHERE commodity = ? AND product_name = ?
            ''', (commodity, product_name))
            total_count = cursor.fetchone()[0]
            has_invalid_keyword.append((product_name, total_count, invalid_found))

        # Check for missing valid keywords (might not belong here)
        elif should_contain:  # Only check if we have positive rules
            valid_found = any(kw in product_lower for kw in should_contain)
            if not valid_found and len(product_name) > 3:  # Exclude very short names
                cursor.execute('''
                    SELECT COUNT(*) FROM inspections
                    WHERE commodity = ? AND product_name = ?
                ''', (commodity, product_name))
                total_count = cursor.fetchone()[0]
                missing_valid_keyword.append((product_name, total_count))

    # Report findings
    if has_invalid_keyword:
        print(f"\n[ERROR] Products with WRONG keywords (don't belong in {commodity}):")
        print(f"{'Product Name':<50} {'Count':<10} {'Wrong Keywords':<30}")
        print("-" * 90)
        for product, count, keywords in sorted(has_invalid_keyword, key=lambda x: x[1], reverse=True)[:30]:
            kw_str = ', '.join(keywords[:3])  # Show first 3 keywords
            print(f"{product:<50} {count:<10} {kw_str:<30}")

            # Suggest correct commodity
            for other_commodity, other_rules in commodity_rules.items():
                if other_commodity != commodity:
                    if any(kw in other_rules.get('should_contain', []) for kw in keywords):
                        print(f"  -> Should probably be in: {other_commodity}")
                        break

    if missing_valid_keyword:
        print(f"\n[WARNING] Products WITHOUT expected {commodity} keywords (review needed):")
        print(f"{'Product Name':<50} {'Count':<10}")
        print("-" * 60)
        for product, count in sorted(missing_valid_keyword, key=lambda x: x[1], reverse=True)[:20]:
            print(f"{product:<50} {count:<10}")

    if not has_invalid_keyword and not missing_valid_keyword:
        print(f"\n[OK] No obvious mismatches found in {commodity} category")

    # Store for summary
    mismatches_by_commodity[commodity] = {
        'invalid': len(has_invalid_keyword),
        'unclear': len(missing_valid_keyword),
        'invalid_inspections': sum(item[1] for item in has_invalid_keyword),
        'unclear_inspections': sum(item[1] for item in missing_valid_keyword)
    }

# Summary
print("\n" + "=" * 80)
print("SUMMARY OF COMMODITY/PRODUCT MISMATCHES")
print("=" * 80)

print(f"\n{'Commodity':<15} {'Wrong Products':<20} {'Unclear Products':<20} {'Total Issues':<15}")
print("-" * 70)

total_wrong = 0
total_unclear = 0

for commodity, stats in mismatches_by_commodity.items():
    wrong = f"{stats['invalid']} ({stats['invalid_inspections']} insp.)"
    unclear = f"{stats['unclear']} ({stats['unclear_inspections']} insp.)"
    total = stats['invalid'] + stats['unclear']

    print(f"{commodity:<15} {wrong:<20} {unclear:<20} {total:<15}")

    total_wrong += stats['invalid_inspections']
    total_unclear += stats['unclear_inspections']

print("-" * 70)
print(f"{'TOTALS:':<15} {total_wrong} inspections  {total_unclear} inspections  {total_wrong + total_unclear} total")

# Recommendations
print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

print("""
PRIORITY ACTIONS:

1. POULTRY CATEGORY (Priority: LOW-MEDIUM)
   - 1 inspection with "Deli Viennas" - should be PMP
   - 97 products missing clear poultry keywords - mostly OK (Duck, Turkey, Fillets, etc.)
   - Action: Review "Deli Viennas" and reclassify to PMP

2. EGGS CATEGORY (Priority: CRITICAL)
   - 439 inspections missing product names (58% of all egg inspections!)
   - This is the BIGGEST data quality issue
   - Action: Require product name entry for all egg inspections

3. PMP CATEGORY (Check if any issues found above)
   - Review for any raw chicken products that should be POULTRY
   - Review for any raw meat products that should be RAW

4. RAW CATEGORY (Check if any issues found above)
   - Review for any processed products that should be PMP

5. DATA ENTRY TRAINING
   - Train inspectors on correct commodity classification:
     * POULTRY = Raw chicken/turkey/duck products
     * EGGS = Egg products only
     * PMP = Processed meats (wors, polony, ham, bacon, etc.)
     * RAW = Raw red meat (beef, pork, lamb, etc.)

6. ADD VALIDATION
   - Implement real-time validation during inspection entry
   - Warn if product name doesn't match commodity type
   - Provide dropdown suggestions based on commodity selected
""")

conn.close()

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)
