#!/usr/bin/env python3
"""
Comprehensive SQL Server Connection Utility
Provides easy access to the AFS SQL Server database for the Legal System
"""

import pyodbc
import logging
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import os
import sys

# Add Django project to path if not already there
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLServerConnection:
    """
    Comprehensive SQL Server connection utility for the AFS database
    """
    
    def __init__(self):
        # SQL Server connection details
        self.server = '102.67.140.12'
        self.port = '1053'
        self.database = 'AFS'
        self.username = 'FSAUser2'
        self.password = 'password'
        self.driver = 'ODBC Driver 17 for SQL Server'
        self.connection = None
        
    def get_connection_string(self) -> str:
        """Get the connection string for SQL Server"""
        return (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=yes;"
        )
    
    def connect(self) -> bool:
        """Establish connection to SQL Server"""
        try:
            if self.connection:
                return True
                
            connection_string = self.get_connection_string()
            self.connection = pyodbc.connect(connection_string, timeout=30)
            logger.info("Successfully connected to SQL Server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQL Server: {e}")
            return False
    
    def disconnect(self):
        """Close SQL Server connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from SQL Server")
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        if not self.connection:
            if not self.connect():
                raise Exception("Failed to connect to SQL Server")
        
        cursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results as list of dictionaries
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
            
        Returns:
            List of dictionaries representing the query results
        """
        try:
            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Get column names
                columns = [column[0] for column in cursor.description]
                
                # Fetch all results and convert to list of dictionaries
                results = []
                for row in cursor.fetchall():
                    row_dict = dict(zip(columns, row))
                    results.append(row_dict)
                
                return results
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def get_inspection_tables(self) -> List[str]:
        """Get list of inspection-related tables"""
        query = """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            AND (TABLE_NAME LIKE '%Inspection%' OR TABLE_NAME LIKE '%PMP%' OR 
                 TABLE_NAME LIKE '%Poultry%' OR TABLE_NAME LIKE '%Raw%' OR 
                 TABLE_NAME LIKE '%RMP%')
            ORDER BY TABLE_NAME
        """
        results = self.execute_query(query)
        return [row['TABLE_NAME'] for row in results]
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a specific table"""
        query = """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """
        return self.execute_query(query, (table_name,))
    
    def get_table_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample data from a table"""
        query = f"SELECT TOP {limit} * FROM {table_name}"
        return self.execute_query(query)
    
    def get_table_row_count(self, table_name: str) -> int:
        """Get row count for a table"""
        query = f"SELECT COUNT(*) as row_count FROM {table_name}"
        results = self.execute_query(query)
        return results[0]['row_count'] if results else 0
    
    def search_tables_by_column(self, column_pattern: str) -> List[Dict[str, Any]]:
        """Search for tables containing columns matching a pattern"""
        query = """
            SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE COLUMN_NAME LIKE ?
            ORDER BY TABLE_NAME, COLUMN_NAME
        """
        return self.execute_query(query, (f"%{column_pattern}%",))
    
    def get_inspection_data(self, inspection_id: Optional[int] = None, 
                          client_name: Optional[str] = None,
                          date_from: Optional[str] = None,
                          date_to: Optional[str] = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get inspection data with optional filters
        
        Args:
            inspection_id: Specific inspection ID
            client_name: Client name filter
            date_from: Start date filter (YYYY-MM-DD)
            date_to: End date filter (YYYY-MM-DD)
            limit: Maximum number of results
            
        Returns:
            List of inspection records
        """
        # This is a simplified query - you may need to adjust based on actual table structure
        query = f"""
            SELECT TOP {limit} *
            FROM InspectionRecords
            WHERE 1=1
        """
        params = []
        
        if inspection_id:
            query += " AND Id = ?"
            params.append(inspection_id)
        
        if client_name:
            query += " AND ClientName LIKE ?"
            params.append(f"%{client_name}%")
        
        if date_from:
            query += " AND CAST(DateOfInspection AS DATE) >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND CAST(DateOfInspection AS DATE) <= ?"
            params.append(date_to)
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_product_names_by_inspection(self, inspection_id: int) -> List[str]:
        """
        Get product names for a specific inspection ID
        This searches across multiple tables that might contain product information
        """
        product_names = []
        
        # Search in PMP tables
        pmp_query = """
            SELECT PMPItemDetails
            FROM PMPInspectedProductRecordTypes 
            WHERE InspectionId = ? AND PMPItemDetails IS NOT NULL AND PMPItemDetails != ''
        """
        pmp_results = self.execute_query(pmp_query, (inspection_id,))
        for row in pmp_results:
            if row['PMPItemDetails'] and row['PMPItemDetails'].strip():
                product_names.append(row['PMPItemDetails'].strip())
        
        # Search in Poultry tables
        poultry_tables = [
            'PoultryGradingInspectionRecordTypes',
            'PoultryLabelInspectionChecklistRecords',
            'PoultryQuidInspectionRecordTypes',
            'PoultryInspectionRecordTypes'
        ]
        
        for table in poultry_tables:
            try:
                query = f"""
                    SELECT ProductName
                    FROM {table}
                    WHERE Id = ? AND ProductName IS NOT NULL AND ProductName != ''
                """
                results = self.execute_query(query, (inspection_id,))
                for row in results:
                    if row['ProductName'] and row['ProductName'].strip():
                        product_names.append(row['ProductName'].strip())
            except Exception as e:
                logger.debug(f"Query failed for table {table}: {e}")
                continue
        
        # Search in Raw RMP tables
        raw_rmp_query = """
            SELECT NewProductItemDetails
            FROM RawRMPInspectedProductRecordTypes 
            WHERE InspectionId = ? AND NewProductItemDetails IS NOT NULL AND NewProductItemDetails != ''
        """
        raw_rmp_results = self.execute_query(raw_rmp_query, (inspection_id,))
        for row in raw_rmp_results:
            if row['NewProductItemDetails'] and row['NewProductItemDetails'].strip():
                product_names.append(row['NewProductItemDetails'].strip())
        
        # Remove duplicates and empty strings
        return list(set([name for name in product_names if name]))
    
    def test_connection(self) -> bool:
        """Test the SQL Server connection"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        try:
            with self.get_cursor() as cursor:
                # Get SQL Server version
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]
                
                # Get current database
                cursor.execute("SELECT DB_NAME()")
                current_db = cursor.fetchone()[0]
                
                # Get database size
                cursor.execute("""
                    SELECT 
                        DB_NAME() as database_name,
                        CAST(SUM(CAST(FILEPROPERTY(name, 'SpaceUsed') AS bigint) * 8.0 / 1024) AS DECIMAL(15,2)) AS used_space_mb,
                        CAST(SUM(CAST(size AS bigint) * 8.0 / 1024) AS DECIMAL(15,2)) AS total_space_mb
                    FROM sys.database_files
                """)
                size_info = cursor.fetchone()
                
                return {
                    'version': version,
                    'current_database': current_db,
                    'used_space_mb': size_info[1] if size_info else 0,
                    'total_space_mb': size_info[2] if size_info else 0
                }
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {}

