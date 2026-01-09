#!/usr/bin/env python3
"""
Check if there's a KM/Hours backup in cache that we can restore
"""
import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.core.cache import cache

print("=" * 100)
print("CHECKING FOR KM/HOURS BACKUP IN CACHE")
print("=" * 100)

# Check for persistent backup
backup = cache.get('km_hours_backup_persistent')

if backup:
    print(f"\n[OK] FOUND BACKUP IN CACHE!")
    print(f"   Backup contains: {len(backup):,} inspection records")
    print(f"\n   Sample backup keys (first 5):")

    for i, (key, data) in enumerate(list(backup.items())[:5]):
        commodity, remote_id, date = key
        km = data.get('km_traveled')
        hours = data.get('hours')
        print(f"   {i+1}. {commodity}-{remote_id} ({date}): KM={km}, Hours={hours}")

    print(f"\n[OK] This backup can be used to restore the data!")

else:
    print(f"\n[ERROR] NO BACKUP FOUND IN CACHE!")
    print(f"   The backup may have expired (cache timeout is 24 hours)")
    print(f"   You will need to restore from Google Sheets or manually")

print("\n" + "=" * 100)