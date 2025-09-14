import os
import json
import csv
from datetime import datetime, timedelta
from django.conf import settings
from django.core import serializers
from django.db import connection
from django.utils import timezone
from ..models import Client, Inspection, Shipment, Settings

class BackupService:
    """Service for handling data backups"""
    
    def __init__(self):
        self.backup_dir = os.path.join(settings.BASE_DIR, 'backups', 'exports')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, backup_type='manual'):
        """Create a comprehensive backup of all data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{backup_type}_backup_{timestamp}"
        
        backup_data = {
            'timestamp': timestamp,
            'backup_type': backup_type,
            'created_at': timezone.now().isoformat(),
            'data': {}
        }
        
        try:
            # Backup Clients
            clients = Client.objects.all()
            backup_data['data']['clients'] = [
                {
                    'client_id': client.client_id,
                    'name': client.name,
                    'internal_account_code': client.internal_account_code,
                    'created_at': client.created_at.isoformat(),
                    'updated_at': client.updated_at.isoformat()
                }
                for client in clients
            ]
            
            # Backup Inspections
            inspections = Inspection.objects.all()
            backup_data['data']['inspections'] = [
                {
                    'inspector': inspection.inspector,
                    'inspection_number': inspection.inspection_number,
                    'inspection_date': inspection.inspection_date.isoformat(),
                    'facility_client_name': inspection.facility_client_name,
                    'town': inspection.town,
                    'commodity': inspection.commodity,
                    'product_name': inspection.product_name,
                    'product_class': inspection.product_class,
                    'inspected': inspection.inspected,
                    'sampled': inspection.sampled,
                    'normal_hours': str(inspection.normal_hours) if inspection.normal_hours else None,
                    'kilometres_traveled': str(inspection.kilometres_traveled) if inspection.kilometres_traveled else None,
                    'fat': inspection.fat,
                    'protein': inspection.protein,
                    'calcium': inspection.calcium,
                    'dna': inspection.dna,
                    'bought_sample_amount': str(inspection.bought_sample_amount) if inspection.bought_sample_amount else None,
                    'lab_used': inspection.lab_used,
                    'follow_up': inspection.follow_up,
                    'occurrence_report': inspection.occurrence_report,
                    'dispensation_application': inspection.dispensation_application,
                    'comments': inspection.comments,
                    'uploaded': inspection.uploaded,
                    'created_at': inspection.created_at.isoformat(),
                    'updated_at': inspection.updated_at.isoformat()
                }
                for inspection in inspections
            ]
            
            # Backup Shipments
            shipments = Shipment.objects.all()
            backup_data['data']['shipments'] = [
                {
                    'Claim_No': shipment.Claim_No,
                    'client_name': shipment.client.name if shipment.client else None,
                    'client_reference': shipment.client_reference,
                    'Branch': shipment.Branch,
                    'Status': shipment.Status,
                    'Claimed_Amount': str(shipment.Claimed_Amount) if shipment.Claimed_Amount else None,
                    'Amount_Paid_By_Carrier': str(shipment.Amount_Paid_By_Carrier) if shipment.Amount_Paid_By_Carrier else None,
                    'Amount_Paid_By_Awa': str(shipment.Amount_Paid_By_Awa) if shipment.Amount_Paid_By_Awa else None,
                    'Amount_Paid_By_Insurance': str(shipment.Amount_Paid_By_Insurance) if shipment.Amount_Paid_By_Insurance else None,
                    'created_at': shipment.created_at.isoformat(),
                    'updated_at': shipment.updated_at.isoformat()
                }
                for shipment in shipments
            ]
            
            # Save as JSON
            json_file_path = os.path.join(self.backup_dir, f"{backup_name}.json")
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # Save as CSV
            csv_file_path = os.path.join(self.backup_dir, f"{backup_name}.csv")
            self._save_as_csv(backup_data, csv_file_path)
            
            # Save as Excel (if pandas is available)
            try:
                import pandas as pd
                excel_file_path = os.path.join(self.backup_dir, f"{backup_name}.xlsx")
                self._save_as_excel(backup_data, excel_file_path)
            except ImportError:
                pass  # pandas not available
            
            return {
                'success': True,
                'backup_name': backup_name,
                'files_created': [
                    f"{backup_name}.json",
                    f"{backup_name}.csv"
                ],
                'record_counts': {
                    'clients': len(backup_data['data']['clients']),
                    'inspections': len(backup_data['data']['inspections']),
                    'shipments': len(backup_data['data']['shipments'])
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_as_csv(self, backup_data, file_path):
        """Save backup data as CSV files"""
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write clients
            writer.writerow(['=== CLIENTS ==='])
            if backup_data['data']['clients']:
                writer.writerow(backup_data['data']['clients'][0].keys())
                for client in backup_data['data']['clients']:
                    writer.writerow(client.values())
            
            writer.writerow([])
            
            # Write inspections
            writer.writerow(['=== INSPECTIONS ==='])
            if backup_data['data']['inspections']:
                writer.writerow(backup_data['data']['inspections'][0].keys())
                for inspection in backup_data['data']['inspections']:
                    writer.writerow(inspection.values())
            
            writer.writerow([])
            
            # Write shipments
            writer.writerow(['=== SHIPMENTS ==='])
            if backup_data['data']['shipments']:
                writer.writerow(backup_data['data']['shipments'][0].keys())
                for shipment in backup_data['data']['shipments']:
                    writer.writerow(shipment.values())
    
    def _save_as_excel(self, backup_data, file_path):
        """Save backup data as Excel file"""
        import pandas as pd
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Clients sheet
            if backup_data['data']['clients']:
                clients_df = pd.DataFrame(backup_data['data']['clients'])
                clients_df.to_excel(writer, sheet_name='Clients', index=False)
            
            # Inspections sheet
            if backup_data['data']['inspections']:
                inspections_df = pd.DataFrame(backup_data['data']['inspections'])
                inspections_df.to_excel(writer, sheet_name='Inspections', index=False)
            
            # Shipments sheet
            if backup_data['data']['shipments']:
                shipments_df = pd.DataFrame(backup_data['data']['shipments'])
                shipments_df.to_excel(writer, sheet_name='Shipments', index=False)
    
    def get_backup_status(self):
        """Get the current backup status and next scheduled backup"""
        settings = Settings.get_settings()
        
        # Calculate next backup based on frequency
        last_backup = self._get_last_backup_time()
        if last_backup:
            if settings.backup_frequency == 'daily':
                next_backup = last_backup + timedelta(days=1)
            elif settings.backup_frequency == 'weekly':
                next_backup = last_backup + timedelta(days=7)
            elif settings.backup_frequency == 'monthly':
                next_backup = last_backup + timedelta(days=30)
            else:
                next_backup = last_backup + timedelta(days=7)  # Default to weekly
        else:
            next_backup = timezone.now()
        
        return {
            'auto_sync_enabled': settings.auto_sync,
            'backup_frequency': settings.backup_frequency,
            'last_backup': last_backup,
            'next_backup': next_backup,
            'backup_files': self._get_backup_files()
        }
    
    def _get_last_backup_time(self):
        """Get the timestamp of the last backup"""
        try:
            backup_files = self._get_backup_files()
            if backup_files:
                # Get the most recent backup file
                latest_file = max(backup_files, key=lambda x: x['timestamp'])
                return latest_file['timestamp']
        except Exception:
            pass
        return None
    
    def _get_backup_files(self):
        """Get list of available backup files"""
        backup_files = []
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.backup_dir, filename)
                    stat = os.stat(file_path)
                    backup_files.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'timestamp': datetime.fromtimestamp(stat.st_mtime),
                        'path': file_path
                    })
        except Exception:
            pass
        return backup_files
