#!/usr/bin/env python3
"""
Create admin users: Anthony and Armand (super admin), Mpho (administrator)
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def create_admin_users():
    """Create admin users with specified roles"""
    print("👑 Creating Admin User Accounts")
    print("=" * 60)
    
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Admin users to create
    admin_users = [
        {
            'username': 'anthony',
            'first_name': 'Anthony',
            'last_name': '',
            'password': 'Anthony2025!',
            'role': 'super_admin',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'armand',
            'first_name': 'Armand',
            'last_name': '',
            'password': 'Armand2025!',
            'role': 'super_admin',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'mpho',
            'first_name': 'Mpho',
            'last_name': '',
            'password': 'Mpho2025!',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': False
        }
    ]
    
    print(f"📊 Creating {len(admin_users)} admin accounts\n")
    
    created_count = 0
    updated_count = 0
    error_count = 0
    credentials = []
    
    for user_data in admin_users:
        try:
            username = user_data['username']
            
            # Check if user already exists
            try:
                user = User.objects.get(username=username)
                print(f"📝 Updating existing user: {username}")
                
                # Update user details
                user.set_password(user_data['password'])
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.role = user_data['role']
                user.is_staff = user_data['is_staff']
                user.is_superuser = user_data['is_superuser']
                user.is_active = True
                user.save()
                
                updated_count += 1
                print(f"   ✅ Updated: {username} | Role: {user_data['role']}")
                
            except User.DoesNotExist:
                # Create new user
                user = User.objects.create_user(
                    username=username,
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_staff=user_data['is_staff'],
                    is_superuser=user_data['is_superuser']
                )
                
                # Set the role
                user.role = user_data['role']
                user.save()
                
                created_count += 1
                print(f"   ✅ Created: {username} | Role: {user_data['role']}")
            
            # Store credentials for README
            credentials.append({
                'username': username,
                'password': user_data['password'],
                'full_name': user_data['first_name'],
                'role': user_data['role'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser']
            })
            
            print(f"      Name: {user_data['first_name']}")
            print(f"      Password: {user_data['password']}")
            print(f"      Role: {user_data['role']}")
            print(f"      Staff: {'Yes' if user_data['is_staff'] else 'No'}")
            print(f"      Superuser: {'Yes' if user_data['is_superuser'] else 'No'}")
            print()
            
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error creating user {username}: {e}")
            print()
    
    print("=" * 60)
    print("📈 USER CREATION SUMMARY")
    print("=" * 60)
    print(f"✅ Created: {created_count} new users")
    print(f"🔄 Updated: {updated_count} existing users")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total Processed: {len(admin_users)}")
    
    return credentials

def generate_admin_credentials_readme(credentials):
    """Generate README file with admin credentials"""
    print("\n📝 Generating admin credentials README...")
    
    readme_content = f"""# Admin User Accounts - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This file contains the login credentials for admin accounts in the Food Safety Agency system.

## Account Information

- **Total Admin Users**: {len(credentials)}
- **Password Format**: Name2025!
- **Status**: Active

## Admin Login Credentials

"""
    
    for i, cred in enumerate(credentials, 1):
        readme_content += f"""### {i}. {cred['full_name']} ({cred['role'].upper()})
- **Username**: `{cred['username']}`
- **Password**: `{cred['password']}`
- **Full Name**: {cred['full_name']}
- **Role**: {cred['role']}
- **Staff Access**: {'Yes' if cred['is_staff'] else 'No'}
- **Superuser**: {'Yes' if cred['is_superuser'] else 'No'}

"""
    
    readme_content += f"""
## Role Permissions

### Super Admin (Anthony, Armand)
- Full system access
- Can create, edit, and delete all records
- User management capabilities
- System configuration access
- Database administration

### Administrator (Mpho)
- Administrative access to most features
- Can manage users and inspections
- Limited system configuration access
- Cannot perform superuser operations

## Login Instructions

1. Navigate to the Food Safety Agency login page
2. Enter the username and password from the table above
3. Click "Login" to access the system

## Password Security

- All passwords follow the format: `Name2025!`
- Passwords are case-sensitive
- Users should change their passwords on first login for security

---
*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*
"""
    
    # Write to file
    with open('ADMIN_CREDENTIALS.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Admin credentials saved to: ADMIN_CREDENTIALS.md")
    print(f"📄 Total accounts documented: {len(credentials)}")

def show_admin_credentials(credentials):
    """Show admin credentials in terminal"""
    print("\n\n🔑 ADMIN LOGIN CREDENTIALS")
    print("=" * 60)
    print("Format: Name2025!")
    print("-" * 60)
    
    for i, cred in enumerate(credentials, 1):
        print(f"{i}. {cred['full_name']} ({cred['role'].upper()})")
        print(f"   Username: {cred['username']}")
        print(f"   Password: {cred['password']}")
        print(f"   Role: {cred['role']}")
        print(f"   Superuser: {'Yes' if cred['is_superuser'] else 'No'}")
        print()

if __name__ == "__main__":
    try:
        print("Food Safety Agency - Admin User Creation")
        print("=" * 60)
        
        # Create admin users
        credentials = create_admin_users()
        
        # Generate README file
        generate_admin_credentials_readme(credentials)
        
        # Show credentials in terminal
        show_admin_credentials(credentials)
        
        print("\n🎉 All admin accounts created successfully!")
        print("📄 Check 'ADMIN_CREDENTIALS.md' for complete credentials list.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
