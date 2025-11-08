#!/bin/bash
# Deployment script for Client Allocation Sheet feature
# Run this on the production server

echo "========================================="
echo "Starting deployment..."
echo "========================================="

# Navigate to project directory
cd /root/Inspection-System || exit 1

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || exit 1

# Pull latest changes from GitHub
echo "Pulling latest changes from GitHub..."
git pull origin master || exit 1

# Run database migrations
echo "Running database migrations..."
python3 manage.py migrate || exit 1

# Collect static files (if needed)
# echo "Collecting static files..."
# python3 manage.py collectstatic --noinput

# Restart Gunicorn
echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

# Restart Nginx
echo "Restarting Nginx..."
sudo systemctl restart nginx

# Check Gunicorn status
echo "========================================="
echo "Checking Gunicorn status..."
echo "========================================="
sudo systemctl status gunicorn --no-pager -l

echo ""
echo "========================================="
echo "Deployment complete!"
echo "========================================="
echo "The Client Allocation Sheet should now be available at:"
echo "https://your-domain.com/client-allocation-sheet/"
echo ""
echo "To verify migrations were applied, run:"
echo "source venv/bin/activate && python3 manage.py showmigrations main | tail -5"
