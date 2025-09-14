#!/usr/bin/env python3
"""
Clean up OneDrive folder structure and recreate it properly
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

def cleanup_onedrive_structure():
    """Clean up OneDrive folder structure and recreate it properly."""
    print("🧹 Cleaning up OneDrive folder structure")
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
        
        # Delete the problematic Legal-System-Media folder and its contents
        print("🗑️ Cleaning up existing structure...")
        
        # Delete the nested Legal-System-Media folder
        delete_url = "https://graph.microsoft.com/v1.0/me/drive/root:/Legal-System-Media/Legal-System-Media"
        delete_response = requests.delete(delete_url, headers=headers)
        if delete_response.status_code in [200, 204]:
            print("✅ Deleted nested Legal-System-Media folder")
        
        # Delete the duplicate inspection folder
        delete_url = "https://graph.microsoft.com/v1.0/me/drive/root:/Legal-System-Media/inspection/inspection"
        delete_response = requests.delete(delete_url, headers=headers)
        if delete_response.status_code in [200, 204]:
            print("✅ Deleted duplicate inspection folder")
        
        # Delete the entire Legal-System-Media folder to start fresh
        delete_url = "https://graph.microsoft.com/v1.0/me/drive/root:/Legal-System-Media"
        delete_response = requests.delete(delete_url, headers=headers)
        if delete_response.status_code in [200, 204]:
            print("✅ Deleted entire Legal-System-Media folder")
        
        print("\n🔄 Recreating clean folder structure...")
        
        # Create the base folder
        create_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        folder_data = {
            'name': 'Legal-System-Media',
            'folder': {},
            '@microsoft.graph.conflictBehavior': 'replace'
        }
        
        create_response = requests.post(create_url, json=folder_data, headers=headers)
        
        if create_response.status_code in [200, 201]:
            print("✅ Created clean Legal-System-Media folder")
            
            # Create the inspection folder
            create_url = "https://graph.microsoft.com/v1.0/me/drive/root:/Legal-System-Media:/children"
            folder_data = {
                'name': 'inspection',
                'folder': {},
                '@microsoft.graph.conflictBehavior': 'replace'
            }
            
            create_response = requests.post(create_url, json=folder_data, headers=headers)
            
            if create_response.status_code in [200, 201]:
                print("✅ Created inspection folder")
                
                # Create the 2025 folder
                create_url = "https://graph.microsoft.com/v1.0/me/drive/root:/Legal-System-Media/inspection:/children"
                folder_data = {
                    'name': '2025',
                    'folder': {},
                    '@microsoft.graph.conflictBehavior': 'replace'
                }
                
                create_response = requests.post(create_url, json=folder_data, headers=headers)
                
                if create_response.status_code in [200, 201]:
                    print("✅ Created 2025 folder")
                    print("\n🎉 Clean OneDrive structure created successfully!")
                    return True
                else:
                    print(f"❌ Failed to create 2025 folder: {create_response.status_code}")
                    return False
            else:
                print(f"❌ Failed to create inspection folder: {create_response.status_code}")
                return False
        else:
            print(f"❌ Failed to create Legal-System-Media folder: {create_response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Error cleaning up OneDrive structure: {e}")
        return False

if __name__ == "__main__":
    success = cleanup_onedrive_structure()
    if success:
        print("\n🎉 OneDrive structure cleanup completed!")
    else:
        print("\n❌ OneDrive structure cleanup failed")
