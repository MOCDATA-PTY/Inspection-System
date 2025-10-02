#!/usr/bin/env python
"""
Check actual column names in SQL Server tables
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

def check_table_columns():
    """Check actual column names in SQL Server tables"""
    print("=" * 80)
    print("CHECKING SQL SERVER TABLE COLUMNS")
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
        
        # Tables to check
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
                # Get column information
                cursor.execute(f"""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = '{table_name}'
                    ORDER BY ORDINAL_POSITION
                """)
                columns = cursor.fetchall()
                
                if columns:
                    print("   Columns:")
                    for col in columns:
                        col_name, data_type, nullable = col
                        nullable_info = "NULL" if nullable == "YES" else "NOT NULL"
                        print(f"      • {col_name}: {data_type} {nullable_info}")
                else:
                    print("   ❌ Table not found or no columns")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    check_table_columns()
