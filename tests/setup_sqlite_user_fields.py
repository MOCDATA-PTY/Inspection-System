"""
Add missing user fields to SQLite database and create test user
"""
import os
import django
import sqlite3

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 80)
print("SETUP SQLITE DATABASE - ADD USER FIELDS")
print("=" * 80)

# Get database path from settings
from mysite.settings import DATABASES
db_path = DATABASES['default']['NAME']

print(f"\nDatabase: {db_path}")

# Connect directly to SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check what columns exist in auth_user
cursor.execute("PRAGMA table_info(auth_user)")
columns = cursor.fetchall()

print("\nCurrent auth_user columns:")
existing_columns = [col[1] for col in columns]
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Add missing columns if they don't exist
columns_to_add = [
    ('role', 'VARCHAR(20)', "'inspector'"),
    ('phone_number', 'VARCHAR(20)', 'NULL'),
    ('department', 'VARCHAR(100)', 'NULL'),
    ('employee_id', 'VARCHAR(50)', 'NULL')
]

print("\nAdding missing columns...")
for col_name, col_type, default in columns_to_add:
    if col_name not in existing_columns:
        try:
            cursor.execute(f"ALTER TABLE auth_user ADD COLUMN {col_name} {col_type} DEFAULT {default}")
            print(f"  [OK] Added column: {col_name}")
        except Exception as e:
            print(f"  [ERROR] Failed to add {col_name}: {e}")
    else:
        print(f"  [SKIP] Column already exists: {col_name}")

conn.commit()

# Verify columns were added
cursor.execute("PRAGMA table_info(auth_user)")
columns = cursor.fetchall()
print("\nFinal auth_user columns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()

# Now create a test superuser using Django ORM
print("\n" + "=" * 80)
print("CREATING TEST SUPERUSER")
print("=" * 80)

try:
    # Check if user already exists
    if User.objects.filter(username='developer').exists():
        user = User.objects.get(username='developer')
        print(f"\n[INFO] User 'developer' already exists")
        print(f"  - Email: {user.email}")
        print(f"  - Is superuser: {user.is_superuser}")
        print(f"  - Is staff: {user.is_staff}")

        # Reset password to known value
        user.set_password('developer123')
        user.save()
        print(f"\n[OK] Password reset to: developer123")
    else:
        # Create new superuser
        user = User.objects.create_superuser(
            username='developer',
            email='developer@example.com',
            password='developer123'
        )
        print(f"\n[OK] Created superuser 'developer'")
        print(f"  - Username: developer")
        print(f"  - Password: developer123")
        print(f"  - Email: developer@example.com")

    # Set role field
    user.role = 'developer'
    user.save()
    print(f"  - Role: {user.role}")

except Exception as e:
    print(f"\n[ERROR] Failed to create user: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("SETUP COMPLETE")
print("=" * 80)
print("""
You can now log in with:
  Username: developer
  Password: developer123

The SQLite database is ready for testing the composite key workaround.
""")
