#!/usr/bin/env python3
"""
Test script to connect to the SQL Server database using the same credentials
that would be used in Power BI. This will help diagnose connection issues.
"""

import pyodbc
import sys
from datetime import datetime

def test_sql_connection():
    """Test SQL Server connection with the exact credentials from the image."""
    
    print("=" * 60)
    print("🔍 SQL SERVER CONNECTION TEST")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Connection details from your configuration
    server = "102.67.140.12"
    port = "1053"
    database = "NAHDIS_FSA"
    username = "FSAUser2"
    password = "password"
    
    print("📋 Connection Details:")
    print(f"   Server: {server}")
    print(f"   Port: {port}")
    print(f"   Database: {database}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    print()
    
    # Test 1: Check if pyodbc is available
    print("🔧 Step 1: Checking pyodbc installation...")
    try:
        import pyodbc
        print("   ✅ pyodbc is installed")
        print(f"   📦 Version: {pyodbc.version}")
    except ImportError as e:
        print(f"   ❌ pyodbc not installed: {e}")
        print("   💡 Install with: pip install pyodbc")
        return False
    
    # Test 2: Check available ODBC drivers
    print("\n🔧 Step 2: Checking available ODBC drivers...")
    try:
        drivers = pyodbc.drivers()
        print(f"   📋 Found {len(drivers)} ODBC drivers:")
        for driver in drivers:
            if 'SQL Server' in driver:
                print(f"      ✅ {driver}")
            else:
                print(f"      📄 {driver}")
        
        # Check for the specific driver we need
        sql_drivers = [d for d in drivers if 'ODBC Driver 17 for SQL Server' in d]
        if sql_drivers:
            print(f"   ✅ Found required driver: {sql_drivers[0]}")
            driver_name = sql_drivers[0]
        else:
            print("   ⚠️  ODBC Driver 17 for SQL Server not found")
            print("   💡 Try installing: https://go.microsoft.com/fwlink/?linkid=2239166")
            # Try alternative driver names
            alt_drivers = [d for d in drivers if 'SQL Server' in d]
            if alt_drivers:
                driver_name = alt_drivers[0]
                print(f"   🔄 Using alternative driver: {driver_name}")
            else:
                print("   ❌ No SQL Server drivers found")
                return False
    except Exception as e:
        print(f"   ❌ Error checking drivers: {e}")
        return False
    
    # Test 3: Test connection string
    print("\n🔧 Step 3: Testing connection string...")
    
    # Try different connection string formats
    connection_strings = [
        # Format 1: With port in server
        f"DRIVER={{{driver_name}}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Encrypt=yes;",
        
        # Format 2: With port as separate parameter
        f"DRIVER={{{driver_name}}};SERVER={server};PORT={port};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Encrypt=yes;",
        
        # Format 3: Without encryption (in case server doesn't support it)
        f"DRIVER={{{driver_name}}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;",
        
        # Format 4: Basic connection
        f"DRIVER={{{driver_name}}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password};"
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"\n   🧪 Trying connection string format {i}...")
        print(f"   📝 String: {conn_str[:80]}...")
        
        try:
            # Test connection
            connection = pyodbc.connect(conn_str, timeout=10)
            print("   ✅ Connection successful!")
            
            # Test query
            print("   🔍 Testing query execution...")
            cursor = connection.cursor()
            cursor.execute("SELECT @@VERSION as version")
            version = cursor.fetchone()[0]
            print(f"   📊 SQL Server version: {version[:50]}...")
            
            # Test database access
            print("   🔍 Testing database access...")
            cursor.execute("SELECT DB_NAME() as current_database")
            current_db = cursor.fetchone()[0]
            print(f"   📊 Current database: {current_db}")
            
            # List some tables
            print("   🔍 Listing available tables...")
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE' 
                ORDER BY TABLE_NAME
            """)
            tables = cursor.fetchall()
            print(f"   📊 Found {len(tables)} tables:")
            for table in tables[:10]:  # Show first 10 tables
                print(f"      📄 {table[0]}")
            if len(tables) > 10:
                print(f"      ... and {len(tables) - 10} more tables")
            
            # Close connection
            cursor.close()
            connection.close()
            print("   ✅ Connection test completed successfully!")
            
            print("\n" + "=" * 60)
            print("🎉 SUCCESS! Your SQL Server is accessible!")
            print("=" * 60)
            print("💡 Power BI should be able to connect using these settings:")
            print(f"   Server: {server},{port}")
            print(f"   Database: {database}")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print("=" * 60)
            return True
            
        except pyodbc.Error as e:
            print(f"   ❌ Connection failed: {e}")
            print(f"   🔍 Error details: {e.args}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("❌ CONNECTION FAILED")
    print("=" * 60)
    print("🔍 Possible issues:")
    print("   1. Server is not accessible from your network")
    print("   2. Firewall blocking port 1053")
    print("   3. SQL Server not running or configured properly")
    print("   4. Wrong credentials")
    print("   5. ODBC Driver not installed correctly")
    print("\n💡 Next steps:")
    print("   1. Check if you can ping the server: ping 102.67.140.12")
    print("   2. Test port connectivity: telnet 102.67.140.12 1053")
    print("   3. Verify credentials with database administrator")
    print("   4. Try connecting from SQL Server Management Studio")
    print("=" * 60)
    return False

if __name__ == "__main__":
    print("🚀 Starting SQL Server connection test...")
    print("This will test the same connection that Power BI would use.")
    print()
    
    try:
        success = test_sql_connection()
        if success:
            print("\n✅ Test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Test failed - see details above")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


