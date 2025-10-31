"""
Show the directory structure of downloaded compliance documents
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

download_dir = os.path.join(settings.MEDIA_ROOT, 'compliance_documents_all')

print("=" * 80)
print("COMPLIANCE DOCUMENTS DIRECTORY STRUCTURE")
print("=" * 80)
print()
print(f"Location: {download_dir}")
print()

if os.path.exists(download_dir):
    files = os.listdir(download_dir)
    
    print(f"Total files: {len(files)}")
    print()
    
    # Get total size
    total_size = sum(os.path.getsize(os.path.join(download_dir, f)) for f in files)
    size_mb = total_size / (1024 * 1024)
    print(f"Total size: {size_mb:.2f} MB")
    print()
    
    # Show first 20 files
    print("First 20 files:")
    for i, filename in enumerate(files[:20], 1):
        file_path = os.path.join(download_dir, filename)
        size_kb = os.path.getsize(file_path) / 1024
        print(f"  {i:2d}. {filename} ({size_kb:.1f} KB)")
    
    if len(files) > 20:
        print(f"  ... and {len(files) - 20} more files")
    
    print()
    print("=" * 80)
    print("DIRECTORY STRUCTURE")
    print("=" * 80)
    print()
    print(f"media/")
    print(f"  compliance_documents_all/")
    print(f"    ├── {files[0] if files else 'file.zip'}")
    print(f"    ├── {files[1] if len(files) > 1 else 'file.zip'}")
    print(f"    ├── {files[2] if len(files) > 2 else 'file.zip'}")
    print(f"    └── ... ({len(files)} total files)")
    print()
    print("Files are organized as:")
    print("  media/compliance_documents_all/[FILENAME].zip")
    print()
    print("Each file follows the naming pattern:")
    print("  COMMODITY-ACCOUNTCODE-DATE.zip")
    print()
    print("Example: Poultry-RE-IND-RAW-NA-1953-2025-09-22.zip")
    print("  - Commodity: Poultry")
    print("  - Account: RE-IND-RAW-NA-1953")
    print("  - Date: 2025-09-22")
    print()
    print("=" * 80)
else:
    print("Directory does not exist yet")

