"""
Check what compliance documents have been downloaded
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

print("Checking downloaded compliance documents...")
print()

base_path = os.path.join(settings.MEDIA_ROOT, 'inspection')

if os.path.exists(base_path):
    # Count all compliance folders
    compliance_folders = []
    for root, dirs, files in os.walk(base_path):
        if 'Compliance' in dirs:
            compliance_path = os.path.join(root, 'Compliance')
            compliance_folders.append(compliance_path)
    
    print(f"Found {len(compliance_folders)} Compliance folders")
    print()
    
    # Count ZIP files
    zip_count = 0
    total_size = 0
    for compliance_folder in compliance_folders:
        for root, dirs, files in os.walk(compliance_folder):
            for file in files:
                if file.endswith('.zip'):
                    file_path = os.path.join(root, file)
                    zip_count += 1
                    total_size += os.path.getsize(file_path) if os.path.exists(file_path) else 0
    
    print(f"Total ZIP files: {zip_count}")
    print(f"Total size: {total_size / (1024*1024):.2f} MB")
    print()
    
    # Show first few files
    print("First 10 files found:")
    count = 0
    for compliance_folder in compliance_folders[:3]:
        for root, dirs, files in os.walk(compliance_folder):
            for file in files:
                if file.endswith('.zip') and count < 10:
                    rel_path = os.path.relpath(os.path.join(root, file), base_path)
                    print(f"  {rel_path}")
                    count += 1
else:
    print("No compliance documents downloaded yet")

