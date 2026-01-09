import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.core.cache import cache

print("=" * 80)
print("KM/HOURS DIAGNOSTIC CHECK")
print("=" * 80)

# Check current inspections with km/hours
inspections_with_data = FoodSafetyAgencyInspection.objects.filter(
    km_traveled__isnull=False
) | FoodSafetyAgencyInspection.objects.filter(
    hours__isnull=False
)

count = inspections_with_data.count()
print(f"\n[CURRENT] Inspections with km or hours data: {count:,}")

if count > 0:
    print(f"\n[SAMPLE] First 5 inspections with data:")
    for insp in inspections_with_data[:5]:
        print(f"  - ID {insp.remote_id}: {insp.commodity} | {insp.client_name}")
        print(f"    KM: {insp.km_traveled}, Hours: {insp.hours}")
        print(f"    Date: {insp.date_of_inspection}")

# Check if there's a backup in cache
backup = cache.get('km_hours_backup_persistent')
if backup:
    print(f"\n[BACKUP] Found backup in cache with {len(backup):,} entries")
    print(f"[OK] Backup exists and will be restored on next sync!")
else:
    print(f"\n[WARNING] No backup found in cache")
    print(f"[INFO] Backup is created automatically during sync")

# Check for backup files
import glob
backup_files = glob.glob('km_hours_backup_*.json')
if backup_files:
    print(f"\n[FILES] Found {len(backup_files)} backup files:")
    for f in sorted(backup_files, reverse=True)[:3]:
        print(f"  - {f}")
else:
    print(f"\n[INFO] No backup files found")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
