import os
import sys
import django
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import ClientAllocation
from django.db.models import Max

# Simulate the auto-detection logic
def detect_corporate_group(client_name):
    if not client_name:
        return "Other (Unlisted Group)"

    name = client_name.lower().strip()

    rules = [
        (['pick n pay franchise', 'pnp franchise'], 'Pick n Pay - Franchise'),
        (['pick n pay corporate', 'pnp corporate'], 'Pick n Pay - Corporate'),
        (['pick n pay', 'pnp'], 'Pick n Pay - Corporate'),
        (['spar'], 'Spar'),
        (['shoprite'], 'Shoprite'),
        (['checkers'], 'Checkers'),
    ]

    for keywords, group in rules:
        for keyword in keywords:
            if keyword in name:
                return group

    return "Other (Unlisted Group)"

# Get next client ID
max_id = ClientAllocation.objects.aggregate(Max('client_id'))['client_id__max']
next_client_id = (max_id or 0) + 1

client_name = "Pick n Pay Test Store"
detected_group = detect_corporate_group(client_name)

# Create test client
client = ClientAllocation.objects.create(
    client_id=next_client_id,
    eclick_name=client_name,
    facility_type="Retailer",
    group_type="Corporate Store",
    commodity="Eggs",
    province="Gauteng",
    corporate_group=detected_group,
    internal_account_code=f"RE-COR-EGG-NA-{str(next_client_id).zfill(4)}",
    representative_email="test@picknpay.com",
    phone_number="0123456789"
)

print(f"Successfully created client:")
print(f"  Client ID: {client.client_id}")
print(f"  Name: {client.eclick_name}")
print(f"  Detected Corporate Group: {detected_group}")
print(f"  Facility Type: {client.facility_type}")
print(f"  Account Code: {client.internal_account_code}")
