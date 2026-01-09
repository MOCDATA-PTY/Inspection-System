"""
Check what commodity prefixes are in the Drive files
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.views.core_views import load_drive_files_real
from collections import Counter

def check_commodities():
    print("Loading Drive files...")

    class MockRequest:
        def __init__(self):
            self.session = {}

    mock_request = MockRequest()
    file_lookup = load_drive_files_real(mock_request, use_cache=True)

    print(f"Total files: {len(file_lookup)}\n")

    # Extract commodity prefixes from file names
    commodities = Counter()

    for key, file_info in file_lookup.items():
        file_name = file_info['name']
        # Get the part before the first hyphen
        if '-' in file_name:
            commodity = file_name.split('-')[0]
            commodities[commodity] += 1

    print("Commodity prefixes found in files:")
    print("="*50)
    for commodity, count in commodities.most_common():
        print(f"{commodity:15} : {count:4} files")

    print("\n" + "="*50)
    print(f"Total: {sum(commodities.values())} files")

    # Show sample file names for each commodity
    print("\n\nSample files for each commodity:")
    print("="*50)

    shown_commodities = set()
    for key, file_info in file_lookup.items():
        file_name = file_info['name']
        if '-' in file_name:
            commodity = file_name.split('-')[0]
            if commodity not in shown_commodities:
                print(f"\n{commodity}:")
                print(f"  {file_name}")
                shown_commodities.add(commodity)

if __name__ == "__main__":
    check_commodities()
