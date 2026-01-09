"""Examine what DirectiveAudit tables contain"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
import pymssql

sql_server_config = settings.DATABASES.get('sql_server', {})

connection = pymssql.connect(
    server=sql_server_config.get('HOST'),
    port=int(sql_server_config.get('PORT', 1433)),
    user=sql_server_config.get('USER'),
    password=sql_server_config.get('PASSWORD'),
    database=sql_server_config.get('NAME'),
    timeout=30
)
cursor = connection.cursor(as_dict=True)

print("=" * 100)
print("EXAMINING PMPInspectionDirectiveAuditRecordTypes")
print("=" * 100)

# Get a few sample records
cursor.execute("""
    SELECT TOP 5 *
    FROM AFS.dbo.PMPInspectionDirectiveAuditRecordTypes
    WHERE InspectionRecordId IN (8795, 8796, 8797, 8798)
    ORDER BY InspectionRecordId
""")
records = cursor.fetchall()

if records:
    print(f"\nFound {len(records)} records:")
    for record in records:
        print(f"\nInspectionRecordId: {record.get('InspectionRecordId')}")
        print(f"  Columns: {list(record.keys())[:10]}...")  # Show first 10 columns
        # Look for key fields that might indicate direction status
        for key in record.keys():
            if 'direction' in key.lower() or 'status' in key.lower() or 'compliant' in key.lower() or 'issue' in key.lower():
                print(f"  {key}: {record[key]}")
else:
    print("No records found")

# Check what percentage of inspections have DirectiveAudit records
print("\n" + "=" * 100)
print("CHECKING COVERAGE")
print("=" * 100)

cursor.execute("""
    SELECT
        COUNT(DISTINCT insp.Id) as TotalInspections,
        COUNT(DISTINCT audit.InspectionRecordId) as InspectionsWithAudit
    FROM [AFS].[dbo].[PMPInspectionRecordTypes] insp
    LEFT JOIN AFS.dbo.PMPInspectionDirectiveAuditRecordTypes audit
        ON audit.InspectionRecordId = insp.Id
    WHERE insp.DateOfInspection >= '2025-10-01'
""")
result = cursor.fetchone()
print(f"\nPMP Inspections: {result['TotalInspections']}")
print(f"With DirectiveAudit records: {result['InspectionsWithAudit']}")
print(f"Percentage: {result['InspectionsWithAudit']/result['TotalInspections']*100:.1f}%")

connection.close()
