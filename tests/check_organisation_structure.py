#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check organisation structure to understand Festive's multi-commodity setup
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

def check_organisation():
    """Check organisation and registration structure"""

    print(f"\n{'='*120}")
    print(f"FESTIVE ORGANISATION STRUCTURE ANALYSIS")
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

    # Get Organisation info
    print("="*120)
    print("ORGANISATION #4 (Festive's Organisation)")
    print("="*120 + "\n")

    cursor.execute("""
        SELECT *
        FROM AFS.dbo.Organisations
        WHERE Id = 4
    """)

    org = cursor.fetchone()
    if org:
        for field, value in org.items():
            print(f"  {field:30} : {value}")
        print()

    # Get all clients under Organisation 4
    print("="*120)
    print("ALL CLIENTS UNDER ORGANISATION #4")
    print("="*120 + "\n")

    cursor.execute("""
        SELECT Id, Name, InternalAccountNumber, PhysicalAddress, IsActive
        FROM AFS.dbo.Clients
        WHERE OrganisationId = 4
        ORDER BY Name
    """)

    clients = cursor.fetchall()
    print(f"Found {len(clients)} clients under this organisation:\n")

    for client in clients:
        print(f"Client {client['Id']:5} | {client['Name']:30} | {client['InternalAccountNumber']:25} | Active: {client['IsActive']}")
        print(f"           Address: {client['PhysicalAddress']}")
        print()

    # Check registration numbers
    print("="*120)
    print("FESTIVE REGISTRATION NUMBERS (from inspections)")
    print("="*120 + "\n")

    cursor.execute("""
        SELECT DISTINCT RegistrationNumber, ClientId, c.Name, c.InternalAccountNumber
        FROM AFS.dbo.PoultryQuidInspectionRecordTypes i
        JOIN AFS.dbo.Clients c ON c.Id = i.ClientId
        WHERE c.OrganisationId = 4
        ORDER BY RegistrationNumber
    """)

    registrations = cursor.fetchall()
    if registrations:
        print("Registration Numbers found in POULTRY inspections:")
        for reg in registrations:
            print(f"  Reg: {reg['RegistrationNumber']:15} | Client {reg['ClientId']:5} | {reg['Name']:30} | {reg['InternalAccountNumber']}")
        print()

    # Summary of inspections by commodity for all Festive clients
    print("="*120)
    print("INSPECTION SUMMARY BY COMMODITY (All Organisation #4 clients)")
    print("="*120 + "\n")

    # POULTRY inspections
    cursor.execute("""
        SELECT c.Id as ClientId, c.Name, c.InternalAccountNumber, COUNT(*) as InspectionCount
        FROM AFS.dbo.PoultryQuidInspectionRecordTypes i
        JOIN AFS.dbo.Clients c ON c.Id = i.ClientId
        WHERE c.OrganisationId = 4
        AND i.DateOfInspection >= '2025-10-01'
        GROUP BY c.Id, c.Name, c.InternalAccountNumber
        ORDER BY c.Name
    """)

    poultry = cursor.fetchall()
    if poultry:
        print("POULTRY Inspections (Oct 2025+):")
        for p in poultry:
            print(f"  Client {p['ClientId']:5} | {p['Name']:30} | {p['InternalAccountNumber']:25} | {p['InspectionCount']:3} inspections")
        print()

    # RAW inspections (will probably fail due to ClientId issue, but let's try with product table)
    try:
        cursor.execute("""
            SELECT c.Id as ClientId, c.Name, c.InternalAccountNumber, COUNT(DISTINCT i.Id) as InspectionCount
            FROM AFS.dbo.RawRMPInspectionRecordTypes i
            JOIN AFS.dbo.RawRMPInspectedProductRecordTypes p ON p.InspectionId = i.Id
            JOIN AFS.dbo.Clients c ON c.Id = p.ClientId
            WHERE c.OrganisationId = 4
            AND i.DateOfInspection >= '2025-10-01'
            GROUP BY c.Id, c.Name, c.InternalAccountNumber
            ORDER BY c.Name
        """)

        raw = cursor.fetchall()
        if raw:
            print("RAW Inspections (Oct 2025+):")
            for r in raw:
                print(f"  Client {r['ClientId']:5} | {r['Name']:30} | {r['InternalAccountNumber']:25} | {r['InspectionCount']:3} inspections")
            print()
        else:
            print("RAW Inspections: None found\n")
    except Exception as e:
        print(f"Could not query RAW inspections: {e}\n")

    cursor.close()
    connection.close()

    print(f"{'='*120}\n")


if __name__ == "__main__":
    try:
        check_organisation()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
