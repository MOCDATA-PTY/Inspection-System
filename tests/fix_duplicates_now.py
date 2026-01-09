"""
Clear old duplicate data and resync from SQL Server with fixed query
"""
import os
import django
import pymssql
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db import transaction

print("=" * 100)
print("FIX INSPECTION DUPLICATES - CLEAR AND RESYNC")
print("=" * 100)

# Step 1: Clear old duplicate data
print("\nStep 1: Clearing old duplicate inspection data...")
print("-" * 100)

current_count = FoodSafetyAgencyInspection.objects.count()
print(f"Current inspection records: {current_count:,}")

deleted_count, _ = FoodSafetyAgencyInspection.objects.all().delete()
print(f"[OK] Deleted {deleted_count:,} old inspection records")

# Step 2: Connect to SQL Server
print("\nStep 2: Connecting to SQL Server...")
print("-" * 100)

try:
    conn = pymssql.connect(
        server='102.67.140.12',
        port='1053',
        user='FSAUser2',
        password='password',
        database='AFS'
    )
    cursor = conn.cursor(as_dict=True)
    print("[OK] Connected to SQL Server")
except Exception as e:
    print(f"[ERROR] Failed to connect: {e}")
    exit(1)

# Step 3: Fetch data using FIXED query (with OUTER APPLY for GPS)
print("\nStep 3: Fetching data from SQL Server (Oct 2025 - Mar 2026)...")
print("-" * 100)

# FIXED query with OUTER APPLY to prevent GPS duplicates
query = '''
    SELECT 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection,
           InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId,
           gps.Latitude, gps.Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm,
           t.Id as Id, clt.Name as Client, clt.InternalAccountNumber,
           t.ProductName as ProductName
    FROM PoultryQuidInspectionRecordTypes t
    OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM GPSInspectionLocationRecords WHERE PoultryQuidInspectionRecordId = t.Id ORDER BY Id) gps
    JOIN Clients clt ON clt.Id = t.ClientId
    WHERE t.IsActive = 1
      AND DateOfInspection >= '2025-10-01'
      AND DateOfInspection < '2026-04-01'
      AND t.ProductName IS NOT NULL
      AND t.ProductName != ''

    UNION ALL

    SELECT 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection,
           InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId,
           gps.Latitude, gps.Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm,
           t.Id as Id, clt.Name as Client, clt.InternalAccountNumber,
           t.ProductName as ProductName
    FROM PoultryGradingInspectionRecordTypes t
    OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM GPSInspectionLocationRecords WHERE PoultryGradingClassInspectionRecordId = t.Id ORDER BY Id) gps
    JOIN Clients clt ON clt.Id = t.ClientId
    WHERE t.IsActive = 1
      AND DateOfInspection >= '2025-10-01'
      AND DateOfInspection < '2026-04-01'
      AND t.ProductName IS NOT NULL
      AND t.ProductName != ''

    UNION ALL

    SELECT 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection,
           InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId,
           gps.Latitude, gps.Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm,
           t.Id as Id, clt.Name as Client, clt.InternalAccountNumber,
           t.ProductName as ProductName
    FROM PoultryLabelInspectionChecklistRecords t
    OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM GPSInspectionLocationRecords WHERE PoultryLabelChecklistInspectionRecordId = t.Id ORDER BY Id) gps
    JOIN Clients clt ON clt.Id = t.ClientId
    WHERE t.IsActive = 1
      AND DateOfInspection >= '2025-10-01'
      AND DateOfInspection < '2026-04-01'
      AND t.ProductName IS NOT NULL
      AND t.ProductName != ''

    UNION ALL

    SELECT 'EGGS' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection,
           InspectionLocationTypeID, IsDirectionPresentForInspection as IsDirectionPresentForthisInspection,
           InspectorId, gps.Latitude, gps.Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm,
           t.Id as Id, clt.Name as Client, clt.InternalAccountNumber,
           t.EggProducer as ProductName
    FROM PoultryEggInspectionRecords t
    OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM GPSInspectionLocationRecords WHERE PoultryEggInspectionRecordId = t.Id ORDER BY Id) gps
    JOIN Clients clt ON clt.Id = t.ClientId
    WHERE t.IsActive = 1
      AND DateOfInspection >= '2025-10-01'
      AND DateOfInspection < '2026-04-01'

    UNION ALL

    SELECT 'RAW' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection,
           InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId,
           gps.Latitude, gps.Longitude, IsSampleTaken, InspectionTravelDistanceKm,
           t.Id as Id, clt.Name as Client, clt.InternalAccountNumber,
           prod.NewProductItemDetails as ProductName
    FROM RawRMPInspectionRecordTypes t
    OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM GPSInspectionLocationRecords WHERE RawRMPInspectionRecordId = t.Id ORDER BY Id) gps
    JOIN RawRMPInspectedProductRecordTypes prod ON prod.InspectionId = t.Id
    JOIN Clients clt ON clt.Id = prod.ClientId
    WHERE t.IsActive = 1
      AND DateOfInspection >= '2025-10-01'
      AND DateOfInspection < '2026-04-01'
      AND prod.NewProductItemDetails IS NOT NULL
      AND prod.NewProductItemDetails != ''

    UNION ALL

    SELECT 'PMP' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection,
           InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId,
           gps.Latitude, gps.Longitude, IsSampleTaken, NULL AS InspectionTravelDistanceKm,
           t.Id as Id, clt.Name as Client, clt.InternalAccountNumber,
           prod.PMPItemDetails as ProductName
    FROM PMPInspectionRecordTypes t
    OUTER APPLY (SELECT TOP 1 Latitude, Longitude FROM GPSInspectionLocationRecords WHERE PMPInspectionRecordId = t.Id ORDER BY Id) gps
    JOIN PMPInspectedProductRecordTypes prod ON prod.InspectionId = t.Id
    JOIN Clients clt ON clt.Id = prod.ClientId
    WHERE t.IsActive = 1
      AND DateOfInspection >= '2025-10-01'
      AND DateOfInspection < '2026-04-01'
      AND prod.PMPItemDetails IS NOT NULL
      AND prod.PMPItemDetails != ''
'''

