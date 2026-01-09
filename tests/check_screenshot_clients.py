import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, Client
from datetime import datetime

def check_specific_clients():
    """Check specific clients from the screenshot"""

    clients_to_check = [
        "Checkers Dada Complex Lichtenburg",
        "Grootboom Slaghuis",
        "Kwa Nyama Butchery",
        "Kwa nyama Butchery",
        "Superspar Mini Market",
        "Enkomeni Butchery",
        "Frank's Meat at Mall/N4",
        "Jwayelani Warwick",
        "Lester's Meat East London",
        "New Egg Producer",
        "New Retailer"
    ]

    print("Checking specific clients from screenshot...")
    print()
    print("=" * 140)
    print(f"{'Client Name':<50} {'Has Inspection?':<18} {'Inspection Code':<25} {'Client DB Code':<25} {'Match?':<12}")
    print("=" * 140)

    for client_name in clients_to_check:
        # Check if client exists in Client table
        client = Client.objects.filter(name__iexact=client_name).first()
        client_code = client.internal_account_code if client else None

        # Check recent inspections for this client
        inspection = FoodSafetyAgencyInspection.objects.filter(
            client_name__iexact=client_name
        ).order_by('-date_of_inspection').first()

        if inspection:
            has_inspection = "YES"
            inspection_code = inspection.internal_account_code or "NULL/EMPTY"
        else:
            has_inspection = "NO"
            inspection_code = "NO INSPECTION"

        if client:
            client_db_code = client_code or "NULL/EMPTY"
        else:
            client_db_code = "NO CLIENT IN DB"

        # Check if they match
        if inspection and client:
            if inspection.internal_account_code == client.internal_account_code:
                match = "YES"
            else:
                match = "NO - MISMATCH"
        else:
            match = "N/A"

        print(f"{client_name:<50} {has_inspection:<18} {inspection_code:<25} {client_db_code:<25} {match:<12}")

    print("=" * 140)

if __name__ == '__main__':
    check_specific_clients()
