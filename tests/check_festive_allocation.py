#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Festive allocation and division information in SQL Server
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

def check_festive_allocation():
    """Check all fields for Festive client in SQL Server"""

    print(f"\n{'='*120}")
    print(f"FESTIVE CLIENT - COMPLETE SQL SERVER RECORD")
    print(f"{'='*120}\n")

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

    # Get ALL columns for Festive
    print("="*120)
    print("FESTIVE CLIENT - ALL FIELDS")
    print("="*120 + "\n")

    cursor.execute("""
        SELECT *
        FROM AFS.dbo.Clients
        WHERE Name LIKE '%Festive%'
        ORDER BY Id
    """)

    clients = cursor.fetchall()

    for idx, client in enumerate(clients, 1):
        print(f"CLIENT RECORD #{idx}")
        print("-" * 120)

        # Print all fields
        for field, value in client.items():
            print(f"  {field:30} : {value}")

        print()

    # Check if there's a CommodityType or Division table
    print("="*120)
    print("CHECKING FOR COMMODITY/DIVISION TABLES")
    print("="*120 + "\n")

    try:
        cursor.execute("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'dbo'
            AND (TABLE_NAME LIKE '%Commodity%'
                 OR TABLE_NAME LIKE '%Division%'
                 OR TABLE_NAME LIKE '%Allocation%'
                 OR TABLE_NAME LIKE '%Category%')
            ORDER BY TABLE_NAME
        """)

        tables = cursor.fetchall()
        if tables:
            print("Found related tables:")
            for table in tables:
                print(f"  - {table['TABLE_NAME']}")
        else:
            print("No commodity/division/allocation related tables found")
        print()
    except Exception as e:
        print(f"Could not query table structure: {e}\n")

    # Check inspections to see if there's a division field
    print("="*120)
    print("POULTRY INSPECTION RECORDS FOR FESTIVE - ALL FIELDS")
    print("="*120 + "\n")

    cursor.execute("""
        SELECT TOP 1 *
        FROM AFS.dbo.PoultryQuidInspectionRecordTypes
        WHERE ClientId = 3420
        ORDER BY DateOfInspection DESC
    """)

    inspection = cursor.fetchone()
    if inspection:
        print("Sample POULTRY Inspection Fields:")
        print("-" * 120)
        for field, value in inspection.items():
            print(f"  {field:40} : {value}")
        print()

    cursor.close()
    connection.close()

    print(f"{'='*120}\n")


if __name__ == "__main__":
    try:
        check_festive_allocation()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
