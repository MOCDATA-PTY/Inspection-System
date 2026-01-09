#!/usr/bin/env python3
"""
Create user accounts for all inspectors from the terminal output
Password format: InspectorName2025!
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

def create_all_inspectors():
    """Create user accounts for all inspectors from the terminal output"""
    print("👥 Creating All Inspector User Accounts")
    print("=" * 80)
    
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # All inspectors from the terminal output
    inspectors_data = [
        # MEAT INSPECTORS
        {"name": "BEN VISAGIE", "inspections": 286, "category": "MEAT"},
        {"name": "GLADYS MANGANYE", "inspections": 184, "category": "MEAT"},
        {"name": "THATO SEKHOTHO", "inspections": 142, "category": "MEAT"},
        {"name": "PERCY MALEKA", "inspections": 130, "category": "MEAT"},
        {"name": "CINGA NGONGO", "inspections": 129, "category": "MEAT"},
        {"name": "SANDISIWE DLISANI", "inspections": 89, "category": "MEAT"},
        {"name": "XOLA MPELUZA", "inspections": 88, "category": "MEAT"},
        {"name": "KUTLWANO KUNTWANE", "inspections": 60, "category": "MEAT"},
        {"name": "NELISA NTOYAPHI", "inspections": 55, "category": "MEAT"},
        {"name": "JOFRED STEYN", "inspections": 18, "category": "MEAT"},
        {"name": "NEO NOE", "inspections": 17, "category": "MEAT"},
        {"name": "LWANDILE MAQINA", "inspections": 14, "category": "MEAT"},
        {"name": "MOKGADI SELONE", "inspections": 14, "category": "MEAT"},
        
        # EGGS INSPECTORS (same people, different category)
        {"name": "BEN VISAGIE", "inspections": 286, "category": "EGGS"},
        {"name": "GLADYS MANGANYE", "inspections": 184, "category": "EGGS"},
        {"name": "THATO SEKHOTHO", "inspections": 142, "category": "EGGS"},
        {"name": "PERCY MALEKA", "inspections": 130, "category": "EGGS"},
        {"name": "CINGA NGONGO", "inspections": 129, "category": "EGGS"},
        {"name": "SANDISIWE DLISANI", "inspections": 89, "category": "EGGS"},
        {"name": "XOLA MPELUZA", "inspections": 88, "category": "EGGS"},
        {"name": "KUTLWANO KUNTWANE", "inspections": 60, "category": "EGGS"},
        {"name": "NELISA NTOYAPHI", "inspections": 55, "category": "EGGS"},
        {"name": "JOFRED STEYN", "inspections": 18, "category": "EGGS"},
        {"name": "NEO NOE", "inspections": 17, "category": "EGGS"},
        {"name": "LWANDILE MAQINA", "inspections": 14, "category": "EGGS"},
        {"name": "MOKGADI SELONE", "inspections": 14, "category": "EGGS"},
    ]
    
    # Get unique inspectors (remove duplicates)
    unique_inspectors = {}
    for inspector in inspectors_data:
        name = inspector["name"]
        if name not in unique_inspectors:
            unique_inspectors[name] = inspector
        else:
            # Keep the one with more inspections
            if inspector["inspections"] > unique_inspectors[name]["inspections"]:
                unique_inspectors[name] = inspector
    
    print(f"📊 Found {len(unique_inspectors)} unique inspectors to create accounts for\n")
    
    created_count = 0
    updated_count = 0
    error_count = 0
    credentials = []
    
    for inspector_name, inspector_data in unique_inspectors.items():
        try:
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
                'inspections': inspector_data['inspections'],
                'category': inspector_data['category']
            })
            
            print(f"      Inspector Name: {inspector_name}")
            print(f"      Inspections: {inspector_data['inspections']}")
            print(f"      Category: {inspector_data['category']}")
            print(f"      Role: inspector")
            print()
            
        except Exception as e:
            error_count += 1
            print(f"   ❌ Error creating user for {inspector_name}: {e}")
            print()
    
    print("=" * 80)
    print("📈 USER CREATION SUMMARY")
    print("=" * 80)
    print(f"✅ Created: {created_count} new users")
    print(f"🔄 Updated: {updated_count} existing users")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total Processed: {len(unique_inspectors)}")
    
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
- **Category**: {cred['category']}
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
    print("=" * 80)
    print("Format: InspectorName2025!")
    print("-" * 80)
    
    # Sort by inspection count
    sorted_credentials = sorted(credentials, key=lambda x: x['inspections'], reverse=True)
    
    for i, cred in enumerate(sorted_credentials, 1):
        print(f"{i:2d}. {cred['full_name']}")
        print(f"     Username: {cred['username']}")
        print(f"     Password: {cred['password']}")
        print(f"     Inspections: {cred['inspections']}")
        print(f"     Category: {cred['category']}")
        print()

if __name__ == "__main__":
    try:
        print("Food Safety Agency - Inspector Account Creation")
        print("=" * 80)
        
        # Create all inspector accounts
        credentials = create_all_inspectors()
        
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
