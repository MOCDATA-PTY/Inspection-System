import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

# Check for inspections with the specific account code
inspections = FoodSafetyAgencyInspection.objects.filter(account_code='FA-IND-EGG-NA-0014')
print(f"Found {inspections.count()} inspections with account code FA-IND-EGG-NA-0014")

if inspections.exists():
    print("\nInspections found:")
    for i in inspections:
        print(f"ID: {i.remote_id}, Client: {i.client_name}, Date: {i.date_of_inspection}, Commodity: {i.commodity}, Account: {i.account_code}")
else:
    print("No inspections found with that account code")
    
    # Check for any inspections with EGG in account code
    egg_inspections = FoodSafetyAgencyInspection.objects.filter(account_code__icontains='EGG')
    print(f"\nFound {egg_inspections.count()} inspections with 'EGG' in account code")
    for i in egg_inspections[:10]:  # Show first 10
        print(f"ID: {i.remote_id}, Client: {i.client_name}, Date: {i.date_of_inspection}, Commodity: {i.commodity}, Account: {i.account_code}")
