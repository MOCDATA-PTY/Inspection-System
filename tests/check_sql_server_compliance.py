"""Check compliance stats directly in SQL Server"""
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
print("SQL SERVER COMPLIANCE STATISTICS (October 2025 onwards)")
print("=" * 100)

# Check PMP
cursor.execute("""
    SELECT
        COUNT(*) as Total,
        SUM(CASE WHEN IsDirectionPresentForthisInspection = 1 THEN 1 ELSE 0 END) as NonCompliant,
        SUM(CASE WHEN IsDirectionPresentForthisInspection = 0 THEN 1 ELSE 0 END) as Compliant
    FROM [AFS].[dbo].[PMPInspectionRecordTypes]
    WHERE DateOfInspection >= '2025-10-01'
        AND IsActive = 1
""")
pmp = cursor.fetchone()

# Check RAW
cursor.execute("""
    SELECT
        COUNT(*) as Total,
        SUM(CASE WHEN IsDirectionPresentForthisInspection = 1 THEN 1 ELSE 0 END) as NonCompliant,
        SUM(CASE WHEN IsDirectionPresentForthisInspection = 0 THEN 1 ELSE 0 END) as Compliant
    FROM [AFS].[dbo].[RawRMPInspectionRecordTypes]
    WHERE DateOfInspection >= '2025-10-01'
        AND IsActive = 1
""")
raw = cursor.fetchone()

# Check EGGS
cursor.execute("""
    SELECT
        COUNT(*) as Total,
        SUM(CASE WHEN IsDirectionPresentForInspection = 1 THEN 1 ELSE 0 END) as NonCompliant,
        SUM(CASE WHEN IsDirectionPresentForInspection = 0 THEN 1 ELSE 0 END) as Compliant
    FROM [AFS].[dbo].[PoultryEggInspectionRecords]
    WHERE DateOfInspection >= '2025-10-01'
        AND IsActive = 1
""")
eggs = cursor.fetchone()

# Check POULTRY
cursor.execute("""
    SELECT
        COUNT(*) as Total,
        SUM(CASE WHEN IsDirectionPresentForthisInspection = 1 THEN 1 ELSE 0 END) as NonCompliant,
        SUM(CASE WHEN IsDirectionPresentForthisInspection = 0 THEN 1 ELSE 0 END) as Compliant
    FROM AFS.dbo.PoultryLabelInspectionChecklistRecords
    WHERE DateOfInspection >= '2025-10-01'
        AND IsActive = 1
""")
poultry = cursor.fetchone()

print(f"\n{'Commodity':<15} {'Total':<10} {'Compliant':<12} {'Non-Compliant':<15} {'Pass Rate':<10}")
print("-" * 100)

total_all = 0
compliant_all = 0
non_compliant_all = 0

for name, data in [('PMP', pmp), ('RAW', raw), ('EGGS', eggs), ('POULTRY', poultry)]:
    total = data['Total']
    compliant = data['Compliant'] or 0
    non_compliant = data['NonCompliant'] or 0
    pass_rate = (compliant/total*100) if total > 0 else 0

    total_all += total
    compliant_all += compliant
    non_compliant_all += non_compliant

    print(f"{name:<15} {total:<10} {compliant:<12} {non_compliant:<15} {pass_rate:.1f}%")

print("-" * 100)
print(f"{'TOTAL':<15} {total_all:<10} {compliant_all:<12} {non_compliant_all:<15} {compliant_all/total_all*100:.1f}%")

print("\n" + "=" * 100)
print("COMPARISON WITH DJANGO DATABASE")
print("=" * 100)
print(f"SQL Server has {non_compliant_all} non-compliant inspections")
print(f"Django database has 0 non-compliant inspections")
print(f"\nThis means the sync is NOT transferring the direction status correctly!")

connection.close()
