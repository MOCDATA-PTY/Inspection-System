"""
Reset daily compliance sync to allow it to run again
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import SystemSettings
from datetime import datetime, timedelta

print("Resetting daily compliance sync...")
print()

# Get system settings
settings = SystemSettings.objects.first()
if settings:
    old_date = settings.compliance_last_processed_date
    # Set to yesterday so it will run again today
    settings.compliance_last_processed_date = datetime.now() - timedelta(days=1)
    settings.save()

    print(f"Previous last run: {old_date}")
    print(f"New last run: {settings.compliance_last_processed_date}")
    print()
    print("Daily compliance sync will run on next check!")
else:
    print("No system settings found")