def main():
    """Main function for testing the SQL Server connection"""
    print("🚀 SQL Server Connection Utility")
    print("=" * 50)
    
    # Create connection instance
    sql_conn = SQLServerConnection()
    
    try:
        # Test connection
        print("🔌 Testing connection...")
        if not sql_conn.test_connection():
            print("❌ Connection test failed!")
            return False
        
        print("✅ Connection successful!")
        
        # Get database info
        print("\n📊 Database Information:")
        db_info = sql_conn.get_database_info()
        if db_info:
            print(f"   Database: {db_info.get('current_database', 'Unknown')}")
            print(f"   Used Space: {db_info.get('used_space_mb', 0):.2f} MB")
            print(f"   Total Space: {db_info.get('total_space_mb', 0):.2f} MB")
        
        # Get inspection tables
        print("\n🔍 Inspection Tables:")
        inspection_tables = sql_conn.get_inspection_tables()
        for table in inspection_tables[:10]:  # Show first 10
            row_count = sql_conn.get_table_row_count(table)
            print(f"   • {table} ({row_count:,} rows)")
        
        if len(inspection_tables) > 10:
            print(f"   ... and {len(inspection_tables) - 10} more tables")
        
        print(f"\n✅ Found {len(inspection_tables)} inspection-related tables")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        sql_conn.disconnect()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
