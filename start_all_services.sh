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
python manage.py start_data_sync &

# Start daily compliance sync service (every 5 minutes)
echo "Starting compliance document processor..."
python manage.py process_compliance_documents &

# Start OneDrive auto-upload service (every 1 hour)
echo "Starting OneDrive scheduler..."
python manage.py run_onedrive_scheduler &

echo ""
echo "=========================================="
echo "All services started successfully!"
echo "=========================================="
echo ""
echo "Services running:"
echo "  - Data Sync (every 1 hour)"
echo "  - Compliance Document Processor (every 5 minutes)"
echo "  - OneDrive Auto-Upload (every 1 hour)"
echo ""
echo "Services will continue running in background."
echo "=========================================="
