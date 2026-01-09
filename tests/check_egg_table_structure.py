#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check PoultryEggInspectionRecords table structure to find product name field
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

def check_egg_table():
    """Check PoultryEggInspectionRecords table structure"""

    print(f"\n{'='*120}")
    print(f"POULTRY EGG INSPECTION RECORDS TABLE STRUCTURE")
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

    # Get column information
    print("="*120)
    print("TABLE COLUMNS")
    print("="*120 + "\n")

    cursor.execute("""
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
        AND TABLE_NAME = 'PoultryEggInspectionRecords'
        ORDER BY ORDINAL_POSITION
    """)

    columns = cursor.fetchall()
    print(f"Found {len(columns)} columns:\n")

    for col in columns:
        nullable = "NULL" if col['IS_NULLABLE'] == 'YES' else "NOT NULL"
        max_len = f"({col['CHARACTER_MAXIMUM_LENGTH']})" if col['CHARACTER_MAXIMUM_LENGTH'] else ""
        print(f"  {col['COLUMN_NAME']:40} {col['DATA_TYPE']:15}{max_len:10} {nullable}")

    # Get sample records
    print(f"\n{'='*120}")
    print("SAMPLE RECORDS (last 5)")
    print("="*120 + "\n")

    cursor.execute("""
        SELECT TOP 5 *
        FROM AFS.dbo.PoultryEggInspectionRecords
        WHERE IsActive = 1
        AND DateOfInspection >= '2025-10-01'
        ORDER BY DateOfInspection DESC
    """)

    records = cursor.fetchall()
    if records:
        print(f"Found {len(records)} sample records:\n")
        for idx, rec in enumerate(records, 1):
            print(f"Record {idx}:")
            print("-" * 120)
            for field, value in rec.items():
                print(f"  {field:40} : {value}")
            print()
    else:
        print("No recent egg inspection records found")

    cursor.close()
    connection.close()

    print(f"{'='*120}\n")


if __name__ == "__main__":
    try:
        check_egg_table()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
