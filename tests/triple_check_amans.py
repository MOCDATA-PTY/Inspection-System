"""TRIPLE CHECK - Leave no stone unturned for Amans inspection data"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from django.db.models import Q

print("=" * 100)
print("TRIPLE CHECK - EXHAUSTIVE SEARCH FOR AMANS PMP DATA")
print("=" * 100)

print("\n[CHECK 1] Search by EXACT client name variations")
print("=" * 100)

client_variations = [
    "Amans meat & deli",
    "Amans meat and deli",
    "Amans meat",
    "Amans",
    "amans",
    "AMANS",
]

for variant in client_variations:
    results = FoodSafetyAgencyInspection.objects.filter(
        client_name__iexact=variant
    ).order_by('-date_of_inspection')[:5]

    if results:
        print(f"\nFound {len(results)} for '{variant}':")
        for r in results:
            print(f"  - {r.date_of_inspection}: [{r.commodity}] {r.product_name}")

print("\n[CHECK 2] Search for ANY inspection on 2025-12-03 (same date)")
print("=" * 100)

same_date = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection='2025-12-03'
).order_by('client_name', 'commodity')

print(f"\nFound {len(same_date)} total inspections on 2025-12-03:")
print("\nGrouped by client:")

from collections import defaultdict
by_client = defaultdict(list)
for insp in same_date:
    by_client[insp.client_name].append(insp)

for client_name, inspections in sorted(by_client.items()):
    pmp_count = sum(1 for i in inspections if 'PMP' in (i.commodity or '').upper())
    raw_count = sum(1 for i in inspections if 'RAW' in (i.commodity or '').upper())
    print(f"\n  {client_name}: {len(inspections)} products ({pmp_count} PMP, {raw_count} RAW)")

    # If this client has both PMP and RAW, show details
    if pmp_count > 0 and raw_count > 0:
        print(f"    >>> HAS BOTH PMP AND RAW:")
        for i in inspections:
            print(f"      - [{i.commodity}] {i.product_name}")

print("\n[CHECK 3] Search for PMP products by inspector CINGA NGONGO around Dec 3")
print("=" * 100)

cinga_pmp = FoodSafetyAgencyInspection.objects.filter(
    Q(inspector_name__icontains="CINGA") | Q(inspector_name__icontains="NGONGO"),
    commodity__icontains="PMP",
    date_of_inspection__year=2025,
    date_of_inspection__month=12
).order_by('date_of_inspection', 'client_name')

print(f"\nFound {len(cinga_pmp)} PMP inspections by CINGA in December 2025:")
for insp in cinga_pmp:
    print(f"  {insp.date_of_inspection}: {insp.client_name} - {insp.product_name}")
    print(f"    Sample: {insp.is_sample_taken}, Fat: {insp.fat}, Protein: {insp.protein}")

print("\n[CHECK 4] Search for ANY product with samples and tests (Fat or Protein)")
print("=" * 100)

with_tests = FoodSafetyAgencyInspection.objects.filter(
    Q(fat=True) | Q(protein=True),
    is_sample_taken=True,
    date_of_inspection__year=2025,
    date_of_inspection__month=12,
    date_of_inspection__day=3
).order_by('client_name', 'commodity')

print(f"\nFound {len(with_tests)} products with Fat/Protein tests on 2025-12-03:")
for insp in with_tests:
    print(f"  {insp.client_name}: [{insp.commodity}] {insp.product_name}")
    print(f"    Fat: {insp.fat}, Protein: {insp.protein}, Sample: {insp.is_sample_taken}")

print("\n[CHECK 5] Check remote_id 10221 and 10222 - what do they link to?")
print("=" * 100)

for remote_id in [10221, 10222]:
    matches = FoodSafetyAgencyInspection.objects.filter(remote_id=remote_id)
    print(f"\nRemote ID {remote_id}:")
    for m in matches:
        print(f"  Django ID: {m.id}")
        print(f"  Client: {m.client_name}")
        print(f"  Date: {m.date_of_inspection}")
        print(f"  Commodity: {m.commodity}")
        print(f"  Product: {m.product_name}")
        print(f"  Hours: {m.hours}, KM: {m.km_traveled}")
        print(f"  Sample: {m.is_sample_taken}")

print("\n[CHECK 6] Look for related inspections (same remote_id base)")
print("=" * 100)
print("If RAW inspection has remote_id 10221-10222, PMP might be 10220, 10223, etc.")

for remote_id in range(10218, 10226):
    matches = FoodSafetyAgencyInspection.objects.filter(remote_id=remote_id)
    if matches:
        for m in matches:
            print(f"\nRemote ID {remote_id}: [{m.commodity}] {m.product_name} - {m.client_name}")

print("\n[CHECK 7] Search database for EXACT values from Google Sheet")
print("=" * 100)
print("Looking for hours=0.5 and quantity combinations that match Google Sheet...")

# Google Sheet shows: 0.5 hours, 35 km for split values
split_matches = FoodSafetyAgencyInspection.objects.filter(
    hours=0.5,
    km_traveled=35.0
)

print(f"\nFound {len(split_matches)} inspections with hours=0.5, km=35:")
for insp in split_matches:
    print(f"  {insp.date_of_inspection}: {insp.client_name} - [{insp.commodity}] {insp.product_name}")

print("\n[CHECK 8] Check if there are multiple records for same date/inspector/client")
print("=" * 100)

# Get all Amans inspections
all_amans = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains="Amans"
).order_by('-date_of_inspection')

print(f"\nALL Amans inspections in database ({len(all_amans)} total):")
for insp in all_amans:
    print(f"\n  ID: {insp.id} | Remote: {insp.remote_id}")
    print(f"  Date: {insp.date_of_inspection}")
    print(f"  Inspector: {insp.inspector_name}")
    print(f"  Client: {insp.client_name}")
    print(f"  Commodity: {insp.commodity}")
    print(f"  Product: {insp.product_name}")
    print(f"  Hours: {insp.hours}, KM: {insp.km_traveled}")
    print(f"  Sample: {insp.is_sample_taken}")
    print(f"  Tests: Fat={insp.fat}, Protein={insp.protein}, Calcium={insp.calcium}, DNA={insp.dna}")

print("\n" + "=" * 100)
print("[CHECK 9] Check database table count and last sync time")
print("=" * 100)

total_inspections = FoodSafetyAgencyInspection.objects.count()
pmp_inspections = FoodSafetyAgencyInspection.objects.filter(commodity__icontains='PMP').count()
raw_inspections = FoodSafetyAgencyInspection.objects.filter(commodity__icontains='RAW').count()

print(f"\nDatabase statistics:")
print(f"  Total inspections: {total_inspections}")
print(f"  PMP inspections: {pmp_inspections}")
print(f"  RAW inspections: {raw_inspections}")

# Check last updated inspection
latest = FoodSafetyAgencyInspection.objects.order_by('-id').first()
if latest:
    print(f"\nMost recently added inspection:")
    print(f"  ID: {latest.id}")
    print(f"  Client: {latest.client_name}")
    print(f"  Date: {latest.date_of_inspection}")
    print(f"  Commodity: {latest.commodity}")

print("\n" + "=" * 100)
print("FINAL VERDICT")
print("=" * 100)

amans_dec3 = FoodSafetyAgencyInspection.objects.filter(
    client_name__icontains="Amans",
    date_of_inspection='2025-12-03'
)

pmp_amans_dec3 = amans_dec3.filter(commodity__icontains='PMP')
raw_amans_dec3 = amans_dec3.filter(commodity__icontains='RAW')

print(f"\nFor Amans meat & deli on 2025-12-03:")
print(f"  RAW products found: {raw_amans_dec3.count()}")
print(f"  PMP products found: {pmp_amans_dec3.count()}")
print(f"  Products with samples: {amans_dec3.filter(is_sample_taken=True).count()}")
print(f"  Products with Fat test: {amans_dec3.filter(fat=True).count()}")
print(f"  Products with Protein test: {amans_dec3.filter(protein=True).count()}")

if pmp_amans_dec3.count() == 0:
    print("\n*** CONFIRMED: NO PMP DATA IN DATABASE ***")
    print("The Google Sheet data was manually entered and is NOT in the database.")
else:
    print("\n*** WAIT - FOUND PMP DATA! ***")
    print("Details:")
    for p in pmp_amans_dec3:
        print(f"  - {p.product_name}: Sample={p.is_sample_taken}, Fat={p.fat}, Protein={p.protein}")

print("\n" + "=" * 100)
