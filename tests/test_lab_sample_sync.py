#!/usr/bin/env python3
"""Quick test of lab sample sync with limited records"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.utils.lab_sample_sync import sync_all_lab_samples

print("Testing lab sample sync with first 10 inspections...")
result = sync_all_lab_samples(limit=10, show_progress=True)

print("\nTest Results:")
print(f"  Success: {result.get('success', 0)}")
print(f"  Failed: {result.get('failed', 0)}")
print(f"  PMP: {result.get('pmp_samples', 0)}")
print(f"  RAW: {result.get('raw_samples', 0)}")
