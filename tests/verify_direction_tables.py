"""
Verify that IsDirectionPresentForthisInspection boolean matches actual direction tables
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
import pymssql

def verify_direction_data():
    """Check if the boolean field matches the actual direction tables"""
    print("=" * 100)
    print("VERIFYING DIRECTION BOOLEAN VS ACTUAL DIRECTION TABLES")
    print("=" * 100)

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

    # Check PMP: Compare boolean field vs actual direction tables
    print("\n[1] PMP INSPECTIONS - Checking direction data accuracy")
    print("-" * 100)

    pmp_query = """
        SELECT TOP 10
            insp.Id,
            insp.IsDirectionPresentForthisInspection as BooleanField,
            CASE WHEN EXISTS (
                SELECT 1 FROM AFS.dbo.PMPDirectionRecordTypes dir
                WHERE dir.InspectionRecordLinkId = insp.Id
            ) THEN 1 ELSE 0 END AS DirectionTableExists,
            CASE WHEN EXISTS (
                SELECT 1 FROM AFS.dbo.PMPInspectionDirectiveAuditRecordTypes dir
                WHERE dir.InspectionRecordId = insp.Id
            ) THEN 1 ELSE 0 END AS DirectiveAuditExists
        FROM [AFS].[dbo].[PMPInspectionRecordTypes] insp
        WHERE insp.DateOfInspection >= '2025-10-01'
        ORDER BY insp.DateOfInspection DESC
    """

    cursor.execute(pmp_query)
    pmp_results = cursor.fetchall()

    pmp_direction_mismatch = 0
    pmp_directive_mismatch = 0
    for row in pmp_results:
        boolean = row['BooleanField']
        direction = row['DirectionTableExists']
        directive = row['DirectiveAuditExists']

        dir_match = 'OK' if boolean == direction else 'MISMATCH'
        directive_match = 'OK' if boolean == directive else 'MISMATCH'

        if boolean != direction:
            pmp_direction_mismatch += 1
        if boolean != directive:
            pmp_directive_mismatch += 1

        print(f"  PMP ID {row['Id']}: Boolean={boolean}, Direction={direction} {dir_match}, Directive={directive} {directive_match}")

    print(f"\n  PMP Direction table mismatches: {pmp_direction_mismatch}/{len(pmp_results)}")
    print(f"  PMP DirectiveAudit mismatches: {pmp_directive_mismatch}/{len(pmp_results)}")

    # Check RAW: Compare boolean field vs actual direction tables
    print("\n[2] RAW INSPECTIONS - Checking direction data accuracy")
    print("-" * 100)

    raw_query = """
        SELECT TOP 10
            insp.Id,
            insp.IsDirectionPresentForthisInspection as BooleanField,
            CASE WHEN EXISTS (
                SELECT 1 FROM AFS.dbo.RawRMPDirectionRecordTypes dir
                WHERE dir.InspectionRecordLinkId = insp.Id
            ) THEN 1 ELSE 0 END AS DirectionTableExists,
            CASE WHEN EXISTS (
                SELECT 1 FROM AFS.dbo.RawRMPInspectionDirectiveAuditRecordTypes dir
                WHERE dir.InspectionRecordId = insp.Id
            ) THEN 1 ELSE 0 END AS DirectiveAuditExists
        FROM [AFS].[dbo].[RawRMPInspectionRecordTypes] insp
        WHERE insp.DateOfInspection >= '2025-10-01'
        ORDER BY insp.DateOfInspection DESC
    """

    cursor.execute(raw_query)
    raw_results = cursor.fetchall()

    raw_direction_mismatch = 0
    raw_directive_mismatch = 0
    for row in raw_results:
        boolean = row['BooleanField']
        direction = row['DirectionTableExists']
        directive = row['DirectiveAuditExists']

        dir_match = 'OK' if boolean == direction else 'MISMATCH'
        directive_match = 'OK' if boolean == directive else 'MISMATCH'

        if boolean != direction:
            raw_direction_mismatch += 1
        if boolean != directive:
            raw_directive_mismatch += 1

        print(f"  RAW ID {row['Id']}: Boolean={boolean}, Direction={direction} {dir_match}, Directive={directive} {directive_match}")

    print(f"\n  RAW Direction table mismatches: {raw_direction_mismatch}/{len(raw_results)}")
    print(f"  RAW DirectiveAudit mismatches: {raw_directive_mismatch}/{len(raw_results)}")

    # Check EGGS: Compare boolean field vs actual direction tables
    print("\n[3] EGGS INSPECTIONS - Checking direction data accuracy")
    print("-" * 100)

    eggs_query = """
        SELECT TOP 10
            insp.Id,
            insp.IsDirectionPresentForInspection as BooleanField,
            CASE WHEN EXISTS (
                SELECT 1 FROM AFS.dbo.PoultryEggDirections dir
                WHERE dir.InspectionRecordLinkId = insp.Id
            ) THEN 1 ELSE 0 END AS DirectionTableExists,
            CASE WHEN EXISTS (
                SELECT 1 FROM AFS.dbo.EggInspectionDirectiveAuditRecordTypes dir
                WHERE dir.InspectionRecordId = insp.Id
            ) THEN 1 ELSE 0 END AS DirectiveAuditExists
        FROM [AFS].[dbo].[PoultryEggInspectionRecords] insp
        WHERE insp.DateOfInspection >= '2025-10-01'
        ORDER BY insp.DateOfInspection DESC
    """

    cursor.execute(eggs_query)
    eggs_results = cursor.fetchall()

    eggs_direction_mismatch = 0
    eggs_directive_mismatch = 0
    for row in eggs_results:
        boolean = row['BooleanField']
        direction = row['DirectionTableExists']
        directive = row['DirectiveAuditExists']

        dir_match = 'OK' if boolean == direction else 'MISMATCH'
        directive_match = 'OK' if boolean == directive else 'MISMATCH'

        if boolean != direction:
            eggs_direction_mismatch += 1
        if boolean != directive:
            eggs_directive_mismatch += 1

        print(f"  EGGS ID {row['Id']}: Boolean={boolean}, Direction={direction} {dir_match}, Directive={directive} {directive_match}")

    print(f"\n  EGGS Direction table mismatches: {eggs_direction_mismatch}/{len(eggs_results)}")
    print(f"  EGGS DirectiveAudit mismatches: {eggs_directive_mismatch}/{len(eggs_results)}")

    # Check POULTRY: Compare boolean field vs DirectiveAudit table (Direction table has no FK)
    print("\n[4] POULTRY INSPECTIONS - Checking direction data accuracy")
    print("-" * 100)

    poultry_query = """
        SELECT TOP 10
            insp.Id,
            insp.IsDirectionPresentForthisInspection as BooleanField,
            0 AS DirectionTableExists,
            CASE WHEN EXISTS (
                SELECT 1 FROM AFS.dbo.PoultryInspectionDirectiveAuditRecordTypes dir
                WHERE dir.LabelContainerInspectionRecordId = insp.Id
            ) THEN 1 ELSE 0 END AS DirectiveAuditExists
        FROM AFS.dbo.PoultryLabelInspectionChecklistRecords insp
        WHERE insp.DateOfInspection >= '2025-10-01'
        ORDER BY insp.DateOfInspection DESC
    """

    cursor.execute(poultry_query)
    poultry_results = cursor.fetchall()

    poultry_direction_mismatch = 0
    poultry_directive_mismatch = 0
    for row in poultry_results:
        boolean = row['BooleanField']
        direction = row['DirectionTableExists']
        directive = row['DirectiveAuditExists']

        dir_match = 'OK' if boolean == direction else 'MISMATCH'
        directive_match = 'OK' if boolean == directive else 'MISMATCH'

        if boolean != direction:
            poultry_direction_mismatch += 1
        if boolean != directive:
            poultry_directive_mismatch += 1

        print(f"  POULTRY ID {row['Id']}: Boolean={boolean}, Direction={direction} {dir_match}, Directive={directive} {directive_match}")

    print(f"\n  POULTRY Direction table mismatches: {poultry_direction_mismatch}/{len(poultry_results)}")
    print(f"  POULTRY DirectiveAudit mismatches: {poultry_directive_mismatch}/{len(poultry_results)}")

    # Summary
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)

    direction_total_mismatch = pmp_direction_mismatch + raw_direction_mismatch + eggs_direction_mismatch + poultry_direction_mismatch
    directive_total_mismatch = pmp_directive_mismatch + raw_directive_mismatch + eggs_directive_mismatch + poultry_directive_mismatch
    total_checked = len(pmp_results) + len(raw_results) + len(eggs_results) + len(poultry_results)

    print(f"\nDirection table mismatches: {direction_total_mismatch}/{total_checked}")
    print(f"DirectiveAudit table mismatches: {directive_total_mismatch}/{total_checked}")

    if direction_total_mismatch == 0:
        print("\n[SUCCESS] Boolean field matches Direction tables perfectly!")
        print("  Using: PMPDirectionRecordTypes, RawRMPDirectionRecordTypes, etc.")
    elif directive_total_mismatch == 0:
        print("\n[SUCCESS] Boolean field matches DirectiveAudit tables perfectly!")
        print("  Using: PMPInspectionDirectiveAuditRecordTypes, etc.")
    else:
        print("\n[WARNING] MISMATCHES FOUND!")
        print("The boolean field doesn't match either table type consistently.")
        print("Need to investigate which table is the source of truth.")

    connection.close()

if __name__ == '__main__':
    verify_direction_data()
