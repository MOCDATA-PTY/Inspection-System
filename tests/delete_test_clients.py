import os
import sys
import django
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import ClientAllocation

# Delete test clients
deleted_count = 0

# Delete by name pattern
test_clients = ClientAllocation.objects.filter(eclick_name__icontains="Test")
for client in test_clients:
    print(f"Deleting: Client ID {client.client_id} - {client.eclick_name}")
    client.delete()
    deleted_count += 1

print(f"\nTotal test clients deleted: {deleted_count}")
