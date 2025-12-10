#!/bin/bash
# Auto-start all background services

# Activate virtual environment
source venv/bin/activate

# Start services silently
python manage.py start_data_sync >/dev/null 2>&1 &
python manage.py process_compliance_documents >/dev/null 2>&1 &
python manage.py run_onedrive_scheduler >/dev/null 2>&1 &
