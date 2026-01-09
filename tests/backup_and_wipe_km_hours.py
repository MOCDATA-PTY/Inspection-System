#!/usr/bin/env python3
"""
Backup and Wipe KM and Hours Data from PostgreSQL Database
This script will:
1. Extract all km_traveled and hours data from the FoodSafetyAgencyInspection table
2. Save the data to a backup CSV file with timestamp
3. Clear all km_traveled and hours fields in the database
4. Verify the operation was successful
"""

import os
import django
import csv
from datetime import datetime
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import connection
from main.models import FoodSafetyAgencyInspection

def backup_km_hours_data():
    """Extract and backup all km and hours data to CSV file"""
    print("\n" + "="*80)
    print("BACKING UP KM AND HOURS DATA")
    print("="*80)
    
    # Create timestamp for backup file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"km_hours_backup_{timestamp}.csv"
    
    with connection.cursor() as cursor:
        # Get all inspections with km or hours data
        cursor.execute("""
            SELECT
                id,
                remote_id,
                client_name,
                date_of_inspection,
                inspector_name,
                km_traveled,
                hours,
                inspection_travel_distance_km,
                bought_sample,
                commodity,
                product_name,
                product_class,
                latitude,
                longitude,
                approved_status,
                lab,
                fat,
                protein,
                calcium,
                dna
            FROM food_safety_agency_inspections
            WHERE km_traveled IS NOT NULL OR hours IS NOT NULL
            ORDER BY date_of_inspection DESC, id DESC
        """)
        
        results = cursor.fetchall()
        
        if not results:
            print("[INFO] No inspections with KM or Hours data found to backup")
            return None, 0
        
        # Write to CSV file
        with open(backup_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'remote_id', 'client_name', 'date_of_inspection', 'inspector_name',
                'km_traveled', 'hours', 'inspection_travel_distance_km', 'bought_sample',
                'commodity', 'product_name', 'product_class', 'latitude', 'longitude',
                'approved_status', 'lab', 'fat', 'protein', 'calcium', 'dna'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in results:
                writer.writerow({
                    'id': row[0],
                    'remote_id': row[1],
                    'client_name': row[2],
                    'date_of_inspection': row[3].strftime('%Y-%m-%d') if row[3] else '',
                    'inspector_name': row[4],
                    'km_traveled': row[5],
                    'hours': row[6],
                    'inspection_travel_distance_km': row[7],
                    'bought_sample': row[8],
                    'commodity': row[9],
                    'product_name': row[10],
                    'product_class': row[11],
                    'latitude': row[12],
                    'longitude': row[13],
                    'approved_status': row[14],
                    'lab': row[15],
                    'fat': row[16],
                    'protein': row[17],
                    'calcium': row[18],
                    'dna': row[19]
                })
        
        print(f"[SUCCESS] Backed up {len(results)} inspections to: {backup_filename}")
        
        # Also create a summary JSON file
        summary_filename = f"km_hours_summary_{timestamp}.json"
        summary_data = {
            'backup_timestamp': timestamp,
            'total_records_backed_up': len(results),
            'backup_file': backup_filename,
            'database': 'inspection_system',
            'table': 'food_safety_agency_inspections',
            'fields_backed_up': ['km_traveled', 'hours'],
            'additional_fields_included': [
                'id', 'remote_id', 'client_name', 'date_of_inspection', 'inspector_name',
                'inspection_travel_distance_km', 'bought_sample', 'commodity', 'product_name',
                'product_class', 'latitude', 'longitude', 'approved_status', 'lab',
                'fat', 'protein', 'calcium', 'dna'
            ],
            'statistics': {
                'records_with_km': len([r for r in results if r[5] is not None]),
                'records_with_hours': len([r for r in results if r[6] is not None]),
                'records_with_both': len([r for r in results if r[5] is not None and r[6] is not None])
            }
        }
        
        with open(summary_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(summary_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] Created summary file: {summary_filename}")
        
        return backup_filename, len(results)

def wipe_km_hours_data():
    """Clear all km_traveled and hours data from the database"""
    print("\n" + "="*80)
    print("WIPING KM AND HOURS DATA FROM DATABASE")
    print("="*80)
    
    # Count how many inspections have KM or Hours data before wiping
    inspections_with_data = FoodSafetyAgencyInspection.objects.filter(
        km_traveled__isnull=False
    ) | FoodSafetyAgencyInspection.objects.filter(
        hours__isnull=False
    )
    
    count_with_data = inspections_with_data.count()
    print(f"[INFO] Found {count_with_data} inspections with KM or Hours data to wipe")
    
    if count_with_data > 0:
        # Clear all KM and Hours fields
        updated_count = FoodSafetyAgencyInspection.objects.all().update(
            km_traveled=None,
            hours=None
        )
        print(f"[SUCCESS] Cleared KM and Hours data from {updated_count} inspections")
        return updated_count
    else:
        print("[INFO] No inspections with KM or Hours data found to wipe")
        return 0

def verify_wipe():
    """Verify that all km and hours data has been cleared"""
    print("\n" + "="*80)
    print("VERIFYING DATA WIPE")
    print("="*80)
    
    # Check remaining data
    remaining = FoodSafetyAgencyInspection.objects.filter(
        km_traveled__isnull=False
    ) | FoodSafetyAgencyInspection.objects.filter(
        hours__isnull=False
    )
    
    remaining_count = remaining.count()
    
    if remaining_count == 0:
        print("[SUCCESS] All KM and Hours data has been cleared successfully!")
        return True
    else:
        print(f"[WARNING] {remaining_count} inspections still have KM or Hours data")
        return False

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("KM AND HOURS DATA BACKUP AND WIPE OPERATION")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Backup the data
        backup_file, backup_count = backup_km_hours_data()
        
        if backup_count == 0:
            print("\n[INFO] No data to backup or wipe. Exiting.")
            return
        
        # Step 2: Wipe the data
        wiped_count = wipe_km_hours_data()
        
        # Step 3: Verify the operation
        verification_success = verify_wipe()
        
        # Final summary
        print("\n" + "="*80)
        print("OPERATION SUMMARY")
        print("="*80)
        print(f"Records backed up: {backup_count}")
        print(f"Records wiped: {wiped_count}")
        print(f"Backup file: {backup_file}")
        print(f"Verification: {'PASSED' if verification_success else 'FAILED'}")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if verification_success:
            print("\n[SUCCESS] Operation completed successfully!")
        else:
            print("\n[ERROR] Operation completed with warnings!")
            
    except Exception as e:
        print(f"\n[ERROR] Operation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
