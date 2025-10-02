#!/usr/bin/env python3
"""
Test script to check SQL Server connectivity and test the FSA inspection query.
Run this script to verify if the database connection and query work before testing in Django.
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sql_connection():
    """Test SQL Server connection and query execution."""
    
    print("=== SQL Server Connection Test ===\n")
    
    # Test 1: Check if pyodbc is available
    try:
        import pyodbc
        print("✓ pyodbc is available")
    except ImportError as e:
        print(f"✗ pyodbc import failed: {e}")
        print("Please install pyodbc: pip install pyodbc")
        return False
    
    # Test 2: Test connection string
    connection_string = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=102.67.140.12,1053;'
        'DATABASE=AFS;'
        'UID=FSAUser2;'
        'PWD=password;'
        'TrustServerCertificate=yes;'
        'Encrypt=yes;'
    )
    
    print(f"Connection string: {connection_string[:50]}...")
    
    # Test 3: Test database connection
    try:
        print("\nAttempting to connect to SQL Server...")
        connection = pyodbc.connect(connection_string)
        print("✓ SQL Server connection successful!")
        
        # Test 4: Test cursor creation
        cursor = connection.cursor()
        print("✓ Cursor created successfully")
        
        # Test 5: Test simple query first
        print("\nTesting simple query...")
        simple_query = "SELECT @@VERSION as version"
        cursor.execute(simple_query)
        version_row = cursor.fetchone()
        if version_row:
            print(f"✓ SQL Server version: {version_row[0][:50]}...")
        else:
            print("✗ No version info returned")
        
        # Test 6: Test table existence
        print("\nTesting table existence...")
        tables_query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'dbo' 
        AND TABLE_NAME IN (
            'PoultryQuidInspectionRecordTypes',
            'PoultryGradingInspectionRecordTypes', 
            'PoultryLabelInspectionChecklistRecords',
            'PoultryEggInspectionRecords',
            'RawRMPInspectionRecordTypes',
            'PMPInspectionRecordTypes',
            'GPSInspectionLocationRecords',
            'Clients'
        )
        """
        
        cursor.execute(tables_query)
        tables = cursor.fetchall()
        print(f"✓ Found {len(tables)} required tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Test 7: Test the actual FSA inspection query
        print("\nTesting FSA inspection query...")
        fsa_query = '''
        SELECT TOP 5 'POULTRY' as Commodity, 
               DateOfInspection, 
               StartOfInspection, 
               EndOfInspection, 
               InspectionLocationTypeID, 
               IsDirectionPresentForthisInspection, 
               InspectorId, 
               gps.Latitude AS Latitude, 
               gps.Longitude AS Longitude, 
               NULL AS IsSampleTaken, 
               NULL AS InspectionTravelDistanceKm, 
               [AFS].[dbo].[PoultryQuidInspectionRecordTypes].Id as Id, 
               clt.Name as Client 
        FROM AFS.dbo.PoultryQuidInspectionRecordTypes 
        JOIN AFS.dbo.GPSInspectionLocationRecords gps 
            ON gps.PoultryQuidInspectionRecordId = [AFS].[dbo].PoultryQuidInspectionRecordTypes.Id 
        JOIN AFS.dbo.Clients clt 
            ON clt.Id = [AFS].[dbo].PoultryQuidInspectionRecordTypes.ClientId 
        WHERE AFS.dbo.PoultryQuidInspectionRecordTypes.IsActive = 1
        '''
        
        cursor.execute(fsa_query)
        columns = [column[0] for column in cursor.description]
        print(f"✓ Query columns: {columns}")
        
        rows = cursor.fetchall()
        print(f"✓ Query returned {len(rows)} rows")
        
        if rows:
            print("\nSample data (first row):")
            for i, (col, val) in enumerate(zip(columns, rows[0])):
                print(f"  {col}: {val}")
        
        # Test 8: Test full query with LIMIT
        print("\nTesting full FSA query with TOP 100...")
        full_query = '''
        SELECT DISTINCT TOP 100 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PoultryQuidInspectionRecordTypes].Id as Id, clt.Name as Client FROM AFS.dbo.PoultryQuidInspectionRecordTypes JOIN AFS.dbo.GPSInspectionLocationRecords gps ON gps.PoultryQuidInspectionRecordId = [AFS].[dbo].PoultryQuidInspectionRecordTypes.Id join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].PoultryQuidInspectionRecordTypes.ClientId where AFS.dbo.PoultryQuidInspectionRecordTypes.IsActive = 1 
        UNION 
        SELECT DISTINCT TOP 100 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PoultryGradingInspectionRecordTypes].Id as Id, clt.Name as Client FROM AFS.dbo.PoultryGradingInspectionRecordTypes JOIN AFS.dbo.GPSInspectionLocationRecords gps ON gps.PoultryGradingClassInspectionRecordId = [AFS].[dbo].[PoultryGradingInspectionRecordTypes].Id join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].PoultryGradingInspectionRecordTypes.ClientId where AFS.dbo.[PoultryGradingInspectionRecordTypes].IsActive = 1 
        UNION 
        SELECT DISTINCT TOP 100 'POULTRY' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].Id as Id, clt.Name as Client FROM AFS.dbo.PoultryLabelInspectionChecklistRecords JOIN AFS.dbo.GPSInspectionLocationRecords gps ON gps.PoultryLabelChecklistInspectionRecordId = [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].Id join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].[PoultryLabelInspectionChecklistRecords].ClientId where AFS.dbo.[PoultryLabelInspectionChecklistRecords].IsActive = 1 
        UNION 
        SELECT DISTINCT TOP 100 'EGGS' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForInspection as IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, NULL AS IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PoultryEggInspectionRecords].Id as Id, clt.Name as Client FROM [AFS].[dbo].[PoultryEggInspectionRecords] JOIN AFS.dbo.GPSInspectionLocationRecords gps ON gps.PoultryEggInspectionRecordId = [AFS].[dbo].[PoultryEggInspectionRecords].Id join AFS.dbo.Clients clt on clt.Id = [AFS].[dbo].[PoultryEggInspectionRecords].ClientId where AFS.dbo.[PoultryEggInspectionRecords].IsActive = 1 
        UNION 
        SELECT DISTINCT TOP 100 'RAW' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, IsSampleTaken, InspectionTravelDistanceKm, [AFS].[dbo].[RawRMPInspectionRecordTypes].Id as Id, clt.Name as Client FROM [AFS].[dbo].[RawRMPInspectionRecordTypes] JOIN AFS.dbo.GPSInspectionLocationRecords gps ON gps.RawRMPInspectionRecordId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id JOIN AFS.dbo.RawRMPInspectedProductRecordTypes prod on prod.InspectionId = [AFS].[dbo].[RawRMPInspectionRecordTypes].Id join AFS.dbo.Clients clt on clt.Id = prod.ClientId where AFS.dbo.[RawRMPInspectionRecordTypes].IsActive = 1 
        UNION 
        SELECT DISTINCT TOP 100 'PMP' as Commodity, DateOfInspection, StartOfInspection, EndOfInspection, InspectionLocationTypeID, IsDirectionPresentForthisInspection, InspectorId, gps.Latitude AS Latitude, gps.Longitude AS Longitude, IsSampleTaken, NULL AS InspectionTravelDistanceKm, [AFS].[dbo].[PMPInspectionRecordTypes].Id as Id, clt.Name as Client FROM [AFS].[dbo].[PMPInspectionRecordTypes] join AFS.dbo.GPSInspectionLocationRecords gps on gps.PMPInspectionRecordId = [AFS].[dbo].[PMPInspectionRecordTypes].Id JOIN AFS.dbo.PMPInspectedProductRecordTypes prod on prod.InspectionId = [AFS].[dbo].[PMPInspectionRecordTypes].Id join AFS.dbo.Clients clt on clt.Id = prod.ClientId where AFS.dbo.[PMPInspectionRecordTypes].IsActive = 1
        '''
        
        cursor.execute(full_query)
        full_rows = cursor.fetchall()
        print(f"✓ Full query returned {len(full_rows)} rows")
        
        # Close connection
        cursor.close()
        connection.close()
        print("\n✓ Connection closed successfully")
        
        return True
        
    except pyodbc.Error as e:
        print(f"✗ pyodbc error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_odbc_drivers():
    """Test available ODBC drivers."""
    print("\n=== ODBC Drivers Test ===\n")
    
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        print("Available ODBC drivers:")
        for driver in drivers:
            print(f"  - {driver}")
        
        # Check for SQL Server drivers
        sql_server_drivers = [d for d in drivers if 'SQL Server' in d]
        if sql_server_drivers:
            print(f"\n✓ Found {len(sql_server_drivers)} SQL Server drivers:")
            for driver in sql_server_drivers:
                print(f"  - {driver}")
        else:
            print("\n✗ No SQL Server drivers found!")
            print("You may need to install SQL Server ODBC drivers.")
            
    except Exception as e:
        print(f"✗ Error checking drivers: {e}")

if __name__ == "__main__":
    print("Starting SQL Server connection tests...\n")
    
    # Test ODBC drivers first
    test_odbc_drivers()
    
    # Test connection
    success = test_sql_connection()
    
    if success:
        print("\n🎉 All tests passed! SQL Server connection is working.")
        print("The issue might be in the Django view or template.")
    else:
        print("\n❌ Tests failed! Check the error messages above.")
        print("Fix the connection issues before testing in Django.")
