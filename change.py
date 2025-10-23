"""
Change password for user Neo
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def change_neo_password():
    """Change Neo's password to Neon@0127"""

    print("=" * 80)
    print(" " * 25 + "CHANGE NEO'S PASSWORD")
    print("=" * 80)
    print()

    try:
        # Search for user with username containing "Neo"
        users = User.objects.filter(username__icontains='neo')

        if not users.exists():
            print("No users found with username containing 'Neo'")
            print()
            print("Searching all users to find similar names...")
            all_users = User.objects.all().order_by('username')
            print()
            print("All users in the system:")
            print("-" * 80)
            for user in all_users:
                print(f"  - {user.username} (Email: {user.email})")
            print()
            return False

        print(f"Found {users.count()} user(s) matching 'Neo':")
        print("-" * 80)
        for user in users:
            print(f"  - Username: {user.username}")
            print(f"    Email: {user.email}")
            print(f"    First Name: {user.first_name}")
            print(f"    Last Name: {user.last_name}")
            print(f"    Role: {getattr(user, 'role', 'N/A')}")
            print()

        # If multiple users found, ask which one
        if users.count() > 1:
            print("Multiple users found. Changing password for all matching users.")
            print()

        # Change password for all matching users
        new_password = "Neon@0127"

        for user in users:
            user.set_password(new_password)
            user.save()
            print(f"SUCCESS: Password changed for user: {user.username}")
            print(f"   New password: {new_password}")
            print()

        print("=" * 80)
        print("Password change completed!")
        print("=" * 80)
        print()
        print("Users can now login with:")
        for user in users:
            print(f"  Username: {user.username}")
        print(f"  Password: {new_password}")
        print()

        return True

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        change_neo_password()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
