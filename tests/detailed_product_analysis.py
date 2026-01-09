"""
Detailed analysis of product name issues in the inspection database
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
print("DETAILED PRODUCT NAME ANALYSIS")
print("=" * 80)

# 1. Analyze EGG product name patterns
print("\n1. EGG INSPECTION PRODUCT NAME PATTERNS")
print("=" * 80)

cursor.execute('''
    SELECT
        CASE
            WHEN product_name IS NULL OR product_name = '' OR TRIM(product_name) = '' THEN '[MISSING/EMPTY]'
            WHEN product_name = client_name THEN '[SAME AS CLIENT]'
            WHEN LOWER(product_name) LIKE '%spar%' OR LOWER(product_name) LIKE '%boxer%'
                 OR LOWER(product_name) LIKE '%pick%pay%' THEN '[RETAILER NAME]'
            ELSE '[HAS BRAND NAME]'
        END as pattern_type,
        COUNT(*) as count
    FROM inspections
    WHERE commodity = 'EGGS'
    GROUP BY pattern_type
    ORDER BY count DESC
''')

print("\nEgg Inspection Pattern Summary:")
for row in cursor.fetchall():
    pattern, count = row
    print(f"  {pattern}: {count} inspections")

# 2. Show examples of each pattern
print("\n2. EXAMPLES OF EACH PATTERN TYPE")
print("=" * 80)

# Missing/Empty
print("\n[A] MISSING/EMPTY PRODUCT NAMES:")
print("-" * 80)
cursor.execute('''
    SELECT remote_id, client_name, date_of_inspection
    FROM inspections
    WHERE commodity = 'EGGS'
    AND (product_name IS NULL OR product_name = '' OR TRIM(product_name) = '')
    ORDER BY date_of_inspection DESC
    LIMIT 10
''')
for row in cursor.fetchall():
    remote_id, client, date = row
    print(f"  Inspection {remote_id}: {client} on {date} - NO PRODUCT NAME")

# Same as client
print("\n[B] PRODUCT NAME SAME AS CLIENT NAME:")
print("-" * 80)
cursor.execute('''
    SELECT remote_id, client_name, product_name, date_of_inspection
    FROM inspections
    WHERE commodity = 'EGGS'
    AND product_name IS NOT NULL AND product_name != ''
    AND product_name = client_name
    ORDER BY date_of_inspection DESC
    LIMIT 10
''')
for row in cursor.fetchall():
    remote_id, client, product, date = row
    print(f"  Inspection {remote_id}: {client} - Product: '{product}' (SAME) on {date}")

# Retailer name as product
print("\n[C] RETAILER NAME AS PRODUCT NAME:")
print("-" * 80)
cursor.execute('''
    SELECT remote_id, client_name, product_name, date_of_inspection
    FROM inspections
    WHERE commodity = 'EGGS'
    AND product_name IS NOT NULL AND product_name != ''
    AND (LOWER(product_name) LIKE '%spar%' OR LOWER(product_name) LIKE '%boxer%'
         OR LOWER(product_name) LIKE '%pick%pay%' OR LOWER(product_name) LIKE '%shoprite%')
    ORDER BY date_of_inspection DESC
    LIMIT 15
''')
for row in cursor.fetchall():
    remote_id, client, product, date = row
    print(f"  Inspection {remote_id}: {client} - Product: '{product}' on {date}")

# Has brand name (good examples)
print("\n[D] PROPER BRAND NAMES (GOOD EXAMPLES):")
print("-" * 80)
cursor.execute('''
    SELECT remote_id, client_name, product_name, date_of_inspection
    FROM inspections
    WHERE commodity = 'EGGS'
    AND product_name IS NOT NULL AND product_name != ''
    AND product_name != client_name
    AND LOWER(product_name) NOT LIKE '%spar%'
    AND LOWER(product_name) NOT LIKE '%boxer%'
    AND LOWER(product_name) NOT LIKE '%pick%pay%'
    AND LOWER(product_name) NOT LIKE '%shoprite%'
    ORDER BY date_of_inspection DESC
    LIMIT 15
''')
for row in cursor.fetchall():
    remote_id, client, product, date = row
    print(f"  Inspection {remote_id}: {client} - Product: '{product}' on {date}")

# 3. Analyze by client type (Farm vs Retailer)
print("\n3. MISSING PRODUCT NAMES BY CLIENT TYPE")
print("=" * 80)

cursor.execute('''
    SELECT
        CASE
            WHEN LOWER(client_name) LIKE '%farm%' OR LOWER(client_name) LIKE '%eggs%'
                 OR LOWER(client_name) LIKE '%poultry%' OR LOWER(client_name) LIKE '%layers%' THEN 'FARM/PRODUCER'
            WHEN LOWER(client_name) LIKE '%spar%' OR LOWER(client_name) LIKE '%boxer%'
                 OR LOWER(client_name) LIKE '%pick%pay%' OR LOWER(client_name) LIKE '%shoprite%'
                 OR LOWER(client_name) LIKE '%butchery%' OR LOWER(client_name) LIKE '%market%' THEN 'RETAILER/STORE'
            ELSE 'OTHER'
        END as client_type,
        COUNT(*) as total_inspections,
        SUM(CASE WHEN product_name IS NULL OR product_name = '' THEN 1 ELSE 0 END) as missing_product,
        ROUND(SUM(CASE WHEN product_name IS NULL OR product_name = '' THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*), 1) as missing_percent
    FROM inspections
    WHERE commodity = 'EGGS'
    GROUP BY client_type
    ORDER BY missing_product DESC
''')

print("\nMissing Product Names by Client Type:")
print(f"{'Client Type':<20} {'Total':<10} {'Missing':<10} {'% Missing':<10}")
print("-" * 80)
for row in cursor.fetchall():
    client_type, total, missing, percent = row
    print(f"{client_type:<20} {total:<10} {missing:<10} {percent:.1f}%")

# 4. Top clients with missing product names
print("\n4. TOP CLIENTS WITH MISSING PRODUCT NAMES (EGGS)")
print("=" * 80)

cursor.execute('''
    SELECT client_name, COUNT(*) as missing_count
    FROM inspections
    WHERE commodity = 'EGGS'
    AND (product_name IS NULL OR product_name = '' OR TRIM(product_name) = '')
    GROUP BY client_name
    ORDER BY missing_count DESC
    LIMIT 20
''')

print(f"\n{'Client Name':<60} {'Missing Count':<15}")
print("-" * 80)
for row in cursor.fetchall():
    client, count = row
    print(f"{client:<60} {count:<15}")

# 5. Analyze other commodities
print("\n5. PRODUCT NAME ISSUES IN OTHER COMMODITIES")
print("=" * 80)

for commodity in ['POULTRY', 'RAW', 'PMP']:
    cursor.execute('''
        SELECT COUNT(*) as total,
               SUM(CASE WHEN product_name IS NULL OR product_name = '' THEN 1 ELSE 0 END) as missing
        FROM inspections
        WHERE commodity = ?
    ''', (commodity,))

    total, missing = cursor.fetchone()
    if total > 0:
        percent = (missing / total) * 100
        print(f"\n{commodity}:")
        print(f"  Total inspections: {total}")
        print(f"  Missing product names: {missing} ({percent:.1f}%)")

        if missing > 0:
            cursor.execute('''
                SELECT client_name, COUNT(*) as count
                FROM inspections
                WHERE commodity = ? AND (product_name IS NULL OR product_name = '')
                GROUP BY client_name
                ORDER BY count DESC
                LIMIT 5
            ''', (commodity,))

            print(f"  Top clients with missing product names:")
            for row in cursor.fetchall():
                client, count = row
                print(f"    - {client}: {count} inspections")

# 6. Recommendations
print("\n6. RECOMMENDATIONS")
print("=" * 80)
print("""
Based on the analysis, here are the key issues and recommendations:

1. MISSING PRODUCT NAMES (Priority: HIGH)
   - Issue: 580+ inspections (mostly EGGS) have no product name
   - Root Cause: "New Retailer" placeholder has 79 missing product names
   - Recommendation:
     * Update data entry process to require product name
     * For retailers, product name should be the EGG BRAND being sold (not store name)
     * For farms, product name should be the brand/product line

2. RETAILER NAME AS PRODUCT (Priority: MEDIUM)
   - Issue: Some inspections use retailer name (Spar, Boxer) as product name
   - Recommendation: Product name should be the actual egg brand (e.g., "Nulaid", "Farmer Brown")

3. DUPLICATE INSPECTIONS (Priority: LOW)
   - Issue: 241 groups of potential duplicates found
   - Recommendation: Review inspection process to avoid duplicate entries

4. DATA ENTRY TRAINING NEEDED
   - Train inspectors on proper product name entry
   - Clarify that product name = brand name, not client/retailer name
   - For egg inspections at retailers, record the egg brand being inspected
""")

conn.close()

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)
