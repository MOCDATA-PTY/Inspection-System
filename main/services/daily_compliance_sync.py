#!/usr/bin/env python3
"""
Daily Compliance Sync Service
Handles daily synchronization of compliance documents with skip logic
"""

import os
import sys
import django
import threading
import time
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from django.core.cache import cache
from ..models import SystemSettings, FoodSafetyAgencyInspection
from ..views.core_views import load_drive_files_real, find_document_link_apps_script_replica, download_compliance_document


class DailyComplianceSyncService:
    """Service for daily compliance document synchronization with skip logic."""
    
    def __init__(self):
        self.is_running = False
        self.sync_thread = None
        self.last_sync_time = None
        self.sync_stats = {
            'total_documents_processed': 0,
            'documents_skipped': 0,
            'documents_processed': 0,
            'last_sync_time': None,
            'next_sync_time': None
        }
    
    def get_system_settings(self):
        """Get current system settings."""
        try:
            return SystemSettings.get_settings()
        except Exception as e:
            print(f"Error getting system settings: {e}")
            return None
    
    def should_run_daily_sync(self, manual_start=False):
        """Check if daily sync should run based on settings and last run time."""
        settings = self.get_system_settings()
        if not settings or not settings.compliance_daily_sync_enabled:
            return False
        
        # If this is a manual start, always run regardless of last run time
        if manual_start:
            print("Manual start requested - running daily sync regardless of last run time.")
            return True
        
        # Check if we've already run today (only for automatic runs)
        if settings.compliance_last_processed_date:
            last_run = settings.compliance_last_processed_date.date()
            today = datetime.now().date()
            if last_run >= today:
                print(f"Daily compliance sync already ran today ({last_run}). Skipping.")
                return False
        
        return True
    
    def get_processed_documents_cache(self):
        """Get cache of already processed documents with automatic reset detection."""
        import os
        from django.conf import settings
        
        cache_key = 'processed_compliance_documents'
        media_check_key = 'media_folder_exists'
        
        # Check if media/inspection folder exists
        media_inspection_path = os.path.join(settings.MEDIA_ROOT, 'inspection')
        media_exists = os.path.exists(media_inspection_path)
        
        # Get previous media folder state from cache
        previous_media_state = cache.get(media_check_key, True)
        
        # If media folder was deleted since last check, clear the processed cache
        if previous_media_state and not media_exists:
            print("🧹 DETECTED: Media folder was deleted! Clearing processed documents cache...")
            cache.delete(cache_key)
            cache.set(media_check_key, False, 60 * 60 * 24)  # Remember for 24 hours
            return set()  # Return empty set to force reprocessing
        
        # If media folder was recreated, also clear cache
        if not previous_media_state and media_exists:
            print("🗂️ DETECTED: Media folder was recreated! Clearing processed documents cache...")
            cache.delete(cache_key)
            cache.set(media_check_key, True, 60 * 60 * 24)  # Remember for 24 hours
            return set()  # Return empty set to force reprocessing
        
        # Update media folder state in cache
        cache.set(media_check_key, media_exists, 60 * 60 * 24)
        
        # Return normal processed documents cache
        processed_docs = cache.get(cache_key, set())
        return processed_docs
    
    def add_to_processed_cache(self, document_id):
        """Add document to processed cache."""
        cache_key = 'processed_compliance_documents'
        processed_docs = self.get_processed_documents_cache()
        processed_docs.add(document_id)
        # Cache for 7 days
        cache.set(cache_key, processed_docs, 7 * 24 * 60 * 60)
    
    def is_document_processed(self, document_id):
        """Check if document has already been processed."""
        if not self.get_system_settings().compliance_skip_processed:
            return False
        
        processed_docs = self.get_processed_documents_cache()
        return document_id in processed_docs
    
    def generate_document_id(self, inspection):
        """Generate unique document ID for tracking."""
        return f"{inspection.id}_{inspection.date_of_inspection.strftime('%Y%m%d')}"
    
    def load_drive_files_standalone(self):
        """Load Google Drive files without requiring a request object."""
        try:
            from ..services.google_drive_service import GoogleDriveService
            import re
            from datetime import datetime
            
            drive_service = GoogleDriveService()
            folder_id = "18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4"  # From Apps Script
            
            print("☁️ Loading Google Drive files for daily sync...")
            start_time = datetime.now()
            
            # Get ALL files from Drive folder (not limited to 1000)
            files = drive_service.list_files_in_folder(folder_id, request=None, max_items=None)
            
            file_lookup = {}
            file_count = 0
            
            for file in files:
                file_name = file.get('name', '')
                file_id = file.get('id', '')
                web_view_link = file.get('webViewLink', '')
                
                # Apps Script pattern: COMMODITY-ACCOUNT_CODE-DATE
                # Example: RAW-RE-IND-RAW-NA-1000-2025-01-15
                full_pattern = re.match(r'^([A-Za-z]+)-([A-Z]{2}-[A-Z]{3}-[A-Z]{3}-[A-Z]{2,3}-\d+)-(\d{4}-\d{2}-\d{2})', file_name)
                
                if full_pattern and file_id:
                    commodity_prefix = full_pattern.group(1)
                    account_code = full_pattern.group(2)
                    zip_date_str = full_pattern.group(3)
                    
                    try:
                        zip_date = datetime.strptime(zip_date_str, '%Y-%m-%d')
                    except:
                        continue
                    
                    # Create compound key exactly like Apps Script
                    compound_key = f"{commodity_prefix.lower()}|{account_code}|{zip_date_str}"
                    
                    file_lookup[compound_key] = {
                        'url': web_view_link or f"https://drive.google.com/file/d/{file_id}/view",
                        'name': file_name,
                        'commodity': commodity_prefix,
                        'accountCode': account_code,
                        'zipDate': zip_date,
                        'zipDateStr': zip_date_str,
                        'file_id': file_id
                    }
                    
                    file_count += 1
                    
                    # Progress logging
                    if file_count % 1000 == 0 and file_count > 0:
                        print(f"📁 Loaded {file_count} files...")
            
            load_time = (datetime.now() - start_time).total_seconds()
            print(f"✅ Loaded {len(file_lookup)} files in {load_time:.1f} seconds")
            
            return file_lookup
            
        except Exception as e:
            print(f"❌ Error loading Drive files: {e}")
            return {}

    def get_client_account_code(self, client_name):
        """Get account code for a client name."""
        try:
            from ..models import Client
            
            # Normalize client name
            normalized_name = client_name.strip().lower().replace('\u00A0', ' ').replace('\u200B', '').replace('\u2002', ' ').replace('\u2003', ' ').replace('  ', ' ')
            
            # Find client with matching name
            client = Client.objects.filter(
                name__iexact=normalized_name
            ).exclude(internal_account_code__isnull=True).exclude(internal_account_code='').first()
            
            if client:
                return client.internal_account_code
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting account code for {client_name}: {e}")
            return None

    def process_compliance_documents(self):
        """Process compliance documents with skip logic."""
        print("🔄 Starting daily compliance document sync...")
        
        settings = self.get_system_settings()
        if not settings or not settings.compliance_daily_sync_enabled:
            print("❌ Daily compliance sync is disabled.")
            return
        
        try:
            # Load Google Drive files once at the start
            print("☁️ Loading Google Drive files...")
            file_lookup = self.load_drive_files_standalone()
            
            if not file_lookup:
                print("❌ Failed to load Google Drive files. Aborting sync.")
                return
            
            # Get all inspections from the last 6 months
            six_months_ago = datetime.now() - timedelta(days=180)
            inspections = FoodSafetyAgencyInspection.objects.filter(
                date_of_inspection__gte=six_months_ago
            ).order_by('-date_of_inspection')
            
            print(f"📊 Found {inspections.count()} inspections to process")
            
            documents_processed = 0
            documents_skipped = 0
            
            for inspection in inspections:
                document_id = self.generate_document_id(inspection)
                
                # Skip if already processed
                if self.is_document_processed(document_id):
                    documents_skipped += 1
                    print(f"⏭️  Skipping already processed: {inspection.id}")
                    continue
                
                try:
                    # Process compliance documents for this inspection - SEQUENTIAL APPROACH
                    print(f"🔄 Processing: {inspection.id}")
                    
                    # Get account code for this client
                    account_code = self.get_client_account_code(inspection.client_name)
                    
                    if not account_code:
                        print(f"⚠️  No account code found for client: {inspection.client_name}")
                        continue
                    
                    # Find document links using account code
                    document_link = find_document_link_apps_script_replica(
                        account_code, 
                        inspection.commodity or "Unknown",
                        inspection.date_of_inspection,
                        file_lookup
                    )
                    
                    if document_link and document_link != "Document Not Found":
                        print(f"✅ Found compliance document for {inspection.id} (Account: {account_code})")
                        
                        # IMMEDIATELY DOWNLOAD the document
                        try:
                            # Find the matching file in lookup for download
                            for file_key, file_info in file_lookup.items():
                                if (file_info.get('commodity', '').lower() == str(inspection.commodity).lower().strip() and
                                    file_info.get('accountCode') == account_code):
                                    
                                    print(f"📥 Downloading: {file_info['name']} for {inspection.client_name}")
                                    
                                    # Download to client's compliance folder
                                    downloaded_path = download_compliance_document(
                                        file_info['file_id'],
                                        account_code,
                                        inspection.commodity,
                                        inspection.date_of_inspection,
                                        file_info['name'],
                                        inspection.client_name,
                                        None  # No request object needed
                                    )
                                    
                                    if downloaded_path:
                                        print(f"✅ Downloaded successfully: {file_info['name']} -> {downloaded_path}")
                                        documents_processed += 1
                                    else:
                                        print(f"❌ Download failed for: {file_info['name']}")
                                    break
                            else:
                                print(f"⚠️  Could not find file details for download: {account_code}")
                        
                        except Exception as download_error:
                            print(f"❌ Download error for {inspection.id}: {download_error}")
                        
                        # Mark as processed only after successful download attempt
                        self.add_to_processed_cache(document_id)
                    else:
                        print(f"⚠️  No document found for {inspection.id} (Account: {account_code})")
                    
                    # Small delay to prevent overwhelming the system
                    time.sleep(0.2)  # Slightly longer delay for download operations
                    
                except Exception as e:
                    print(f"❌ Error processing {inspection.id}: {e}")
                    continue
            
            # Update statistics
            self.sync_stats['total_documents_processed'] += documents_processed
            self.sync_stats['documents_skipped'] += documents_skipped
            self.sync_stats['documents_processed'] += documents_processed
            self.sync_stats['last_sync_time'] = datetime.now()
            
            # Update last processed date
            settings.compliance_last_processed_date = datetime.now()
            settings.save()
            
            print(f"✅ Daily compliance sync completed!")
            print(f"📊 Processed: {documents_processed}, Skipped: {documents_skipped}")
            
        except Exception as e:
            print(f"❌ Error in daily compliance sync: {e}")
    
    def start_daily_sync(self, manual_start=False):
        """Start the daily sync service."""
        if self.is_running:
            print("⚠️  Daily compliance sync is already running.")
            return
        
        self.is_running = True
        self.manual_start = manual_start  # Store manual start flag
        self.sync_thread = threading.Thread(target=self._run_daily_sync_loop, daemon=True)
        self.sync_thread.start()
        print("🚀 Daily compliance sync service started.")
    
    def stop_daily_sync(self):
        """Stop the daily sync service."""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        print("🛑 Daily compliance sync service stopped.")
    
    def _run_daily_sync_loop(self):
        """Main loop for daily sync service."""
        while self.is_running:
            try:
                # Check if we should run daily sync (use manual_start flag if available)
                manual_start = getattr(self, 'manual_start', False)
                if self.should_run_daily_sync(manual_start):
                    self.process_compliance_documents()
                    # Reset manual start flag after first run
                    if manual_start:
                        self.manual_start = False
                
                # Wait 1 hour before checking again
                time.sleep(3600)  # 1 hour
                
            except Exception as e:
                print(f"❌ Error in daily sync loop: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def get_status(self):
        """Get current status of the daily sync service."""
        return {
            'is_running': self.is_running,
            'last_sync_time': self.sync_stats['last_sync_time'].isoformat() if self.sync_stats['last_sync_time'] else None,
            'total_documents_processed': self.sync_stats['total_documents_processed'],
            'documents_skipped': self.sync_stats['documents_skipped'],
            'documents_processed': self.sync_stats['documents_processed']
        }


# Global instance
daily_sync_service = DailyComplianceSyncService()
