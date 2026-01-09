"""
Simple script to create a super admin user
"""
import os
import django
from getpass import getpass

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def create_super_admin():
    """Create a super admin user with role='super_admin'"""

    print("="*60)
    print("CREATE SUPER ADMIN USER")
    print("="*60)

    # Get user details
    username = input("\nEnter username: ").strip()

    if not username:
        print("ERROR: Username cannot be empty")
        return

    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"\nERROR: User '{username}' already exists!")
        update = input("Do you want to update this user to super_admin? (yes/no): ").strip().lower()

        if update == 'yes':
            user = User.objects.get(username=username)
            user.role = 'super_admin'
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print(f"\n✓ User '{username}' updated to super_admin role!")
            return
        else:
            print("Operation cancelled.")
            return

    # Get additional details
    email = input("Enter email (optional, press Enter to skip): ").strip()
    first_name = input("Enter first name (optional, press Enter to skip): ").strip()
    last_name = input("Enter last name (optional, press Enter to skip): ").strip()

    # Get password
    while True:
        password = getpass("Enter password: ")
        password_confirm = getpass("Confirm password: ")

        if password != password_confirm:
            print("ERROR: Passwords don't match. Try again.")
            continue

        if len(password) < 4:
            print("ERROR: Password too short (minimum 4 characters)")
            continue

        break

    # Create the user
    try:
        user = User.objects.create_user(
            username=username,
            email=email if email else '',
            password=password,
            first_name=first_name if first_name else '',
            last_name=last_name if last_name else ''
        )

        # Set super admin permissions
        user.role = 'super_admin'
        user.is_staff = True
        user.is_superuser = True
        user.save()

        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print(f"Username: {user.username}")
        print(f"Email: {user.email or 'Not provided'}")
        print(f"Name: {user.first_name} {user.last_name}".strip() or 'Not provided')
        print(f"Role: {user.role}")
        print(f"Is Staff: {user.is_staff}")
        print(f"Is Superuser: {user.is_superuser}")
        print("\nThe user can now log in with full admin access!")
        print("="*60)

    except Exception as e:
        print(f"\nERROR: Failed to create user: {str(e)}")

if __name__ == "__main__":
    create_super_admin()
