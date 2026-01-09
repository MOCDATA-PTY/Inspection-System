#!/usr/bin/env python
"""
Debug script to check actual data in SQL Server tables
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

def debug_sql_server_data():
    """Debug actual data in SQL Server tables"""
    print("=" * 80)
    print("DEBUGGING SQL SERVER DATA")
    print("=" * 80)
    
    # Get SQL Server connection details
    sql_server_config = settings.DATABASES.get('sql_server', {})
    
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
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if tables exist and have data
        tables_to_check = [
            'PMPInspectedProductRecordTypes',
            'PoultryGradingInspectionRecordTypes', 
            'PoultryLabelInspectionChecklistRecords',
            'PoultryQuidInspectionRecordTypes',
            'RawRMPInspectedProductRecordTypes'
        ]
        
        for table_name in tables_to_check:
            print(f"\n📋 Table: {table_name}")
            print("-" * 50)
            
            try:
                # Check if table exists and get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                print(f"   Total rows: {row_count}")
                
                if row_count > 0:
                    # Get sample data
                    cursor.execute(f"SELECT TOP 3 * FROM {table_name}")
                    sample_data = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute(f"""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = '{table_name}'
                        ORDER BY ORDINAL_POSITION
                    """)
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    print(f"   Columns: {', '.join(columns)}")
                    print(f"   Sample data (first 3 rows):")
                    
                    for i, row in enumerate(sample_data, 1):
                        print(f"      Row {i}: {dict(zip(columns, row))}")
                        
                        # Look for product-related fields
                        for col, val in zip(columns, row):
                            if val and ('product' in col.lower() or 'item' in col.lower() or 'name' in col.lower()):
                                print(f"         🎯 Found product data: {col} = {val}")
                else:
                    print("   ❌ No data in table")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Check for any tables with product-related data
        print(f"\n🔍 SEARCHING FOR PRODUCT DATA ACROSS ALL TABLES")
        print("-" * 50)
        
        try:
            cursor.execute("""
                SELECT TABLE_NAME, COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE COLUMN_NAME LIKE '%product%' 
                   OR COLUMN_NAME LIKE '%item%' 
                   OR COLUMN_NAME LIKE '%name%'
                ORDER BY TABLE_NAME, COLUMN_NAME
            """)
            product_columns = cursor.fetchall()
            
            if product_columns:
                print("   Found product-related columns:")
                for table, column in product_columns:
                    print(f"      • {table}.{column}")
            else:
                print("   ❌ No product-related columns found")
                
        except Exception as e:
            print(f"   ❌ Error searching for product columns: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    debug_sql_server_data()
