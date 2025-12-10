from django.db import migrations, connection


def run_postgres_sql(apps, schema_editor):
    """Run PostgreSQL-specific SQL only if using PostgreSQL."""
    # Skip for non-PostgreSQL databases (e.g., SQLite for testing)
    if connection.vendor != 'postgresql':
        return

    # These fields are now added by auth app migrations (0013-0023)
    # This migration is kept for backward compatibility but may be redundant
    with connection.cursor() as cursor:
        cursor.execute('''
DO $$
BEGIN
    -- Add role column if it does not exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='auth_user' AND column_name='role'
    ) THEN
        ALTER TABLE auth_user ADD COLUMN role varchar(20) DEFAULT 'inspector';
    END IF;

    -- Add phone_number column if it does not exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='auth_user' AND column_name='phone_number'
    ) THEN
        ALTER TABLE auth_user ADD COLUMN phone_number varchar(20);
    END IF;

    -- Add department column if it does not exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='auth_user' AND column_name='department'
    ) THEN
        ALTER TABLE auth_user ADD COLUMN department varchar(100);
    END IF;

    -- Add employee_id column if it does not exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='auth_user' AND column_name='employee_id'
    ) THEN
        ALTER TABLE auth_user ADD COLUMN employee_id varchar(50);
        -- Unique constraint for employee_id
        BEGIN
            ALTER TABLE auth_user ADD CONSTRAINT auth_user_employee_id_key UNIQUE (employee_id);
        EXCEPTION WHEN duplicate_table THEN
            -- Constraint already exists, do nothing
            NULL;
        END;
    END IF;
END $$;
''')


def reverse_postgres_sql(apps, schema_editor):
    """Reverse PostgreSQL-specific SQL only if using PostgreSQL."""
    if connection.vendor != 'postgresql':
        return

    with connection.cursor() as cursor:
        cursor.execute('''
DO $$
BEGIN
    -- Drop columns only if they exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='auth_user' AND column_name='employee_id'
    ) THEN
        -- Drop unique constraint if exists
        IF EXISTS (
            SELECT 1 FROM information_schema.table_constraints
            WHERE table_name='auth_user' AND constraint_name='auth_user_employee_id_key'
        ) THEN
            ALTER TABLE auth_user DROP CONSTRAINT auth_user_employee_id_key;
        END IF;
        ALTER TABLE auth_user DROP COLUMN employee_id;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='auth_user' AND column_name='department'
    ) THEN
        ALTER TABLE auth_user DROP COLUMN department;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='auth_user' AND column_name='phone_number'
    ) THEN
        ALTER TABLE auth_user DROP COLUMN phone_number;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='auth_user' AND column_name='role'
    ) THEN
        ALTER TABLE auth_user DROP COLUMN role;
    END IF;
END $$;
''')


class Migration(migrations.Migration):
    initial = False

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(run_postgres_sql, reverse_postgres_sql),
    ]