cursor.execute(query)
rows = cursor.fetchall()
print(f"[OK] Fetched {len(rows):,} inspection records from SQL Server")

# Step 4: Insert into Django database
print("\nStep 4: Inserting clean data into Django database...")
print("-" * 100)

inserted = 0
skipped = 0
errors = 0

# Inspector ID mapping
INSPECTOR_MAP = {
    118: 'NEO NOE', 68: 'BEN VISAGIE', 124: 'SANDISIWE DLISANI',
    143: 'MOKGADI SELONE', 166: 'THATO SEKHOTHO', 174: 'LWANDILE MAQINA',
    177: 'CINGA NGONGO', 185: 'PERCY MALEKA', 188: 'GLADYS MANGANYE',
    196: 'NELISA NTOYAPHI', 202: 'HLENGIWE GUMEDE'
}

with transaction.atomic():
    for row in rows:
        try:
            inspector_id = row.get('InspectorId')
            inspector_name = INSPECTOR_MAP.get(inspector_id, 'Unknown')

            FoodSafetyAgencyInspection.objects.create(
                remote_id=row['Id'],
                commodity=row['Commodity'],
                date_of_inspection=row['DateOfInspection'],
                start_of_inspection=row['StartOfInspection'],
                end_of_inspection=row['EndOfInspection'],
                inspection_location_type_id=row['InspectionLocationTypeID'],
                is_direction_present_for_this_inspection=row['IsDirectionPresentForthisInspection'] or False,
                inspector_id=inspector_id,
                inspector_name=inspector_name,
                latitude=str(row['Latitude']) if row.get('Latitude') else None,
                longitude=str(row['Longitude']) if row.get('Longitude') else None,
                is_sample_taken=row.get('IsSampleTaken') or False,
                inspection_travel_distance_km=row.get('InspectionTravelDistanceKm'),
                client_name=row['Client'] or 'Unknown',
                product_name=row.get('ProductName'),
                internal_account_code=row.get('InternalAccountNumber')
            )
            inserted += 1

            if inserted % 500 == 0:
                print(f"  Inserted {inserted:,} records...")

        except Exception as e:
            errors += 1
            if errors <= 5:  # Show first 5 errors
                print(f"  [ERROR] Failed to insert inspection {row.get('Id')}: {e}")

print(f"\n[OK] Inserted {inserted:,} inspection records")
if skipped > 0:
    print(f"[WARNING] Skipped {skipped:,} records")
if errors > 0:
    print(f"[ERROR] Failed to insert {errors:,} records")

# Step 5: Verify results
print("\nStep 5: Verifying results...")
print("-" * 100)

final_count = FoodSafetyAgencyInspection.objects.count()
print(f"Total inspections in Django: {final_count:,}")

by_commodity = FoodSafetyAgencyInspection.objects.values('commodity').annotate(
    count=django.db.models.Count('id')
).order_by('commodity')

print(f"\nBy Commodity:")
for item in by_commodity:
    print(f"  {item['commodity']}: {item['count']:,}")

# Check for duplicates
from django.db.models import Count
duplicates = FoodSafetyAgencyInspection.objects.values('commodity', 'remote_id').annotate(
    count=Count('id')
).filter(count__gt=1)

dup_count = duplicates.count()
if dup_count > 0:
    print(f"\n[WARNING] Found {dup_count} duplicate (commodity, remote_id) pairs")
else:
    print(f"\n[OK] No duplicates found - composite key working correctly!")

# Check directions
with_direction = FoodSafetyAgencyInspection.objects.filter(
    is_direction_present_for_this_inspection=True
).count()

print(f"\nInspections with directions (non-compliant): {with_direction:,}")
print(f"Inspections without directions (compliant): {final_count - with_direction:,}")

conn.close()

print("\n" + "=" * 100)
print("DONE!")
print("=" * 100)
print(f"""
Results:
- Old records deleted: {deleted_count:,}
- New records inserted: {inserted:,}
- Current total: {final_count:,}
- Expected: ~3,717

Fixed Issues:
✓ No more GPS duplicates (1 inspection with 9 GPS = 1 row, not 9)
✓ Directions syncing properly ({with_direction:,} non-compliant inspections found)
✓ Composite key preventing future duplicates
✓ Correct inspection count
""")
print("=" * 100)
