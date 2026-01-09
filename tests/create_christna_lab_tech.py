#!/usr/bin/env python
"""
Script to create a lab technician account for Christna.
Run this script with: python create_christna_lab_tech.py
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

def create_christna_lab_tech():
    """Create a lab technician account for Christna."""
    
    # Lab technician credentials
    username = "Christna"
    email = "christna@foodsafety.com"
    password = "Christna2025!"
    first_name = "Christna"
    last_name = ""
    role = "scientist"  # Lab technician role
    
    try:
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"User '{username}' already exists. Skipping user creation.")
            user = User.objects.get(username=username)
        else:
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role  # Set role to scientist (lab technician)
            )
            print(f"✅ Created user: {username}")
        
        print("\n" + "="*50)
        print("🎯 LAB TECHNICIAN CREDENTIALS:")
        print("="*50)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Email: {email}")
        print(f"Full Name: {first_name} {last_name}")
        print(f"Role: Lab Technician (Scientist)")
        print("="*50)
        print("\n📝 INSTRUCTIONS:")
        print("1. Login with these credentials")
        print("2. Lab technicians can access scientist features")
        print("3. Lab technicians can upload lab results and forms")
        print("4. Lab technicians can view all inspections")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating lab technician: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Creating lab technician account for Christna...")
    success = create_christna_lab_tech()
    
    if success:
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed!")
