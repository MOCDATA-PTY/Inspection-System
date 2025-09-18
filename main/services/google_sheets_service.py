import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.conf import settings
from django.utils import timezone
import pickle

class GoogleSheetsService:
    """Service class for interacting with Google Sheets API"""
    
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.token_path = os.path.join(settings.BASE_DIR, 'token.pickle')
        self.credentials_path = os.path.join(settings.BASE_DIR, 'credentials.json')
        # Use the exact redirect URI from your Google Cloud Console
        self.redirect_uri = 'http://127.0.0.1:8000/google-sheets/oauth2callback/'
        
    def authenticate(self, request=None):
        """Authenticate with Google Sheets API"""
        # The file token.pickle stores the user's access and refresh tokens,
        # and is created automatically when the authorization flow completes for the first time.
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        "credentials.json file not found. Please download it from Google Cloud Console "
                        "and place it in your project root directory."
                    )
                
                # Check if we have an authorization code from Django session
                auth_code = None
                if request and hasattr(request, 'session'):
                    auth_code = request.session.get('google_auth_code')
                    if auth_code:
                        # Clear the code from session after use
                        del request.session['google_auth_code']
                
                if auth_code:
                    # Use the authorization code from Django session
                    flow = Flow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES, redirect_uri=self.redirect_uri)
                    flow.fetch_token(code=auth_code)
                    self.creds = flow.credentials
                else:
                    # Generate authorization URL for manual flow
                    flow = Flow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES, redirect_uri=self.redirect_uri)
                    
                    auth_url, _ = flow.authorization_url(
                        prompt='consent', access_type='offline', include_granted_scopes='true'
                    )
                    print(f"\n🔐 Please visit this URL to authorize the application:")
                    print(f"   {auth_url}")
                    print(f"\n📝 After authorization, you'll be redirected to: {self.redirect_uri}")
                    print(f"📋 Copy the 'code' parameter from the URL and paste it below.")
                    
                    # Get authorization code from user
                    auth_code = input("\n🔑 Enter the authorization code: ").strip()
                    
                    # Exchange code for tokens
                    flow.fetch_token(code=auth_code)
                    self.creds = flow.credentials
            
            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)
        
        # Build the service
        self.service = build('sheets', 'v4', credentials=self.creds)
        return self.service
    
    def get_sheet_data(self, spreadsheet_id, range_name, request=None):
        """Get data from a specific range in the spreadsheet"""
        if not self.service:
            self.authenticate(request)
        
        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            return values
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def get_columns_h_and_j(self, spreadsheet_id, start_row=2, request=None):
        """Get data from columns H and J starting from row 2"""
        # Column H is the 8th column (0-indexed), Column J is the 10th column (0-indexed)
        # We'll fetch both columns and combine them
        range_h = f"H{start_row}:H"
        range_j = f"J{start_row}:J"
        
        data_h = self.get_sheet_data(spreadsheet_id, range_h, request)
        data_j = self.get_sheet_data(spreadsheet_id, range_j, request)
        
        if not data_h or not data_j:
            return []
        
        # Combine the data from both columns
        combined_data = []
        max_rows = max(len(data_h), len(data_j))
        
        for i in range(max_rows):
            h_value = data_h[i][0] if i < len(data_h) and data_h[i] else ""
            j_value = data_j[i][0] if i < len(data_j) and data_j[i] else ""
            combined_data.append({
                'column_h': h_value,
                'column_j': j_value,
                'row_number': start_row + i
            })
        
        return combined_data
    
    def get_columns_h_j_k_from_sheet(self, spreadsheet_id, sheet_name, start_row=2, request=None):
        """Get data from columns H, J, and K starting from row 2 from a specific sheet"""
        # Column H is the 8th column (0-indexed), Column J is the 10th column (0-indexed), Column K is the 11th column (0-indexed)
        # We'll fetch all three columns and combine them from the specified sheet
        range_h = f"'{sheet_name}'!H{start_row}:H"
        range_j = f"'{sheet_name}'!J{start_row}:J"
        range_k = f"'{sheet_name}'!K{start_row}:K"
        
        data_h = self.get_sheet_data(spreadsheet_id, range_h, request)
        data_j = self.get_sheet_data(spreadsheet_id, range_j, request)
        data_k = self.get_sheet_data(spreadsheet_id, range_k, request)
        
        if not data_h or not data_j:
            return []
        
        # Combine the data from all three columns
        combined_data = []
        max_rows = max(len(data_h), len(data_j), len(data_k) if data_k else 0)
        
        for i in range(max_rows):
            h_value = data_h[i][0] if i < len(data_h) and data_h[i] else ""
            j_value = data_j[i][0] if i < len(data_j) and data_j[i] else ""
            k_value = data_k[i][0] if data_k and i < len(data_k) and data_k[i] else ""
            combined_data.append({
                'column_h': h_value,
                'column_j': j_value,
                'column_k': k_value,
                'row_number': start_row + i
            })
        
        return combined_data
    
    def get_specific_sheet_data(self, request=None):
        """Get data from the specific spreadsheet you mentioned - ONLY GET DATA, DON'T POPULATE"""
        spreadsheet_id = "1iNULGBAzJ9n2ZulxwP8ZZZbwcPhj7X6e6rPwYqtI_fM"
        # Specify the sheet name - "Internal Account Code Generator"
        sheet_name = "Internal Account Code Generator"
        
        # Fetch the data including emails (columns H, J, K) - NO AUTO POPULATION
        sheet_data = self.get_columns_h_j_k_from_sheet(spreadsheet_id, sheet_name, start_row=2, request=request)
        
        return sheet_data
    
    def populate_clients_table(self, sheet_data, request=None):
        """Populate the Food Safety Agency clients table with data from Google Sheets"""
        from django.contrib import messages
        from ..models import Client
        
        if not sheet_data:
            return {'success': False, 'error': 'No data provided'}
        
        clients_created = 0
        clients_updated = 0
        total_processed = 0
        
        try:
            for row_data in sheet_data:
                total_processed += 1
                
                # Column H = internal account code, Column J = client name, Column K = email
                internal_account_code = row_data.get('column_h', '').strip()
                client_name = row_data.get('column_j', '').strip()
                email = row_data.get('column_k', '').strip()
                
                # Skip empty rows
                if not client_name or not internal_account_code:
                    continue
                
                # Clean email (remove whitespace, validate basic format)
                if email and '@' not in email:
                    email = ''  # Invalid email format
                
                # Convert "None" to null/empty string
                if email.lower() == 'none':
                    email = ''
                
                # Check if client already exists by client_id
                existing_client = Client.objects.filter(name=client_name).first()
                
                if existing_client:
                    # Update existing client
                    existing_client.name = client_name
                    existing_client.internal_account_code = internal_account_code
                    existing_client.email = email if email else None
                    existing_client.save()
                    clients_updated += 1
                else:
                    # Create new client with unique ID
                    import time
                    unique_id = f"CL{int(time.time() * 1000) % 100000:05d}{total_processed:03d}"
                    Client.objects.create(
                        name=client_name,
                        client_id=unique_id,
                        internal_account_code=internal_account_code,
                        email=email if email else None
                    )
                    clients_created += 1
            
            return {
                'success': True,
                'clients_created': clients_created,
                'clients_updated': clients_updated,
                'total_processed': total_processed
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'clients_created': clients_created,
                'clients_updated': clients_updated,
                'total_processed': total_processed
            }

    def refresh_clients_table(self, request=None):
        """Sync the Food Safety Agency clients table with fresh data from Google Sheets (preserves existing relationships)"""
        from django.contrib import messages
        from django.db import transaction
        from ..models import Client, Shipment
        
        try:
            # Check if there are shipments that would prevent full deletion
            shipment_count = Shipment.objects.count()
            
            if shipment_count > 0:
                print(f"🛡️  Found {shipment_count:,} existing shipments - using preservation sync")
                return self._sync_with_preservation(request)
            else:
                print("🗑️  No existing shipments - using full replacement sync")
                return self._sync_with_full_replacement(request)
                
        except Exception as e:
            print(f"      ❌ Exception during client sync: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'deleted_count': 0,
                'clients_created': 0,
                'total_processed': 0
            }
    
    def _sync_with_preservation(self, request=None):
        """Sync clients while preserving existing relationships"""
        from ..models import Client
        import uuid
        
        print("   🔄 Step 2.1: Starting preservation sync...")
        initial_count = Client.objects.count()
        print(f"      📊 Initial client count: {initial_count:,}")
        
        print("\n   📥 Step 2.2: Fetching fresh data from Google Sheets...")
        sheet_data = self.get_specific_sheet_data(request)
        
        if not sheet_data:
            print("      ❌ No data received from Google Sheets")
            return {
                'success': False,
                'error': 'No data fetched from Google Sheets',
                'deleted_count': 0,
                'clients_created': 0,
                'total_processed': 0
            }
        
        print(f"      📊 Received {len(sheet_data)} rows from Google Sheets")
        
        # Get existing clients for comparison
        existing_clients_by_code = {}
        existing_clients_by_name = {}
        for client in Client.objects.all():
            if client.internal_account_code:
                existing_clients_by_code[client.internal_account_code] = client
            existing_clients_by_name[client.name] = client
        
        clients_created = 0
        clients_updated = 0
        total_processed = 0
        skipped_rows = 0
        
        print("\n   🔄 Step 2.3: Processing and updating/creating clients...")
        
        # Simple processing - just grab data as it is
        for i, row_data in enumerate(sheet_data, 1):
            total_processed += 1
            
            # Extract data exactly as it is
            internal_account_code = row_data.get('column_h', '').strip()
            client_name = row_data.get('column_j', '').strip()
            email = row_data.get('column_k', '').strip()
            
            # Skip empty rows only
            if not client_name or not internal_account_code:
                skipped_rows += 1
                continue
            
            # Clean email only
            if email and email.lower() == 'none':
                email = ''
            
            # Try to find existing client by account code
            existing_client = existing_clients_by_code.get(internal_account_code)
            
            if existing_client:
                # Update existing client
                updated = False
                if existing_client.name != client_name:
                    existing_client.name = client_name
                    updated = True
                if not existing_client.manual_email and existing_client.email != (email if email else None):
                    existing_client.email = email if email else None
                    updated = True
                
                if updated:
                    existing_client.save()
                    clients_updated += 1
                    if i <= 5:
                        print(f"      ✅ Updated: {client_name}")
            else:
                # Create new client
                unique_id = f"CL{uuid.uuid4().hex[:8].upper()}{i:04d}"
                new_client = Client.objects.create(
                    name=client_name,
                    client_id=unique_id,
                    internal_account_code=internal_account_code,
                    email=email if email else None
                )
                clients_created += 1
                if i <= 5:
                    print(f"      ✅ Created: {client_name}")
            
            # Periodically save session to prevent timeout
            if request and i % 1000 == 0:
                try:
                    request.session.save()
                except:
                    pass
        
        final_count = Client.objects.count()
        
        print(f"      📈 Summary: Created {clients_created} new clients, updated {clients_updated} existing clients, skipped {skipped_rows} empty rows")
        
        return {
            'success': True,
            'deleted_count': 0,  # No deletions with preservation
            'clients_created': clients_created,
            'clients_updated': clients_updated,
            'total_processed': total_processed,
            'final_count': final_count
        }
    
    def _sync_with_full_replacement(self, request=None):
        """Full replacement sync (original logic) - SINGLE RUN ONLY"""
        from ..models import Client
        from django.db import transaction
        from django.core.cache import cache
        import uuid
        
        # Check if sync is already running
        if cache.get('client_sync_running'):
            print("   ⚠️  Client sync already running - skipping duplicate request")
            return {
                'success': False,
                'error': 'Client sync is already running',
                'deleted_count': 0,
                'clients_created': 0,
                'total_processed': 0
            }
        
        # Set sync lock
        cache.set('client_sync_running', True, 300)  # 5 minutes timeout
        
        try:
            # Wrap the entire operation in a transaction to ensure atomicity
            with transaction.atomic():
                print("   🗑️  Step 2.1: Clearing existing clients from database...")
                # Clear all existing Food Safety Agency clients
                deleted_count = Client.objects.count()
                print(f"      📊 Found {deleted_count} existing clients to delete")
                Client.objects.all().delete()
                print(f"      ✅ Successfully deleted {deleted_count} existing clients")
            
            print("\n   📥 Step 2.2: Fetching fresh data from Google Sheets...")
            # Fetch fresh data from Google Sheets including emails
            sheet_data = self.get_specific_sheet_data(request)
            
            if not sheet_data:
                print("      ❌ No data received from Google Sheets")
                return {
                    'success': False,
                    'error': 'No data fetched from Google Sheets',
                    'deleted_count': deleted_count,
                    'clients_created': 0,
                    'total_processed': 0
                }
            
            print(f"      📊 Received {len(sheet_data)} rows from Google Sheets")
            
            clients_created = 0
            total_processed = 0
            skipped_rows = 0
            
            print("\n   🔄 Step 2.3: Processing and creating new clients...")
            
            # Use bulk_create for efficiency
            client_objects = []
            
            # Create new clients from fresh data - SIMPLE, NO PROCESSING
            for i, row_data in enumerate(sheet_data, 1):
                total_processed += 1
                
                # Extract data exactly as it is
                internal_account_code = row_data.get('column_h', '').strip()
                client_name = row_data.get('column_j', '').strip()
                email = row_data.get('column_k', '').strip()
                
                # Only skip completely empty rows
                if not client_name or not internal_account_code:
                    skipped_rows += 1
                    continue
                
                # Clean email only
                if email and email.lower() == 'none':
                    email = ''
                
                # Create client object - simple and direct
                unique_id = f"CL{uuid.uuid4().hex[:8].upper()}{i:04d}"
                client_obj = Client(
                    name=client_name,
                    client_id=unique_id,
                    internal_account_code=internal_account_code,
                    email=email if email else None
                )
                client_objects.append(client_obj)
                clients_created += 1
                
                if i <= 5:  # Show first 5 created clients
                    print(f"      ✅ Client {i}: {client_name}")
            
            # Use bulk_create for efficiency with batch processing
            if client_objects:
                print(f"      🔄 Creating {len(client_objects)} clients using bulk operations...")
                batch_size = 500  # Smaller batches for faster processing
                individual_created = 0
                total_batches = (len(client_objects) + batch_size - 1) // batch_size
                
                for i in range(0, len(client_objects), batch_size):
                    batch = client_objects[i:i + batch_size]
                    batch_num = i // batch_size + 1
                    try:
                        Client.objects.bulk_create(batch)
                        individual_created += len(batch)
                        print(f"      ✅ Batch {batch_num}/{total_batches}: {len(batch)} clients ({individual_created}/{len(client_objects)} total)")
                    except Exception as batch_error:
                        print(f"      ⚠️ Batch {batch_num} failed: {str(batch_error)}")
                        # Fallback to individual creation for this batch
                        for client_obj in batch:
                            try:
                                client_obj.save()
                                individual_created += 1
                            except Exception as individual_error:
                                print(f"      ⚠️ Failed to create client {client_obj.name}: {str(individual_error)}")
                
                print(f"      ✅ Successfully created {individual_created} clients in database")
            
            print(f"      📈 Summary: Created {clients_created} new clients, skipped {skipped_rows} empty rows")
            
            # Clear sync lock
            cache.delete('client_sync_running')
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'clients_created': clients_created,
                'total_processed': total_processed
            }
            
        except Exception as e:
            # Clear sync lock on error
            cache.delete('client_sync_running')
            print(f"      ❌ Exception during client sync: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'deleted_count': 0,
                'clients_created': 0,
                'total_processed': 0
            }

    def populate_inspections_table(self, request=None):
        """Populate the Food Safety Agency inspections table with data from remote SQL Server"""
        from django.contrib import messages
        from ..models import FoodSafetyAgencyInspection
        
        try:
            print("   🔌 Step 2.1: Connecting to SQL Server...")
            import pyodbc
            from ..views.data_views import SQLSERVER_CONNECTION_STRING, FSA_INSPECTION_QUERY, INSPECTOR_NAME_MAP
            
            # Connect to SQL Server
            connection = pyodbc.connect(SQLSERVER_CONNECTION_STRING)
            cursor = connection.cursor()
            print("      ✅ Successfully connected to SQL Server")
            
            print("\n   📋 Step 2.2: Executing inspection query...")
            # Execute the FSA inspection query
            cursor.execute(FSA_INSPECTION_QUERY)
            print("      ✅ Query executed successfully")
            
            # Fetch all results and convert to list of dictionaries
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            print(f"      📊 Retrieved {len(rows)} inspection records from SQL Server")
            
            print("\n   🗑️  Step 2.3: Clearing existing inspections from database...")
            # Clear existing data - need to delete in correct order due to foreign key constraints
            deleted_count = FoodSafetyAgencyInspection.objects.count()
            print(f"      📊 Found {deleted_count} existing inspections to delete")
            
            # First, delete inspection_document_logs records that reference inspections (if table exists)
            from django.db import connection
            with connection.cursor() as cursor:
                try:
                    cursor.execute("DELETE FROM inspection_document_logs")
                    document_logs_deleted = cursor.rowcount
                    print(f"      🗑️  Deleted {document_logs_deleted} inspection_document_logs records")
                except Exception as e:
                    if "does not exist" in str(e) or "relation" in str(e).lower():
                        print(f"      ℹ️  inspection_document_logs table does not exist (skipping)")
                    else:
                        print(f"      ⚠️  Warning: Could not delete inspection_document_logs: {e}")
            
            # PRESERVE LOCAL FIELDS: Save sent status and OneDrive tracking to temporary table
            print("      💾 Preserving local fields (sent status, OneDrive tracking)...")
            
            # Store local data in memory instead of temporary table (more reliable)
            print("      💾 Storing local data in memory...")
            local_data_dict = {}
            local_data_count = 0
            processed_remote_ids = set()
            
            for inspection in FoodSafetyAgencyInspection.objects.all():
                # Skip if we've already processed this remote_id
                if inspection.remote_id in processed_remote_ids:
                    continue
                
                local_data_dict[inspection.remote_id] = {
                    'is_sent': inspection.is_sent,
                    'sent_date': inspection.sent_date,
                    'sent_by_id': inspection.sent_by_id if inspection.sent_by else None,
                    'onedrive_uploaded': inspection.onedrive_uploaded,
                    'onedrive_upload_date': inspection.onedrive_upload_date,
                    'onedrive_folder_id': inspection.onedrive_folder_id
                }
                local_data_count += 1
                processed_remote_ids.add(inspection.remote_id)
            
            print(f"      💾 Preserved local data for {local_data_count} inspections in memory")
            
            # Now delete the inspections
            FoodSafetyAgencyInspection.objects.all().delete()
            print(f"      ✅ Successfully deleted {deleted_count} existing inspections")
            
            inspections_created = 0
            total_processed = 0
            
            print("\n   🔄 Step 2.4: Processing and creating new inspections...")
            
            # OPTIMIZATION: Use bulk_create instead of individual creates
            inspection_objects = []
            
            for i, row in enumerate(rows, 1):
                total_processed += 1
                row_dict = dict(zip(columns, row))
                
                # Extract inspector name
                inspector_id = row_dict.get('InspectorId')
                try:
                    inspector_id_int = int(inspector_id) if inspector_id is not None else None
                except (TypeError, ValueError):
                    inspector_id_int = None
                
                inspector_name = INSPECTOR_NAME_MAP.get(inspector_id_int, 'Unknown')
                
                # Create inspection object (but don't save yet)
                remote_id = row_dict.get('Id')
                inspection_obj = FoodSafetyAgencyInspection(
                    commodity=row_dict.get('Commodity'),
                    date_of_inspection=row_dict.get('DateOfInspection'),
                    start_of_inspection=row_dict.get('StartOfInspection'),
                    end_of_inspection=row_dict.get('EndOfInspection'),
                    inspection_location_type_id=row_dict.get('InspectionLocationTypeID'),
                    is_direction_present_for_this_inspection=row_dict.get('IsDirectionPresentForthisInspection', False),
                    inspector_id=inspector_id_int,
                    inspector_name=inspector_name,
                    latitude=row_dict.get('Latitude'),
                    longitude=row_dict.get('Longitude'),
                    is_sample_taken=row_dict.get('IsSampleTaken', False),
                    inspection_travel_distance_km=row_dict.get('InspectionTravelDistanceKm'),
                    remote_id=remote_id,
                    client_name=row_dict.get('Client')
                )
                
                # RESTORE LOCAL FIELDS: Apply preserved local data if it exists
                # We'll restore this data after bulk_create for better performance
                inspection_objects.append(inspection_obj)
                
                if i <= 5:  # Show first 5 created inspections for debugging
                    client_name = row_dict.get('Client', 'Unknown')
                    commodity = row_dict.get('Commodity', 'Unknown')
                    print(f"      ✅ Prepared inspection {i}: {client_name} - {commodity} (Inspector: {inspector_name})")
            
            # BULK CREATE ALL INSPECTIONS - OPTIMIZED FOR MASSIVE DATASETS
            total_inspections = len(inspection_objects)
            print(f"      🚀 Bulk creating {total_inspections} inspections...")
            
            if total_inspections > 50000:
                # For massive datasets (50k+), use larger batches and progress reporting
                batch_size = 5000
                print(f"      📊 Large dataset detected - using batch size of {batch_size}")
                
                for i in range(0, total_inspections, batch_size):
                    batch = inspection_objects[i:i + batch_size]
                    FoodSafetyAgencyInspection.objects.bulk_create(batch, batch_size=batch_size)
                    progress = ((i + len(batch)) / total_inspections) * 100
                    print(f"      ⏳ Progress: {i + len(batch):,}/{total_inspections:,} ({progress:.1f}%)")
            else:
                # For smaller datasets, use standard batch size
                FoodSafetyAgencyInspection.objects.bulk_create(inspection_objects, batch_size=2000)
            
            inspections_created = len(inspection_objects)
            print(f"      ✅ Summary: Created {inspections_created:,} inspections from {total_processed:,} records")
            
            # RESTORE LOCAL FIELDS: Apply preserved data from memory - TRUE BULK OPERATION
            print(f"      🔄 Restoring local fields for {len(local_data_dict):,} inspections from memory...")
            updated_count = 0
            
            # Get all inspections that need updating in one query
            remote_ids = list(local_data_dict.keys())
            inspections_to_update = FoodSafetyAgencyInspection.objects.filter(remote_id__in=remote_ids)
            
            # Create a mapping for quick lookup
            inspection_map = {insp.remote_id: insp for insp in inspections_to_update}
            
            # Prepare all inspections for bulk update
            inspections_for_bulk_update = []
            
            for remote_id, local_data in local_data_dict.items():
                if remote_id in inspection_map:
                    inspection = inspection_map[remote_id]
                    
                    # Get the data from our in-memory dictionary
                    is_sent = local_data['is_sent']
                    sent_date = local_data['sent_date']
                    sent_by_id = local_data['sent_by_id']
                    onedrive_uploaded = local_data['onedrive_uploaded']
                    onedrive_upload_date = local_data['onedrive_upload_date']
                    onedrive_folder_id = local_data['onedrive_folder_id']
                    
                    # Convert naive datetimes to timezone-aware if needed
                    if sent_date and timezone.is_naive(sent_date):
                        sent_date = timezone.make_aware(sent_date)
                    if onedrive_upload_date and timezone.is_naive(onedrive_upload_date):
                        onedrive_upload_date = timezone.make_aware(onedrive_upload_date)
                    
                    # Update the inspection object
                    inspection.is_sent = is_sent
                    inspection.sent_date = sent_date
                    inspection.sent_by_id = sent_by_id
                    inspection.onedrive_uploaded = onedrive_uploaded
                    inspection.onedrive_upload_date = onedrive_upload_date
                    inspection.onedrive_folder_id = onedrive_folder_id
                    
                    inspections_for_bulk_update.append(inspection)
            
            # Perform ONE bulk update operation
            if inspections_for_bulk_update:
                print(f"      🚀 Performing single bulk update for {len(inspections_for_bulk_update):,} inspections...")
                FoodSafetyAgencyInspection.objects.bulk_update(
                    inspections_for_bulk_update,
                    ['is_sent', 'sent_date', 'sent_by_id', 'onedrive_uploaded', 'onedrive_upload_date', 'onedrive_folder_id'],
                    batch_size=2000
                )
                updated_count = len(inspections_for_bulk_update)
                print(f"      ✅ Bulk update completed in one operation!")
            
            print(f"      ✅ Restored local data for {updated_count:,} inspections")
            print("      🗑️ Memory cleanup complete")
            
            # Report on preserved local data
            preserved_sent = FoodSafetyAgencyInspection.objects.filter(is_sent=True).count()
            preserved_onedrive = FoodSafetyAgencyInspection.objects.filter(onedrive_uploaded=True).count()
            print(f"      💾 Final counts: {preserved_sent} sent inspections, {preserved_onedrive} OneDrive uploads")
            
            # Close connection
            cursor.close()
            connection.close()
            print("      🔌 SQL Server connection closed")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'inspections_created': inspections_created,
                'total_processed': total_processed
            }
            
        except ImportError as e:
            print(f"      ❌ Import Error: SQL Server connector not installed")
            print(f"         Error: {str(e)}")
            return {
                'success': False,
                'error': f"SQL Server connector not installed. Please install pyodbc. Error: {str(e)}",
                'deleted_count': 0,
                'inspections_created': 0,
                'total_processed': 0
            }
        except pyodbc.Error as e:
            print(f"      ❌ SQL Server Connection Error: {str(e)}")
            return {
                'success': False,
                'error': f"SQL Server connection error: {str(e)}",
                'deleted_count': 0,
                'inspections_created': 0,
                'total_processed': 0
            }
        except Exception as e:
            print(f"      ❌ Unexpected Error: {str(e)}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'deleted_count': 0,
                'inspections_created': 0,
                'total_processed': 0
            }

    def populate_shipments_table(self, request=None):
        """Populate the shipments table with data from remote SQL Server"""
        from django.contrib import messages
        from ..models import Shipment, Client
        
        try:
            print("   🔌 Step 2.1: Connecting to SQL Server...")
            import pyodbc
            from ..views.data_views import SQLSERVER_CONNECTION_STRING
            
            # Connect to SQL Server
            connection = pyodbc.connect(SQLSERVER_CONNECTION_STRING)
            cursor = connection.cursor()
            print("      ✅ Successfully connected to SQL Server")
            
            print("\n   📋 Step 2.2: Discovering available tables...")
            # First, let's see what tables exist in the database
            DISCOVER_TABLES_QUERY = """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'dbo' 
            AND (TABLE_NAME LIKE '%Claim%' OR TABLE_NAME LIKE '%Shipment%' OR TABLE_NAME LIKE '%Legal%' OR TABLE_NAME LIKE '%Case%' OR TABLE_NAME LIKE '%Record%')
            ORDER BY TABLE_NAME
            """
            
            cursor.execute(DISCOVER_TABLES_QUERY)
            tables = cursor.fetchall()
            print(f"      📊 Found {len(tables)} potential shipment/claim tables:")
            for table in tables:
                print(f"         - {table[0]}")
            
            if not tables:
                print("      ⚠️  No shipment/claim tables found. Let's check ALL tables...")
                ALL_TABLES_QUERY = """
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = 'dbo' 
                ORDER BY TABLE_NAME
                """
                cursor.execute(ALL_TABLES_QUERY)
                all_tables = cursor.fetchall()
                print(f"      📊 Found {len(all_tables)} total tables in database:")
                for table in all_tables:
                    print(f"         - {table[0]}")
                
                # Let's also check the Clients table structure since it exists
                print("\n      🔍 Checking Clients table structure...")
                try:
                    cursor.execute("SELECT TOP 5 * FROM Clients")
                    client_columns = [column[0] for column in cursor.description]
                    print(f"      📊 Clients table columns: {', '.join(client_columns)}")
                    
                    # Check if Clients table has any shipment-related data
                    cursor.execute("SELECT TOP 3 * FROM Clients")
                    client_rows = cursor.fetchall()
                    print(f"      📊 Sample Clients data:")
                    for i, row in enumerate(client_rows, 1):
                        row_dict = dict(zip(client_columns, row))
                        print(f"         Row {i}: {row_dict}")
                        
                except Exception as e:
                    print(f"      ❌ Error checking Clients table: {str(e)}")
                
                return {
                    'success': False,
                    'error': f'No shipment/claim tables found in database. Found {len(all_tables)} total tables. Please check the table names.',
                    'deleted_count': 0,
                    'shipments_created': 0,
                    'total_processed': 0
                }
            
            # For now, let's try the first table that might contain shipment data
            table_name = tables[0][0]
            print(f"      🔍 Trying table: {table_name}")
            
            # Execute the shipment query with the discovered table
            SHIPMENT_QUERY = f"""
            SELECT TOP 10 *
            FROM {table_name}
            """
            
            cursor.execute(SHIPMENT_QUERY)
            print("      ✅ Query executed successfully")
            
            # Get column information
            columns = [column[0] for column in cursor.description]
            print(f"      📊 Table columns: {', '.join(columns)}")
            
            # Fetch all results and convert to list of dictionaries
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            print(f"      📊 Retrieved {len(rows)} shipment records from SQL Server")
            
            print("\n   🗑️  Step 2.3: Clearing existing shipments from database...")
            # Clear existing data
            deleted_count = Shipment.objects.count()
            print(f"      📊 Found {deleted_count} existing shipments to delete")
            Shipment.objects.all().delete()
            print(f"      ✅ Successfully deleted {deleted_count} existing shipments")
            
            shipments_created = 0
            total_processed = 0
            
            print("\n   🔄 Step 2.4: Processing and creating new shipments...")
            for i, row in enumerate(rows, 1):
                total_processed += 1
                row_dict = dict(zip(columns, row))
                
                # Find or create client
                client_name = row_dict.get('Client_Name', 'Unknown Client')
                # Generate unique client_id to avoid duplicates
                import time
                unique_id = f"CL{int(time.time() * 1000) % 100000:05d}{total_processed:03d}"
                client, created = Client.objects.get_or_create(
                    name=client_name,
                    defaults={'client_id': unique_id}
                )
                
                # Create shipment record
                Shipment.objects.create(
                    Claim_No=row_dict.get('Claim_No'),
                    client=client,
                    Brand=row_dict.get('Brand'),
                    Claimant=row_dict.get('Claimant'),
                    Intent_To_Claim=row_dict.get('Intent_To_Claim'),
                    Intend_Claim_Date=row_dict.get('Intend_Claim_Date'),
                    Formal_Claim_Received=row_dict.get('Formal_Claim_Received'),
                    Formal_Claim_Date_Received=row_dict.get('Formal_Claim_Date_Received'),
                    Claimed_Amount=row_dict.get('Claimed_Amount'),
                    Amount_Paid_By_Carrier=row_dict.get('Amount_Paid_By_Carrier'),
                    Amount_Paid_By_Awa=row_dict.get('Amount_Paid_By_Awa'),
                    Amount_Paid_By_Insurance=row_dict.get('Amount_Paid_By_Insurance'),
                    Total_Savings=row_dict.get('Total_Savings'),
                    Financial_Exposure=row_dict.get('Financial_Exposure'),
                    Settlement_Status=row_dict.get('Settlement_Status'),
                    Status=row_dict.get('Status', 'OPEN'),
                    Closed_Date=row_dict.get('Closed_Date'),
                    Branch=row_dict.get('Branch', 'ATL')
                )
                shipments_created += 1
                
                if i <= 5:  # Show first 5 created shipments for debugging
                    print(f"      ✅ Created shipment {i}: {row_dict.get('Claim_No')} - {client_name}")
            
            print(f"      📈 Summary: Created {shipments_created} shipments from {total_processed} records")
            
            # Close connection
            cursor.close()
            connection.close()
            print("      🔌 SQL Server connection closed")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'shipments_created': shipments_created,
                'total_processed': total_processed
            }
            
        except ImportError as e:
            print(f"      ❌ Import Error: SQL Server connector not installed")
            print(f"         Error: {str(e)}")
            return {
                'success': False,
                'error': f"SQL Server connector not installed. Please install pyodbc. Error: {str(e)}",
                'deleted_count': 0,
                'shipments_created': 0,
                'total_processed': 0
            }
        except pyodbc.Error as e:
            print(f"      ❌ SQL Server Connection Error: {str(e)}")
            return {
                'success': False,
                'error': f"SQL Server connection error: {str(e)}",
                'deleted_count': 0,
                'shipments_created': 0,
                'total_processed': 0
            }
        except Exception as e:
            print(f"      ❌ Unexpected Error: {str(e)}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'deleted_count': 0,
                'shipments_created': 0,
                'total_processed': 0
            }
