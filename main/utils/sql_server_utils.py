"""
SQL Server utilities for fetching product names and other data
"""

import pyodbc
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SQLServerConnection:
    """Utility class for connecting to SQL Server and fetching data"""
    
    def __init__(self):
        self.sql_server_config = settings.DATABASES.get('sql_server', {})
        self.connection = None
    
    def connect(self):
        """Establish connection to SQL Server"""
        try:
            connection_string = (
                f"DRIVER={{{self.sql_server_config.get('OPTIONS', {}).get('driver', 'ODBC Driver 17 for SQL Server')}}};"
                f"SERVER={self.sql_server_config.get('HOST')},{self.sql_server_config.get('PORT')};"
                f"DATABASE={self.sql_server_config.get('NAME')};"
                f"UID={self.sql_server_config.get('USER')};"
                f"PWD={self.sql_server_config.get('PASSWORD')};"
                f"Trusted_Connection=no;"
            )
            
            self.connection = pyodbc.connect(connection_string)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQL Server: {e}")
            return False
    
    def disconnect(self):
        """Close SQL Server connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_product_names_by_inspection_id(self, inspection_id):
        """
        Fetch product names for a specific inspection ID from SQL Server
        Returns a list of product names found in various tables
        """
        if not self.connection:
            if not self.connect():
                return []
        
        product_names = []
        
        try:
            cursor = self.connection.cursor()
            
            # Query PMP (Processed Meat Products) table - only get actual product names
            pmp_query = """
                SELECT PMPItemDetails
                FROM PMPInspectedProductRecordTypes 
                WHERE InspectionId = ? AND PMPItemDetails IS NOT NULL AND PMPItemDetails != ''
            """
            cursor.execute(pmp_query, (inspection_id,))
            pmp_results = cursor.fetchall()
            
            for row in pmp_results:
                if row[0] and row[0].strip():  # Only PMPItemDetails (actual product name)
                    product_names.append(row[0].strip())
            
            # Query Poultry tables - only get actual product names
            poultry_queries = [
                "SELECT ProductName FROM PoultryGradingInspectionRecordTypes WHERE Id = ? AND ProductName IS NOT NULL AND ProductName != ''",
                "SELECT ProductName FROM PoultryLabelInspectionChecklistRecords WHERE Id = ? AND ProductName IS NOT NULL AND ProductName != ''",
                "SELECT ProductName FROM PoultryQuidInspectionRecordTypes WHERE Id = ? AND ProductName IS NOT NULL AND ProductName != ''",
                "SELECT ProductName FROM PoultryInspectionRecordTypes WHERE Id = ? AND ProductName IS NOT NULL AND ProductName != ''"
            ]
            
            for query in poultry_queries:
                try:
                    cursor.execute(query, (inspection_id,))
                    results = cursor.fetchall()
                    for row in results:
                        if row[0] and row[0].strip():
                            product_names.append(row[0].strip())
                except Exception as e:
                    # Table might not exist or have different structure
                    logger.debug(f"Query failed (expected): {e}")
                    continue
            
            # Query Raw RMP table - only get actual product names
            raw_rmp_query = """
                SELECT NewProductItemDetails
                FROM RawRMPInspectedProductRecordTypes 
                WHERE InspectionId = ? AND NewProductItemDetails IS NOT NULL AND NewProductItemDetails != ''
            """
            cursor.execute(raw_rmp_query, (inspection_id,))
            raw_rmp_results = cursor.fetchall()
            
            for row in raw_rmp_results:
                if row[0] and row[0].strip():  # Only NewProductItemDetails (actual product name)
                    product_names.append(row[0].strip())
            
            # Remove duplicates and empty strings
            product_names = list(set([name.strip() for name in product_names if name and name.strip()]))
            
            logger.info(f"Found {len(product_names)} product names for inspection {inspection_id}: {product_names}")
            return product_names
            
        except Exception as e:
            logger.error(f"Error fetching product names for inspection {inspection_id}: {e}")
            return []
    
    def get_product_names_by_client_and_date(self, client_name, inspection_date):
        """
        Fetch product names for a client on a specific date
        This is useful when we have client name and date but not specific inspection ID
        """
        if not self.connection:
            if not self.connect():
                return []
        
        product_names = []
        
        try:
            cursor = self.connection.cursor()
            
            # Query PMP table by client and date - only get actual product names
            pmp_query = """
                SELECT p.PMPItemDetails
                FROM PMPInspectedProductRecordTypes p
                INNER JOIN PMPInspectionRecordTypes i ON p.InspectionId = i.Id
                WHERE i.ClientName = ? AND CAST(i.DateOfInspection AS DATE) = ? 
                AND p.PMPItemDetails IS NOT NULL AND p.PMPItemDetails != ''
            """
            cursor.execute(pmp_query, (client_name, inspection_date))
            pmp_results = cursor.fetchall()
            
            for row in pmp_results:
                if row[0] and row[0].strip():  # Only PMPItemDetails (actual product name)
                    product_names.append(row[0].strip())
            
            # Query Poultry tables by client and date - only get actual product names
            poultry_queries = [
                """
                SELECT ProductName FROM PoultryGradingInspectionRecordTypes 
                WHERE ClientName = ? AND CAST(DateOfInspection AS DATE) = ?
                AND ProductName IS NOT NULL AND ProductName != ''
                """,
                """
                SELECT ProductName FROM PoultryLabelInspectionChecklistRecords 
                WHERE ClientName = ? AND CAST(DateOfInspection AS DATE) = ?
                AND ProductName IS NOT NULL AND ProductName != ''
                """,
                """
                SELECT ProductName FROM PoultryQuidInspectionRecordTypes 
                WHERE ClientName = ? AND CAST(DateOfInspection AS DATE) = ?
                AND ProductName IS NOT NULL AND ProductName != ''
                """
            ]
            
            for query in poultry_queries:
                try:
                    cursor.execute(query, (client_name, inspection_date))
                    results = cursor.fetchall()
                    for row in results:
                        if row[0] and row[0].strip():
                            product_names.append(row[0].strip())
                except Exception as e:
                    logger.debug(f"Poultry query failed (expected): {e}")
                    continue
            
            # Query Raw RMP table by client and date - only get actual product names
            raw_rmp_query = """
                SELECT p.NewProductItemDetails
                FROM RawRMPInspectedProductRecordTypes p
                INNER JOIN RawRMPInspectionRecordTypes i ON p.InspectionId = i.Id
                WHERE i.ClientName = ? AND CAST(i.DateOfInspection AS DATE) = ?
                AND p.NewProductItemDetails IS NOT NULL AND p.NewProductItemDetails != ''
            """
            cursor.execute(raw_rmp_query, (client_name, inspection_date))
            raw_rmp_results = cursor.fetchall()
            
            for row in raw_rmp_results:
                if row[0] and row[0].strip():  # Only NewProductItemDetails (actual product name)
                    product_names.append(row[0].strip())
            
            # Remove duplicates and empty strings
            product_names = list(set([name.strip() for name in product_names if name and name.strip()]))
            
            logger.info(f"Found {len(product_names)} product names for {client_name} on {inspection_date}: {product_names}")
            return product_names
            
        except Exception as e:
            logger.error(f"Error fetching product names for {client_name} on {inspection_date}: {e}")
            return []

def fetch_product_names_for_inspection(inspection_id=None, client_name=None, inspection_date=None):
    """
    Main function to fetch product names from SQL Server
    Can be called with either inspection_id or client_name + inspection_date
    """
    sql_conn = SQLServerConnection()
    
    try:
        if inspection_id:
            return sql_conn.get_product_names_by_inspection_id(inspection_id)
        elif client_name and inspection_date:
            return sql_conn.get_product_names_by_client_and_date(client_name, inspection_date)
        else:
            logger.error("Either inspection_id or (client_name + inspection_date) must be provided")
            return []
    finally:
        sql_conn.disconnect()
