#!/usr/bin/env python3
"""
Set User as Financial Admin
============================
Sets a user's role to 'financial' to give them financial admin access.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User


def set_user_financial(username):
    """Set a user as financial admin."""
    try:
        user = User.objects.get(username=username)

        print(f"\n{'='*60}")
        print(f"UPDATING USER: {username}")
        print(f"{'='*60}")
        print(f"Current role: {getattr(user, 'role', 'None')}")
        print(f"Email: {user.email}")
        print(f"Active: {user.is_active}")
        print()

        # Set role to financial
        user.role = 'financial'
        user.save()

        print(f"✅ Successfully updated {username} to Financial role!")
        print(f"New role: {user.role}")
        print()
        print(f"{'='*60}")
        print(f"USER PERMISSIONS")
        print(f"{'='*60}")
        print(f"✅ Can access export sheet")
        print(f"✅ Can view financial reports")
        print(f"✅ Can manage invoices")
        print(f"{'='*60}")

        return True

    except User.DoesNotExist:
        print(f"\n❌ ERROR: User '{username}' does not exist!")
        print(f"\nAvailable users:")
        for u in User.objects.all():
            print(f"  - {u.username} (role: {getattr(u, 'role', 'None')})")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Set user as financial admin',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set mpho as financial admin
  python set_user_financial.py --username mpho

  # List all users
  python set_user_financial.py --list
        """
    )

    parser.add_argument(
        '--username',
        type=str,
        help='Username to set as financial admin'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all users'
    )

    args = parser.parse_args()

    if args.list:
        print(f"\n{'='*60}")
        print(f"ALL USERS")
        print(f"{'='*60}")
        for user in User.objects.all().order_by('username'):
            role = getattr(user, 'role', 'None')
            status = '✅ Active' if user.is_active else '❌ Inactive'
            print(f"{user.username:20} | Role: {role:15} | {status}")
        print(f"{'='*60}\n")
        return 0

    if not args.username:
        print("ERROR: --username is required (or use --list to see all users)")
        return 1

    success = set_user_financial(args.username)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
