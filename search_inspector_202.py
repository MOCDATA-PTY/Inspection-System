"""
Search for inspector ID 202 or related users
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.contrib.auth.models import User

print("="*80)
print("SEARCHING FOR INSPECTOR ID 202")
print("="*80)

# List all users with IDs around 202
print("\nUsers with IDs from 190 to 210:")
users = User.objects.filter(id__gte=190, id__lte=210).order_by('id')
for user in users:
    print(f"  ID {user.id}: {user.username} - {user.first_name} {user.last_name}")

# Check if there are any inspections with inspector_id=202
print("\n" + "-"*80)
inspections_202 = FoodSafetyAgencyInspection.objects.filter(inspector_id=202).count()
print(f"Inspections with inspector_id=202: {inspections_202}")

if inspections_202 > 0:
    sample = FoodSafetyAgencyInspection.objects.filter(inspector_id=202).first()
    print(f"Sample inspection: {sample.date_of_inspection} - {sample.client_name}")

# Search for Dimakatso users
print("\n" + "-"*80)
print("All Dimakatso-related users:")
dimakatso_users = User.objects.filter(
    first_name__icontains='dimakatso'
) | User.objects.filter(
    username__icontains='dimakatso'
) | User.objects.filter(
    last_name__icontains='modiba'
)
for user in dimakatso_users:
    print(f"  ID {user.id}: {user.username} - {user.first_name} {user.last_name}")
    inspections = FoodSafetyAgencyInspection.objects.filter(inspector_id=user.id).count()
    print(f"    Inspections: {inspections}")

# List all users
print("\n" + "-"*80)
print("All users (showing ID, username, name):")
all_users = User.objects.all().order_by('id')
for user in all_users:
    print(f"  ID {user.id}: {user.username} - {user.first_name} {user.last_name}")

print("\n" + "="*80)
print("Done!")
