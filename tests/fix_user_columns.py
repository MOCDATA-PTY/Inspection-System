"""
Manually add missing user columns to PostgreSQL
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import connection

print("=" * 80)
print("ADDING MISSING USER COLUMNS TO POSTGRESQL")
print("=" * 80)

with connection.cursor() as cursor:
    print("\nAdding missing columns to auth_user table...")

    try:
        cursor.execute('''
DO $$
BEGIN
    -- Add role column if it does not exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='auth_user' AND column_name='role'
    ) THEN
        ALTER TABLE auth_user ADD COLUMN role varchar(20) DEFAULT 'inspector';
        RAISE NOTICE 'Added role column';
    ELSE
        RAISE NOTICE 'role column already exists';
    END IF;

    -- Add phone_number column if it does not exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='auth_user' AND column_name='phone_number'
    ) THEN
        ALTER TABLE auth_user ADD COLUMN phone_number varchar(20);
        RAISE NOTICE 'Added phone_number column';
    ELSE
        RAISE NOTICE 'phone_number column already exists';
    END IF;

    -- Add department column if it does not exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='auth_user' AND column_name='department'
    ) THEN
        ALTER TABLE auth_user ADD COLUMN department varchar(100);
        RAISE NOTICE 'Added department column';
    ELSE
        RAISE NOTICE 'department column already exists';
    END IF;

    -- Add employee_id column if it does not exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='auth_user' AND column_name='employee_id'
    ) THEN
        ALTER TABLE auth_user ADD COLUMN employee_id varchar(50);
        RAISE NOTICE 'Added employee_id column';

        -- Add unique constraint for employee_id
        BEGIN
            ALTER TABLE auth_user ADD CONSTRAINT auth_user_employee_id_key UNIQUE (employee_id);
            RAISE NOTICE 'Added unique constraint on employee_id';
        EXCEPTION WHEN duplicate_table THEN
            RAISE NOTICE 'Unique constraint on employee_id already exists';
        END;
    ELSE
        RAISE NOTICE 'employee_id column already exists';
    END IF;
END $$;
''')

        print("[OK] Successfully added missing columns!")

        # Verify columns were added
        print("\nVerifying columns...")
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'auth_user'
            AND column_name IN ('role', 'phone_number', 'department', 'employee_id')
            ORDER BY column_name
        """)

        columns = cursor.fetchall()
        if columns:
            print(f"\n{'Column Name':<20} {'Data Type':<20} {'Max Length':<12}")
            print("-" * 55)
            for col in columns:
                col_name = col[0]
                data_type = col[1]
                max_length = col[2] if col[2] else 'N/A'
                print(f"{col_name:<20} {data_type:<20} {max_length:<12}")
        else:
            print("[ERROR] Columns still not found!")

    except Exception as e:
        print(f"[ERROR] Failed to add columns: {e}")

print("\n" + "=" * 80)
print("DONE - Try logging in again")
print("=" * 80)
