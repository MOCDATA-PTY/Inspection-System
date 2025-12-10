#!/bin/bash
# Deployment script for Inspection System

echo "Deploying..."

# Navigate to project directory
cd /root/Inspection-System || exit 1

# Activate virtual environment
source venv/bin/activate || exit 1

# Pull latest changes
git pull origin master -q || exit 1

# Run migrations
python3 manage.py makemigrations --noinput >/dev/null 2>&1
python3 manage.py migrate --noinput >/dev/null 2>&1 || exit 1

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Start background services
chmod +x start_all_services.sh
./start_all_services.sh

echo "Done!"
