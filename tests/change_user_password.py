import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def change_user_password():
    """Change password for a user by username"""
    
    # Get username
    username = input("Enter username: ").strip()
    
    if not username:
        print("Username cannot be empty.")
        return
    
    # Check if user exists
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"User '{username}' does not exist.")
        return
    
    # Get new password
    new_password = input("Enter new password: ").strip()
    
    if not new_password:
        print("Password cannot be empty.")
        return
    
    # Confirm password
    confirm_password = input("Confirm new password: ").strip()
    
    if new_password != confirm_password:
        print("Passwords do not match.")
        return
    
    # Change password
    user.set_password(new_password)
    user.save()
    
    print(f"\nPassword successfully changed for user '{username}'.")
    print(f"User details:")
    print(f"  - Username: {user.username}")
    print(f"  - Email: {user.email}")
    print(f"  - Role: {getattr(user, 'role', 'N/A')}")
    print(f"  - Active: {user.is_active}")

if __name__ == "__main__":
    change_user_password()