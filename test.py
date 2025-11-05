#!/usr/bin/env python3
"""
Test script to display all users in the database with their roles
Shows which users are inspectors and displays all user information
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model
from main.models import InspectorMapping

User = get_user_model()

if __name__ == '__main__':
    print("=" * 100)
    print("ALL USERS IN DATABASE WITH ROLES")
    print("=" * 100)
    print()

    users = User.objects.all().order_by('username')
    
    # Get all inspector mappings
    inspector_mappings = InspectorMapping.objects.all()
    inspector_id_map = {}
    for mapping in inspector_mappings:
        inspector_id_map[mapping.inspector_name] = mapping.inspector_id

    if not users:
        print("No users found in database.")
    else:
        print(f"Total Users: {users.count()}")
        print()
        
        # Count users by role
        role_counts = {}
        inspectors = []
        
        for user in users:
            role = getattr(user, 'role', 'inspector')
            role_counts[role] = role_counts.get(role, 0) + 1
            if role == 'inspector':
                inspectors.append(user)
        
        print("=" * 100)
        print("ROLE SUMMARY")
        print("=" * 100)
        role_display = {
            'inspector': 'Inspector',
            'admin': 'HR/Admin Staff',
            'super_admin': 'Super Admin',
            'financial': 'Financial',
            'scientist': 'Scientist',
            'developer': 'Developer',
        }
        for role, count in sorted(role_counts.items()):
            display_name = role_display.get(role, role.title())
            print(f"  {display_name:20s}: {count}")
        print()
        print(f"  Total Inspectors: {len(inspectors)}")
        print()
        
        print("=" * 100)
        print("ALL USERS DETAILED LIST")
        print("=" * 100)
        print()

        for i, user in enumerate(users, 1):
            role = getattr(user, 'role', 'inspector')
            is_inspector = role == 'inspector'
            
            # Mark inspectors with special indicator
            inspector_marker = " [INSPECTOR]" if is_inspector else ""
            
            print(f"{i}. User ID: {user.id}{inspector_marker}")
            print(f"   Username: {user.username}")
            print(f"   Full Name: {user.get_full_name() or 'N/A'}")
            print(f"   First Name: {user.first_name or 'N/A'}")
            print(f"   Last Name: {user.last_name or 'N/A'}")
            print(f"   Email: {user.email or 'N/A'}")
            
            # Role information
            role_display_name = role_display.get(role, role.title())
            print(f"   Role: {role_display_name} ({role})")
            
            # Additional user fields
            phone_number = getattr(user, 'phone_number', None)
            if phone_number:
                print(f"   Phone: {phone_number}")
            
            department = getattr(user, 'department', None)
            if department:
                print(f"   Department: {department}")
            
            employee_id = getattr(user, 'employee_id', None)
            if employee_id:
                print(f"   Employee ID: {employee_id}")
            
            # Inspector-specific information
            if is_inspector:
                full_name = user.get_full_name() or user.username
                inspector_id = inspector_id_map.get(full_name)
                if inspector_id:
                    print(f"   Inspector ID: {inspector_id}")
                else:
                    print(f"   Inspector ID: Not mapped")
            
            # Status flags
            print(f"   Is Active: {user.is_active}")
            print(f"   Is Staff: {user.is_staff}")
            print(f"   Is Superuser: {user.is_superuser}")
            
            # Dates
            print(f"   Date Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else 'N/A'}")
            print(f"   Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}")
            print()

        print("=" * 100)
        print("INSPECTORS ONLY")
        print("=" * 100)
        print()
        
        if inspectors:
            for i, inspector in enumerate(inspectors, 1):
                full_name = inspector.get_full_name() or inspector.username
                inspector_id = inspector_id_map.get(full_name)
                
                print(f"{i}. {full_name}")
                print(f"   Username: {inspector.username}")
                print(f"   Email: {inspector.email or 'N/A'}")
                if inspector_id:
                    print(f"   Inspector ID: {inspector_id}")
                else:
                    print(f"   Inspector ID: Not mapped")
                print(f"   Employee ID: {getattr(inspector, 'employee_id', 'N/A')}")
                print(f"   Active: {inspector.is_active}")
                print()
        else:
            print("No inspectors found in database.")
            print()

    print("=" * 100)
