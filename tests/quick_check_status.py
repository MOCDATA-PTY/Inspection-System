import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

# Check the specific inspection from the console log
client = "Marang Layers Farming Enterprises t/a Maranga Eggs"
date_str = "2025-11-19"

inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name=client,
    date_of_inspection=date_str
)

print("\nCurrent status in database:")
print("="*60)
for insp in inspections:
    print(f"ID {insp.id}: approved_status = '{insp.approved_status}'")
    print(f"  Client: {insp.client_name}")
    print(f"  Date: {insp.date_of_inspection}")
    print(f"  Inspector: {insp.inspector_name}")
    print()

print(f"Total inspections found: {inspections.count()}")
