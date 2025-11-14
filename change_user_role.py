import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def change_user_role():
    """Change role for a user by username"""
    
    # Available roles
    roles = {
        '1': ('inspector', 'Inspector'),
        '2': ('admin', 'HR/Admin Staff'),
        '3': ('super_admin', 'Super Admin'),
        '4': ('financial', 'Financial'),
        '5': ('scientist', 'Scientist'),
        '6': ('developer', 'Developer'),
    }
    
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
    
    # Display current role
    current_role = getattr(user, 'role', 'inspector')
    print(f"\nCurrent role: {current_role}")
    
    # Display available roles
    print("\nAvailable roles:")
    for key, (role_value, role_name) in roles.items():
        print(f"  {key}. {role_name} ({role_value})")
    
    # Get new role
    choice = input("\nSelect new role (1-6): ").strip()
    
    if choice not in roles:
        print("Invalid choice.")
        return
    
    new_role_value, new_role_name = roles[choice]
    
    # Confirm change
    confirm = input(f"Change role to '{new_role_name}'? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("Role change cancelled.")
        return
    
    # Change role
    user.role = new_role_value
    user.save()
    
    print(f"\nRole successfully changed for user '{username}'.")
    print(f"User details:")
    print(f"  - Username: {user.username}")
    print(f"  - Email: {user.email}")
    print(f"  - New Role: {user.role}")
    print(f"  - Active: {user.is_active}")

if __name__ == "__main__":
    change_user_role()