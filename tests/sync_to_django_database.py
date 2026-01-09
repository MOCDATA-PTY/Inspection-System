"""
Sync data from SQL Server directly into Django database (SQLite)
This populates the Django database for composite key testing
"""
import os
import django
import pymssql
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db import transaction, IntegrityError

print("=" * 80)
print("SYNC DATA TO DJANGO DATABASE")
print("=" * 80)

# SQL Server connection
SQL_SERVER_CONFIG = {
    'server': '102.67.140.12',
    'port': '1053',
    'user': 'FSAUser2',
    'password': 'password',
    'database': 'AFS'
}

print("\nStep 1: Connecting to SQL Server...")
print("-" * 80)

try:
    conn = pymssql.connect(**SQL_SERVER_CONFIG)
    cursor = conn.cursor(as_dict=True)
    print("[OK] Connected to SQL Server")
except Exception as e:
    print(f"[ERROR] Failed to connect: {e}")
    exit(1)

# Clear existing data
print("\nStep 2: Clearing existing Django database...")
print("-" * 80)

current_count = FoodSafetyAgencyInspection.objects.count()
print(f"Current records: {current_count}")

if current_count > 0:
    FoodSafetyAgencyInspection.objects.all().delete()
    print("[OK] Database cleared")
else:
    print("[OK] Database already empty")

# Pull data from SQL Server (last 90 days)
print("\nStep 3: Fetching data from SQL Server (last 90 days)...")
print("-" * 80)

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

print(f"Fetching inspections since {ninety_days_ago}...")
cursor.execute(query)
rows = cursor.fetchall()
print(f"[OK] Fetched {len(rows):,} inspections from SQL Server")

# Insert into Django database
print("\nStep 4: Inserting into Django database...")
print("-" * 80)

inserted = 0
duplicates_blocked = 0
errors = []

for i, row in enumerate(rows):
    try:
        with transaction.atomic():
            FoodSafetyAgencyInspection.objects.create(
                remote_id=row['Id'],
                commodity=row['Commodity'],
                date_of_inspection=row['DateOfInspection'],
                start_of_inspection=row['StartOfInspection'],
                end_of_inspection=row['EndOfInspection'],
                inspection_location_type_id=row['InspectionLocationTypeID'],
                is_direction_present_for_this_inspection=row['IsDirectionPresentForthisInspection'],
                inspector_id=row['InspectorId'],
                inspector_name='Unknown',
                latitude=str(row['Latitude']) if row['Latitude'] else None,
                longitude=str(row['Longitude']) if row['Longitude'] else None,
                is_sample_taken=row.get('IsSampleTaken'),
                inspection_travel_distance_km=row.get('InspectionTravelDistanceKm'),
                client_name=row['Client'] or 'Unknown',
                product_name=row['ProductName'],
                internal_account_code=row['InternalAccountNumber']
            )
            inserted += 1

            if inserted % 500 == 0:
                print(f"  Inserted {inserted:,} / {len(rows):,}...")

    except IntegrityError as e:
        error_str = str(e).lower()
        if 'unique constraint' in error_str or 'commodity, remote_id' in error_str:
            duplicates_blocked += 1
            if duplicates_blocked <= 10:  # Show first 10
                print(f"  [DUPLICATE BLOCKED] {row['Commodity']}-{row['Id']} - Composite key working!")
        else:
            errors.append((row['Commodity'], row['Id'], str(e)[:100]))
    except Exception as e:
        errors.append((row['Commodity'], row['Id'], str(e)[:100]))

print(f"\n[OK] Inserted {inserted:,} inspections")

if duplicates_blocked > 0:
    print(f"[INFO] Blocked {duplicates_blocked} duplicate (commodity, remote_id) pairs")
    print("       This proves the composite key constraint is working!")

if errors:
    print(f"[WARNING] {len(errors)} other errors:")
    for commodity, remote_id, error in errors[:5]:
        print(f"  {commodity}-{remote_id}: {error}")

conn.close()

# Verify the sync
print("\nStep 5: Verification")
print("-" * 80)

total = FoodSafetyAgencyInspection.objects.count()
print(f"Total records in Django database: {total:,}")

for commodity in ['POULTRY', 'PMP', 'RAW', 'EGGS']:
    count = FoodSafetyAgencyInspection.objects.filter(commodity=commodity).count()
    if count > 0:
        print(f"  {commodity}: {count:,}")

print("\n" + "=" * 80)
print("SYNC COMPLETE")
print("=" * 80)

if duplicates_blocked > 0:
    print(f"""
[SUCCESS] Composite key constraint is working!

- Synced {inserted:,} inspections from SQL Server
- Blocked {duplicates_blocked} duplicate (commodity, remote_id) attempts
- The constraint prevented data corruption

Next step: Run verification script
  python verify_composite_key_with_existing_data.py
""")
else:
    print(f"""
[OK] Data synced successfully!

- Synced {inserted:,} inspections from SQL Server
- No duplicates encountered in this dataset

Next step: Run verification script
  python verify_composite_key_with_existing_data.py
""")

print("=" * 80)
