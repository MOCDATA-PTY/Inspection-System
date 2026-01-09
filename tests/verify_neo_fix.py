"""Verify that NEO can now see their inspections"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, InspectorMapping
from django.db.models import Q
from datetime import datetime, timedelta

print("=" * 80)
print("VERIFYING NEO INSPECTION FIX")
print("=" * 80)

# Get Neo's inspector mapping
try:
    inspector_mapping = InspectorMapping.objects.get(inspector_name='Neo Noe')
    inspector_id = inspector_mapping.inspector_id
    inspector_name = inspector_mapping.inspector_name
    print(f"\nInspector Mapping Found:")
    print(f"  ID: {inspector_id}")
    print(f"  Name: {inspector_name}")
except InspectorMapping.DoesNotExist:
    print("ERROR: No inspector mapping found for 'Neo Noe'")
    sys.exit(1)

# Filter inspections using the OLD method (case-sensitive)
print("\n" + "=" * 80)
print("OLD METHOD (case-sensitive):")
print("=" * 80)
sixty_days_ago = (datetime.now() - timedelta(days=60)).date()
inspections_old = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=sixty_days_ago
).filter(
    Q(inspector_id=inspector_id) | Q(inspector_name=inspector_name)
)
print(f"Inspections found: {inspections_old.count()}")

# Filter inspections using the NEW method (case-insensitive)
print("\n" + "=" * 80)
print("NEW METHOD (case-insensitive):")
print("=" * 80)
inspections_new = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=sixty_days_ago
).filter(
    Q(inspector_id=inspector_id) | Q(inspector_name__iexact=inspector_name)
)
print(f"Inspections found: {inspections_new.count()}")

if inspections_new.exists():
    print("\nSample inspections:")
    for insp in inspections_new[:5]:
        print(f"  - ID: {insp.remote_id}, Client: {insp.client_name}, Date: {insp.date_of_inspection}, Inspector: {insp.inspector_name}")

print("\n" + "=" * 80)
print("RESULT:")
print("=" * 80)
if inspections_new.count() > 0:
    print(f"✓ SUCCESS! NEO can now see {inspections_new.count()} inspections")
else:
    print("✗ FAILED! NEO still cannot see inspections")
