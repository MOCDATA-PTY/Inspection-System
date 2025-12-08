#!/bin/bash
# Auto-start all background services
# Run this script after deployment or system restart

echo "=========================================="
echo "Starting all background services..."
echo "=========================================="

# Activate virtual environment
source venv/bin/activate

# Start data sync service (SQL Server + Google Sheets)
echo "Starting data sync service..."
python manage.py start_sync_service &

# Start backup service
echo "Starting backup service..."
python manage.py start_backup_service &

# Start daily compliance sync service
echo "Starting daily compliance sync..."
python manage.py start_daily_sync &

# Start OneDrive auto-upload service
echo "Starting OneDrive service..."
python manage.py start_onedrive_service &

echo ""
echo "=========================================="
echo "All services started successfully!"
echo "=========================================="
echo ""
echo "Services running:"
echo "  - Data Sync (every 1 hour)"
echo "  - Backup Service"
echo "  - Daily Compliance Sync"
echo "  - OneDrive Auto-Upload"
echo ""
echo "Services will continue running in background."
echo "=========================================="
