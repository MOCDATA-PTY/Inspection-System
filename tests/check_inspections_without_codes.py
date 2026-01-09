import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, Client

def check_inspections_without_codes():
    """Check recent inspections without client account codes"""

    print("Checking recent inspections for clients without account codes...")
    print()

    # Get recent inspections (last 7 days)
    from datetime import datetime, timedelta
    recent_date = datetime.now() - timedelta(days=7)

    inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=recent_date
    ).order_by('-date_of_inspection')

    print(f"Found {inspections.count()} inspections in the last 7 days")
    print()

    # Check which ones have no account code
    print("=" * 130)
    print(f"{'Client Name':<50} {'Date':<12} {'Account Code':<25} {'Client ID':<10} {'Has Client?':<12}")
    print("=" * 130)

    no_code_count = 0
    has_code_count = 0

    for inspection in inspections:
        client_name = inspection.client_name or 'NULL'
        inspection_date = inspection.date_of_inspection.strftime('%d/%m/%Y') if inspection.date_of_inspection else 'NULL'
        account_code = inspection.internal_account_code or '-'

        # Try to find matching client by name
        try:
            client = Client.objects.filter(name=client_name).first()
            if client:
                client_code_in_db = client.internal_account_code or 'MISSING IN DB'
                client_db_id = str(client.id)
                has_client = 'YES'
            else:
                client_code_in_db = 'NO MATCH'
                client_db_id = 'NULL'
                has_client = 'NO'
        except Exception as e:
            client_code_in_db = 'ERROR'
            client_db_id = 'NULL'
            has_client = 'ERROR'

        if account_code == '-':
            no_code_count += 1
            print(f"{client_name:<50} {inspection_date:<12} {account_code:<25} {client_db_id:<10} {has_client:<12}")
            if client_code_in_db not in ['NO MATCH', 'ERROR', 'MISSING IN DB']:
                print(f"  -> Client DB has code: {client_code_in_db}")
        else:
            has_code_count += 1

    print("=" * 130)
    print()
    print("SUMMARY:")
    print(f"  Total inspections: {inspections.count()}")
    print(f"  With account codes: {has_code_count}")
    print(f"  WITHOUT account codes: {no_code_count}")

if __name__ == '__main__':
    check_inspections_without_codes()
