"""
Test SQL Server connection using Django's connection pool
NO ODBC DRIVERS NEEDED!
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# Import after Django setup
from main.utils.sql_server_utils import fetch_product_names_for_inspection
from main.models import FoodSafetyAgencyInspection
from datetime import date

print("=" * 80)
print("Testing SQL Server Connection using Django (NO ODBC DRIVERS!)")
print("=" * 80)

# Find a recent inspection
inspections = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=date(2025, 10, 1)
).order_by('-date_of_inspection')[:3]

print(f"\nFound {inspections.count()} recent inspections to test")

for inspection in inspections:
    if inspection.remote_id:
        print(f"\nInspection {inspection.remote_id} ({inspection.client_name}):")
        product_names = fetch_product_names_for_inspection(inspection_id=inspection.remote_id)
        print(f"  Products: {product_names}")

print("\n" + "=" * 80)
print("✅ Test complete - Django connection works WITHOUT ODBC drivers!")
print("=" * 80)
