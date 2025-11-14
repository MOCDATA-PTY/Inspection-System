#!/usr/bin/env python3
"""
Create user accounts for all unique inspectors
Password format: InspectorName2025UniqueCode
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

def create_inspector_users():
    """Create user accounts for all inspectors"""
    print("👥 Creating Inspector User Accounts")
    print("=" * 80)
    
    from main.models import FoodSafetyAgencyInspection
    from django.contrib.auth import get_user_model
    from django.db.models import Count
    import re
    
    User = get_user_model()
    
    # Get all unique inspectors with their details
    inspectors = FoodSafetyAgencyInspection.objects.values(
        'inspector_name', 'inspector_id'
    ).annotate(
        inspection_count=Count('id')
    ).exclude(
        inspector_name__isnull=True
    ).exclude(
        inspector_name=''
    ).exclude(
        inspector_name='Unknown'
    ).order_by('-inspection_count')
    
    print(f"📊 Found {len(inspectors)} unique inspectors to create accounts for\n")
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    for inspector in inspectors:
        inspector_name = inspector['inspector_name']
        inspector_id = inspector['inspector_id'] or 'NOID'
        inspection_count = inspector['inspection_count']
        
        try:
            # Create username from inspector name (remove spaces, special chars)
            username = re.sub(r'[^a-zA-Z0-9]', '', inspector_name.lower())
            
            # Create password: InspectorName2025UniqueCode
            # Remove spaces and special chars from name for password
            clean_name = re.sub(r'[^a-zA-Z0-9]', '', inspector_name)
            password = f"{clean_name}2025{inspector_id}"
            
            # Check if user already exists
            try:
                user = User.objects.get(username=username)
                print(f"📝 Updating existing user: {username}")
                
                # Update password and role
                user.set_password(password)
                user.role = 'inspector'
                user.first_name = inspector_name.split()[0] if inspector_name.split() else inspector_name
                user.last_name = ' '.join(inspector_name.split()[1:]) if len(inspector_name.split()) > 1 else ''
                user.save()
                
                updated_count += 1
                print(f"   ✅ Updated: {username} | Password: {password}")
                
            except User.DoesNotExist:
                # Create new user
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=inspector_name.split()[0] if inspector_name.split() else inspector_name,
                    last_name=' '.join(inspector_name.split()[1:]) if len(inspector_name.split()) > 1 else '',
                    role='inspector'
                )
                
                created_count += 1
                print(f"   ✅ Created: {username} | Password: {password}")
            
            print(f"      Inspector Name: {inspector_name}")
            print(f"      Inspector ID: {inspector_id}")
            print(f"      Inspections: {inspection_count}")
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
    print(f"📊 Total Processed: {len(inspectors)}")
    
    # Show all inspector users
    print(f"\n👥 ALL INSPECTOR USER ACCOUNTS:")
    print("-" * 50)
    
    inspector_users = User.objects.filter(role='inspector').order_by('username')
    for i, user in enumerate(inspector_users, 1):
        full_name = f"{user.first_name} {user.last_name}".strip()
        print(f"{i:2d}. Username: {user.username}")
        print(f"     Name: {full_name}")
        print(f"     Role: {user.role}")
        print(f"     Active: {'Yes' if user.is_active else 'No'}")
        print()

def show_login_credentials():
    """Show login credentials for all inspector users"""
    print("\n\n🔑 INSPECTOR LOGIN CREDENTIALS")
    print("=" * 80)
    print("Format: InspectorName2025UniqueCode")
    print("-" * 80)
    
    from django.contrib.auth import get_user_model
    from main.models import FoodSafetyAgencyInspection
    
    User = get_user_model()
    
    # Get inspector users with their corresponding inspector data
    inspector_users = User.objects.filter(role='inspector').order_by('username')
    
    for user in inspector_users:
        # Find corresponding inspector data
        full_name = f"{user.first_name} {user.last_name}".strip()
        
        try:
            inspector_data = FoodSafetyAgencyInspection.objects.filter(
                inspector_name__icontains=user.first_name
            ).values('inspector_name', 'inspector_id').distinct().first()
            
            if inspector_data:
                inspector_id = inspector_data['inspector_id'] or 'NOID'
                clean_name = re.sub(r'[^a-zA-Z0-9]', '', inspector_data['inspector_name'])
                expected_password = f"{clean_name}2025{inspector_id}"
                
                print(f"👤 {full_name}")
                print(f"   Username: {user.username}")
                print(f"   Password: {expected_password}")
                print(f"   Inspector ID: {inspector_id}")
                print()
        except:
            print(f"👤 {full_name}")
            print(f"   Username: {user.username}")
            print(f"   Password: [Check manually]")
            print()

if __name__ == "__main__":
    try:
        create_inspector_users()
        show_login_credentials()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
