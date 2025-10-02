#!/usr/bin/env python3
"""
Create additional user accounts and generate README with all credentials
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def create_additional_users():
    """Create the additional user accounts"""
    print("👥 Creating Additional User Accounts")
    print("=" * 60)
    
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Define additional users
    additional_users = [
        {
            'username': 'armand',
            'password': 'Armand2025SuperAdmin',
            'first_name': 'Armand',
            'last_name': '',
            'role': 'super_admin',
            'email': 'armand@foodsafetyagency.com'
        },
        {
            'username': 'anthony',
            'password': 'Anthony2025SuperAdmin',
            'first_name': 'Anthony',
            'last_name': '',
            'role': 'super_admin',
            'email': 'anthony@foodsafetyagency.com'
        },
        {
            'username': 'christina',
            'password': 'Christina2025LabTech',
            'first_name': 'Christina',
            'last_name': '',
            'role': 'scientist',
            'email': 'christina@foodsafetyagency.com'
        },
        {
            'username': 'mpho',
            'password': 'Mpho2025Admin',
            'first_name': 'Mpho',
            'last_name': '',
            'role': 'admin',
            'email': 'mpho@foodsafetyagency.com'
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for user_data in additional_users:
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
                user.email = user_data['email']
                user.is_active = True
                user.save()
                
                updated_count += 1
                print(f"   ✅ Updated: {username} | Role: {user_data['role']}")
                
            except User.DoesNotExist:
                # Create new user
                user = User.objects.create_user(
                    username=user_data['username'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    role=user_data['role']
                )
                
                created_count += 1
                print(f"   ✅ Created: {username} | Role: {user_data['role']}")
            
            print(f"      Password: {user_data['password']}")
            print(f"      Email: {user_data['email']}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error creating user {user_data['username']}: {e}")
            print()
    
    print("=" * 60)
    print(f"✅ Created: {created_count} new users")
    print(f"🔄 Updated: {updated_count} existing users")
    
    return created_count, updated_count

def generate_readme():
    """Generate README with all user credentials"""
    print("\n📝 Generating README with User Credentials")
    print("=" * 60)
    
    from django.contrib.auth import get_user_model
    from main.models import FoodSafetyAgencyInspection
    import re
    
    User = get_user_model()
    
    readme_content = """# Food Safety Agency - User Accounts

This document contains all user accounts and their login credentials for the Food Safety Agency system.

## 🔐 Login URL
```
http://127.0.0.1:8000/login/
```

## 👥 User Accounts by Role

### 🔴 Super Administrators
Super admins have full system access including user management, settings, and all features.

| Name | Username | Password | Email |
|------|----------|----------|-------|
| Armand | `armand` | `Armand2025SuperAdmin` | armand@foodsafetyagency.com |
| Anthony | `anthony` | `Anthony2025SuperAdmin` | anthony@foodsafetyagency.com |

### 🟡 Administrators  
Administrators have most system access but limited user management.

| Name | Username | Password | Email |
|------|----------|----------|-------|
| Mpho | `mpho` | `Mpho2025Admin` | mpho@foodsafetyagency.com |

### 🧪 Lab Technicians (Scientists)
Lab technicians can only see inspections where samples were taken.

| Name | Username | Password | Email |
|------|----------|----------|-------|
| Christina | `christina` | `Christina2025LabTech` | christina@foodsafetyagency.com |

### 👮 Inspectors
Inspectors can only see their own inspections and have limited editing capabilities.

| Inspector Name | Username | Password | Inspector ID | Inspections |
|---------------|----------|----------|--------------|-------------|
"""
    
    # Get all inspector users and their details
    inspector_users = User.objects.filter(role='inspector').order_by('first_name')
    
    for user in inspector_users:
        full_name = f"{user.first_name} {user.last_name}".strip()
        
        # Skip non-inspector accounts that might have inspector role
        if user.username in ['admin', 'test_inspector']:
            continue
            
        try:
            # Find corresponding inspector data to get the password
            inspector_data = FoodSafetyAgencyInspection.objects.filter(
                inspector_name=full_name
            ).values('inspector_name', 'inspector_id').distinct().first()
            
            if inspector_data:
                inspector_id = inspector_data['inspector_id'] or 'NOID'
                clean_name = re.sub(r'[^a-zA-Z0-9]', '', inspector_data['inspector_name'])
                password = f"{clean_name}2025{inspector_id}"
                
                # Get inspection count
                inspection_count = FoodSafetyAgencyInspection.objects.filter(
                    inspector_name=full_name
                ).count()
                
                readme_content += f"| {full_name} | `{user.username}` | `{password}` | {inspector_id} | {inspection_count:,} |\n"
            
        except Exception as e:
            readme_content += f"| {full_name} | `{user.username}` | [Error getting password] | - | - |\n"
    
    readme_content += """
### 🔧 Developer Accounts
Developer accounts have full system access including compliance document management.

| Name | Username | Password | Role |
|------|----------|----------|------|
| Developer | `developer` | [Existing Password] | developer |

## 📋 Role Permissions

### 🔴 Super Admin (`super_admin`)
- ✅ Full system access
- ✅ User management (create, edit, delete users)
- ✅ System settings
- ✅ All inspections (view, edit, delete)
- ✅ Client management
- ✅ File uploads and downloads
- ✅ System logs
- ✅ Analytics and reports

### 🟡 Admin (`admin`)
- ✅ Most system access
- ✅ Limited user management
- ✅ All inspections (view, edit)
- ✅ Client management  
- ✅ File uploads and downloads
- ✅ System logs
- ✅ Analytics and reports
- ❌ Cannot delete inspections
- ❌ Limited system settings

### 👮 Inspector (`inspector`)
- ✅ View own inspections only
- ✅ Edit own inspection details
- ✅ Upload documents for own inspections
- ❌ Cannot see other inspectors' work
- ❌ No user management
- ❌ No system settings
- ❌ No client management

### 🧪 Scientist/Lab Technician (`scientist`)
- ✅ View inspections with samples only
- ✅ Edit lab-related fields
- ✅ Upload lab results
- ❌ Cannot see non-sampled inspections
- ❌ No user management
- ❌ Limited system access

### 🔧 Developer (`developer`)
- ✅ Full system access
- ✅ Compliance document management
- ✅ Performance monitoring
- ✅ System debugging tools
- ✅ All admin capabilities

## 🚀 Getting Started

1. **Go to**: http://127.0.0.1:8000/login/
2. **Enter credentials** from the tables above
3. **Access your role-specific features**

## 📧 System Logging

All user activities are logged in the System Logs, including:
- Login/logout events
- Sent status changes
- File uploads
- Data modifications
- User management actions

Access System Logs at: http://127.0.0.1:8000/system-logs/

## 🔄 Password Policy

- **Inspector passwords**: `InspectorName2025InspectorID`
- **Admin passwords**: `Name2025Role`
- **All passwords are case-sensitive**
- **No special characters in passwords for simplicity**

---
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # Write README file
    try:
        with open('USER_ACCOUNTS_README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ README file created: USER_ACCOUNTS_README.md")
        return True
    except Exception as e:
        print(f"❌ Error creating README: {e}")
        return False

if __name__ == "__main__":
    try:
        # Create additional users
        created, updated = create_additional_users()
        
        # Generate README
        if generate_readme():
            print(f"\n🎉 SUCCESS: Created {created} users, updated {updated} users")
            print("📄 All credentials saved to USER_ACCOUNTS_README.md")
        else:
            print("\n⚠️ Users created but README generation failed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
