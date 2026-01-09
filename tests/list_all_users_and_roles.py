#!/usr/bin/env python3
"""
List all users and their roles in the system
"""
import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 100)
print("ALL USERS AND THEIR ROLES")
print("=" * 100)

users = User.objects.all().order_by('username')

print(f"\nTotal users: {users.count()}\n")
print(f"{'Username':<25} {'Full Name':<35} {'Role':<20} {'Active':<10}")
print("-" * 100)

for user in users:
    full_name = f"{user.first_name} {user.last_name}".strip() or "N/A"

    # Get role from user object (added via add_to_class in models.py)
    role = getattr(user, 'role', 'inspector')

    # Make role display name more readable
    role_display = {
        'inspector': 'Inspector',
        'admin': 'HR/Admin Staff',
        'super_admin': 'Super Admin',
        'financial_admin': 'Financial Admin',
        'lab_technician': 'Lab Technician',
        'scientist': 'Scientist',
        'developer': 'Developer'
    }.get(role, role)

    # Check if user is active
    is_active = "Yes" if user.is_active else "No"

    # Check if user is staff or superuser
    if user.is_superuser:
        role_display = f"{role_display} (SU)"
    elif user.is_staff:
        role_display = f"{role_display} (Staff)"

    print(f"{user.username:<25} {full_name:<35} {role_display:<20} {is_active:<10}")

print("\n" + "=" * 100)
print("ROLE SUMMARY")
print("=" * 100)

# Count users by role
from collections import Counter

roles = [getattr(user, 'role', 'inspector') for user in users]
role_counts = Counter(roles)

role_display_names = {
    'inspector': 'Inspector',
    'admin': 'HR/Admin Staff',
    'super_admin': 'Super Admin',
    'financial_admin': 'Financial Admin',
    'lab_technician': 'Lab Technician',
    'scientist': 'Scientist',
    'developer': 'Developer'
}

print(f"\n{'Role':<30} {'Count':<10}")
print("-" * 40)
for role, count in sorted(role_counts.items()):
    role_name = role_display_names.get(role, role)
    print(f"{role_name:<30} {count:<10}")

print("\n" + "=" * 100)