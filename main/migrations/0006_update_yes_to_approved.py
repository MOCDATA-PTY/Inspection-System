# Generated manually to update existing data

from django.db import migrations

def update_yes_to_approved(apps, schema_editor):
    """Update existing 'YES' values to 'APPROVED'"""
    FoodSafetyAgencyInspection = apps.get_model('main', 'FoodSafetyAgencyInspection')
    
    # Update all records with 'YES' to 'APPROVED'
    updated_count = FoodSafetyAgencyInspection.objects.filter(approved_status='YES').update(approved_status='APPROVED')
    print(f"Updated {updated_count} records from 'YES' to 'APPROVED'")

def reverse_approved_to_yes(apps, schema_editor):
    """Reverse migration: Update 'APPROVED' back to 'YES'"""
    FoodSafetyAgencyInspection = apps.get_model('main', 'FoodSafetyAgencyInspection')
    
    # Update all records with 'APPROVED' back to 'YES'
    updated_count = FoodSafetyAgencyInspection.objects.filter(approved_status='APPROVED').update(approved_status='YES')
    print(f"Updated {updated_count} records from 'APPROVED' to 'YES'")

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_update_approved_status_choices'),
    ]

    operations = [
        migrations.RunPython(update_yes_to_approved, reverse_approved_to_yes),
    ]
