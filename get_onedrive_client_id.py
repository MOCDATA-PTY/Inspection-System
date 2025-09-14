#!/usr/bin/env python
"""
Quick script to get your Azure Application (client) ID
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

print("🔍 OneDrive Configuration Check")
print("=" * 40)
print(f"ONEDRIVE_CLIENT_ID: {getattr(settings, 'ONEDRIVE_CLIENT_ID', 'Not set')}")
print(f"ONEDRIVE_CLIENT_SECRET: {'*' * 20 if getattr(settings, 'ONEDRIVE_CLIENT_SECRET', '') else 'Not set'}")
print(f"ONEDRIVE_REDIRECT_URI: {getattr(settings, 'ONEDRIVE_REDIRECT_URI', 'Not set')}")
print(f"ONEDRIVE_ENABLED: {getattr(settings, 'ONEDRIVE_ENABLED', False)}")

print("\n📋 Next Steps:")
print("1. Go to Azure Portal → App registrations → OneDriveAppIntegration")
print("2. Copy the 'Application (client) ID' from the Overview page")
print("3. Replace 'your_client_id_here' in mysite/settings.py with your actual Client ID")
print("4. Run this script again to verify the setup")
