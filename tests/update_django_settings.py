#!/usr/bin/env python3
"""
Script to update Django settings for server deployment
"""

import os
import sys

def update_settings():
    settings_file = "mysite/settings.py"
    
    if not os.path.exists(settings_file):
        print(f"❌ Settings file not found: {settings_file}")
        return False
    
    # Read current settings
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Update database configuration
    new_db_config = '''# Database (PostgreSQL on Server)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inspection_db',
        'USER': 'postgres',
        'PASSWORD': 'root',  # PostgreSQL password
        'HOST': '82.25.97.159',  # Your server IP
        'PORT': '5432',
    }
}'''
    
    # Find and replace the database configuration
    import re
    pattern = r'# Database.*?DATABASES = \{.*?\}'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, new_db_config, content, flags=re.DOTALL)
        print("✅ Updated existing database configuration")
    else:
        # If no database config found, add it after WSGI_APPLICATION
        wsgi_pattern = r'(WSGI_APPLICATION = [^\n]+\n)'
        if re.search(wsgi_pattern, content):
            content = re.sub(wsgi_pattern, r'\1\n' + new_db_config + '\n', content)
            print("✅ Added new database configuration")
        else:
            print("❌ Could not find location to add database configuration")
            return False
    
    # Update ALLOWED_HOSTS for production
    allowed_hosts_pattern = r'ALLOWED_HOSTS = \[.*?\]'
    new_allowed_hosts = "ALLOWED_HOSTS = ['82.25.97.159', 'localhost', '127.0.0.1', '*']"
    
    if re.search(allowed_hosts_pattern, content):
        content = re.sub(allowed_hosts_pattern, new_allowed_hosts, content)
        print("✅ Updated ALLOWED_HOSTS")
    
    # Write updated settings
    with open(settings_file, 'w') as f:
        f.write(content)
    
    print("✅ Django settings updated successfully")
    return True

if __name__ == "__main__":
    print("=== Updating Django Settings for Server ===")
    if update_settings():
        print("✅ All settings updated successfully!")
        print("Your Django app is now configured to connect to the PostgreSQL server.")
    else:
        print("❌ Failed to update settings")
        sys.exit(1)
