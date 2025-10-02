#!/usr/bin/env python3
"""
Check and Create OneDrive Folder Structure
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def check_onedrive_structure():
    """Check and create OneDrive folder structure."""
    print("🔍 Checking OneDrive Folder Structure")
    print("=" * 60)
    
    try:
        # Load saved tokens
        token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
        
        if not os.path.exists(token_file):
            print("❌ No OneDrive tokens found")
            return False
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        access_token = token_data.get('access_token')
        
        if not access_token:
            print("❌ No access token found")
            return False
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Check if Legal-System-Media folder exists
        onedrive_base = getattr(settings, 'ONEDRIVE_FOLDER', 'Legal-System-Media')
        print(f"📁 Checking for base folder: {onedrive_base}")
        
        # List root items to see what's there
        root_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        response = requests.get(root_url, headers=headers)
        
        if response.status_code == 200:
            items = response.json().get('value', [])
            print(f"📋 Found {len(items)} items in root:")
            
            base_folder_exists = False
            for item in items:
                print(f"  - {item.get('name', 'Unknown')} ({item.get('@microsoft.graph.downloadUrl', 'No URL')})")
                if item.get('name') == onedrive_base:
                    base_folder_exists = True
                    print(f"    ✅ Base folder '{onedrive_base}' found!")
            
            if not base_folder_exists:
                print(f"❌ Base folder '{onedrive_base}' not found")
                print("🔧 Creating base folder...")
                
                # Create the base folder
                create_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
                folder_data = {
                    'name': onedrive_base,
                    'folder': {},
                    '@microsoft.graph.conflictBehavior': 'replace'
                }
                
                create_response = requests.post(create_url, json=folder_data, headers=headers)
                
                if create_response.status_code in [200, 201]:
                    print(f"✅ Created base folder: {onedrive_base}")
                    base_folder_exists = True
                else:
                    print(f"❌ Failed to create base folder: {create_response.status_code} - {create_response.text}")
                    return False
            
            # Now check the structure inside Legal-System-Media
            if base_folder_exists:
                print(f"\n📁 Checking structure inside '{onedrive_base}':")
                
                # Get the folder ID for Legal-System-Media
                folder_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{onedrive_base}:/children"
                folder_response = requests.get(folder_url, headers=headers)
                
                if folder_response.status_code == 200:
                    folder_items = folder_response.json().get('value', [])
                    print(f"📋 Found {len(folder_items)} items in '{onedrive_base}':")
                    
                    for item in folder_items:
                        print(f"  - {item.get('name', 'Unknown')} ({item.get('@microsoft.graph.downloadUrl', 'No URL')})")
                        
                        # If it's a folder, check its contents
                        if item.get('folder'):
                            subfolder_name = item.get('name')
                            subfolder_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{onedrive_base}/{subfolder_name}:/children"
                            subfolder_response = requests.get(subfolder_url, headers=headers)
                            
                            if subfolder_response.status_code == 200:
                                subfolder_items = subfolder_response.json().get('value', [])
                                print(f"    📁 '{subfolder_name}' contains {len(subfolder_items)} items:")
                                for subitem in subfolder_items[:5]:  # Show first 5 items
                                    print(f"      - {subitem.get('name', 'Unknown')}")
                                if len(subfolder_items) > 5:
                                    print(f"      ... and {len(subfolder_items) - 5} more items")
                else:
                    print(f"❌ Failed to access '{onedrive_base}' folder: {folder_response.status_code}")
                    return False
        
        else:
            print(f"❌ Failed to access root: {response.status_code}")
            return False
        
        print("\n✅ OneDrive structure check complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking OneDrive structure: {e}")
        return False

if __name__ == "__main__":
    success = check_onedrive_structure()
    if success:
        print("\n🎉 OneDrive structure is ready!")
    else:
        print("\n❌ OneDrive structure check failed")
