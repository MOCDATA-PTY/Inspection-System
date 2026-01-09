"""
Show all users and their roles
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 100)
print("ALL USERS AND THEIR ROLES")
print("=" * 100)

users = User.objects.all().order_by('username')
total_count = users.count()

print(f"\nTotal Users: {total_count}\n")

# Display header
print(f"{'Username':<20} {'Role':<15} {'Email':<35} {'Staff':<8} {'Super':<8} {'Active':<8}")
print("=" * 100)

# Track role counts
role_counts = {}

for user in users:
    username = user.username[:18]
    role = (user.role if hasattr(user, 'role') and user.role else 'N/A')[:13]
    email = (user.email or 'N/A')[:33]
    is_staff = 'Yes' if user.is_staff else 'No'
    is_super = 'Yes' if user.is_superuser else 'No'
    is_active = 'Yes' if user.is_active else 'No'

    print(f"{username:<20} {role:<15} {email:<35} {is_staff:<8} {is_super:<8} {is_active:<8}")

    # Count roles
    if role not in role_counts:
        role_counts[role] = 0
    role_counts[role] += 1

# Summary
print("\n" + "=" * 100)
print("ROLE SUMMARY")
print("=" * 100)

print(f"\n{'Role':<20} {'Count':<10} {'Percentage':<12}")
print("-" * 45)
for role, count in sorted(role_counts.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total_count * 100)
    print(f"{role:<20} {count:<10} {percentage:>5.1f}%")

print("\n" + "=" * 100)
