"""Check for orphaned inspections 65931, 65932, 65933"""
import sys
import os
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

for insp_id in [65931, 65932, 65933]:
    insp = FoodSafetyAgencyInspection.objects.filter(remote_id=insp_id).first()
    if insp:
        print(f'\nInspection {insp_id}:')
        print(f'  Client: {insp.client_name}')
        print(f'  Commodity: {insp.commodity}')
        print(f'  Product: {insp.product_name}')
        print(f'  Date: {insp.date_of_inspection}')
        print(f'  Created: {insp.created_at}')
        print(f'  Updated: {insp.updated_at}')
    else:
        print(f'\nInspection {insp_id}: Not found in local database')
