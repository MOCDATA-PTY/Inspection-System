import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("\n[INFO] Clearing all KM and Hours data from inspections...")

# Count how many inspections have KM or Hours data
inspections_with_data = FoodSafetyAgencyInspection.objects.filter(
    km_traveled__isnull=False
) | FoodSafetyAgencyInspection.objects.filter(
    hours__isnull=False
)

count_with_data = inspections_with_data.count()
print(f"[INFO] Found {count_with_data} inspections with KM or Hours data")

if count_with_data > 0:
    # Clear all KM and Hours fields
    updated_count = FoodSafetyAgencyInspection.objects.all().update(
        km_traveled=None,
        hours=None
    )
    print(f"[SUCCESS] Cleared KM and Hours data from {updated_count} inspections")
else:
    print("[INFO] No inspections with KM or Hours data found")

# Verify the update
remaining = FoodSafetyAgencyInspection.objects.filter(
    km_traveled__isnull=False
) | FoodSafetyAgencyInspection.objects.filter(
    hours__isnull=False
)

remaining_count = remaining.count()
if remaining_count == 0:
    print("[SUCCESS] All KM and Hours data has been cleared successfully!")
else:
    print(f"[WARNING] {remaining_count} inspections still have KM or Hours data")

print("\n[DONE] Operation completed")
