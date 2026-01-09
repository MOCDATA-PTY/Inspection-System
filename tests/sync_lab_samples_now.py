#!/usr/bin/env python3
"""
Manual Lab Sample Sync Script
Run this to sync lab sample data from SQL Server to Django database
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.lab_sample_sync import sync_all_lab_samples

if __name__ == '__main__':
    print("=" * 80)
    print("LAB SAMPLE SYNC - Manual Execution")
    print("=" * 80)
    print("\nThis script will sync lab sample data from SQL Server to Django database.")
    print("It will set fat, protein, calcium, and dna fields based on lab sample records.")
    print("\nStarting sync...\n")

    # Run the sync
    result = sync_all_lab_samples(show_progress=True)

    print("\n" + "=" * 80)
    print("SYNC COMPLETE")
    print("=" * 80)

    if result.get('total', 0) > 0:
        print(f"\nResults:")
        print(f"  Total inspections with lab samples: {result['total']}")
        print(f"  Successfully synced: {result['success']}")
        print(f"  Failed: {result['failed']}")
        print(f"  Not found in Django: {result['not_found']}")
        print(f"\nSample types:")
        print(f"  PMP samples: {result['pmp_samples']}")
        print(f"  RAW samples: {result['raw_samples']}")
    else:
        print("\nNo lab samples found in SQL Server.")

    print("\nYou can now check the export sheet to see inspections with lab samples!")
    print("=" * 80)
