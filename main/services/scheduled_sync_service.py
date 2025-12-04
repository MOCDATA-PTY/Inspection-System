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

        # Auto-restart service if it was running before (persists across Django reloads/page refreshes)
        self._auto_restart_if_needed()
    
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
        from django.db import close_old_connections

        try:
            print("📊 Starting Google Sheets sync...")

            # Ensure fresh database connection
            close_old_connections()

            # Import Google Sheets service
            from ..services.google_sheets_service import GoogleSheetsService

            sheets_service = GoogleSheetsService()

            # Refresh clients table
            result = sheets_service.refresh_clients_table()

            # Check if result is a dictionary (error response) or boolean (success/failure)
            if isinstance(result, dict):
                if result.get('success'):
                    print(f"✅ Google Sheets sync completed successfully")
                    print(f"   - Clients created: {result.get('clients_created', 0)}")
                    print(f"   - Clients updated: {result.get('clients_updated', 0)}")
                    print(f"   - Total processed: {result.get('total_processed', 0)}")
                    self.last_sync_times['google_sheets'] = datetime.now()
                    return True
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"❌ Google Sheets sync failed: {error_msg}")
                    # Store error in cache for frontend
                    cache.set('google_sheets_sync_error', error_msg, 300)
                    return False
            elif result:
                # Boolean True - success
                print("✅ Google Sheets sync completed successfully")
                self.last_sync_times['google_sheets'] = datetime.now()
                return True
            else:
                # Boolean False - failure
                print("❌ Google Sheets sync failed")
                cache.set('google_sheets_sync_error', 'Unknown error - sync returned False', 300)
                return False

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error in Google Sheets sync: {error_msg}")
            import traceback
            traceback.print_exc()
            # Store error in cache for frontend
            cache.set('google_sheets_sync_error', f'Exception: {error_msg}', 300)
            return False
        finally:
            # Clean up connections after sync
            try:
                close_old_connections()
            except:
                pass
    
    def sync_sql_server(self):
        """Sync inspection data with SQL Server - DELETE ALL then fetch fresh data."""
        try:
            print("\n" + "="*80)
            print("🗄️  STARTING SQL SERVER SYNC (FULL REFRESH)")
            print("="*80)

            from ..models import FoodSafetyAgencyInspection, Inspection
            from ..utils.sql_server_utils import fetch_all_product_names_bulk
            from ..views.data_views import FSA_INSPECTION_QUERY, INSPECTOR_NAME_MAP
            import pymssql
            from datetime import datetime, timedelta

            # DELETE ALL EXISTING INSPECTIONS FIRST (prevents duplicates)
            print(f"\n🗑️  STEP 1: CLEARING EXISTING INSPECTION DATA...")
            existing_count = FoodSafetyAgencyInspection.objects.count()
            print(f"   Found {existing_count:,} existing inspection records")
            print(f"   Deleting all records to ensure fresh sync...")

            FoodSafetyAgencyInspection.objects.all().delete()

            final_count = FoodSafetyAgencyInspection.objects.count()
            print(f"✅ Database cleared: {final_count:,} inspections remaining (should be 0)")
            print(f"   This prevents duplicates and ensures fresh data!\n")

            # Connect to SQL Server using pymssql
            sql_server_config = settings.DATABASES.get('sql_server', {})

            print(f"📡 STEP 2: CONNECTING TO SQL SERVER...")
            print(f"   Server: {sql_server_config.get('HOST')}:{sql_server_config.get('PORT', 1433)}")
            print(f"   Database: {sql_server_config.get('NAME')}")

            connection = pymssql.connect(
                server=sql_server_config.get('HOST'),
                port=int(sql_server_config.get('PORT', 1433)),
                user=sql_server_config.get('USER'),
                password=sql_server_config.get('PASSWORD'),
                database=sql_server_config.get('NAME'),
                timeout=30
            )
            cursor = connection.cursor(as_dict=True)
            print(f"✅ Connected successfully!\n")

            print(f"📅 Fetching inspections and account codes from SQL Server...")
            print(f"   Query: FSA_INSPECTION_QUERY (includes InternalAccountNumber)")

            # Use the FSA_INSPECTION_QUERY that's already working
            cursor.execute(FSA_INSPECTION_QUERY)

            sql_inspections = cursor.fetchall()
            print(f"\n📊 Retrieved {len(sql_inspections)} inspections from SQL Server")
            print(f"   Each inspection includes: Client Name, Account Code, Date, Inspector, Commodity")

            # Tracking stats
            synced_count = 0
            updated_count = 0
            product_names_updated = 0

            # NEW: Account code tracking
            account_codes_found = 0
            google_sheets_matched = 0
            google_sheets_used = 0
            sql_server_fallback = 0

            # Set initial progress
            cache.set('sync_progress', {
                'status': 'running',
                'current': 0,
                'total': len(sql_inspections),
                'percent': 0,
                'message': 'Phase 1/3: Syncing inspections with Google Sheets...'
            }, 300)

            print(f"\n" + "="*80)
            print(f"📋 PHASE 1/3: SYNC INSPECTIONS + MATCH CLIENT NAMES")
            print(f"   SQL Server → Inspection Data + Account Codes")
            print(f"   Google Sheets → Client Names (SOLE SOURCE)")
            print(f"   (Product names will be fetched in bulk in Phase 2)")
            print("="*80)

            for idx, sql_insp in enumerate(sql_inspections, 1):
                try:
                    inspection_id = sql_insp.get('Id')
                    client_name_sql = sql_insp.get('Client')  # Client name from SQL Server
                    internal_account_code = sql_insp.get('InternalAccountNumber')  # Account code from SQL Server
                    inspection_date = sql_insp.get('DateOfInspection')
                    inspector_id = sql_insp.get('InspectorId')
                    commodity = sql_insp.get('Commodity')

                    # Get inspector name from mapping
                    try:
                        inspector_id_int = int(inspector_id) if inspector_id is not None else None
                    except (TypeError, ValueError):
                        inspector_id_int = None
                    inspector_name = INSPECTOR_NAME_MAP.get(inspector_id_int, 'Unknown')

                    # IMPORTANT: ONLY use Google Sheets for client names
                    # SQL Server ONLY provides: inspection data, account code
                    # Google Sheets is the SOLE source for client names
                    from ..models import Client
                    client_name = None  # Will be set from Google Sheets ONLY
                    google_sheets_match_found = False

                    # Log only every 100th inspection to reduce console spam (was every 10th - too verbose!)
                    # Only log first 3 inspections for initial verification
                    show_detailed_log = (idx <= 3) or (idx % 100 == 0)

                    if internal_account_code:
                        account_codes_found += 1

                        # Look up client in Google Sheets by account code
                        try:
                            google_client = Client.objects.filter(
                                internal_account_code=internal_account_code
                            ).first()

                            if google_client and google_client.name:
                                # Use Google Sheets name (ONLY source for names)
                                google_sheets_matched += 1
                                google_sheets_match_found = True
                                client_name = google_client.name
                                google_sheets_used += 1

                                if show_detailed_log:
                                    print(f"\n   [{idx}/{len(sql_inspections)}] Inspection #{inspection_id}")
                                    print(f"      📋 Account Code: {internal_account_code}")
                                    print(f"      ✅ Google Sheets Match: FOUND")
                                    print(f"      📊 Google Sheets Name: {google_client.name}")
                                    print(f"      ⭐ USING: {client_name} (from Google Sheets)")
                            else:
                                # No match in Google Sheets - leave as "-"
                                sql_server_fallback += 1
                                client_name = "-"
                                if show_detailed_log:
                                    print(f"\n   [{idx}/{len(sql_inspections)}] Inspection #{inspection_id}")
                                    print(f"      📋 Account Code: {internal_account_code}")
                                    print(f"      ❌ Google Sheets Match: NOT FOUND")
                                    print(f"      ⚠️  Client name set to: -")
                                    print(f"      → Add account code '{internal_account_code}' to Google Sheets to set client name!")

                        except Exception as e:
                            # Error looking up Google Sheets - leave as "-"
                            sql_server_fallback += 1
                            client_name = "-"
                            if show_detailed_log:
                                print(f"\n   [{idx}/{len(sql_inspections)}] Inspection #{inspection_id}")
                                print(f"      📋 Account Code: {internal_account_code}")
                                print(f"      ⚠️  Error looking up Google Sheets: {e}")
                                print(f"      ⚠️  Client name set to: -")
                    else:
                        # No account code - leave as "-" (cannot look up in Google Sheets without account code)
                        sql_server_fallback += 1
                        client_name = "-"
                        if show_detailed_log:
                            print(f"\n   [{idx}/{len(sql_inspections)}] Inspection #{inspection_id}")
                            print(f"      📋 Account Code: NONE")
                            print(f"      ⚠️  Cannot look up in Google Sheets without account code")
                            print(f"      ⚠️  Client name set to: -")

                    # PHASE 1: Create inspection WITHOUT product names (products will be added in bulk in Phase 2)
                    # Using create() since we deleted all records - no need for update_or_create
                    inspection = FoodSafetyAgencyInspection.objects.create(
                        remote_id=inspection_id,
                        client_name=client_name,  # Use Google Sheets name if matched
                        internal_account_code=internal_account_code,  # Store account code for future matches
                        date_of_inspection=inspection_date,
                        inspector_name=inspector_name,
                        commodity=commodity
                        # Note: product_name will be added in Phase 2 bulk fetch
                    )

                    synced_count += 1

                    # Progress indicator every 250 inspections (was 50 - reduced console spam)
                    if idx % 250 == 0:
                        print(f"\n   📈 Phase 1 Progress: {idx}/{len(sql_inspections)} inspections synced...")
                        print(f"      - Account codes found: {account_codes_found}")
                        print(f"      - Google Sheets matches: {google_sheets_matched}")
                        print(f"      - Using Google Sheets names: {google_sheets_used}")
                        print(f"      - Using placeholder names: {sql_server_fallback}")

                        # Update progress in cache for frontend (Phase 1 = 0-60% of total progress)
                        progress_percent = int((idx / len(sql_inspections)) * 60)
                        cache.set('sync_progress', {
                            'status': 'running',
                            'current': idx,
                            'total': len(sql_inspections),
                            'percent': progress_percent,
                            'message': f'Phase 1/3: Syncing inspections {idx}/{len(sql_inspections)} ({progress_percent}%)'
                        }, 300)

                except Exception as e:
                    print(f"\n   ⚠️  Error syncing inspection {inspection_id}: {e}")
                    continue

            # PHASE 1 COMPLETE
            print(f"\n" + "="*80)
            print(f"✅ PHASE 1 COMPLETE: Inspections created with client names!")
            print(f"   - New inspections created: {synced_count}")
            print(f"   - Google Sheets matches: {google_sheets_matched}/{account_codes_found}")
            print("="*80)

            # Update progress: Phase 1 done (60%)
            cache.set('sync_progress', {
                'status': 'running',
                'current': len(sql_inspections),
                'total': len(sql_inspections),
                'percent': 60,
                'message': 'Phase 2/3: Fetching product names in bulk...'
            }, 300)

            # PHASE 2: BULK FETCH ALL PRODUCT NAMES
            print(f"\n" + "="*80)
            print(f"📦 PHASE 2/3: BULK FETCH PRODUCT NAMES")
            print(f"   Fetching products for ALL {len(sql_inspections)} inspections at once...")
            print(f"   (This is MUCH faster than fetching individually!)")
            print("="*80)

            # Get all inspection IDs
            inspection_ids = [insp.get('Id') for insp in sql_inspections if insp.get('Id')]

            # Bulk fetch all product names
            product_map = fetch_all_product_names_bulk(inspection_ids)

            # Update progress: Phase 2 done (80%)
            cache.set('sync_progress', {
                'status': 'running',
                'current': len(sql_inspections),
                'total': len(sql_inspections),
                'percent': 80,
                'message': 'Phase 3/3: Updating inspections with product names...'
            }, 300)

            # PHASE 3: UPDATE INSPECTIONS WITH PRODUCT NAMES (NO SPLITTING)
            print(f"\n" + "="*80)
            print(f"🔄 PHASE 3/3: UPDATE INSPECTIONS WITH PRODUCT NAMES")
            print(f"   Adding product names to existing inspection records...")
            print(f"   (Multiple products will be comma-separated in one record)")
            print("="*80)

            # Update inspections with product names (NO splitting - keep one record per inspection)
            for idx, sql_insp in enumerate(sql_inspections, 1):
                try:
                    inspection_id = sql_insp.get('Id')

                    # Get the inspection record
                    inspection = FoodSafetyAgencyInspection.objects.filter(
                        remote_id=inspection_id
                    ).first()

                    if inspection and inspection_id in product_map:
                        product_names = product_map[inspection_id]
                        if product_names and len(product_names) > 0:
                            # Join multiple products with comma separation
                            combined_product_name = ", ".join(product_names)
                            inspection.product_name = combined_product_name
                            inspection.save()
                            product_names_updated += 1

                    # Progress every 200 inspections
                    if idx % 200 == 0:
                        progress_percent = 80 + int((idx / len(sql_inspections)) * 20)  # 80-100%
                        print(f"   📈 Phase 3 Progress: {idx}/{len(sql_inspections)} updated ({progress_percent}%)...")
                        cache.set('sync_progress', {
                            'status': 'running',
                            'current': idx,
                            'total': len(sql_inspections),
                            'percent': progress_percent,
                            'message': f'Phase 3/3: Updating products {idx}/{len(sql_inspections)} ({progress_percent}%)'
                        }, 300)

                except Exception as e:
                    print(f"   ⚠️  Error updating products for inspection {inspection_id}: {e}")
                    continue

            print(f"\n✅ PHASE 3 COMPLETE: Product names updated!")
            print(f"   - Inspections processed: {len(sql_inspections)}")
            print(f"   - Inspections with products: {product_names_updated}")
            print(f"   - Multiple products stored as comma-separated values")

            cursor.close()
            connection.close()

            # Summary
            total_inspections = FoodSafetyAgencyInspection.objects.count()

            print(f"\n" + "="*80)
            print(f"✅ SQL SERVER SYNC COMPLETED (FULL REFRESH)")
            print("="*80)
            print(f"\n📊 Sync Statistics:")
            print(f"   - Old inspections deleted: {existing_count:,}")
            print(f"   - SQL Server inspections fetched: {len(sql_inspections)}")
            print(f"   - New inspections created: {synced_count:,}")
            print(f"   - Inspections with product names: {product_names_updated:,}")
            print(f"\n📋 Account Code & Name Matching Statistics:")
            print(f"   - Inspections with account codes: {account_codes_found} ({(account_codes_found/len(sql_inspections)*100) if len(sql_inspections) > 0 else 0:.1f}%)")
            print(f"   - Google Sheets matches found: {google_sheets_matched} ({(google_sheets_matched/account_codes_found*100) if account_codes_found > 0 else 0:.1f}% of those with codes)")
            print(f"   - Using Google Sheets names: {google_sheets_used}")
            print(f"   - Using placeholders (no match): {sql_server_fallback}")
            print(f"\n💾 Database Status:")
            print(f"   - Total inspection records in database: {total_inspections:,}")
            print(f"   - (One record per inspection, multiple products comma-separated)")
            print(f"\n⭐ Data Sources:")
            print(f"   - SQL Server provides: inspection data + account codes + products")
            print(f"   - Google Sheets provides: client names (via account code lookup)")
            print(f"   - Update client names in Google Sheets and resync to see changes instantly!")
            print("="*80 + "\n")

            # Set final progress to 100%
            cache.set('sync_progress', {
                'status': 'completed',
                'current': len(sql_inspections),
                'total': len(sql_inspections),
                'percent': 100,
                'message': f'Sync completed! Processed {len(sql_inspections)} inspections.'
            }, 300)

            self.last_sync_times['sql_server'] = datetime.now()
            return True

        except Exception as e:
            print(f"\n❌ Error in SQL Server sync: {e}")
            import traceback
            traceback.print_exc()
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

    def _auto_restart_if_needed(self):
        """Auto-restart service if it was running before Django reloaded."""
        try:
            was_running = cache.get('scheduled_sync_service:running', False)
            if was_running:
                # Don't print on every page load - only on actual restart
                if not self.sync_thread or not self.sync_thread.is_alive():
                    print("🔄 Auto-restarting sync service (was running before)...")
                    self.is_running = True
                    self._load_stats()
                    self.sync_thread = threading.Thread(target=self._background_service_loop, daemon=True)
                    self.sync_thread.start()
                    print("✅ Sync service auto-restarted successfully")
        except Exception as e:
            print(f"⚠️ Failed to auto-restart sync service: {e}")

    def start_background_service(self):
        """Start the background sync service."""
        # Check if already running via cache (persistent across page refreshes)
        if cache.get('scheduled_sync_service:running'):
            if self.sync_thread and self.sync_thread.is_alive():
                return False, "Background sync service already running"
            # Thread died but cache says running - restart it
            print("⚠️ Service was marked running but thread died. Restarting...")

        self.is_running = True
        self._load_stats()
        # Increase cache TTL to 7 days (604800 seconds) for true persistence
        cache.set('scheduled_sync_service:running', True, 604800)

        # Start background thread (daemon=True means it won't block shutdown)
        self.sync_thread = threading.Thread(target=self._background_service_loop, daemon=True)
        self.sync_thread.start()

        print("✅ Scheduled sync service started successfully")
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
        from django.db import close_old_connections

        print("🚀 Background sync service loop started")

        while self.is_running:
            try:
                # Update heartbeat to show service is alive
                cache.set('scheduled_sync_service:heartbeat', datetime.now().isoformat(), 60)

                # Close old database connections to prevent stale connection errors
                close_old_connections()

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
                            try:
                                close_old_connections()  # Ensure fresh connection
                                sync_results['google_sheets'] = self.sync_google_sheets()
                            except Exception as e:
                                print(f"❌ Google Sheets sync failed: {e}")
                                sync_results['google_sheets'] = False

                        # SQL Server sync
                        if sql_server_due:
                            try:
                                close_old_connections()  # Ensure fresh connection
                                sync_results['sql_server'] = self.sync_sql_server()
                            except Exception as e:
                                print(f"❌ SQL Server sync failed: {e}")
                                sync_results['sql_server'] = False

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
                import traceback
                traceback.print_exc()
                # Close connections on error too
                try:
                    close_old_connections()
                except:
                    pass
                time.sleep(60)  # Wait 1 minute before retrying

        print("🛑 Background sync service loop stopped")
    
    def get_service_status(self):
        """Get current service status."""
        try:
            is_running = cache.get('scheduled_sync_service:running', False)
            heartbeat = cache.get('scheduled_sync_service:heartbeat')
            settings = self.get_system_settings()

            # Check if service is truly alive by checking heartbeat
            service_alive = False
            if is_running and heartbeat:
                try:
                    from dateutil.parser import parse
                    heartbeat_time = parse(heartbeat)
                    time_since_heartbeat = (datetime.now() - heartbeat_time).total_seconds()
                    service_alive = time_since_heartbeat < 120  # Service is alive if heartbeat within 2 minutes
                except:
                    service_alive = False

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

            # Check for Google Sheets sync errors
            google_sheets_error = cache.get('google_sheets_sync_error')

            return {
                'is_running': is_running,
                'service_alive': service_alive,
                'heartbeat': heartbeat,
                'auto_sync_enabled': settings.get('auto_sync_enabled', False),
                'last_sync_times': self.last_sync_times,
                'next_sync_times': next_syncs,
                'sync_stats': self.sync_stats,
                'settings': settings,
                'google_sheets_error': google_sheets_error  # Include any Google Sheets sync errors
            }

        except Exception as e:
            print(f"❌ Error getting service status: {e}")
            import traceback
            traceback.print_exc()
            return {
                'is_running': False,
                'service_alive': False,
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
    
    def get_configuration(self):
        """Get service configuration."""
        try:
            settings = self.get_system_settings()
            return {
                'sync_interval': settings.get('sync_interval_hours', 24),
                'google_sheets_enabled': settings.get('google_sheets_enabled', True),
                'sql_server_enabled': settings.get('sql_server_enabled', True),
                'is_running': self.is_running
            }
        except Exception as e:
            print(f"Error getting configuration: {e}")
            return {
                'sync_interval': 24,
                'google_sheets_enabled': False,
                'sql_server_enabled': False,
                'is_running': False
            }
    
    def get_status(self):
        """Get current service status."""
        try:
            self._load_stats()
            return {
                'running': self.is_running,
                'last_sync_time': self.sync_stats.get('last_sync_time'),
                'next_sync_time': self.sync_stats.get('next_sync_time'),
                'total_syncs': self.sync_stats.get('total_syncs', 0),
                'successful_syncs': self.sync_stats.get('successful_syncs', 0),
                'failed_syncs': self.sync_stats.get('failed_syncs', 0),
                'configuration': self.get_configuration()
            }
        except Exception as e:
            print(f"Error getting status: {e}")
            return {
                'running': False,
                'error': str(e)
            }


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
