import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def show_all_users():
    """Display all users in the database"""
    users = User.objects.all()
    
    if not users.exists():
        print("No users found in the database.")
        return
    
    print(f"\nTotal Users: {users.count()}\n")
    print("-" * 100)
    
    for user in users:
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"First Name: {user.first_name}")
        print(f"Last Name: {user.last_name}")
        print(f"Role: {getattr(user, 'role', 'N/A')}")
        print(f"Phone: {getattr(user, 'phone_number', 'N/A')}")
        print(f"Department: {getattr(user, 'department', 'N/A')}")
        print(f"Employee ID: {getattr(user, 'employee_id', 'N/A')}")
        print(f"Active: {user.is_active}")
        print(f"Staff: {user.is_staff}")
        print(f"Superuser: {user.is_superuser}")
        print(f"Last Login: {user.last_login}")
        print(f"Date Joined: {user.date_joined}")
        print("-" * 100)

if __name__ == "__main__":
    show_all_users()