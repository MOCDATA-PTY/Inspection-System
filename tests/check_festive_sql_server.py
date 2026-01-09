#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Festive account code directly in SQL Server
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

def check_festive_in_sql_server():
    """Check Festive client and inspections in SQL Server"""

    print(f"\n{'='*100}")
    print(f"CHECKING FESTIVE IN SQL SERVER")
    print(f"{'='*100}\n")

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

    # Check Festive in Clients table
    print("="*100)
    print("FESTIVE CLIENTS IN SQL SERVER")
    print("="*100 + "\n")

    cursor.execute("""
        SELECT Id, Name, InternalAccountNumber, IsActive
        FROM AFS.dbo.Clients
        WHERE Name LIKE '%Festive%'
    """)

    clients = cursor.fetchall()
    for client in clients:
        print(f"Client ID: {client['Id']}")
        print(f"Name: {client['Name']}")
        print(f"Account Number: {client['InternalAccountNumber']}")
        print(f"Active: {client['IsActive']}")
        print()

    # Check Festive in POULTRY inspections
    print("="*100)
    print("FESTIVE POULTRY INSPECTIONS IN SQL SERVER")
    print("="*100 + "\n")

    cursor.execute("""
        SELECT TOP 5
            i.Id,
            i.DateOfInspection,
            i.ClientId,
            c.Name as ClientName,
            c.InternalAccountNumber,
            i.ProductName
        FROM AFS.dbo.PoultryQuidInspectionRecordTypes i
        JOIN AFS.dbo.Clients c ON c.Id = i.ClientId
        WHERE c.Name LIKE '%Festive%'
        ORDER BY i.DateOfInspection DESC
    """)

    poultry_inspections = cursor.fetchall()
    print(f"Found {len(poultry_inspections)} POULTRY Quid inspections\n")

    for insp in poultry_inspections:
        print(f"Inspection ID: {insp['Id']}")
        print(f"Date: {insp['DateOfInspection']}")
        print(f"Client ID: {insp['ClientId']}")
        print(f"Client Name: {insp['ClientName']}")
        print(f"Account Number: {insp['InternalAccountNumber']}")
        print(f"Product: {insp['ProductName']}")
        print()

    # Check if Festive has RAW inspections
    print("="*100)
    print("FESTIVE RAW INSPECTIONS IN SQL SERVER")
    print("="*100 + "\n")

    cursor.execute("""
        SELECT TOP 5
            i.Id,
            i.DateOfInspection,
            c.Name as ClientName,
            c.InternalAccountNumber
        FROM AFS.dbo.RawRMPInspectionRecordTypes i
        JOIN AFS.dbo.Clients c ON c.Id = i.ClientId
        WHERE c.Name LIKE '%Festive%'
        ORDER BY i.DateOfInspection DESC
    """)

    raw_inspections = cursor.fetchall()
    print(f"Found {len(raw_inspections)} RAW inspections\n")

    for insp in raw_inspections:
        print(f"Inspection ID: {insp['Id']}")
        print(f"Date: {insp['DateOfInspection']}")
        print(f"Client Name: {insp['ClientName']}")
        print(f"Account Number: {insp['InternalAccountNumber']}")
        print()

    cursor.close()
    connection.close()

    print(f"{'='*100}\n")


if __name__ == "__main__":
    try:
        check_festive_in_sql_server()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
