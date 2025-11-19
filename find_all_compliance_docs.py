"""
Find ALL compliance documents in the inspection system
"""
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings

def find_all_compliance_documents():
    """Find and list ALL compliance documents"""

    print("=" * 100)
    print("FINDING ALL COMPLIANCE DOCUMENTS")
    print("=" * 100)
    print()

    media_root = Path(settings.MEDIA_ROOT)
    inspection_folder = media_root / 'inspection'

    if not inspection_folder.exists():
        print(f"ERROR: Inspection folder does not exist: {inspection_folder}")
        return

    # Find ALL PDF files
    all_pdfs = list(inspection_folder.rglob('*.pdf'))

    print(f"Total PDF files found: {len(all_pdfs)}")
    print()

    # Organize by folder type
    compliance_docs = {
        'RFI': [],
        'Invoice': [],
        'COA': [],
        'Lab Form': [],
        'Retest': [],
        'Occurrence': [],
        'Composition': [],
        'Compliance Folder (POULTRY/EGGS/etc)': [],
        'Other': []
    }

    for pdf in all_pdfs:
        path_lower = str(pdf).lower()
        relative = pdf.relative_to(inspection_folder)

        # Categorize
        if '/rfi/' in path_lower:
            compliance_docs['RFI'].append(relative)
        elif '/invoice/' in path_lower:
            compliance_docs['Invoice'].append(relative)
        elif '/coa/' in path_lower or 'certificate' in path_lower:
            compliance_docs['COA'].append(relative)
        elif '/lab/' in path_lower:
            compliance_docs['Lab Form'].append(relative)
        elif '/retest/' in path_lower:
            compliance_docs['Retest'].append(relative)
        elif '/occurrence/' in path_lower:
            compliance_docs['Occurrence'].append(relative)
        elif '/composition/' in path_lower:
            compliance_docs['Composition'].append(relative)
        elif '/compliance/' in path_lower:
            compliance_docs['Compliance Folder (POULTRY/EGGS/etc)'].append(relative)
        else:
            compliance_docs['Other'].append(relative)

    # Print summary
    print("=" * 100)
    print("COMPLIANCE DOCUMENTS BY TYPE")
    print("=" * 100)
    print()

    for doc_type, files in compliance_docs.items():
        if files:
            print(f"{doc_type}: {len(files)} files")
            print("-" * 100)
            for f in files:
                full_path = inspection_folder / f
                size_kb = full_path.stat().st_size / 1024
                print(f"  {f} ({size_kb:.1f} KB)")
            print()

    # Print by client
    print("=" * 100)
    print("COMPLIANCE DOCUMENTS BY CLIENT")
    print("=" * 100)
    print()

    # Group by client (first subfolder after inspection/YYYY/Month/)
    clients = {}
    for pdf in all_pdfs:
        parts = pdf.relative_to(inspection_folder).parts
        if len(parts) >= 3:
            client = parts[2]  # 2025/November/[CLIENT]/...
            if client not in clients:
                clients[client] = []
            clients[client].append(pdf.relative_to(inspection_folder))

    for client in sorted(clients.keys()):
        files = clients[client]
        print(f"\n{client} ({len(files)} files)")
        print("-" * 100)
        for f in files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more files")

    print()
    print("=" * 100)
    print(f"TOTAL: {len(all_pdfs)} compliance documents found")
    print("=" * 100)

if __name__ == '__main__':
    find_all_compliance_documents()
