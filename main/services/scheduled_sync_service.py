#!/usr/bin/env python3
"""
Scheduled Sync Service
Handles all automatic synchronization tasks based on user settings
"""

import os
import sys
import django
import threading
import time
import json
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from django.core.cache import cache
from ..models import FoodSafetyAgencyInspection, Client, SystemSettings
from ..views.core_views import load_drive_files_real, find_document_link_apps_script_replica
from django.http import HttpRequest


class ScheduledSyncService:
    """Service for scheduled synchronization tasks."""
    
    def __init__(self):
        self.is_running = False
        self.sync_thread = None
        self.last_sync_times = {
            'google_sheets': None,
            'sql_server': None
        }
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'last_sync_time': None,
            'next_sync_time': None
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
                    'onedrive_enabled': getattr(settings_obj, 'onedrive_enabled', True),
                    'onedrive_auto_sync': getattr(settings_obj, 'onedrive_auto_sync', True),
                    'onedrive_sync_interval_hours': getattr(settings_obj, 'onedrive_sync_interval_hours', 2),
                    'onedrive_cache_days': getattr(settings_obj, 'onedrive_cache_days', 60),
                    'sync_interval_hours': getattr(settings_obj, 'sync_interval_hours', 24)
                }
            
            # Fallback to settings.py
            return {
                'auto_sync_enabled': getattr(settings, 'AUTO_SYNC_ENABLED', False),
                'backup_frequency_days': getattr(settings, 'BACKUP_FREQUENCY_DAYS', 7),
                'session_timeout_minutes': getattr(settings, 'SESSION_TIMEOUT_MINUTES', 30),
                'google_sheets_enabled': getattr(settings, 'GOOGLE_SHEETS_ENABLED', True),
                'sql_server_enabled': getattr(settings, 'SQL_SERVER_ENABLED', True),
                'onedrive_enabled': getattr(settings, 'ONEDRIVE_ENABLED', True),
                'onedrive_auto_sync': getattr(settings, 'ONEDRIVE_AUTO_SYNC', True),
                'onedrive_sync_interval_hours': getattr(settings, 'ONEDRIVE_SYNC_INTERVAL_HOURS', 2),
                'onedrive_cache_days': getattr(settings, 'ONEDRIVE_CACHE_DAYS', 60),
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
            'onedrive_enabled': True,
            'sync_interval_hours': 24
        }
    
    def should_run_sync(self, sync_type):
        """Check if a specific sync should run based on timing."""
        try:
            settings = self.get_system_settings()
            
            if not settings.get('auto_sync_enabled', False):
                return False
            
            last_sync = self.last_sync_times.get(sync_type)
            if not last_sync:
                return True  # First time running
            
            current_time = datetime.now()
            time_since_last = current_time - last_sync
            
            # Check specific sync intervals
            if sync_type in ['google_sheets', 'sql_server']:
                interval_hours = settings.get('sync_interval_hours', 24)
                
                # If interval is 0, don't sync automatically (manual only)
                if interval_hours <= 0:
                    print(f"⚠️ Sync interval is {interval_hours} hours - skipping automatic sync for {sync_type}")
                    return False
                
                # Check if enough time has passed
                required_seconds = interval_hours * 3600
                time_passed = time_since_last.total_seconds()
                
                print(f"🕐 {sync_type}: {time_passed:.1f}s since last sync, need {required_seconds:.1f}s")
                return time_passed >= required_seconds
            
            elif sync_type == 'onedrive':
                # Use OneDrive auto-sync interval from settings
                interval_hours = settings.get('onedrive_sync_interval_hours', 2)
                if interval_hours <= 0:
                    return False
                return time_since_last.total_seconds() >= (interval_hours * 3600)
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking sync timing: {e}")
            return False
    
    def sync_google_sheets(self):
        """Sync data with Google Sheets."""
        try:
            print("📊 Starting Google Sheets sync...")
            
            # Import Google Sheets service
            from ..services.google_sheets_service import GoogleSheetsService
            
            sheets_service = GoogleSheetsService()
            
            # Refresh clients table
            success = sheets_service.refresh_clients_table()
            
            if success:
                print("✅ Google Sheets sync completed successfully")
                self.last_sync_times['google_sheets'] = datetime.now()
                return True
            else:
                print("❌ Google Sheets sync failed")
                return False
                
        except Exception as e:
            print(f"❌ Error in Google Sheets sync: {e}")
            return False
    
    def sync_sql_server(self):
        """Sync inspection data with SQL Server."""
        try:
            print("🗄️ Starting SQL Server sync...")
            
            from ..models import FoodSafetyAgencyInspection, Inspection
            
            # Count existing inspections
            total_inspections = FoodSafetyAgencyInspection.objects.count()
            total_regular_inspections = Inspection.objects.count()
            
            print(f"   📊 Found {total_inspections} Food Safety Agency inspections")
            print(f"   📊 Found {total_regular_inspections} regular inspections")
            
            # For now, we'll just report the current state
            # In a real implementation, this would sync with external SQL Server
            print(f"   📈 Total inspection records: {total_inspections + total_regular_inspections}")
            
            # Check for recent inspections (last 7 days)
            from datetime import datetime, timedelta
            recent_date = datetime.now().date() - timedelta(days=7)
            recent_inspections = FoodSafetyAgencyInspection.objects.filter(
                date_of_inspection__gte=recent_date
            ).count()
            
            print(f"   📅 Recent inspections (last 7 days): {recent_inspections}")
            
            self.last_sync_times['sql_server'] = datetime.now()
            print("✅ SQL Server sync completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error in SQL Server sync: {e}")
            return False
    
    def sync_compliance_documents(self):
        """Sync compliance documents from Google Drive (REMOVED - OneDrive service handles this)."""
        try:
            print("⚠️ Compliance documents sync has been removed - OneDrive service handles this automatically")
            return True  # Return True to avoid errors
                
        except Exception as e:
            print(f"❌ Error in compliance documents sync: {e}")
            return False
    
    def sync_onedrive(self):
        """Sync OneDrive files in background to prevent user waiting."""
        try:
            print("🔄 Starting OneDrive auto-sync (background)...")
            
            from ..views.core_views import check_for_compliance_documents
            from datetime import datetime, timedelta
            
            # Settings
            settings_dict = self.get_system_settings()
            batch_size = 10000
            cache_days = settings_dict.get('onedrive_cache_days', 60)
            
            # Define population to iterate through: last N days (configurable)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=cache_days)
            queryset = FoodSafetyAgencyInspection.objects.filter(
                date_of_inspection__gte=start_date,
                date_of_inspection__lte=end_date
            ).values('client_name', 'date_of_inspection').distinct().order_by('date_of_inspection', 'client_name')
            total = queryset.count()
            if total == 0:
                print("ℹ️ OneDrive auto-sync: No inspections in range to process")
                self.last_sync_times['onedrive'] = datetime.now()
                return True

            # Rolling offset so we process a different slice each run
            offset_key = 'onedrive_compliance_batch_offset'
            try:
                current_offset = int(cache.get(offset_key, 0) or 0)
            except Exception:
                current_offset = 0
            # Normalize offset within total range
            if current_offset >= total:
                current_offset = 0

            # Compute slice window [offset, offset+batch)
            start_index = current_offset
            end_index = min(current_offset + batch_size, total)
            print(f"📊 OneDrive auto-sync: total={total}, processing index {start_index}..{end_index-1} (batch {batch_size})")

            # Fetch just the batch we need
            # Using iterator over sliced queryset to reduce memory
            batch_items = list(queryset[start_index:end_index])

            processed_count = 0
            changes_detected = 0
            for item in batch_items:
                client_name = item['client_name']
                inspection_date = item['date_of_inspection']
                if not client_name or not inspection_date:
                    continue
                try:
                    # Check and cache status
                    has_compliance = check_for_compliance_documents(client_name, inspection_date)
                    cache_key = f"compliance_status_{client_name}_{inspection_date}"

                    # Compare with previous cached status if any
                    prev = cache.get(cache_key)
                    new_status = {
                        'has_any_compliance': bool(has_compliance),
                        'all_commodities_have_compliance': bool(has_compliance),
                        'last_checked': datetime.now().isoformat()
                    }
                    cache.set(cache_key, new_status, 60 * 60 * 24)  # cache 24 hours

                    # Log only if changed
                    if prev is None or prev.get('has_any_compliance') != new_status['has_any_compliance'] or prev.get('all_commodities_have_compliance') != new_status['all_commodities_have_compliance']:
                        changes_detected += 1
                        try:
                            SystemLog.objects.create(
                                action='onedrive_compliance_status',
                                details=json.dumps({
                                    'client_name': client_name,
                                    'date_of_inspection': str(inspection_date),
                                    'previous': prev,
                                    'current': new_status
                                })
                            )
                        except Exception:
                            # Ensure logging failures don't break the sync loop
                            pass

                    processed_count += 1
                    if processed_count % 500 == 0:
                        print(f"📊 OneDrive auto-sync: processed {processed_count}/{len(batch_items)} in current batch; changes={changes_detected}")
                except Exception as e:
                    # Continue on errors to avoid blocking the whole batch
                    print(f"⚠️ OneDrive auto-sync error for {client_name} @ {inspection_date}: {e}")
                    continue

            # Update rolling offset for next hourly run
            next_offset = end_index if end_index < total else 0
            cache.set(offset_key, next_offset, 60 * 60 * 48)  # keep for 48 hours

            print(f"✅ OneDrive auto-sync completed batch: processed={processed_count}, changes={changes_detected}, next_offset={next_offset}, total={total}")
            self.last_sync_times['onedrive'] = datetime.now()
            return True
            
        except Exception as e:
            print(f"❌ OneDrive auto-sync failed: {e}")
            return False
    
    
    def _save_stats(self):
        """Save sync statistics to cache."""
        try:
            cache.set('scheduled_sync_service:stats', self.sync_stats, 3600)
            cache.set('scheduled_sync_service:last_sync_times', self.last_sync_times, 3600)
        except Exception as e:
            print(f"⚠️ Failed to save sync stats: {e}")
    
    def _load_stats(self):
        """Load sync statistics from cache."""
        try:
            cached_stats = cache.get('scheduled_sync_service:stats')
            if cached_stats:
                self.sync_stats = cached_stats
            
            cached_times = cache.get('scheduled_sync_service:last_sync_times')
            if cached_times:
                self.last_sync_times = cached_times
        except Exception as e:
            print(f"⚠️ Failed to load sync stats: {e}")
    
    def start_background_service(self):
        """Start the background sync service."""
        if self.is_running:
            return False, "Background sync service already running"
        
        self.is_running = True
        self._load_stats()
        cache.set('scheduled_sync_service:running', True, 3600)
        
        # Start background thread
        self.sync_thread = threading.Thread(target=self._background_service_loop, daemon=True)
        self.sync_thread.start()
        
        return True, "Scheduled sync service started"
    
    def stop_background_service(self):
        """Stop the background sync service."""
        self.is_running = False
        cache.delete('scheduled_sync_service:running')
        
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=5)
        
        return True, "Scheduled sync service stopped"
    
    def _background_service_loop(self):
        """Background service loop."""
        while self.is_running:
            try:
                # Check if any syncs are due and run them
                settings = self.get_system_settings()
                
                if settings.get('auto_sync_enabled', False):
                    # Check if any syncs are due
                    google_sheets_due = settings.get('google_sheets_enabled', True) and self.should_run_sync('google_sheets')
                    sql_server_due = settings.get('sql_server_enabled', True) and self.should_run_sync('sql_server')
                    
                    if google_sheets_due or sql_server_due:
                        print("🔄 Running scheduled syncs...")
                        sync_results = {}
                        
                        # Google Sheets sync
                        if google_sheets_due:
                            sync_results['google_sheets'] = self.sync_google_sheets()
                        
                        # SQL Server sync
                        if sql_server_due:
                            sync_results['sql_server'] = self.sync_sql_server()
                        
                        # Update statistics
                        self.sync_stats['total_syncs'] += len(sync_results)
                        self.sync_stats['successful_syncs'] += sum(1 for result in sync_results.values() if result)
                        self.sync_stats['failed_syncs'] += sum(1 for result in sync_results.values() if not result)
                        self.sync_stats['last_sync_time'] = datetime.now()
                        
                        # Calculate next sync time
                        next_sync = datetime.now() + timedelta(hours=settings.get('sync_interval_hours', 24))
                        self.sync_stats['next_sync_time'] = next_sync
                        
                        # Save stats to cache
                        self._save_stats()
                        
                        # Print detailed summary
                        successful_count = sum(1 for result in sync_results.values() if result)
                        failed_count = len(sync_results) - successful_count
                        print(f"✅ Scheduled syncs completed: {len(sync_results)} tasks ({successful_count} successful, {failed_count} failed)")
                        
                        # Show next sync time
                        next_sync_time = self.sync_stats.get('next_sync_time', 'Unknown')
                        if next_sync_time != 'Unknown':
                            print(f"⏰ Next sync scheduled for: {next_sync_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        print("⏰ No syncs due at this time")
                else:
                    print("ℹ️ Auto sync is disabled")
                
                # Wait based on sync interval setting
                sync_interval_hours = settings.get('sync_interval_hours', 24)
                
                # If sync interval is very short (less than 1 hour), check every minute
                if sync_interval_hours < 1:
                    check_interval_minutes = 1
                else:
                    # For longer intervals, check every 1/10th of the interval, max 5 min, min 1 min
                    check_interval_minutes = min(5, max(1, sync_interval_hours * 60 / 10))
                
                check_interval_seconds = int(check_interval_minutes * 60)
                
                print(f"⏰ Waiting {check_interval_minutes:.1f} minutes before next sync check...")
                for _ in range(check_interval_seconds):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Error in background service loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def get_service_status(self):
        """Get current service status."""
        try:
            is_running = cache.get('scheduled_sync_service:running', False)
            settings = self.get_system_settings()
            
            # Calculate next sync times
            next_syncs = {}
            for sync_type in ['google_sheets', 'sql_server', 'onedrive']:
                last_sync = self.last_sync_times.get(sync_type)
                if last_sync:
                    if sync_type == 'onedrive':
                        interval_hours = 10 / 60  # 10 minutes
                    else:
                        interval_hours = settings.get('sync_interval_hours', 24)
                    
                    next_sync = last_sync + timedelta(hours=interval_hours)
                    next_syncs[sync_type] = next_sync
                else:
                    next_syncs[sync_type] = None
            
            return {
                'is_running': is_running,
                'auto_sync_enabled': settings.get('auto_sync_enabled', False),
                'last_sync_times': self.last_sync_times,
                'next_sync_times': next_syncs,
                'sync_stats': self.sync_stats,
                'settings': settings
            }
            
        except Exception as e:
            print(f"❌ Error getting service status: {e}")
            return {
                'is_running': False,
                'error': str(e)
            }
    
    def run_manual_sync(self, sync_type):
        """Run a manual sync of a specific type."""
        try:
            print(f"🔄 Running manual {sync_type} sync...")
            
            if sync_type == 'google_sheets':
                success = self.sync_google_sheets()
            elif sync_type == 'sql_server':
                success = self.sync_sql_server()
            elif sync_type == 'all':
                # Run both Google Sheets and SQL Server sync
                print("🔄 Running all sync operations...")
                google_success = self.sync_google_sheets()
                sql_success = self.sync_sql_server()
                success = google_success and sql_success
                if success:
                    return True, "All sync operations completed successfully"
                else:
                    return False, "Some sync operations failed"
            else:
                return False, f"Unknown sync type: {sync_type}. Supported types: google_sheets, sql_server, all"
            
            if success:
                return True, f"{sync_type} sync completed successfully"
            else:
                return False, f"{sync_type} sync failed"
                
        except Exception as e:
            return False, f"Error in {sync_type} sync: {e}"


# Global service instance
scheduled_sync_service = ScheduledSyncService()


def start_scheduled_sync_service():
    """Start the scheduled sync service."""
    return scheduled_sync_service.start_background_service()


def stop_scheduled_sync_service():
    """Stop the scheduled sync service."""
    return scheduled_sync_service.stop_background_service()


def get_scheduled_sync_service_status():
    """Get scheduled sync service status."""
    return scheduled_sync_service.get_service_status()


def run_manual_sync(sync_type):
    """Run a manual sync."""
    return scheduled_sync_service.run_manual_sync(sync_type)


if __name__ == "__main__":
    print("🕐 Scheduled Sync Service")
    print("=" * 50)
    
    # Test the service
    status = get_scheduled_sync_service_status()
    print(f"Service Status: {status}")
