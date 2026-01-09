#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check specific egg inspection IDs to see what's in SQL Server
"""

import os
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()

import pymssql
from django.conf import settings

def check_egg_inspections():
    """Check specific egg inspection IDs in SQL Server"""

    print(f"\n{'='*120}")
    print(f"CHECKING SPECIFIC EGG INSPECTIONS IN SQL SERVER")
    print(f"{'='*120}\n")

    # The inspection IDs from the server
    inspection_ids = [17093, 17091, 17088, 17087, 17090, 17092, 17089, 17084, 17080, 17081]

    # Get SQL Server configuration
    sql_server_config = settings.DATABASES.get('sql_server', {})

    # Connect to SQL Server
    connection = pymssql.connect(
        server=sql_server_config.get('HOST'),
        port=int(sql_server_config.get('PORT', 1433)),
        user=sql_server_config.get('USER'),
        password=sql_server_config.get('PASSWORD'),
        database=sql_server_config.get('NAME'),
        timeout=30
    )
    cursor = connection.cursor(as_dict=True)

    print("Connected to SQL Server\n")

    # Create placeholders for the IN clause
    placeholders = ','.join(['%s'] * len(inspection_ids))

    query = f"""
        SELECT
            PoultryEggInspectionRecords.Id,
            PoultryEggInspectionRecords.DateOfInspection,
            PoultryEggInspectionRecords.ClientId,
            clt.Name as ClientName,
            clt.InternalAccountNumber,
            PoultryEggInspectionRecords.EggProducer,
            PoultryEggInspectionRecords.ProducerId
        FROM AFS.dbo.PoultryEggInspectionRecords
        JOIN AFS.dbo.Clients clt ON clt.Id = PoultryEggInspectionRecords.ClientId
        WHERE PoultryEggInspectionRecords.Id IN ({placeholders})
        ORDER BY PoultryEggInspectionRecords.DateOfInspection DESC
    """

    cursor.execute(query, inspection_ids)
    results = cursor.fetchall()

    print(f"Found {len(results)} egg inspections in SQL Server:\n")
    print("="*120)

    for rec in results:
        print(f"Inspection ID: {rec['Id']}")
        print(f"  Date: {rec['DateOfInspection']}")
        print(f"  Client: {rec['ClientName']}")
        print(f"  Account Code: {rec['InternalAccountNumber']}")
        print(f"  EggProducer: '{rec['EggProducer'] or '(EMPTY)'}'")
        print(f"  ProducerId: {rec['ProducerId']}")
        print()

    # Summary
    with_producer = sum(1 for r in results if r['EggProducer'] and r['EggProducer'].strip())
    without_producer = len(results) - with_producer

    print("="*120)
    print(f"SUMMARY:")
    print(f"  Inspections checked: {len(results)}")
    print(f"  With EggProducer: {with_producer}")
    print(f"  Without EggProducer (empty/NULL): {without_producer}")
    print("="*120 + "\n")

    # Check the ProducerId table to see what producers exist
    print("="*120)
    print("CHECKING PRODUCERS TABLE")
    print("="*120 + "\n")

    cursor.execute("""
        SELECT TOP 20 Id, Name
        FROM AFS.dbo.EggProducers
        ORDER BY Name
    """)

    producers = cursor.fetchall()
    if producers:
        print(f"Found {len(producers)} producers (showing first 20):\n")
        for prod in producers:
            print(f"  ID {prod['Id']:5} | {prod['Name']}")
    else:
        print("No producers table found or table is empty")

    cursor.close()
    connection.close()

    print(f"\n{'='*120}\n")


if __name__ == "__main__":
    try:
        check_egg_inspections()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
