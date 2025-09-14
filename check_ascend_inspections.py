import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

# Check for Ascend inspections
inspections = FoodSafetyAgencyInspection.objects.filter(client_name__icontains='Ascend')
print(f"Found {inspections.count()} inspections for Ascend")

if inspections.exists():
    print("\nInspections found:")
    for i in inspections:
        print(f"ID: {i.remote_id}, Client: {i.client_name}, Date: {i.date_of_inspection}, Commodity: {i.commodity}, Account: {i.account_code}")
else:
    print("No Ascend inspections found")
    
    # Check for Xing Xing
    xing_inspections = FoodSafetyAgencyInspection.objects.filter(client_name__icontains='Xing')
    print(f"\nFound {xing_inspections.count()} inspections with 'Xing' in name")
    for i in xing_inspections:
        print(f"ID: {i.remote_id}, Client: {i.client_name}, Date: {i.date_of_inspection}, Commodity: {i.commodity}, Account: {i.account_code}")
