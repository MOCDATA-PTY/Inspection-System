"""
Test script to pull the latest inspection and diagnose issues
"""
import os
import django
import sys
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection, InspectorMapping
from django.db.models import Max, Count, Q

def format_value(value):
    """Format value for display"""
    if value is None:
        return "[X] None"
    elif value == "":
        return "[X] Empty String"
    elif isinstance(value, bool):
        return "[YES] True" if value else "[NO] False"
    elif isinstance(value, (datetime, )):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return str(value)

def main():
    print("=" * 80)
    print("LATEST INSPECTION DIAGNOSTIC REPORT")
    print("=" * 80)
    print()

    # Get total count
    total_count = FoodSafetyAgencyInspection.objects.count()
    print(f"Total Inspections in Database: {total_count}")
    print()

    # Get latest inspection
    latest = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection', '-created_at').first()

    if not latest:
        print("[ERROR] No inspections found in database!")
        return

    print(f"LATEST INSPECTION DETAILS")
    print("-" * 80)
    print(f"ID: {latest.id}")
    print(f"Unique Inspection ID: {latest.unique_inspection_id}")
    print(f"String Representation: {latest}")
    print()

    # Basic Fields
    print("BASIC INFORMATION")
    print("-" * 80)
    print(f"Commodity: {format_value(latest.commodity)}")
    print(f"Date of Inspection: {format_value(latest.date_of_inspection)}")
    print(f"Start Time: {format_value(latest.start_of_inspection)}")
    print(f"End Time: {format_value(latest.end_of_inspection)}")
    print(f"Inspector ID: {format_value(latest.inspector_id)}")
    print(f"Inspector Name: {format_value(latest.inspector_name)}")
    print(f"Client Name: {format_value(latest.client_name)}")
    print(f"Internal Account Code: {format_value(latest.internal_account_code)}")
    print()

    # Location
    print("LOCATION DATA")
    print("-" * 80)
    print(f"Latitude: {format_value(latest.latitude)}")
    print(f"Longitude: {format_value(latest.longitude)}")
    print(f"Location Type ID: {format_value(latest.inspection_location_type_id)}")
    print()

    # Product Information
    print("PRODUCT INFORMATION")
    print("-" * 80)
    print(f"Product Name: {format_value(latest.product_name)}")
    print(f"Product Class: {format_value(latest.product_class)}")
    print()

    # Sample Information
    print("SAMPLE & TESTING")
    print("-" * 80)
    print(f"Sample Taken: {format_value(latest.is_sample_taken)}")
    print(f"Bought Sample (R): {format_value(latest.bought_sample)}")
    print(f"Fat Test: {format_value(latest.fat)}")
    print(f"Protein Test: {format_value(latest.protein)}")
    print(f"Calcium Test: {format_value(latest.calcium)}")
    print(f"DNA Test: {format_value(latest.dna)}")
    print(f"Needs Retest: {format_value(latest.needs_retest)}")
    print(f"Lab: {format_value(latest.lab)}")
    print()

    # Travel & Hours
    print("TRAVEL & HOURS")
    print("-" * 80)
    print(f"Travel Distance (km): {format_value(latest.inspection_travel_distance_km)}")
    print(f"KM Traveled (manual): {format_value(latest.km_traveled)}")
    print(f"Hours (manual): {format_value(latest.hours)}")
    print()

    # Document Status
    print("DOCUMENT STATUS")
    print("-" * 80)
    print(f"RFI Uploaded: {format_value(latest.rfi_uploaded)}")
    print(f"RFI Upload Date: {format_value(latest.rfi_uploaded_date)}")
    print(f"Invoice Uploaded: {format_value(latest.invoice_uploaded)}")
    print(f"Invoice Upload Date: {format_value(latest.invoice_uploaded_date)}")
    print(f"COA Upload Date: {format_value(latest.coa_uploaded_date)}")
    print(f"Lab Form Upload Date: {format_value(latest.lab_form_uploaded_date)}")
    print(f"Retest Upload Date: {format_value(latest.retest_uploaded_date)}")
    print(f"Occurrence Upload Date: {format_value(latest.occurrence_uploaded_date)}")
    print(f"Composition Upload Date: {format_value(latest.composition_uploaded_date)}")
    print()

    # Email & Status
    print("EMAIL & STATUS")
    print("-" * 80)
    print(f"Additional Email: {format_value(latest.additional_email)}")
    print(f"Is Sent: {format_value(latest.is_sent)}")
    print(f"Sent Date: {format_value(latest.sent_date)}")
    print(f"Sent By: {format_value(latest.sent_by)}")
    print(f"Approved Status: {format_value(latest.approved_status)}")
    print(f"Invoice Number: {format_value(latest.invoice_number)}")
    print()

    # OneDrive Status
    print("ONEDRIVE STATUS")
    print("-" * 80)
    print(f"OneDrive Uploaded: {format_value(latest.onedrive_uploaded)}")
    print(f"OneDrive Upload Date: {format_value(latest.onedrive_upload_date)}")
    print(f"OneDrive Folder ID: {format_value(latest.onedrive_folder_id)}")
    print()

    # Additional
    print("ADDITIONAL")
    print("-" * 80)
    print(f"Direction Present: {format_value(latest.is_direction_present_for_this_inspection)}")
    print(f"Comment: {format_value(latest.comment)}")
    print(f"Remote ID: {format_value(latest.remote_id)}")
    print(f"Created At: {format_value(latest.created_at)}")
    print(f"Updated At: {format_value(latest.updated_at)}")
    print()

    # Summary Statistics
    print("=" * 80)
    print("SUMMARY STATISTICS (Last 30 Days)")
    print("=" * 80)

    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=thirty_days_ago
    )

    print(f"Total Recent Inspections: {recent_inspections.count()}")
    print()

    # By Commodity
    print("By Commodity:")
    commodity_counts = recent_inspections.values('commodity').annotate(
        count=Count('id')
    ).order_by('-count')
    for item in commodity_counts:
        print(f"  {item['commodity'] or 'Unknown'}: {item['count']}")
    print()

    # By Inspector
    print("By Inspector (Top 5):")
    inspector_counts = recent_inspections.values('inspector_name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    for item in inspector_counts:
        print(f"  {item['inspector_name'] or 'Unknown'}: {item['count']}")
    print()

    # Missing Data Analysis
    print("=" * 80)
    print("MISSING DATA ANALYSIS (Latest Inspection)")
    print("=" * 80)

    issues = []

    if not latest.client_name:
        issues.append("[CRITICAL] Client Name is missing")
    if not latest.product_name:
        issues.append("[WARNING] Product Name is missing")
    if not latest.product_class:
        issues.append("[WARNING] Product Class is missing")
    if not latest.inspector_name:
        issues.append("[CRITICAL] Inspector Name is missing")
    if latest.km_traveled is None:
        issues.append("[WARNING] KM Traveled is not set")
    if latest.hours is None:
        issues.append("[WARNING] Hours is not set")
    if not latest.additional_email:
        issues.append("[WARNING] Additional Email is not set")

    if issues:
        for issue in issues:
            print(issue)
    else:
        print("[OK] No critical data missing!")

    print()
    print("=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
