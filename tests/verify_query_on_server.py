"""
Verify that the production server is using the OUTER APPLY query
Run this ON THE PRODUCTION SERVER
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/root/Inspection-System')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

print("=" * 80)
print("VERIFYING QUERY ON PRODUCTION SERVER")
print("=" * 80)

# Import the query
from main.views.data_views import FSA_INSPECTION_QUERY

# Check if OUTER APPLY is in the query
outer_apply_count = FSA_INSPECTION_QUERY.count('OUTER APPLY')

print(f"\nOUTER APPLY count in query: {outer_apply_count}")
print(f"Expected: 6 (one for each commodity type)")

if outer_apply_count == 6:
    print("\n✅ CORRECT - Query has OUTER APPLY for all 6 commodities")
    print("   GPS duplicates should NOT occur")
else:
    print(f"\n❌ WRONG - Query has only {outer_apply_count} OUTER APPLY statements")
    print("   GPS duplicates WILL occur!")

# Show first 200 characters of query to verify
print("\n" + "=" * 80)
print("QUERY PREVIEW (first 200 chars):")
print("=" * 80)
print(FSA_INSPECTION_QUERY[:200])
print("...")

# Check if JOIN to GPS table exists (this would be wrong)
if 'JOIN AFS.dbo.GPSInspectionLocationRecords' in FSA_INSPECTION_QUERY:
    print("\n❌ ERROR: Found JOIN to GPSInspectionLocationRecords!")
    print("   This will create duplicates. The query is NOT using OUTER APPLY.")
else:
    print("\n✅ GOOD: No JOIN to GPSInspectionLocationRecords found")
    print("   Query is using OUTER APPLY as expected")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if outer_apply_count == 6 and 'JOIN AFS.dbo.GPSInspectionLocationRecords' not in FSA_INSPECTION_QUERY:
    print("\n✅ Server is using the CORRECT fixed query")
    print("   Sync should produce ~3.1k-3.7k inspections")
else:
    print("\n❌ Server is using the OLD broken query")
    print("   You need to:")
    print("   1. Clear Python cache: find . -name '*.pyc' -delete")
    print("   2. Restart Gunicorn: sudo systemctl restart gunicorn")

print("=" * 80)
