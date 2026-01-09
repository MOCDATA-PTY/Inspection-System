"""
Diagnose login issues - check database connection and users
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import connection

print("=" * 80)
print("LOGIN DIAGNOSTICS")
print("=" * 80)

# Test database connection
print("\n1. Testing PostgreSQL Database Connection...")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"   [OK] Connected to PostgreSQL: {version[0][:50]}...")
except Exception as e:
    print(f"   [ERROR] Database connection failed: {e}")
    sys.exit(1)

# Check users table
print("\n2. Checking Users in Database...")
try:
    users = User.objects.all()
    user_count = users.count()
    print(f"   [OK] Found {user_count} users in database")

    if user_count > 0:
        print("\n   User List:")
        print(f"   {'Username':<20} {'Email':<30} {'Staff':<8} {'Active':<8} {'Superuser':<10}")
        print("   " + "-" * 80)
        for user in users[:10]:  # Show first 10 users
            username = user.username[:18]
            email = (user.email or 'N/A')[:28]
            is_staff = 'Yes' if user.is_staff else 'No'
            is_active = 'Yes' if user.is_active else 'No'
            is_super = 'Yes' if user.is_superuser else 'No'
            print(f"   {username:<20} {email:<30} {is_staff:<8} {is_active:<8} {is_super:<10}")
    else:
        print("   [WARNING] No users found in database!")
        print("   Create a superuser with: python manage.py createsuperuser")

except Exception as e:
    print(f"   [ERROR] Failed to query users: {e}")

# Check for inactive users
print("\n3. Checking for Inactive Users...")
try:
    inactive_users = User.objects.filter(is_active=False)
    inactive_count = inactive_users.count()
    if inactive_count > 0:
        print(f"   [WARNING] Found {inactive_count} inactive users:")
        for user in inactive_users:
            print(f"   - {user.username} (inactive)")
    else:
        print("   [OK] All users are active")
except Exception as e:
    print(f"   [ERROR] Failed to check inactive users: {e}")

# Check authentication backends
print("\n4. Checking Authentication Settings...")
from django.conf import settings
backends = settings.AUTHENTICATION_BACKENDS
print(f"   Authentication backends configured:")
for backend in backends:
    print(f"   - {backend}")

# Check session configuration
print("\n5. Checking Session Configuration...")
print(f"   Session Engine: {settings.SESSION_ENGINE}")
if hasattr(settings, 'SESSION_COOKIE_AGE'):
    print(f"   Session Cookie Age: {settings.SESSION_COOKIE_AGE} seconds")

# Check if migrations are applied
print("\n6. Checking Database Migrations...")
try:
    from django.db.migrations.executor import MigrationExecutor
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

    if plan:
        print(f"   [WARNING] {len(plan)} unapplied migrations found!")
        print("   Run: python manage.py migrate")
        for migration, backwards in plan[:5]:
            print(f"   - {migration}")
    else:
        print("   [OK] All migrations are applied")
except Exception as e:
    print(f"   [WARNING] Could not check migrations: {e}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

if user_count == 0:
    print("""
No users found! Create a superuser:
    python manage.py createsuperuser

Then try logging in with those credentials.
""")
else:
    print("""
If you still can't login:
1. Check browser console for JavaScript errors
2. Verify the login URL is correct
3. Check Django server logs for errors
4. Try resetting a user's password:
   python manage.py changepassword <username>
5. Clear browser cache and cookies
6. Check if the server is actually running on the correct port
""")

print("=" * 80)
