import os
import sys
import django
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 100)
print("BLOU BUL MEAT MARKET - INSPECTIONS ON 02/12/2025")
print("=" * 100)

blou = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains='Blou Bul',
    date_of_inspection=datetime(2025, 12, 2).date()
).order_by('commodity', 'product_name')

print(f"\nFound {blou.count()} total inspections:\n")

raw = [i for i in blou if i.commodity == 'RAW']
pmp = [i for i in blou if i.commodity == 'PMP']

print(f"RAW Inspections ({len(raw)}):")
for idx, insp in enumerate(raw, 1):
    print(f"  {idx}. Product: '{insp.product_name}' | Hours: {insp.hours} | KM: {insp.km_traveled} | Fat: {insp.fat} | Protein: {insp.protein}")

print(f"\nPMP Inspections ({len(pmp)}):")
for idx, insp in enumerate(pmp, 1):
    print(f"  {idx}. Product: '{insp.product_name}' | Hours: {insp.hours} | KM: {insp.km_traveled} | Fat: {insp.fat} | Protein: {insp.protein}")

print("\n" + "=" * 100)
print("\nCURRENT EXPORT LOGIC:")
print("Each product generates its own set of line items (050, 051, 052, 053)")
print(f"So {len(raw)} RAW products = {len(raw)} × RAW 050 + {len(raw)} × RAW 051 + lab items")
print(f"And {len(pmp)} PMP products = {len(pmp)} × PMP 060 + {len(pmp)} × PMP 061 + lab items")
print("\n" + "=" * 100)
print("\nYOUR WORKING SYSTEM:")
print("Shows only ONE of each item code per client/date")
print("Question: Should all products at same client/date be AGGREGATED into single line items?")
print("=" * 100)
