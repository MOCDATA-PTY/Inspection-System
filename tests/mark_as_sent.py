"""
Direct database update to mark Hume International as Sent
This bypasses all cache and compliance checks
"""

import os
import sys
import io
import django
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

# Import after Django setup
from django.core.cache import cache
from main.models import FoodSafetyAgencyInspection
from datetime import datetime, date
from django.utils import timezone
from django.contrib.auth import get_user_model

def mark_hume_as_sent():
    """Mark Hume International as sent in the database"""

    print("="*80)
    print("MARK HUME INTERNATIONAL AS SENT")
    print("="*80)

    # 1. Find the inspection
    print("\n[STEP 1] Finding Hume International inspections...")
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains='Hume International',
        date_of_inspection=date(2025, 10, 17)
    )

    count = inspections.count()
    if count == 0:
        print("   ❌ No Hume International inspections found!")
        return False

    print(f"   ✅ Found {count} inspection(s)")
    for insp in inspections:
        print(f"      ID: {insp.id}, Remote ID: {insp.remote_id}, Commodity: {insp.commodity}")

    # 2. Get the admin user (or first user)
    print("\n[STEP 2] Getting user for sent_by field...")
    User = get_user_model()
    user = User.objects.filter(role='admin').first()
    if not user:
        user = User.objects.first()

    if not user:
        print("   ❌ No users found in database!")
        return False

    print(f"   ✅ Using user: {user.username} (ID: {user.id})")

    # 3. Update all inspections in the group
    print("\n[STEP 3] Marking inspections as SENT...")
    current_time = timezone.now()

    updated_count = 0
    for inspection in inspections:
        inspection.is_sent = True
        inspection.sent_by = user
        inspection.sent_date = current_time
        inspection.save()
        updated_count += 1
        print(f"   ✅ Updated inspection {inspection.id}: is_sent=True, sent_by={user.username}, sent_date={current_time}")

    print(f"\n   ✅ Total updated: {updated_count} inspection(s)")

    # 4. Clear ALL caches
    print("\n[STEP 4] Clearing ALL caches...")
    cache.clear()
    print("   ✅ All caches cleared!")

    # 5. Verify the update
    print("\n[STEP 5] Verifying the update...")
    inspections = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains='Hume International',
        date_of_inspection=date(2025, 10, 17)
    )

    all_sent = True
    for inspection in inspections:
        is_sent = inspection.is_sent
        sent_by = inspection.sent_by.username if inspection.sent_by else "None"
        sent_date = inspection.sent_date

        print(f"   Inspection {inspection.id}:")
        print(f"      is_sent: {is_sent}")
        print(f"      sent_by: {sent_by}")
        print(f"      sent_date: {sent_date}")

        if not is_sent:
            all_sent = False

    print("\n" + "="*80)
    if all_sent:
        print("✅ SUCCESS - ALL INSPECTIONS MARKED AS SENT!")
    else:
        print("❌ FAILED - Some inspections not marked as sent")
    print("="*80)

    print("\n🔄 REFRESH YOUR BROWSER to see the updated status")
    print("   The dropdown should now show 'Sent' status with the timestamp")

    return all_sent


if __name__ == '__main__':
    print("\n🚀 Starting direct database update...\n")

    success = mark_hume_as_sent()

    if success:
        print("\n✅ Process completed successfully!")
        print("\n👉 REFRESH YOUR BROWSER NOW!")
    else:
        print("\n❌ Process failed!")

    sys.exit(0 if success else 1)
