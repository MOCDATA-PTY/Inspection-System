import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

# Search for users with "neo" in their username
print("Searching for users with 'neo' in username...")
neo_users = User.objects.filter(username__icontains='neo')

if neo_users.exists():
    print(f"\nFound {neo_users.count()} user(s):")
    for user in neo_users:
        print(f"\nUsername: {user.username}")
        print(f"Email: {user.email}")
        print(f"First Name: {user.first_name}")
        print(f"Last Name: {user.last_name}")
        print(f"Role: {getattr(user, 'role', 'N/A')}")
        print(f"Is Active: {user.is_active}")
        print(f"Last Login: {user.last_login}")

        # Reset password
        new_password = "Neo123456"
        user.set_password(new_password)
        user.save()
        print(f"Password reset to: {new_password}")
else:
    print("\nNo users found with 'neo' in username.")
    print("\nLet me show all users:")
    all_users = User.objects.all()
    for user in all_users:
        print(f"- {user.username} ({user.email}) - {user.first_name} {user.last_name}")
