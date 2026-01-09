#!/usr/bin/env python
"""Test the actual view response to check account codes in HTML"""
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

print("=" * 80)
print("TESTING ACTUAL VIEW RESPONSE FOR ACCOUNT CODES")
print("=" * 80)

# Clear cache first
cache.clear()
print("\n[OK] Cache cleared\n")

# Get inspector user
inspector = User.objects.filter(username='Nelisa').first()
if not inspector:
    inspector = User.objects.filter(role='inspector').first()

print(f"Testing with user: {inspector.username} (Role: {inspector.role})")

# Create test client and login
client = Client()
client.force_login(inspector)

# Make request with refresh parameter to bypass any remaining cache
print("\n[1] Making HTTP request to /inspections/?refresh=true")
print("-" * 80)
response = client.get('/inspections/?refresh=true')

print(f"HTTP Status: {response.status_code}")
print(f"Response size: {len(response.content)} bytes")

# Parse HTML response to find account codes
html = response.content.decode('utf-8')

# Find all account code cells in the table
account_code_pattern = r'<td class="col-account-code[^>]*>.*?<span[^>]*>(.*?)</span>'
account_codes = re.findall(account_code_pattern, html, re.DOTALL)

print(f"\n[2] Found {len(account_codes)} account code cells in HTML")
print("-" * 80)

# Count how many are empty/missing
missing_count = sum(1 for code in account_codes if code.strip() in ['-', ''])
valid_count = len(account_codes) - missing_count

print(f"Valid account codes: {valid_count}")
print(f"Missing account codes (-): {missing_count}")

# Show first 10 account codes
print(f"\n[3] First 10 account codes in HTML:")
print("-" * 80)
for i, code in enumerate(account_codes[:10], 1):
    code_display = code.strip() if code.strip() else '[EMPTY]'
    status = "✓ OK" if code.strip() not in ['-', ''] else "✗ MISSING"
    print(f"{i:2d}. {code_display:40s} {status}")

# Extract client names from the table
client_name_pattern = r'<div class="font-medium text-gray-900[^>]*>(.*?)</div>'
client_names = re.findall(client_name_pattern, html)

print(f"\n[4] Client names found: {len(client_names)}")
print("-" * 80)
for i, name in enumerate(client_names[:10], 1):
    name_clean = re.sub(r'<[^>]+>', '', name).strip()
    # Try to find corresponding account code
    if i <= len(account_codes):
        code = account_codes[i-1].strip()
        print(f"{i:2d}. {name_clean:40s} -> {code if code != '-' else '[MISSING]'}")
    else:
        print(f"{i:2d}. {name_clean}")

print("\n" + "=" * 80)
print("RESULT")
print("=" * 80)
if missing_count == 0:
    print("SUCCESS: All account codes are present!")
elif valid_count > 0:
    print(f"PARTIAL: {valid_count} valid codes, {missing_count} missing")
else:
    print("FAILURE: All account codes are missing!")
print("=" * 80)
