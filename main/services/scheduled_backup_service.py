#!/usr/bin/env python3
"""
Scheduled Backup Service
Handles automatic data backups based on user settings
"""

import os
import sys
import django
import threading
import time
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from django.core.cache import cache
from ..models import SystemSettings
from .backup_service import BackupService


class ScheduledBackupService:
    """Service for scheduled backup tasks."""
    
    def __init__(self):
        self.is_running = False
        self.backup_thread = None
        self.last_backup_time = None
        self.backup_stats = {
            'total_backups': 0,
            'successful_backups': 0,
            'failed_backups': 0,
            'last_backup_time': None,
            'next_backup_time': None
        }
    
    def get_system_settings(self):
        """Get current system settings."""
        try:
            # Try to get settings from database
            settings_obj = SystemSettings.objects.first()
            if settings_obj:
                return {
                    'auto_sync_enabled': getattr(settings_obj, 'auto_sync_enabled', False),
                    'backup_frequency_days': getattr(settings_obj, 'backup_frequency_days', 7),
                    'session_timeout_minutes': getattr(settings_obj, 'session_timeout_minutes', 30),
                    'google_sheets_enabled': getattr(settings_obj, 'google_sheets_enabled', True),
                    'sql_server_enabled': getattr(settings_obj, 'sql_server_enabled', True),
                    'sync_interval_hours': getattr(settings_obj, 'sync_interval_hours', 24)
                }
            
            # Fallback to settings.py
            return {
                'auto_sync_enabled': getattr(settings, 'AUTO_SYNC_ENABLED', False),
                'backup_frequency_days': getattr(settings, 'BACKUP_FREQUENCY_DAYS', 7),
                'session_timeout_minutes': getattr(settings, 'SESSION_TIMEOUT_MINUTES', 30),
                'google_sheets_enabled': getattr(settings, 'GOOGLE_SHEETS_ENABLED', True),
                'sql_server_enabled': getattr(settings, 'SQL_SERVER_ENABLED', True),
                'sync_interval_hours': getattr(settings, 'SYNC_INTERVAL_HOURS', 24)
            }
            
        except Exception as e:
            print(f"⚠️ Error getting system settings: {e}")
            return self._get_default_settings()
    
    def _get_default_settings(self):
        """Get default settings if database is not available."""
        return {
            'auto_sync_enabled': False,
            'backup_frequency_days': 7,
            'session_timeout_minutes': 30,
            'google_sheets_enabled': True,
            'sql_server_enabled': True,
            'sync_interval_hours': 24
        }
    
    def should_run_backup(self):
        """Check if a backup should run based on timing."""
        try:
            settings = self.get_system_settings()
            
            if not settings.get('auto_sync_enabled', False):
                return False
            
            if not self.last_backup_time:
                return True  # First time running
            
            current_time = datetime.now()
            time_since_last = current_time - self.last_backup_time
            
            # Check if enough time has passed based on backup frequency
            backup_frequency_days = settings.get('backup_frequency_days', 7)
            required_interval = timedelta(days=backup_frequency_days)
            
            return time_since_last >= required_interval
            
        except Exception as e:
            print(f"❌ Error checking backup timing: {e}")
            return False
    
    def run_automatic_backup(self):
        """Run an automatic backup."""
        try:
            print("💾 Starting automatic backup...")
            
            backup_service = BackupService()
            success = backup_service.create_backup(backup_type='automatic')
            
            if success:
                print("✅ Automatic backup completed successfully")
                self.last_backup_time = datetime.now()
                self.backup_stats['successful_backups'] += 1
                self.backup_stats['last_backup_time'] = self.last_backup_time
                return True
            else:
                print("❌ Automatic backup failed")
                self.backup_stats['failed_backups'] += 1
                return False
                
        except Exception as e:
            print(f"❌ Error in automatic backup: {e}")
            self.backup_stats['failed_backups'] += 1
            return False
    
    def run_scheduled_backups(self):
        """Run scheduled backups based on timing."""
        try:
            settings = self.get_system_settings()
            
            if not settings.get('auto_sync_enabled', False):
                print("ℹ️ Auto sync is disabled - skipping backup")
                return
            
            if self.should_run_backup():
                print("🔄 Running scheduled backup...")
                success = self.run_automatic_backup()
                self.backup_stats['total_backups'] += 1
                
                # Calculate next backup time
                if success:
                    backup_frequency_days = settings.get('backup_frequency_days', 7)
                    next_backup = datetime.now() + timedelta(days=backup_frequency_days)
                    self.backup_stats['next_backup_time'] = next_backup
                    print(f"📅 Next backup scheduled for: {next_backup.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    # If backup failed, try again in 1 hour
                    next_backup = datetime.now() + timedelta(hours=1)
                    self.backup_stats['next_backup_time'] = next_backup
                    print(f"⚠️ Backup failed - retrying in 1 hour: {next_backup.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("⏰ Backup not due yet - skipping")
            
            # Save stats to cache
            self._save_stats()
            
        except Exception as e:
            print(f"❌ Error in scheduled backups: {e}")
            self.backup_stats['failed_backups'] += 1
            self._save_stats()
    
    def _save_stats(self):
        """Save backup statistics to cache."""
        try:
            cache.set('scheduled_backup_service:stats', self.backup_stats, 3600)
            cache.set('scheduled_backup_service:last_backup_time', self.last_backup_time, 3600)
        except Exception as e:
            print(f"⚠️ Failed to save backup stats: {e}")
    
    def _load_stats(self):
        """Load backup statistics from cache."""
        try:
            cached_stats = cache.get('scheduled_backup_service:stats')
            if cached_stats:
                self.backup_stats = cached_stats
            
            cached_time = cache.get('scheduled_backup_service:last_backup_time')
            if cached_time:
                self.last_backup_time = cached_time
        except Exception as e:
            print(f"⚠️ Failed to load backup stats: {e}")
    
    def start_background_service(self):
        """Start the background backup service."""
        if self.is_running:
            return False, "Background backup service already running"
        
        self.is_running = True
        self._load_stats()
        cache.set('scheduled_backup_service:running', True, 3600)
        
        # Start background thread
        self.backup_thread = threading.Thread(target=self._background_service_loop, daemon=True)
        self.backup_thread.start()
        
        return True, "Scheduled backup service started"
    
    def stop_background_service(self):
        """Stop the background backup service."""
        if not self.is_running:
            return False, "Background backup service not running"
        
        self.is_running = False
        cache.delete('scheduled_backup_service:running')
        
        if self.backup_thread and self.backup_thread.is_alive():
            self.backup_thread.join(timeout=5)
        
        return True, "Scheduled backup service stopped"
    
    def _background_service_loop(self):
        """Background service loop."""
        while self.is_running:
            try:
                # Run scheduled backups
                self.run_scheduled_backups()
                
                # Wait 1 hour before checking again
                print("⏰ Waiting 1 hour before next backup check...")
                for _ in range(3600):  # 1 hour = 3600 seconds
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Error in background service loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def get_service_status(self):
        """Get current service status."""
        try:
            is_running = cache.get('scheduled_backup_service:running', False)
            settings = self.get_system_settings()
            
            # Calculate next backup time
            next_backup = None
            if self.last_backup_time:
                backup_frequency_days = settings.get('backup_frequency_days', 7)
                next_backup = self.last_backup_time + timedelta(days=backup_frequency_days)
            else:
                next_backup = datetime.now() + timedelta(days=settings.get('backup_frequency_days', 7))
            
            return {
                'is_running': is_running,
                'auto_sync_enabled': settings.get('auto_sync_enabled', False),
                'backup_frequency_days': settings.get('backup_frequency_days', 7),
                'last_backup_time': self.last_backup_time,
                'next_backup_time': next_backup,
                'backup_stats': self.backup_stats,
                'settings': settings
            }
            
        except Exception as e:
            print(f"❌ Error getting service status: {e}")
            return {
                'is_running': False,
                'error': str(e)
            }
    
    def run_manual_backup(self):
        """Run a manual backup."""
        try:
            print("🔄 Running manual backup...")
            success = self.run_automatic_backup()
            self.backup_stats['total_backups'] += 1
            
            if success:
                return True, "Manual backup completed successfully"
            else:
                return False, "Manual backup failed"
                
        except Exception as e:
            return False, f"Error in manual backup: {e}"


# Global service instance
scheduled_backup_service = ScheduledBackupService()


def start_scheduled_backup_service():
    """Start the scheduled backup service."""
    return scheduled_backup_service.start_background_service()


def stop_scheduled_backup_service():
    """Stop the scheduled backup service."""
    return scheduled_backup_service.stop_background_service()


def get_scheduled_backup_service_status():
    """Get scheduled backup service status."""
    return scheduled_backup_service.get_service_status()


def run_manual_backup():
    """Run a manual backup."""
    return scheduled_backup_service.run_manual_backup()


if __name__ == "__main__":
    print("💾 Scheduled Backup Service")
    print("=" * 50)
    
    # Test the service
    status = get_scheduled_backup_service_status()
    print(f"Service Status: {status}")
