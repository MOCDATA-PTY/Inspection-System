"""
Create new super admin users: Marnus, Henry, and Bernadette
"""

import os
import django
import secrets
import string

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def generate_random_password(length=12):
    """Generate a random password with letters, digits, and special characters"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def create_super_admin_users():
    """Create super admin users: Marnus, Henry, and Bernadette"""

    print("=" * 100)
    print(" " * 35 + "CREATE SUPER ADMIN USERS")
    print("=" * 100)
    print()

    users_to_create = [
        {
            'username': 'Marnus',
            'first_name': 'Marnus',
            'last_name': 'Admin',
            'email': 'marnus@inspection.com'
        },
        {
            'username': 'Henry',
            'first_name': 'Henry',
            'last_name': 'Admin',
            'email': 'henry@inspection.com'
        },
        {
            'username': 'Bernadette',
            'first_name': 'Bernadette',
            'last_name': 'Admin',
            'email': 'bernadette@inspection.com'
        }
    ]

    created_users = []

    for user_data in users_to_create:
        username = user_data['username']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"User '{username}' already exists. Updating password...")
            user = User.objects.get(username=username)

            # Generate random password
            password = generate_random_password()
            user.set_password(password)

            # Update to super admin
            user.is_superuser = True
            user.is_staff = True
            user.role = 'super_admin'
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.email = user_data['email']
            user.save()

            created_users.append({
                'username': username,
                'password': password,
                'status': 'UPDATED'
            })

            print(f"  UPDATED: {username}")
            print(f"  Email: {user_data['email']}")
            print(f"  Password: {password}")
            print()

        else:
            # Create new user
            password = generate_random_password()

            user = User.objects.create_user(
                username=username,
                email=user_data['email'],
                password=password,
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )

            # Set as super admin
            user.is_superuser = True
            user.is_staff = True
            user.role = 'super_admin'
            user.save()

            created_users.append({
                'username': username,
                'password': password,
                'status': 'CREATED'
            })

            print(f"  CREATED: {username}")
            print(f"  Email: {user_data['email']}")
            print(f"  Password: {password}")
            print()

    print("=" * 100)
    print(" " * 40 + "SUMMARY")
    print("=" * 100)
    print()
    print("Super Admin Users Created/Updated:")
    print("-" * 100)
    print()

    for user_info in created_users:
        print(f"Username: {user_info['username']}")
        print(f"Password: {user_info['password']}")
        print(f"Status: {user_info['status']}")
        print(f"Role: Super Admin")
        print()

    print("=" * 100)
    print()
    print("IMPORTANT: Save these passwords securely!")
    print("Users can login at: http://localhost:8000/login/")
    print()
    print("=" * 100)

    return created_users


if __name__ == "__main__":
    try:
        create_super_admin_users()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
