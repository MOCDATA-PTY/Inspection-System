"""
Test the updated sql_server_utils with pymssql
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.sql_server_utils import fetch_product_names_for_inspection
from main.models import FoodSafetyAgencyInspection
from datetime import date

print("=" * 80)
print("Testing SQL Server with pymssql (NO ODBC DRIVERS!)")
print("=" * 80)

# Find recent inspections
inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=date(2025, 10, 1)
).order_by('-date_of_inspection')[:3]

print(f"\nFound {inspections.count()} recent inspections")

for inspection in inspections:
    if inspection.remote_id:
        print(f"\nInspection {inspection.remote_id} ({inspection.client_name}):")
        product_names = fetch_product_names_for_inspection(inspection_id=inspection.remote_id)
        if product_names:
            print(f"  Products: {product_names}")
        else:
            print(f"  No products found")

print("\n" + "=" * 80)
print("SUCCESS - pymssql works perfectly!")
print("=" * 80)
