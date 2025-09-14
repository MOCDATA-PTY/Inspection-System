#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import InspectorMapping
from django.contrib.auth.models import User

def remove_fake_data():
    """Remove fake inspector mappings and users"""
    
    print("Removing fake inspector mappings...")
    
    # Remove fake inspector mappings
    fake_mappings = InspectorMapping.objects.filter(
        inspector_id__in=[120202, 120203, 120204, 120205, 120206]
    )
    
    if fake_mappings.exists():
        print(f"Removing {fake_mappings.count()} fake mappings...")
        fake_mappings.delete()
        print("✓ Fake mappings removed")
    else:
        print("No fake mappings found")
    
    # Remove fake users
    fake_usernames = ['ethan', 'john_smith', 'sarah_johnson', 'mike_wilson', 'lisa_brown']
    fake_users = User.objects.filter(username__in=fake_usernames)
    
    if fake_users.exists():
        print(f"Removing {fake_users.count()} fake users...")
        fake_users.delete()
        print("✓ Fake users removed")
    else:
        print("No fake users found")
    
    print("Cleanup complete!")

if __name__ == "__main__":
    remove_fake_data()
