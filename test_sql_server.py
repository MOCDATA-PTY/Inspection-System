#!/usr/bin/env python
"""
Test script to explore SQL Server database and find product names
"""

import os
import sys
import django
import pyodbc

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def test_sql_server_connection():
    """Test connection to SQL Server and explore databases and tables"""
    print("=" * 80)
    print("SQL SERVER DATABASE EXPLORATION")
    print("=" * 80)
    
    # Get SQL Server connection details from Django settings
    sql_server_config = settings.DATABASES.get('sql_server', {})
    
    if not sql_server_config:
        print("❌ No SQL Server configuration found in Django settings")
        return
    
    print(f"🔍 SQL Server Config:")
    print(f"   Host: {sql_server_config.get('HOST', 'N/A')}")
    print(f"   Database: {sql_server_config.get('NAME', 'N/A')}")
    print(f"   User: {sql_server_config.get('USER', 'N/A')}")
    print(f"   Port: {sql_server_config.get('PORT', 'N/A')}")
    print()
    
    try:
        # Build connection string
        connection_string = (
            f"DRIVER={{{sql_server_config.get('OPTIONS', {}).get('driver', 'ODBC Driver 17 for SQL Server')}}};"
            f"SERVER={sql_server_config.get('HOST')},{sql_server_config.get('PORT')};"
            f"DATABASE={sql_server_config.get('NAME')};"
            f"UID={sql_server_config.get('USER')};"
            f"PWD={sql_server_config.get('PASSWORD')};"
            f"Trusted_Connection=no;"
        )
        
        print("🔌 Attempting to connect to SQL Server...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        print("✅ Successfully connected to SQL Server!")
        print()
        
        # Get all databases
        print("📊 AVAILABLE DATABASES:")
        print("-" * 40)
        cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")  # Exclude system databases
        databases = cursor.fetchall()
        for db in databases:
            print(f"   • {db[0]}")
        print()
        
        # Get all tables in the current database
        current_db = sql_server_config.get('NAME')
        print(f"📋 TABLES IN DATABASE '{current_db}':")
        print("-" * 40)
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"   • {table_name}")
        print()
        
        # Look for tables that might contain product names
        print("🔍 SEARCHING FOR PRODUCT-RELATED TABLES:")
        print("-" * 40)
        product_related_tables = []
        
        for table in tables:
            table_name = table[0].lower()
            if any(keyword in table_name for keyword in ['product', 'item', 'inspection', 'sample', 'food', 'commodity']):
                product_related_tables.append(table[0])
                print(f"   🎯 {table[0]} (contains product-related keywords)")
        
        print()
        
        # Examine each product-related table
        for table_name in product_related_tables:
            print(f"📝 EXAMINING TABLE: {table_name}")
            print("-" * 50)
            
            try:
                # Get column information
                cursor.execute(f"""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = '{table_name}'
                    ORDER BY ORDINAL_POSITION
                """)
                columns = cursor.fetchall()
                
                print("   Columns:")
                for col in columns:
                    col_name, data_type, nullable, max_length = col
                    length_info = f"({max_length})" if max_length else ""
                    nullable_info = "NULL" if nullable == "YES" else "NOT NULL"
                    print(f"      • {col_name}: {data_type}{length_info} {nullable_info}")
                
                # Look for product name columns
                product_name_columns = []
                for col in columns:
                    col_name = col[0].lower()
                    if any(keyword in col_name for keyword in ['product', 'name', 'item', 'description', 'title']):
                        product_name_columns.append(col[0])
                
                if product_name_columns:
                    print(f"   🎯 Product name columns found: {', '.join(product_name_columns)}")
                    
                    # Get sample data for product name columns
                    for col_name in product_name_columns:
                        try:
                            cursor.execute(f"SELECT TOP 5 {col_name} FROM {table_name} WHERE {col_name} IS NOT NULL AND {col_name} != ''")
                            sample_data = cursor.fetchall()
                            if sample_data:
                                print(f"      Sample {col_name} values:")
                                for row in sample_data:
                                    print(f"         • {row[0]}")
                        except Exception as e:
                            print(f"      ❌ Error getting sample data for {col_name}: {e}")
                else:
                    print("   ℹ️  No obvious product name columns found")
                
                # Get row count
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    print(f"   📊 Total rows: {row_count}")
                except Exception as e:
                    print(f"   ❌ Error getting row count: {e}")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error examining table {table_name}: {e}")
                print()
        
        # Look for tables with inspection-related data
        print("🔍 SEARCHING FOR INSPECTION DATA:")
        print("-" * 40)
        
        for table in tables:
            table_name = table[0]
            try:
                # Check if table has inspection-related columns
                cursor.execute(f"""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = '{table_name}'
                    AND (COLUMN_NAME LIKE '%inspection%' OR COLUMN_NAME LIKE '%sample%' OR COLUMN_NAME LIKE '%product%')
                """)
                inspection_columns = cursor.fetchall()
                
                if inspection_columns:
                    print(f"   🎯 {table_name} has inspection-related columns:")
                    for col in inspection_columns:
                        print(f"      • {col[0]}")
                    
                    # Get sample data
                    try:
                        cursor.execute(f"SELECT TOP 3 * FROM {table_name}")
                        sample_rows = cursor.fetchall()
                        if sample_rows:
                            print(f"      Sample data (first 3 rows):")
                            for i, row in enumerate(sample_rows, 1):
                                print(f"         Row {i}: {row}")
                    except Exception as e:
                        print(f"      ❌ Error getting sample data: {e}")
                    print()
                    
            except Exception as e:
                continue
        
        conn.close()
        print("✅ SQL Server exploration completed!")
        
    except Exception as e:
        print(f"❌ Error connecting to SQL Server: {e}")
        print("Make sure the SQL Server is running and accessible.")

def test_django_sql_server():
    """Test Django's SQL Server connection"""
    print("\n" + "=" * 80)
    print("DJANGO SQL SERVER CONNECTION TEST")
    print("=" * 80)
    
    try:
        from django.db import connections
        
        # Test SQL Server connection
        sql_server_conn = connections['sql_server']
        with sql_server_conn.cursor() as cursor:
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print(f"✅ Django SQL Server connection successful!")
            print(f"   SQL Server version: {version[:100]}...")
            
            # Get current database name
            cursor.execute("SELECT DB_NAME()")
            current_db = cursor.fetchone()[0]
            print(f"   Current database: {current_db}")
            
    except Exception as e:
        print(f"❌ Django SQL Server connection failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting SQL Server database exploration...")
    test_sql_server_connection()
    test_django_sql_server()
    print("\n🏁 Exploration completed!")
