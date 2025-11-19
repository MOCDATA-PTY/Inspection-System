"""
Test script to locate all compliance documents in the system
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_safety_agency.settings')
django.setup()

from main.models import ComplianceDocument
from django.conf import settings
from pathlib import Path

def locate_compliance_documents():
    """Find and list all compliance documents and their file locations"""

    print("=" * 80)
    print("COMPLIANCE DOCUMENTS LOCATION FINDER")
    print("=" * 80)
    print()

    # Get all compliance documents from database
    docs = ComplianceDocument.objects.all().order_by('-upload_date')

    print(f"Total compliance documents in database: {docs.count()}")
    print()

    # Media root
    media_root = settings.MEDIA_ROOT
    print(f"Media Root: {media_root}")
    print()

    # Check if compliance folder exists
    compliance_folder = Path(media_root) / 'compliance'
    print(f"Compliance Folder: {compliance_folder}")
    print(f"Exists: {compliance_folder.exists()}")
    print()

    if compliance_folder.exists():
        # List all files in compliance folder
        all_files = list(compliance_folder.rglob('*'))
        pdf_files = [f for f in all_files if f.is_file() and f.suffix.lower() == '.pdf']

        print(f"Total files in compliance folder: {len(all_files)}")
        print(f"Total PDF files: {len(pdf_files)}")
        print()

        # Show directory structure
        print("Directory Structure:")
        print("-" * 80)
        for root, dirs, files in os.walk(compliance_folder):
            level = root.replace(str(compliance_folder), '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Show first 5 files per directory
                print(f"{subindent}{file}")
            if len(files) > 5:
                print(f"{subindent}... and {len(files) - 5} more files")
        print()

    # List some sample documents from database
    print("Sample Documents from Database:")
    print("-" * 80)
    for i, doc in enumerate(docs[:10], 1):
        file_path = Path(media_root) / str(doc.file) if doc.file else None
        file_exists = file_path.exists() if file_path else False

        print(f"{i}. {doc.folder_name}")
        print(f"   File: {doc.file}")
        print(f"   Full Path: {file_path}")
        print(f"   Exists: {file_exists}")
        print(f"   Upload Date: {doc.upload_date}")
        print(f"   Source: {doc.source}")
        print()

    if docs.count() > 10:
        print(f"... and {docs.count() - 10} more documents")
        print()

    # Check for orphaned files (files not in database)
    print("Checking for orphaned files...")
    print("-" * 80)

    if compliance_folder.exists():
        db_files = set(str(doc.file) for doc in docs if doc.file)
        all_pdf_files = [str(f.relative_to(media_root)) for f in pdf_files]

        orphaned = [f for f in all_pdf_files if f not in db_files]

        print(f"Files in database: {len(db_files)}")
        print(f"PDF files on disk: {len(all_pdf_files)}")
        print(f"Orphaned files (on disk but not in DB): {len(orphaned)}")
        print()

        if orphaned:
            print("Sample orphaned files:")
            for f in orphaned[:10]:
                print(f"  - {f}")
            if len(orphaned) > 10:
                print(f"  ... and {len(orphaned) - 10} more")
            print()

    # Check for missing files (in database but not on disk)
    missing = []
    for doc in docs:
        if doc.file:
            file_path = Path(media_root) / str(doc.file)
            if not file_path.exists():
                missing.append(doc)

    print(f"Missing files (in DB but not on disk): {len(missing)}")
    if missing:
        print("Sample missing files:")
        for doc in missing[:10]:
            print(f"  - {doc.file} (Folder: {doc.folder_name})")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
        print()

    print("=" * 80)
    print("DONE")
    print("=" * 80)

if __name__ == '__main__':
    locate_compliance_documents()
