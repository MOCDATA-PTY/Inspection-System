#!/usr/bin/env python3
"""Sync 500 most recent lab samples for testing"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.lab_sample_sync import sync_all_lab_samples

print("Syncing 500 most recent inspections with lab samples...")
result = sync_all_lab_samples(limit=500, show_progress=True)

print("\nResults:")
print(f"  Total processed: {result.get('total', 0)}")
print(f"  Success: {result.get('success', 0)}")
print(f"  PMP: {result.get('pmp_samples', 0)}")
print(f"  RAW: {result.get('raw_samples', 0)}")
