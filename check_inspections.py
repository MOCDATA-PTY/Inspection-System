import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import Inspection
from datetime import datetime

print("\n" + "="*80)
print("INSPECTION DATABASE CHECK")
print("="*80 + "\n")

# Check total count
total = Inspection.objects.count()
print(f"Total inspections in database: {total}\n")

if total == 0:
    print("No inspections found in database!")
    sys.exit(0)

# Get recent inspections
print("Recent 20 inspections:")
recent = Inspection.objects.all().order_by('-inspection_date')[:20]

for i, insp in enumerate(recent, 1):
    print(f"{i}. ID: {insp.id}")
    print(f"   Client: {insp.facility_client_name or 'N/A'}")
    print(f"   Date: {insp.inspection_date}")
    print(f"   Commodity: {insp.commodity or 'N/A'}")
    print()

# Check date range
print("="*80)
print("Date range analysis:")
earliest = Inspection.objects.order_by('inspection_date').first()
latest = Inspection.objects.order_by('-inspection_date').first()

if earliest and latest:
    print(f"Earliest inspection: {earliest.inspection_date}")
    print(f"Latest inspection: {latest.inspection_date}")

    # Count by month
    from django.db.models import Count
    from django.db.models.functions import TruncMonth

    print("\nInspections by month (last 6 months):")
    monthly = (Inspection.objects
               .annotate(month=TruncMonth('inspection_date'))
               .values('month')
               .annotate(count=Count('id'))
               .order_by('-month')[:6])

    for item in monthly:
        print(f"  {item['month'].strftime('%Y-%m')}: {item['count']} inspections")

print("\n" + "="*80)
