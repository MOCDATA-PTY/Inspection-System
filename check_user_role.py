#!/usr/bin/env python3
"""
Check and update user role
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def check_and_update_role():
    try:
        user = User.objects.get(username='developer')
        print(f"Current role: {getattr(user, 'role', 'Not Set')}")
        
        # Update role if not set
        if not hasattr(user, 'role') or not user.role:
            user.role = 'developer'
            user.save()
            print("Updated role to: developer")
        
    except User.DoesNotExist:
        print("User 'developer' not found")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    check_and_update_role()