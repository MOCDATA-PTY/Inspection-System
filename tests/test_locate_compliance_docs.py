"""
Test script to locate all compliance documents in the system
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from pathlib import Path

def locate_compliance_documents():
    """Find and list all compliance documents and their file locations"""

    print("=" * 80)
    print("COMPLIANCE DOCUMENTS LOCATION FINDER")
    print("=" * 80)
    print()

    # Media root
    media_root = Path(settings.MEDIA_ROOT)
    print(f"Media Root: {media_root}")
    print(f"Exists: {media_root.exists()}")
    print()

    # Check for compliance folder
    compliance_folder = media_root / 'compliance'
    print(f"Compliance Folder: {compliance_folder}")
    print(f"Exists: {compliance_folder.exists()}")
    print()

    if compliance_folder.exists():
        # List all files in compliance folder
        all_files = list(compliance_folder.rglob('*'))
        files_only = [f for f in all_files if f.is_file()]
        pdf_files = [f for f in files_only if f.suffix.lower() == '.pdf']

        print(f"Total items (files + folders): {len(all_files)}")
        print(f"Total files: {len(files_only)}")
        print(f"Total PDF files: {len(pdf_files)}")
        print()

        # Show directory structure
        print("Directory Structure:")
        print("-" * 80)

        # Get all subdirectories
        subdirs = sorted([d for d in compliance_folder.rglob('*') if d.is_dir()])

        for subdir in subdirs[:20]:  # Show first 20 directories
            rel_path = subdir.relative_to(compliance_folder)
            level = len(rel_path.parts)
            indent = '  ' * level

            # Count files in this directory
            files_in_dir = [f for f in subdir.iterdir() if f.is_file()]

            print(f"{indent}{subdir.name}/ ({len(files_in_dir)} files)")

        if len(subdirs) > 20:
            print(f"... and {len(subdirs) - 20} more directories")
        print()

        # Show sample files by commodity type
        print("Sample Files by Commodity:")
        print("-" * 80)

        commodities = ['POULTRY', 'PMP', 'RAW', 'EGGS']
        for commodity in commodities:
            commodity_path = compliance_folder / commodity
            if commodity_path.exists():
                files = [f for f in commodity_path.rglob('*.pdf') if f.is_file()]
                print(f"\n{commodity}: {len(files)} PDF files")
                for f in files[:3]:  # Show first 3 files
                    rel_path = f.relative_to(compliance_folder)
                    file_size = f.stat().st_size / 1024  # KB
                    print(f"  - {rel_path} ({file_size:.1f} KB)")
                if len(files) > 3:
                    print(f"  ... and {len(files) - 3} more files")
        print()

    else:
        print("WARNING: Compliance folder does not exist!")
        print()
        print("Checking other possible locations:")

        # Check inspection folder
        inspection_folder = media_root / 'inspection'
        print(f"\nInspection Folder: {inspection_folder}")
        print(f"Exists: {inspection_folder.exists()}")

        if inspection_folder.exists():
            # Analyze inspection folder structure
            all_files = [f for f in inspection_folder.rglob('*') if f.is_file()]
            pdf_files = [f for f in all_files if f.suffix.lower() == '.pdf']

            print(f"Total files in inspection folder: {len(all_files)}")
            print(f"PDF files: {len(pdf_files)}")
            print()

            # Look for compliance document types
            print("Compliance Documents by Type:")
            print("-" * 80)

            doc_types = {
                'RFI': [],
                'Invoice': [],
                'COA': [],
                'Lab Form': [],
                'Retest': [],
                'Occurrence': [],
                'Composition': []
            }

            for pdf in pdf_files:
                path_str = str(pdf).lower()
                if 'rfi' in path_str:
                    doc_types['RFI'].append(pdf)
                elif 'invoice' in path_str:
                    doc_types['Invoice'].append(pdf)
                elif 'coa' in path_str or 'certificate' in path_str:
                    doc_types['COA'].append(pdf)
                elif 'lab' in path_str and 'form' in path_str:
                    doc_types['Lab Form'].append(pdf)
                elif 'retest' in path_str:
                    doc_types['Retest'].append(pdf)
                elif 'occurrence' in path_str:
                    doc_types['Occurrence'].append(pdf)
                elif 'composition' in path_str:
                    doc_types['Composition'].append(pdf)

            for doc_type, files in doc_types.items():
                print(f"\n{doc_type}: {len(files)} files")
                for f in files[:3]:
                    rel_path = f.relative_to(inspection_folder)
                    file_size = f.stat().st_size / 1024  # KB
                    print(f"  - {rel_path} ({file_size:.1f} KB)")
                if len(files) > 3:
                    print(f"  ... and {len(files) - 3} more")

            print()
            print("Inspection Folder Structure (sample):")
            print("-" * 80)

            # Show folder structure
            subfolders = sorted([d for d in inspection_folder.rglob('*') if d.is_dir()])[:15]
            for folder in subfolders:
                rel_path = folder.relative_to(inspection_folder)
                file_count = len([f for f in folder.iterdir() if f.is_file()])
                level = len(rel_path.parts)
                indent = '  ' * level
                print(f"{indent}{folder.name}/ ({file_count} files)")

            if len(subfolders) > 15:
                print(f"... and more subdirectories")

    # Check media root contents
    print("\nMedia Root Contents:")
    print("-" * 80)
    if media_root.exists():
        items = sorted([item for item in media_root.iterdir()])
        for item in items[:15]:
            item_type = "DIR" if item.is_dir() else "FILE"
            if item.is_dir():
                file_count = len([f for f in item.rglob('*') if f.is_file()])
                print(f"  [{item_type}] {item.name}/ ({file_count} files)")
            else:
                size_kb = item.stat().st_size / 1024
                print(f"  [{item_type}] {item.name} ({size_kb:.1f} KB)")
        if len(items) > 15:
            print(f"  ... and {len(items) - 15} more items")
    else:
        print("WARNING: Media root does not exist!")

    print()
    print("=" * 80)
    print("DONE")
    print("=" * 80)

if __name__ == '__main__':
    locate_compliance_documents()
