#!/usr/bin/env python3
"""
Clear the compliance sync lock
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.cache import cache

# Clear the lock
cache.delete('sync_compliance_documents_lock')
print("[OK] Cleared compliance documents sync lock")
