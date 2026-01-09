"""
Create local SQLite3 database, pull inspection data from SQL Server,
and analyze data integrity (product names, inspections, client matching)
"""
import sqlite3
import pymssql
from datetime import datetime, timedelta
import os

# Configuration
LOCAL_DB = 'local_inspection_analysis.sqlite3'
SQL_SERVER_CONFIG = {
    'server': '102.67.140.12',
    'port': 1053,
    'user': 'FSAUser2',
    'password': 'password',
    'database': 'AFS',
    'timeout': 60
}

print("=" * 80)
print("LOCAL SQLITE3 DATABASE CREATION & DATA INTEGRITY ANALYSIS")
print("=" * 80)

# Remove existing database if it exists
if os.path.exists(LOCAL_DB):
    os.remove(LOCAL_DB)
    print(f"\n[OK] Removed existing database: {LOCAL_DB}")

# Create SQLite connection
sqlite_conn = sqlite3.connect(LOCAL_DB)
sqlite_cursor = sqlite_conn.cursor()
print(f"[OK] Created new SQLite database: {LOCAL_DB}")

# Create inspections table
print("\nCreating tables...")
sqlite_cursor.execute('''
CREATE TABLE IF NOT EXISTS inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    remote_id INTEGER,
    commodity TEXT,
    date_of_inspection DATE,
    start_of_inspection TIME,
    end_of_inspection TIME,
    inspection_location_type_id INTEGER,
    is_direction_present BOOLEAN,
    inspector_id INTEGER,
    inspector_name TEXT,
    latitude REAL,
    longitude REAL,
    is_sample_taken BOOLEAN,
    inspection_travel_distance_km REAL,
    client_name TEXT,
    internal_account_number TEXT,
    product_name TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

sqlite_cursor.execute('''
CREATE TABLE IF NOT EXISTS data_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_type TEXT,
    severity TEXT,
    inspection_id INTEGER,
    client_name TEXT,
    product_name TEXT,
    commodity TEXT,
    issue_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

sqlite_conn.commit()
print("[OK] Tables created successfully")

# Connect to SQL Server
print("\n" + "=" * 80)
print("CONNECTING TO SQL SERVER AND PULLING DATA")
print("=" * 80)

try:
    sql_server_conn = pymssql.connect(**SQL_SERVER_CONFIG)
    sql_server_cursor = sql_server_conn.cursor(as_dict=True)
    print("[OK] Connected to SQL Server successfully")

    # Query to fetch inspection data (last 90 days)
    ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    query = f'''
        SELECT 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection,
               InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId,
               gps.Latitude, gps.Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm,
               [AFS].[dbo].[PoultryQuidInspectionRecordTypes].Id as Id,
               clt.Name as Client, clt.InternalAccountNumber,
               [AFS].[dbo].[PoultryQuidInspectionRecordTypes].ProductName as ProductName,
               [AFS].[dbo].[PoultryQuidInspectionRecordTypes].IsActive
        FROM AFS.dbo.PoultryQuidInspectionRecordTypes
        JOIN AFS.dbo.GPSInspectionLocationRecords gps ON gps.PoultryQuidInspectionRecordId = [AFS].[dbo].PoultryQuidInspectionRecordTypes.Id
        JOIN AFS.dbo.Clients clt ON clt.Id = [AFS].[dbo].PoultryQuidInspectionRecordTypes.ClientId
        WHERE AFS.dbo.PoultryQuidInspectionRecordTypes.IsActive = 1
        AND DateOfInspection >= '{ninety_days_ago}'

        UNION ALL

        SELECT 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection,
               InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId,
               gps.Latitude, gps.Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm,
               [AFS].[dbo].[PoultryGradingInspectionRecordTypes].Id as Id,
               clt.Name as Client, clt.InternalAccountNumber,
               [AFS].[dbo].[PoultryGradingInspectionRecordTypes].ProductName as ProductName,
               [AFS].[dbo].[PoultryGradingInspectionRecordTypes].IsActive
        FROM AFS.dbo.PoultryGradingInspectionRecordTypes
        JOIN AFS.dbo.GPSInspectionLocationRecords gps ON gps.PoultryGradingClassInspectionRecordId = [AFS].[dbo].[PoultryGradingInspectionRecordTypes].Id
        JOIN AFS.dbo.Clients clt ON clt.Id = [AFS].[dbo].[PoultryGradingInspectionRecordTypes].ClientId
        WHERE AFS.dbo.[PoultryGradingInspectionRecordTypes].IsActive = 1
        AND DateOfInspection >= '{ninety_days_ago}'

        UNION ALL

        SELECT 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection,
               InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId,
               gps.Latitude, gps.Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm,
               [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].Id as Id,
               clt.Name as Client, clt.InternalAccountNumber,
               [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ProductName as ProductName,
               [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].IsActive
        FROM AFS.dbo.PoultryLabelInspectionChecklistRecords
        JOIN AFS.dbo.GPSInspectionLocationRecords gps ON gps.PoultryLabelChecklistInspectionRecordId = [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].Id
        JOIN AFS.dbo.Clients clt ON clt.Id = [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ClientId
        WHERE AFS.dbo.[PoultryLabelInspectionChecklistRecords].IsActive = 1
        AND DateOfInspection >= '{ninety_days_ago}'

        UNION ALL

        SELECT 'EGGS' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection,
               InspectionLocationTypeID, IsDirectionPresentForInspection as IsDirectionPresentForthisInspection,
               InspectorId, gps.Latitude, gps.Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm,
               [AFS].[dbo].[PoultryEggInspectionRecords].Id as Id,
               clt.Name as Client, clt.InternalAccountNumber,
               [AFS].[dbo].[PoultryEggInspectionRecords].EggProducer as ProductName,
               [AFS].[dbo].[PoultryEggInspectionRecords].IsActive
        FROM [AFS].[dbo].[PoultryEggInspectionRecords]
        JOIN AFS.dbo.GPSInspectionLocationRecords gps ON gps.PoultryEggInspectionRecordId = [AFS].[dbo].[PoultryEggInspectionRecords].Id
        JOIN AFS.dbo.Clients clt ON clt.Id = [AFS].[dbo].[PoultryEggInspectionRecords].ClientId
        WHERE AFS.dbo.[PoultryEggInspectionRecords].IsActive = 1
        AND DateOfInspection >= '{ninety_days_ago}'

        UNION ALL

        SELECT 'RAW' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection,
               InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId,
               gps.Latitude, gps.Longitude, IsSampleTaken, InspectionTravelDistanceKm,
               [AFS].[dbo].[RawRMPInspectionRecordTypes].Id as Id,
               clt.Name as Client, clt.InternalAccountNumber,
               prod.NewProductItemDetails as ProductName,
               [AFS].[dbo].[RawRMPInspectionRecordTypes].IsActive
        FROM [AFS].[dbo].[RawRMPInspectionRecordTypes]
        JOIN AFS.dbo.GPSInspectionLocationRecords gps ON gps.RawRMPInspectionRecordId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id
        JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod ON prod.InspectionId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id
        JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
        WHERE AFS.dbo.[RawRMPInspectionRecordTypes].IsActive = 1
        AND DateOfInspection >= '{ninety_days_ago}'

        UNION ALL

        SELECT 'PMP' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection,
               InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId,
               gps.Latitude, gps.Longitude, IsSampleTaken, NULL AS InspectionTravelDistanceKm,
               [AFS].[dbo].[PMPInspectionRecordTypes].Id as Id,
               clt.Name as Client, clt.InternalAccountNumber,
               prod.PMPItemDetails as ProductName,
               [AFS].[dbo].[PMPInspectionRecordTypes].IsActive
        FROM [AFS].[dbo].[PMPInspectionRecordTypes]
        JOIN AFS.dbo.GPSInspectionLocationRecords gps ON gps.PMPInspectionRecordId = [AFS].[dbo].[PMPInspectionRecordTypes].Id
        JOIN AFS.dbo.PMPInspectedProductRecordTypes prod ON prod.InspectionId = [AFS].[dbo].[PMPInspectionRecordTypes].Id
        JOIN AFS.dbo.Clients clt ON clt.Id = prod.ClientId
        WHERE AFS.dbo.[PMPInspectionRecordTypes].IsActive = 1
        AND DateOfInspection >= '{ninety_days_ago}'

        ORDER BY DateOfInspection DESC, Id DESC
    '''

    print(f"\nFetching inspections from last 90 days (since {ninety_days_ago})...")
    sql_server_cursor.execute(query)
    rows = sql_server_cursor.fetchall()

    print(f"[OK] Fetched {len(rows)} inspection records")

    # Insert data into SQLite
    print("\nInserting data into SQLite database...")
    inserted = 0
    for row in rows:
        try:
            sqlite_cursor.execute('''
                INSERT INTO inspections (
                    remote_id, commodity, date_of_inspection, start_of_inspection, end_of_inspection,
                    inspection_location_type_id, is_direction_present, inspector_id, inspector_name,
                    latitude, longitude, is_sample_taken, inspection_travel_distance_km,
                    client_name, internal_account_number, product_name, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['Id'],
                row['Commodity'],
                row['DateOfInspection'],
                row['StartOfInspection'],
                row['EndOfInspection'],
                row['InspectionLocationTypeID'],
                row['IsDirectionPresentForthisInspection'],
                row['InspectorId'],
                None,  # Inspector name - will be populated from mapping
                row['Latitude'],
                row['Longitude'],
                row.get('IsSampleTaken'),
                row.get('InspectionTravelDistanceKm'),
                row['Client'],
                row['InternalAccountNumber'],
                row['ProductName'],
                row['IsActive']
            ))
            inserted += 1
            if inserted % 100 == 0:
                print(f"  Inserted {inserted} records...")
        except Exception as e:
            print(f"  Error inserting record {row.get('Id')}: {e}")

    sqlite_conn.commit()
    print(f"[OK] Successfully inserted {inserted} inspection records into SQLite")

    sql_server_conn.close()

except Exception as e:
    print(f"[ERROR] Error connecting to SQL Server or fetching data: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Now analyze data integrity
print("\n" + "=" * 80)
print("DATA INTEGRITY ANALYSIS")
print("=" * 80)

issues_found = []

# 1. Check for missing/null product names
print("\n1. Checking for missing product names...")
sqlite_cursor.execute('''
    SELECT COUNT(*) as count, commodity, client_name
    FROM inspections
    WHERE product_name IS NULL OR product_name = '' OR TRIM(product_name) = ''
    GROUP BY commodity, client_name
    ORDER BY count DESC
''')
missing_products = sqlite_cursor.fetchall()

if missing_products:
    print(f"   [ERROR] Found {len(missing_products)} client/commodity combinations with missing product names")
    for row in missing_products:
        count, commodity, client = row
        print(f"     - {client} ({commodity}): {count} inspections with missing product names")
        sqlite_cursor.execute('''
            INSERT INTO data_issues (issue_type, severity, client_name, commodity, issue_description)
            VALUES (?, ?, ?, ?, ?)
        ''', ('MISSING_PRODUCT_NAME', 'HIGH', client, commodity, f'{count} inspections missing product names'))
        issues_found.append(('MISSING_PRODUCT_NAME', client, commodity, count))
else:
    print("   [OK] All inspections have product names")

# 2. Check for mismatched commodity vs product name patterns
print("\n2. Checking for commodity/product name mismatches...")
sqlite_cursor.execute('''
    SELECT id, remote_id, commodity, product_name, client_name
    FROM inspections
    WHERE (
        (commodity = 'EGGS' AND product_name NOT LIKE '%egg%' AND product_name NOT LIKE '%Egg%')
        OR (commodity = 'POULTRY' AND (
            product_name LIKE '%egg%' OR
            product_name LIKE '%Egg%' OR
            product_name LIKE '%beef%' OR
            product_name LIKE '%pork%'
        ))
        OR (commodity = 'RAW' AND (
            product_name LIKE '%egg%' OR
            product_name LIKE '%cooked%'
        ))
    )
''')
mismatches = sqlite_cursor.fetchall()

if mismatches:
    print(f"   [ERROR] Found {len(mismatches)} potential commodity/product mismatches")
    for row in mismatches[:10]:  # Show first 10
        id, remote_id, commodity, product, client = row
        print(f"     - Inspection {remote_id}: {commodity} commodity but product is '{product}' ({client})")
        sqlite_cursor.execute('''
            INSERT INTO data_issues (issue_type, severity, inspection_id, client_name, product_name, commodity, issue_description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('COMMODITY_PRODUCT_MISMATCH', 'MEDIUM', remote_id, client, product, commodity,
              f'Commodity is {commodity} but product is {product}'))
else:
    print("   [OK] No obvious commodity/product mismatches found")

# 3. Check for duplicate inspections (same client, date, commodity, product)
print("\n3. Checking for potential duplicate inspections...")
sqlite_cursor.execute('''
    SELECT client_name, date_of_inspection, commodity, product_name, COUNT(*) as count
    FROM inspections
    GROUP BY client_name, date_of_inspection, commodity, product_name
    HAVING COUNT(*) > 1
    ORDER BY count DESC
''')
duplicates = sqlite_cursor.fetchall()

if duplicates:
    print(f"   [ERROR] Found {len(duplicates)} potential duplicate inspection groups")
    for row in duplicates[:10]:  # Show first 10
        client, date, commodity, product, count = row
        print(f"     - {client} on {date}: {count} inspections for {commodity}/{product}")
        sqlite_cursor.execute('''
            INSERT INTO data_issues (issue_type, severity, client_name, commodity, product_name, issue_description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('POTENTIAL_DUPLICATE', 'LOW', client, commodity, product,
              f'{count} inspections on {date} for same client/commodity/product'))
else:
    print("   [OK] No duplicate inspections found")

# 4. Check for missing client names
print("\n4. Checking for missing client names...")
sqlite_cursor.execute('''
    SELECT COUNT(*) as count, commodity
    FROM inspections
    WHERE client_name IS NULL OR client_name = '' OR TRIM(client_name) = ''
    GROUP BY commodity
''')
missing_clients = sqlite_cursor.fetchall()

if missing_clients:
    total = sum(row[0] for row in missing_clients)
    print(f"   [ERROR] Found {total} inspections with missing client names")
    for row in missing_clients:
        count, commodity = row
        print(f"     - {commodity}: {count} inspections")
        sqlite_cursor.execute('''
            INSERT INTO data_issues (issue_type, severity, commodity, issue_description)
            VALUES (?, ?, ?, ?)
        ''', ('MISSING_CLIENT_NAME', 'CRITICAL', commodity, f'{count} inspections missing client names'))
else:
    print("   [OK] All inspections have client names")

# 5. Check for inspections without inspector ID
print("\n5. Checking for inspections without inspector ID...")
sqlite_cursor.execute('''
    SELECT COUNT(*) as count, commodity, client_name
    FROM inspections
    WHERE inspector_id IS NULL
    GROUP BY commodity, client_name
    ORDER BY count DESC
    LIMIT 20
''')
missing_inspectors = sqlite_cursor.fetchall()

if missing_inspectors:
    total = sum(row[0] for row in missing_inspectors)
    print(f"   [WARNING] Found {total} inspections without inspector IDs")
    print(f"   (Showing top 20 clients)")
    for row in missing_inspectors:
        count, commodity, client = row
        print(f"     - {client} ({commodity}): {count} inspections")
else:
    print("   [OK] All inspections have inspector IDs")

# Commit all issues
sqlite_conn.commit()

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

sqlite_cursor.execute('SELECT COUNT(*) FROM inspections')
total_inspections = sqlite_cursor.fetchone()[0]

sqlite_cursor.execute('SELECT COUNT(DISTINCT client_name) FROM inspections')
total_clients = sqlite_cursor.fetchone()[0]

sqlite_cursor.execute('SELECT COUNT(DISTINCT commodity) FROM inspections')
total_commodities = sqlite_cursor.fetchone()[0]

sqlite_cursor.execute('SELECT COUNT(DISTINCT product_name) FROM inspections WHERE product_name IS NOT NULL')
total_products = sqlite_cursor.fetchone()[0]

sqlite_cursor.execute('SELECT COUNT(*) FROM data_issues')
total_issues = sqlite_cursor.fetchone()[0]

print(f"\nTotal Inspections: {total_inspections}")
print(f"Unique Clients: {total_clients}")
print(f"Commodities: {total_commodities}")
print(f"Unique Products: {total_products}")
print(f"Data Issues Found: {total_issues}")

# Commodity breakdown
print("\nInspections by Commodity:")
sqlite_cursor.execute('''
    SELECT commodity, COUNT(*) as count
    FROM inspections
    GROUP BY commodity
    ORDER BY count DESC
''')
for row in sqlite_cursor.fetchall():
    commodity, count = row
    print(f"  {commodity}: {count}")

# Close connections
sqlite_conn.close()

print("\n" + "=" * 80)
print(f"[OK] Analysis complete! Database saved to: {LOCAL_DB}")
print("=" * 80)
print("\nYou can now query the database using:")
print(f"  sqlite3 {LOCAL_DB}")
print("\nOr view issues with:")
print(f"  sqlite3 {LOCAL_DB} 'SELECT * FROM data_issues;'")
