"""
Update user roles
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("UPDATING USER ROLES")
print("=" * 60)
print()

# Define role updates
role_updates = {
    # Super admins
    'anthony': 'super_admin',
    'armand': 'super_admin',
    'chrisdelport': 'super_admin',
    # Financial admins
    'Nicole': 'financial_admin',
    'mpho': 'financial_admin',
    'henry': 'financial_admin',
    'Bernadette': 'financial_admin',
    # Lab technician
    'chrisna': 'lab_technician',
}

# Update users
for username, new_role in role_updates.items():
    try:
        # Try case-insensitive match
        user = User.objects.filter(username__iexact=username).first()
        if user:
            old_role = user.role
            user.role = new_role
            if new_role == 'super_admin':
                user.is_superuser = True
                user.is_staff = True
            user.save()
            print(f"OK - {user.username}: {old_role} -> {new_role}")
        else:
            print(f"NOT FOUND - {username}")
    except Exception as e:
        print(f"ERROR - {username}: {e}")

print()
print("=" * 60)
print("ALL USERS AND ROLES")
print("=" * 60)
print()

users = User.objects.all().order_by('role', 'username')

print(f"{'Username':<25} {'Role':<20} {'Staff':<8} {'Super':<8}")
print("-" * 60)

for user in users:
    print(f"{user.username:<25} {user.role or 'N/A':<20} {str(user.is_staff):<8} {str(user.is_superuser):<8}")

print()
print(f"Total users: {users.count()}")
print("=" * 60)
