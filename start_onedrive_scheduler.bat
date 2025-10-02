@echo off
echo Starting OneDrive Auto-Upload Scheduler...
echo This will run the upload process every hour
echo Press Ctrl+C to stop
echo.

python manage.py run_onedrive_scheduler --interval 3600

pause
