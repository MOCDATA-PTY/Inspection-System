"""Check if inspections 65931-65933 are in PoultryInspectionRecordTypes (missing from query)"""
import pymssql

conn = pymssql.connect(
    server='102.67.140.12',
    port=1053,
    user='FSAUser2',
    password='password',
    database='AFS',
    timeout=30
)

cursor = conn.cursor(as_dict=True)

print('Checking PoultryInspectionRecordTypes table:')
print()

cursor.execute("""
    SELECT Id, ProductName, DateOfInspection, IsActive
    FROM PoultryInspectionRecordTypes
    WHERE Id IN (65931, 65932, 65933)
    ORDER BY Id
""")

results = cursor.fetchall()

if results:
    print('FOUND in PoultryInspectionRecordTypes:')
    for r in results:
        print(f'  ID {r["Id"]}: {r["ProductName"]}')
        print(f'    Date: {r["DateOfInspection"]}, Active: {r["IsActive"]}')
    print()
    print('=' * 80)
    print('PROBLEM IDENTIFIED')
    print('=' * 80)
    print('These inspections are in PoultryInspectionRecordTypes table,')
    print('but FSA_INSPECTION_QUERY does NOT include this table!')
    print()
    print('The query currently includes:')
    print('  - PoultryQuidInspectionRecordTypes')
    print('  - PoultryGradingInspectionRecordTypes')
    print('  - PoultryLabelInspectionChecklistRecords')
    print('  - PoultryEggInspectionRecords')
    print('  - RawRMPInspectionRecordTypes')
    print('  - PMPInspectionRecordTypes')
    print()
    print('But it DOES NOT include:')
    print('  - PoultryInspectionRecordTypes <- MISSING TABLE')
    print()
    print('SOLUTION: Add PoultryInspectionRecordTypes to FSA_INSPECTION_QUERY')
else:
    print('Not found in PoultryInspectionRecordTypes')

conn.close()
