import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def display_all_users():
    """Display all users in the system with their roles"""
    print("\n" + "="*80)
    print("ALL USERS IN THE SYSTEM")
    print("="*80)

    users = User.objects.all().order_by('username')

    if not users:
        print("No users found in the database.")
        return

    print(f"\nTotal Users: {users.count()}\n")

    for user in users:
        role = getattr(user, 'role', 'Not Set')
        is_superuser = "Yes" if user.is_superuser else "No"
        is_staff = "Yes" if user.is_staff else "No"
        is_active = "Yes" if user.is_active else "No"

        print(f"Username: {user.username}")
        print(f"  Email: {user.email or 'Not Set'}")
        print(f"  Full Name: {user.get_full_name() or 'Not Set'}")
        print(f"  Role: {role}")
        print(f"  Superuser: {is_superuser}")
        print(f"  Staff: {is_staff}")
        print(f"  Active: {is_active}")
        print(f"  Last Login: {user.last_login or 'Never'}")
        print(f"  Date Joined: {user.date_joined}")
        print("-" * 80)

def make_super_admin(username):
    """Make a user a super admin"""
    try:
        user = User.objects.get(username__iexact=username)
        user.role = 'super_admin'
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        print(f"✓ Successfully made '{user.username}' a super admin!")
        return True
    except User.DoesNotExist:
        print(f"✗ User '{username}' not found in the database.")
        return False
    except Exception as e:
        print(f"✗ Error updating user '{username}': {str(e)}")
        return False

def main():
    print("\n" + "="*80)
    print("USER MANAGEMENT SCRIPT")
    print("="*80)

    # Display all users first
    display_all_users()

    # Make Armand and Anthony super admins
    print("\n" + "="*80)
    print("MAKING USERS SUPER ADMINS")
    print("="*80 + "\n")

    success_count = 0

    print("Processing Armand...")
    if make_super_admin('Armand'):
        success_count += 1

    print("\nProcessing Anthony...")
    if make_super_admin('Anthony'):
        success_count += 1

    # Display updated users
    print("\n" + "="*80)
    print("UPDATED USER LIST")
    print("="*80)
    display_all_users()

    print("\n" + "="*80)
    print(f"SUMMARY: {success_count} user(s) successfully updated to super admin")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
