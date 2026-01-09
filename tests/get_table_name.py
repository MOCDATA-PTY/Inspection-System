import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db import connection

# Get the actual table name from Django
table_name = FoodSafetyAgencyInspection._meta.db_table
print(f"Django model table name: {table_name}")

# List all tables in the database
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT tablename
        FROM pg_catalog.pg_tables
        WHERE schemaname = 'public'
        AND tablename LIKE '%inspection%'
        ORDER BY tablename
    """)
    tables = cursor.fetchall()
    print("\nTables with 'inspection' in name:")
    for table in tables:
        print(f"  - {table[0]}")
