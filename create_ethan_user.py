#!/usr/bin/env python3
"""
Create Ethan user account with developer role
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

def create_ethan_user():
    """Create Ethan user account with developer role"""
    print("👨‍💻 Creating Ethan Developer Account")
    print("=" * 50)
    
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    user_data = {
        'username': 'ethan',
        'password': 'Ethan2025Developer',
        'first_name': 'Ethan',
        'last_name': '',
        'role': 'developer',
        'email': 'ethan@foodsafetyagency.com'
    }
    
    try:
        # Check if user already exists
        try:
            user = User.objects.get(username='ethan')
            print(f"📝 Updating existing user: ethan")
            
            # Update user details
            user.set_password(user_data['password'])
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.role = user_data['role']
            user.email = user_data['email']
            user.is_active = True
            user.save()
            
            print(f"   ✅ Updated: ethan | Role: developer")
            action = "updated"
            
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
            
            print(f"   ✅ Created: ethan | Role: developer")
            action = "created"
        
        print(f"      Password: {user_data['password']}")
        print(f"      Email: {user_data['email']}")
        print(f"      Full Access: Yes")
        print()
        
        print("🔧 Developer Role Permissions:")
        print("   ✅ Full system access")
        print("   ✅ Compliance document management")
        print("   ✅ Performance monitoring")
        print("   ✅ System debugging tools")
        print("   ✅ All admin capabilities")
        print("   ✅ User management")
        print()
        
        return True, action
        
    except Exception as e:
        print(f"   ❌ Error creating user ethan: {e}")
        return False, "error"

def update_readme():
    """Update the README file to include Ethan"""
    print("📝 Updating README with Ethan's account")
    print("=" * 50)
    
    try:
        # Read existing README
        with open('USER_ACCOUNTS_README.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the Developer Accounts section and update it
        developer_section = """### 🔧 Developer Accounts
Developer accounts have full system access including compliance document management.

| Name | Username | Password | Role | Email |
|------|----------|----------|------|-------|
| Ethan | `ethan` | `Ethan2025Developer` | developer | ethan@foodsafetyagency.com |
| Developer | `developer` | [Existing Password] | developer | - |"""
        
        # Replace the existing developer section
        import re
        pattern = r'### 🔧 Developer Accounts.*?(?=\n## |\n### |\Z)'
        updated_content = re.sub(pattern, developer_section, content, flags=re.DOTALL)
        
        # Write updated README
        with open('USER_ACCOUNTS_README.md', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ README updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating README: {e}")
        return False

if __name__ == "__main__":
    try:
        success, action = create_ethan_user()
        
        if success:
            print(f"✅ Ethan account {action} successfully")
            
            if update_readme():
                print("📄 README updated with Ethan's credentials")
            else:
                print("⚠️ User created but README update failed")
        else:
            print("❌ Failed to create Ethan account")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
