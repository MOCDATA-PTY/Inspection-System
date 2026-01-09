#!/usr/bin/env python3
"""
Update Nicole's account - set as financial admin and generate new password
"""
import os
import sys
import django
import secrets
import string

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def generate_password(length=12):
    """Generate a secure random password"""
    # Use letters, digits, and some special characters
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

print("=" * 100)
print("UPDATING NICOLE'S ACCOUNT")
print("=" * 100)

# Find Nicole's account
try:
    nicole = User.objects.get(username='Nicole')
    print(f"\nFound user: {nicole.username}")
    print(f"Full name: {nicole.first_name} {nicole.last_name}")
    print(f"Email: {nicole.email}")
    print(f"Current role: {getattr(nicole, 'role', 'inspector')}")
    print(f"Is staff: {nicole.is_staff}")
    print(f"Is active: {nicole.is_active}")

    # Update role to financial_admin
    nicole.role = 'financial_admin'

    # Generate new password
    new_password = generate_password(12)
    nicole.set_password(new_password)

    # Save changes
    nicole.save()

    print("\n" + "-" * 100)
    print("ACCOUNT UPDATED SUCCESSFULLY")
    print("-" * 100)
    print(f"\nUsername: {nicole.username}")
    print(f"New Password: {new_password}")
    print(f"Role: Financial Admin")
    print(f"Status: Active")

    print("\n" + "=" * 100)
    print("IMPORTANT: Save this password securely!")
    print("=" * 100)

except User.DoesNotExist:
    print("\nERROR: User 'Nicole' not found in the system")
except Exception as e:
    print(f"\nERROR: {str(e)}")

print("\n" + "=" * 100)