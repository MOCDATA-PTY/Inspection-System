#!/usr/bin/env python3
"""
OneDrive Integration Setup Script for Ubuntu Server
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.services.onedrive_service import OneDriveService

def setup_onedrive():
    """Setup OneDrive integration."""
    print("🚀 Personal OneDrive Integration Setup (Local Development)")
    print("=" * 60)
    
    print("\n📋 Prerequisites:")
    print("1. Create an Azure App Registration")
    print("2. Get Client ID and Client Secret")
    print("3. Set redirect URI to: http://localhost:8000/onedrive/callback")
    
    print("\n🔧 Configuration Steps:")
    print("1. Go to Azure Portal > App Registrations")
    print("2. Create new registration")
    print("3. Add redirect URI: http://localhost:8000/onedrive/callback")
    print("4. Get Client ID and Secret")
    print("5. Grant API permissions: Files.ReadWrite.All")
    
    print("\n⚙️ Update settings.py with your credentials:")
    print("ONEDRIVE_CLIENT_ID = 'your_client_id'")
    print("ONEDRIVE_CLIENT_SECRET = 'your_client_secret'")
    print("ONEDRIVE_REDIRECT_URI = 'http://localhost:8000/onedrive/callback'")
    print("ONEDRIVE_FOLDER = 'Legal-System-Media'  # Your personal OneDrive folder")
    
    print("\n📦 Install requirements:")
    print("pip install -r requirements_onedrive.txt")
    
    print("\n✅ Setup complete! Files will be saved locally and synced to your personal OneDrive.")
    print("\n🌐 For production deployment, change ONEDRIVE_REDIRECT_URI to your domain.")

if __name__ == "__main__":
    setup_onedrive()
