#!/usr/bin/env python3
"""
Create simple inspector user accounts
Just name, password, and inspection count - no extra fields
"""

import os
import sys
import django
from pathlib import Path
import re
from datetime import datetime

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

def create_simple_inspectors():
    """Create simple inspector user accounts"""
    print("👥 Creating Simple Inspector User Accounts")
    print("=" * 60)
    
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Inspector data from terminal output
    inspectors = [
        {"name": "BEN VISAGIE", "inspections": 286},
        {"name": "GLADYS MANGANYE", "inspections": 184},
        {"name": "THATO SEKHOTHO", "inspections": 142},
        {"name": "PERCY MALEKA", "inspections": 130},
        {"name": "CINGA NGONGO", "inspections": 129},
        {"name": "SANDISIWE DLISANI", "inspections": 89},
        {"name": "XOLA MPELUZA", "inspections": 88},
        {"name": "KUTLWANO KUNTWANE", "inspections": 60},
        {"name": "NELISA NTOYAPHI", "inspections": 55},
        {"name": "JOFRED STEYN", "inspections": 18},
        {"name": "NEO NOE", "inspections": 17},
        {"name": "LWANDILE MAQINA", "inspections": 14},
        {"name": "MOKGADI SELONE", "inspections": 14},
    ]
    
    print(f"📊 Creating {len(inspectors)} inspector accounts\n")
    
    created_count = 0
    updated_count = 0
    error_count = 0
    credentials = []
    
    for inspector in inspectors:
        try:
            inspector_name = inspector["name"]
            inspection_count = inspector["inspections"]
            
            # Create username from inspector name (remove spaces, special chars)
            username = re.sub(r'[^a-zA-Z0-9]', '', inspector_name.lower())
            
            # Create password: InspectorName2025!
            clean_name = re.sub(r'[^a-zA-Z0-9]', '', inspector_name)
            password = f"{clean_name}2025!"
            
            # Split name into first and last
            name_parts = inspector_name.split()
            first_name = name_parts[0] if name_parts else inspector_name
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            # Check if user already exists
            try:
                user = User.objects.get(username=username)
                print(f"📝 Updating existing user: {username}")
                
                # Update password and role
                user.set_password(password)
                user.role = 'inspector'
                user.first_name = first_name
                user.last_name = last_name
                user.is_active = True
                user.save()
                
                updated_count += 1
                print(f"   ✅ Updated: {username} | Password: {password}")
                
            except User.DoesNotExist:
                # Create new user
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role='inspector',
                    is_active=True
                )
                
                created_count += 1
                print(f"   ✅ Created: {username} | Password: {password}")
            
            # Store credentials for README
            credentials.append({
                'username': username,
                'password': password,
                'full_name': inspector_name,
                'first_name': first_name,
                'last_name': last_name,
                'inspections': inspection_count
            })
            
            print(f"      Name: {inspector_name}")
            print(f"      Inspections: {inspection_count}")
            print(f"      Role: inspector")
            print()
            
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error creating user for {inspector_name}: {e}")
            print()
    
    print("=" * 60)
    print("📈 USER CREATION SUMMARY")
    print("=" * 60)
    print(f"✅ Created: {created_count} new users")
    print(f"🔄 Updated: {updated_count} existing users")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total Processed: {len(inspectors)}")
    
    return credentials

def generate_credentials_readme(credentials):
    """Generate README file with all inspector credentials"""
    print("\n📝 Generating credentials README...")
    
    readme_content = f"""# Inspector User Accounts - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This file contains the login credentials for all inspector accounts in the Food Safety Agency system.

## Account Information

- **Total Inspectors**: {len(credentials)}
- **Password Format**: InspectorName2025!
- **Role**: inspector
- **Status**: Active

## Inspector Login Credentials

"""
    
    # Sort credentials by inspection count (descending)
    sorted_credentials = sorted(credentials, key=lambda x: x['inspections'], reverse=True)
    
    for i, cred in enumerate(sorted_credentials, 1):
        readme_content += f"""### {i}. {cred['full_name']}
- **Username**: `{cred['username']}`
- **Password**: `{cred['password']}`
- **Full Name**: {cred['full_name']}
- **Inspections**: {cred['inspections']}
- **Role**: inspector

"""
    
    readme_content += f"""
## Login Instructions

1. Navigate to the Food Safety Agency login page
2. Enter the username and password from the table above
3. Click "Login" to access the system

## Password Security

- All passwords follow the format: `InspectorName2025!`
- Passwords are case-sensitive
- Users should change their passwords on first login for security

## Account Management

- All accounts are set to 'inspector' role
- All accounts are active and ready to use
- Contact system administrator for any account issues

---
*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*
"""
    
    # Write to file
    with open('INSPECTOR_CREDENTIALS.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Credentials saved to: INSPECTOR_CREDENTIALS.md")
    print(f"📄 Total accounts documented: {len(credentials)}")

def show_login_credentials(credentials):
    """Show login credentials for all inspector users"""
    print("\n\n🔑 INSPECTOR LOGIN CREDENTIALS")
    print("=" * 60)
    print("Format: InspectorName2025!")
    print("-" * 60)
    
    # Sort by inspection count
    sorted_credentials = sorted(credentials, key=lambda x: x['inspections'], reverse=True)
    
    for i, cred in enumerate(sorted_credentials, 1):
        print(f"{i:2d}. {cred['full_name']}")
        print(f"     Username: {cred['username']}")
        print(f"     Password: {cred['password']}")
        print(f"     Inspections: {cred['inspections']}")
        print()

if __name__ == "__main__":
    try:
        print("Food Safety Agency - Simple Inspector Account Creation")
        print("=" * 60)
        
        # Create all inspector accounts
        credentials = create_simple_inspectors()
        
        # Generate README file
        generate_credentials_readme(credentials)
        
        # Show credentials in terminal
        show_login_credentials(credentials)
        
        print("\n🎉 All inspector accounts created successfully!")
        print("📄 Check 'INSPECTOR_CREDENTIALS.md' for complete credentials list.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
