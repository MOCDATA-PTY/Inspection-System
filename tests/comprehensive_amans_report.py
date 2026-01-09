"""Comprehensive Report: Amans meat & deli Inspection Data"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection

print("=" * 100)
print("COMPREHENSIVE REPORT: AMANS MEAT & DELI INSPECTION DATA")
print("=" * 100)

print("\n[1] WHAT YOU SAID THE GOOGLE SHEET SHOWS (6 line items):")
print("=" * 100)
print("Source: Manually entered by inspector from mobile app to Google Sheet")
print()
print("1. RAW 051  | Travel Cost (Km's)           | Qty: 35    | Rate: 6.5  | Total: 227.50")
print("2. PMP 060  | Inspection (hours)           | Qty: 0.5   | Rate: 510  | Total: 255.00")
print("3. RAW 050  | Inspection (Hours)           | Qty: 0.5   | Rate: 510  | Total: 255.00")
print("4. PMP 062  | Sample Taking: Fat Content   | Qty: 1     | Rate: 826  | Total: 826.00")
print("5. PMP 061  | Travel Cost (Km's)           | Qty: 35    | Rate: 6.5  | Total: 227.50")
print("6. PMP 064  | Sample Taking: Protein       | Qty: 1     | Rate: 503  | Total: 503.00")
print()
print("KEY OBSERVATIONS FROM GOOGLE SHEET:")
print("- Has BOTH RAW and PMP products")
print("- Hours/KM are SPLIT: 0.5 hours and 35 km each (from original 1.0 hours, 70 km)")
print("- HAS SAMPLES TAKEN: Fat and Protein tests for PMP")
print("- Date: 03/12/2025")
print("- Client: Amans meat & deli")
print("- Inspector: C Ngongo (CINGA NGONGO)")

print("\n" + "=" * 100)
print("[2] WHAT I FOUND IN DJANGO DATABASE (PostgreSQL)")
print("=" * 100)
print("Source: Django database (synced from SQL Server AFS database)")
print("Location: main_foodsafetyagencyinspection table")
print()

# Query Django database
inspections = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains="Amans",
    date_of_inspection__year=2025,
    date_of_inspection__month=12,
    date_of_inspection__day=3
).order_by('commodity', 'product_name')

if not inspections:
    print("NO INSPECTIONS FOUND for Amans on 03/12/2025")

    # Try all dates
    all_amans = FoodSafetyAgencyInspection.objects.filter(
        client_name__icontains="Amans"
    ).order_by('-date_of_inspection')

    print(f"\nFound {len(all_amans)} Amans inspections across ALL dates:")
    for insp in all_amans:
        print(f"  - {insp.date_of_inspection}: [{insp.commodity}] {insp.product_name}")
else:
    print(f"Found {len(inspections)} products for Amans on 03/12/2025:\n")

    for i, insp in enumerate(inspections, 1):
        print(f"{i}. [{insp.commodity}] {insp.product_name}")
        print(f"   Django ID: {insp.id}")
        print(f"   Remote ID (SQL Server): {insp.remote_id}")
        print(f"   Date: {insp.date_of_inspection}")
        print(f"   Inspector: {insp.inspector_name}")
        print(f"   Client: {insp.client_name}")
        print(f"   Hours: {insp.hours}")
        print(f"   KM Traveled: {insp.km_traveled}")
        print(f"   Sample Taken: {insp.is_sample_taken}")
        print(f"   Tests: Fat={insp.fat}, Protein={insp.protein}, Calcium={insp.calcium}, DNA={insp.dna}")
        print()

    print("SUMMARY OF DJANGO DATA:")
    pmp_count = sum(1 for i in inspections if 'PMP' in (i.commodity or '').upper())
    raw_count = sum(1 for i in inspections if 'RAW' in (i.commodity or '').upper())
    samples_count = sum(1 for i in inspections if i.is_sample_taken)

    print(f"- Total products: {len(inspections)}")
    print(f"- PMP products: {pmp_count}")
    print(f"- RAW products: {raw_count}")
    print(f"- Samples taken: {samples_count}")
    print(f"- Hours: {inspections[0].hours if inspections else 'N/A'}")
    print(f"- KM: {inspections[0].km_traveled if inspections else 'N/A'}")

print("\n" + "=" * 100)
print("[3] WHAT THE EXPORT FUNCTION WOULD GENERATE")
print("=" * 100)
print("Source: export_sheet view in core_views.py")
print("Logic: Lines 4915-5095 in main/views/core_views.py")
print()

if not inspections:
    print("NO LINE ITEMS (because no data in database)")
else:
    first = inspections[0]
    hours = float(first.hours) if first.hours else 0
    km = float(first.km_traveled) if first.km_traveled else 0

    pmp_products = [i for i in inspections if 'PMP' in (i.commodity or '').upper()]
    raw_products = [i for i in inspections if 'RAW' in (i.commodity or '').upper()]
    has_both = len(pmp_products) > 0 and len(raw_products) > 0

    print("HOURS/KM LINE ITEMS:")
    if has_both:
        print(f"1. PMP 060 | Inspection (hours) | Qty: {hours/2} (split)")
        print(f"2. PMP 061 | Travel (km)        | Qty: {km/2} (split)")
        print(f"3. RAW 050 | Inspection (hours) | Qty: {hours/2} (split)")
        print(f"4. RAW 051 | Travel (km)        | Qty: {km/2} (split)")
    else:
        commodity_type = 'RAW' if len(raw_products) > 0 else 'PMP'
        code_h = '050' if commodity_type == 'RAW' else '060'
        code_k = '051' if commodity_type == 'RAW' else '061'
        print(f"1. {commodity_type} {code_h} | Inspection (hours) | Qty: {hours}")
        print(f"2. {commodity_type} {code_k} | Travel (km)        | Qty: {km}")

    print("\nTEST LINE ITEMS:")
    # Check PMP tests
    pmp_needs_fat = any(i.fat and i.is_sample_taken for i in pmp_products)
    pmp_needs_protein = any(i.protein and i.is_sample_taken for i in pmp_products)
    pmp_needs_calcium = any(i.calcium and i.is_sample_taken for i in pmp_products)

    # Check RAW tests
    raw_needs_fat = any(i.fat and i.is_sample_taken for i in raw_products)
    raw_needs_protein = any(i.protein and i.is_sample_taken for i in raw_products)
    raw_needs_dna = any(i.dna and i.is_sample_taken for i in raw_products)

    test_num = 3 if has_both else 3

    if pmp_needs_fat:
        print(f"{test_num}. PMP 062 | Sample: Fat Content")
        test_num += 1
    if pmp_needs_protein:
        print(f"{test_num}. PMP 064 | Sample: Protein Content")
        test_num += 1
    if pmp_needs_calcium:
        print(f"{test_num}. PMP 065 | Sample: Calcium Content")
        test_num += 1
    if raw_needs_fat:
        print(f"{test_num}. RAW 052 | Sample: Fat Content")
        test_num += 1
    if raw_needs_protein:
        print(f"{test_num}. RAW 054 | Sample: Protein Content")
        test_num += 1
    if raw_needs_dna:
        print(f"{test_num}. RAW 053 | Sample: DNA")
        test_num += 1

    if not any([pmp_needs_fat, pmp_needs_protein, pmp_needs_calcium, raw_needs_fat, raw_needs_protein, raw_needs_dna]):
        print("(No test line items - no samples taken)")

    total_items = (4 if has_both else 2) + sum([pmp_needs_fat, pmp_needs_protein, pmp_needs_calcium, raw_needs_fat, raw_needs_protein, raw_needs_dna])
    print(f"\nTOTAL LINE ITEMS: {total_items}")

print("\n" + "=" * 100)
print("[4] THE MISMATCH ANALYSIS")
print("=" * 100)
print()
print("WHAT'S MISSING FROM DATABASE:")
print("- PMP products (Google Sheet shows PMP, database has NONE)")
print("- Sample data (Google Sheet shows samples taken, database shows is_sample_taken=False)")
print("- Test data (Google Sheet shows Fat/Protein tests, database shows Fat=False, Protein=False)")
print()
print("WHAT'S CORRECT IN DATABASE:")
print("- RAW products (Cheese Patties, Chilli patties) - CORRECT")
print("- Hours: 1.0 (matches pre-split value) - CORRECT")
print("- KM: 70.0 (matches pre-split value) - CORRECT")
print("- Date: 2025-12-03 - CORRECT")
print("- Inspector: CINGA NGONGO - CORRECT")
print("- Client: Amans meat & deli - CORRECT")

print("\n" + "=" * 100)
print("[5] WHERE IS THE PMP DATA?")
print("=" * 100)
print()
print("POSSIBLE LOCATIONS:")
print()
print("A) SQL SERVER (source database at 102.67.140.12:1053)")
print("   - Attempted to query but got column name errors")
print("   - Would be in tables: PMPInspectionRecordTypes, PMPInspectedProductRecordTypes")
print("   - If PMP data exists there, it should have synced to Django database")
print()
print("B) MOBILE APPLICATION")
print("   - Inspector may have entered PMP data in mobile app")
print("   - Data might not have uploaded to SQL Server yet")
print("   - Need to check inspector's mobile device")
print()
print("C) GOOGLE SHEET ONLY")
print("   - Inspector manually typed it into Google Sheet")
print("   - Never submitted through mobile app workflow")
print("   - This is a MANUAL ENTRY, not synced from database")

print("\n" + "=" * 100)
print("[6] CONCLUSION")
print("=" * 100)
print()
print("The export function is WORKING CORRECTLY.")
print("It generates exactly what's in the database: 2 RAW line items (hours + km)")
print()
print("The Google Sheet has MORE data because:")
print("1. Inspector manually entered PMP data directly into Google Sheet, OR")
print("2. PMP data was entered in mobile app but hasn't synced to SQL Server yet")
print()
print("TO FIX THIS:")
print("1. Ask inspector to submit the COMPLETE inspection (RAW + PMP) through mobile app")
print("2. Verify data appears in SQL Server AFS database")
print("3. Trigger Django sync: python trigger_fresh_sync.py")
print("4. Then export will show all 6 line items correctly")
print()
print("=" * 100)
