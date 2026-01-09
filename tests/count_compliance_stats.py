"""Count compliant vs non-compliant inspections"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import FoodSafetyAgencyInspection
from datetime import datetime, timedelta

print("=" * 100)
print("COMPLIANCE STATISTICS")
print("=" * 100)

# Get all inspections
total = FoodSafetyAgencyInspection.objects.count()

# Count by compliance status
compliant = FoodSafetyAgencyInspection.objects.filter(
    is_direction_present_for_this_inspection=False
).count()

non_compliant = FoodSafetyAgencyInspection.objects.filter(
    is_direction_present_for_this_inspection=True
).count()

print(f"\n[ALL TIME]")
print(f"  Total Inspections:        {total:,}")
print(f"  Compliant (No Direction): {compliant:,} ({compliant/total*100:.1f}%)")
print(f"  Non-Compliant (Direction):{non_compliant:,} ({non_compliant/total*100:.1f}%)")

# Last 60 days
sixty_days_ago = datetime.now().date() - timedelta(days=60)
recent_total = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=sixty_days_ago
).count()

recent_compliant = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=sixty_days_ago,
    is_direction_present_for_this_inspection=False
).count()

recent_non_compliant = FoodSafetyAgencyInspection.objects.filter(
    date_of_inspection__gte=sixty_days_ago,
    is_direction_present_for_this_inspection=True
).count()

print(f"\n[LAST 60 DAYS]")
print(f"  Total Inspections:        {recent_total:,}")
print(f"  Compliant (No Direction): {recent_compliant:,} ({recent_compliant/recent_total*100:.1f}%)")
print(f"  Non-Compliant (Direction):{recent_non_compliant:,} ({recent_non_compliant/recent_total*100:.1f}%)")

# Breakdown by commodity
print(f"\n[BREAKDOWN BY COMMODITY]")
print(f"{'Commodity':<15} {'Total':<10} {'Compliant':<12} {'Non-Compliant':<15} {'Pass Rate':<10}")
print("-" * 100)

for commodity in ['PMP', 'RAW', 'EGGS', 'POULTRY']:
    comm_total = FoodSafetyAgencyInspection.objects.filter(
        commodity=commodity,
        date_of_inspection__gte=sixty_days_ago
    ).count()

    comm_compliant = FoodSafetyAgencyInspection.objects.filter(
        commodity=commodity,
        date_of_inspection__gte=sixty_days_ago,
        is_direction_present_for_this_inspection=False
    ).count()

    comm_non_compliant = FoodSafetyAgencyInspection.objects.filter(
        commodity=commodity,
        date_of_inspection__gte=sixty_days_ago,
        is_direction_present_for_this_inspection=True
    ).count()

    pass_rate = (comm_compliant/comm_total*100) if comm_total > 0 else 0

    print(f"{commodity:<15} {comm_total:<10} {comm_compliant:<12} {comm_non_compliant:<15} {pass_rate:.1f}%")

print("\n" + "=" * 100)
print("EXPLANATION:")
print("  • Compliant = No direction issued (inspection passed)")
print("  • Non-Compliant = Direction issued (business has issues to fix)")
print("=" * 100)
