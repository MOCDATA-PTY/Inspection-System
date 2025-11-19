"""
Reset daily compliance sync to force re-pull of compliance documents
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

import redis
from django.conf import settings

print("=" * 60)
print("RESETTING DAILY COMPLIANCE SYNC")
print("=" * 60)
print()

# Connect to Redis
try:
    redis_client = redis.Redis(
        host=getattr(settings, 'REDIS_HOST', 'localhost'),
        port=getattr(settings, 'REDIS_PORT', 6379),
        db=getattr(settings, 'REDIS_DB', 0)
    )

    # Find and delete all compliance-related keys
    compliance_keys = list(redis_client.scan_iter(match='*compliance*'))
    sync_keys = list(redis_client.scan_iter(match='*sync*'))
    folder_keys = list(redis_client.scan_iter(match='*folder*'))

    all_keys = set(compliance_keys + sync_keys + folder_keys)

    if all_keys:
        print(f"Found {len(all_keys)} cache keys to delete:")
        for key in all_keys:
            key_str = key.decode('utf-8') if isinstance(key, bytes) else key
            print(f"  - {key_str}")
        print()

        # Delete the keys
        for key in all_keys:
            redis_client.delete(key)

        print(f"OK - Deleted {len(all_keys)} keys")
    else:
        print("No compliance/sync cache keys found")
        print()
        print("Flushing entire Redis cache...")
        redis_client.flushdb()
        print("OK - Redis cache flushed")

    print()
    print("Compliance sync has been reset.")
    print("Documents will be re-pulled on next access.")

except Exception as e:
    print(f"ERROR: {e}")
    print()
    print("Try manually clearing Redis:")
    print("  redis-cli FLUSHALL")

print()
print("=" * 60)
print("DONE")
print("=" * 60)
