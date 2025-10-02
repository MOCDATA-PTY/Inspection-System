#!/bin/bash

echo "=== PostgreSQL Setup and Fix Script ==="
echo "This script will fix all PostgreSQL permissions and configuration issues"
echo ""

# Step 1: Fix PostgreSQL Configuration
echo "Step 1: Fixing PostgreSQL configuration..."

# Backup the current config
sudo cp /etc/postgresql/16/main/postgresql.conf /etc/postgresql/16/main/postgresql.conf.backup

# Fix the listen_addresses setting
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/16/main/postgresql.conf
sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/16/main/postgresql.conf

echo "✅ PostgreSQL configuration updated"

# Step 2: Configure pg_hba.conf for remote connections
echo "Step 2: Configuring authentication..."

# Add remote connection rule to pg_hba.conf
echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a /etc/postgresql/16/main/pg_hba.conf

echo "✅ Authentication configured"

# Step 3: Restart PostgreSQL
echo "Step 3: Restarting PostgreSQL..."
sudo systemctl restart postgresql
sudo systemctl status postgresql --no-pager

echo "✅ PostgreSQL restarted"

# Step 4: Fix Database Permissions
echo "Step 4: Fixing database permissions..."

# Connect to PostgreSQL and run permission commands
sudo -u postgres psql -d inspection_db << 'EOF'
-- Grant all necessary permissions to postgres user
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;
GRANT CREATE ON SCHEMA public TO postgres;
GRANT USAGE ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;

-- Also grant permissions to django_user if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'django_user') THEN
        GRANT ALL PRIVILEGES ON SCHEMA public TO django_user;
        GRANT CREATE ON SCHEMA public TO django_user;
        GRANT USAGE ON SCHEMA public TO django_user;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO django_user;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO django_user;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO django_user;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO django_user;
    END IF;
END
$$;

-- Show current permissions
\dp
EOF

echo "✅ Database permissions fixed"

# Step 5: Test Django Connection
echo "Step 5: Testing Django connection..."
cd /root/Inspection-System

# Test database connection
python manage.py check --database default

if [ $? -eq 0 ]; then
    echo "✅ Database connection test passed"
    
    # Run migrations
    echo "Running Django migrations..."
    python manage.py migrate
    
    if [ $? -eq 0 ]; then
        echo "✅ Django migrations completed successfully"
        
        # Create superuser (optional)
        echo "Creating superuser..."
        echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Admin user already exists')" | python manage.py shell
        
        echo "✅ Superuser created (username: admin, password: admin123)"
        
    else
        echo "❌ Django migrations failed"
        exit 1
    fi
else
    echo "❌ Database connection test failed"
    exit 1
fi

echo ""
echo "=== Setup Complete ==="
echo "✅ PostgreSQL is configured and running"
echo "✅ Database permissions are fixed"
echo "✅ Django can connect to the database"
echo "✅ Migrations have been applied"
echo "✅ Superuser created (admin/admin123)"
echo ""
echo "You can now run your Django application!"
echo "Run: python manage.py runserver 0.0.0.0:8000"
