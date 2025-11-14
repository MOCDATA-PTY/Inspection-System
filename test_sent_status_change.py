import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import datetime
from django.utils import timezone
from django.core.cache import cache

# Clear cache first
print("Clearing cache...")
cache.clear()
print("Cache cleared.\n")

# Find the inspection for Hume International
inspection_date = datetime.strptime('17/10/2025', '%d/%m/%Y').date()

inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains='Hume',
    date_of_inspection=inspection_date
)

if inspections:
    print(f"Found {inspections.count()} inspection(s) for Hume International on 17/10/2025\n")

    for inspection in inspections:
        print(f"Inspection ID: {inspection.id}")
        print(f"  Client: {inspection.client_name}")
        print(f"  Date: {inspection.date_of_inspection}")
        print(f"  BEFORE - is_sent: {inspection.is_sent}")
        print(f"  BEFORE - sent_date: {inspection.sent_date}")

        # Change to SENT
        inspection.is_sent = True
        inspection.sent_date = timezone.now()
        inspection.save()

        print(f"  AFTER - is_sent: {inspection.is_sent}")
        print(f"  AFTER - sent_date: {inspection.sent_date}")
        print(f"  [OK] Successfully changed to SENT\n")

        # Now change back to NOT SENT
        inspection.is_sent = False
        inspection.sent_date = None
        inspection.save()

        print(f"  REVERTED - is_sent: {inspection.is_sent}")
        print(f"  REVERTED - sent_date: {inspection.sent_date}")
        print(f"  [OK] Successfully changed back to NOT SENT\n")

    print("=" * 60)
    print("TEST COMPLETE!")
    print("The dropdown should now work in the browser.")
    print("Please do a HARD REFRESH (Ctrl + Shift + R) to reload the JavaScript.")
    print("=" * 60)
else:
    print("No inspections found for Hume International on 17/10/2025")
