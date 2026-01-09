import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import datetime, timedelta
from django.db.models import Q

# Check inspections from last 30 days with hours, km, and samples
today = datetime.now().date()
start_date = today - timedelta(days=30)

inspections = FoodSafetyAgencyInspection.objects.filter(
    hours__isnull=False,
    km_traveled__isnull=False,
    date_of_inspection__gte=start_date,
    date_of_inspection__lte=today
).filter(
    Q(fat=True) |
    Q(protein=True) |
    Q(calcium=True) |
    Q(dna=True) |
    Q(bought_sample__isnull=False)
).select_related(
    'sent_by', 'rfi_uploaded_by', 'invoice_uploaded_by'
).distinct('id').order_by('id', '-date_of_inspection', 'inspector_name')

print(f"Total inspections: {inspections.count()}")
print("\nFirst 20 inspections:")
print("=" * 120)

for insp in inspections[:20]:
    print(f"\nID: {insp.id}, Remote ID: {insp.remote_id}")
    print(f"  Client: {insp.client_name}")
    print(f"  Date: {insp.date_of_inspection}")
    print(f"  Inspector: {insp.inspector_name}")
    print(f"  Commodity: [{insp.commodity}]")
    print(f"  Hours: {insp.hours}, KM: {insp.km_traveled}")

# Check for inspections with same client and date
print("\n" + "=" * 120)
print("Checking for inspections with same client and date:")
print("=" * 120)

seen = {}
for insp in inspections:
    key = (insp.client_name, insp.date_of_inspection, insp.inspector_name)
    if key in seen:
        seen[key].append(insp)
    else:
        seen[key] = [insp]

duplicates = {k: v for k, v in seen.items() if len(v) > 1}

print(f"\nFound {len(duplicates)} sets with same client/date/inspector:")

for key, insps in list(duplicates.items())[:10]:
    print(f"\n  Client: {key[0]}")
    print(f"  Date: {key[1]}")
    print(f"  Inspector: {key[2]}")
    print(f"  Count: {len(insps)}")
    for i in insps:
        print(f"    - ID: {i.id}, Remote ID: {i.remote_id}, Commodity: [{i.commodity}]")
