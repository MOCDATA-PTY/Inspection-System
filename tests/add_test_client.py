import os
import sys
import django
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import ClientAllocation
from django.db.models import Max

# Get next client ID
max_id = ClientAllocation.objects.aggregate(Max('client_id'))['client_id__max']
next_client_id = (max_id or 0) + 1

# Create test client
client = ClientAllocation.objects.create(
    client_id=next_client_id,
    eclick_name="Ethan Test",
    facility_type="Retailer",
    group_type="Individual / Independent Owner",
    commodity="Eggs",
    province="Gauteng",
    corporate_group="Other (Unlisted Group)",
    internal_account_code=f"RE-IND-EGG-NA-{str(next_client_id).zfill(4)}",
    representative_email="ethan@test.com",
    phone_number="0123456789"
)

print(f"Successfully created client:")
print(f"  Client ID: {client.client_id}")
print(f"  Name: {client.eclick_name}")
print(f"  Facility Type: {client.facility_type}")
print(f"  Corporate Group: {client.corporate_group}")
print(f"  Account Code: {client.internal_account_code}")
