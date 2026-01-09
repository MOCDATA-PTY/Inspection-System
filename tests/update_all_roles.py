"""
Update multiple user roles based on their job functions
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 80)
print("UPDATING MULTIPLE USER ROLES")
print("=" * 80)

# Define role updates: username -> new_role
role_updates = {
    'Bernadette': 'financial_admin',
    'Chrisdelport': 'super_admin',
    'Nicole': 'financial_admin',
    'Simphiwe': 'super_admin',
    'anthony': 'super_admin',
    'armand': 'financial_admin',
    'mpho': 'lab_technician',
    'Chrisna': 'lab_technician',
}

success_count = 0
error_count = 0

for username, new_role in role_updates.items():
    try:
        user = User.objects.get(username=username)
        old_role = user.role if hasattr(user, 'role') else 'N/A'

        user.role = new_role
        user.save()

        print(f"\n[OK] Updated {username}:")
        print(f"     Old role: {old_role}")
        print(f"     New role: {new_role}")
        success_count += 1

    except User.DoesNotExist:
        print(f"\n[ERROR] User '{username}' not found")
        error_count += 1
    except Exception as e:
        print(f"\n[ERROR] Failed to update {username}: {e}")
        error_count += 1

# Summary
print("\n" + "=" * 80)
print("UPDATE SUMMARY")
print("=" * 80)
print(f"Successfully updated: {success_count}")
print(f"Errors: {error_count}")

# Show updated role distribution
print("\n" + "=" * 80)
print("ROLE DISTRIBUTION")
print("=" * 80)

from django.db.models import Count

role_summary = User.objects.values('role').annotate(count=Count('id')).order_by('-count')

print(f"\n{'Role':<25} {'Count':<10}")
print("-" * 40)

for item in role_summary:
    role = item['role'] or 'N/A'
    count = item['count']
    print(f"{role:<25} {count:<10}")

# Show users by role
print("\n" + "=" * 80)
print("USERS BY ROLE")
print("=" * 80)

roles = ['super_admin', 'financial_admin', 'lab_technician', 'developer', 'inspector']

for role in roles:
    users = User.objects.filter(role=role).order_by('username')
    if users.exists():
        print(f"\n{role.upper().replace('_', ' ')} ({users.count()} users):")
        for user in users:
            email = f" ({user.email})" if user.email else ""
            superuser = " [SUPERUSER]" if user.is_superuser else ""
            print(f"  - {user.username}{email}{superuser}")

print("\n" + "=" * 80)
