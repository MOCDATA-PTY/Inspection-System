# Data migration to populate default inspection fees (Notice 2996 of 2025)

from django.db import migrations


def populate_default_fees(apps, schema_editor):
    InspectionFee = apps.get_model('main', 'InspectionFee')

    # Default fees from Notice 2996 of 2025 (14 February 2025)
    default_fees = [
        {
            'fee_code': 'inspection_hour_rate',
            'fee_name': 'Inspection Hour Rate (Normal Time 08:00-16:00)',
            'rate': 510.00,
            'description': 'Hourly rate for inspections during normal working hours'
        },
        {
            'fee_code': 'inspection_overtime_rate',
            'fee_name': 'Inspection Overtime Rate (Mon-Sat)',
            'rate': 567.00,
            'description': 'Hourly rate for inspections during overtime (Monday to Saturday)'
        },
        {
            'fee_code': 'inspection_sunday_rate',
            'fee_name': 'Inspection Sunday & Public Holiday Rate',
            'rate': 680.00,
            'description': 'Hourly rate for inspections on Sundays and public holidays'
        },
        {
            'fee_code': 'travel_rate_per_km',
            'fee_name': 'Travel Rate (Per Kilometre)',
            'rate': 6.50,
            'description': 'Rate charged per kilometre traveled for inspections'
        },
        {
            'fee_code': 'fat_test_rate',
            'fee_name': 'Fat Content Test',
            'rate': 826.00,
            'description': 'Sample taking and testing for fat content'
        },
        {
            'fee_code': 'protein_test_rate',
            'fee_name': 'Protein Content Test',
            'rate': 503.00,
            'description': 'Sample taking and testing for protein (meat) content'
        },
        {
            'fee_code': 'calcium_test_rate',
            'fee_name': 'Calcium Determination Test (MRM Only)',
            'rate': 379.00,
            'description': 'Sample taking and testing for calcium determination (applies to both PMP and RAW products)'
        },
        {
            'fee_code': 'dna_test_rate',
            'fee_name': 'DNA Test (Meat Species Identification)',
            'rate': 2605.00,
            'description': 'Sample taking and testing for meat species identification (DNA)'
        },
        {
            'fee_code': 'soya_test_rate',
            'fee_name': 'Soya Content Test',
            'rate': 1665.00,
            'description': 'Sample taking and testing for soya content'
        },
        {
            'fee_code': 'starch_test_rate',
            'fee_name': 'Starch Content Test',
            'rate': 1472.00,
            'description': 'Sample taking and testing for starch content'
        },
        {
            'fee_code': 'physical_test_rate',
            'fee_name': 'Physical Test (Coated Products)',
            'rate': 200.00,
            'description': 'Physical testing for coated products'
        },
    ]

    for fee_data in default_fees:
        InspectionFee.objects.get_or_create(
            fee_code=fee_data['fee_code'],
            defaults={
                'fee_name': fee_data['fee_name'],
                'rate': fee_data['rate'],
                'description': fee_data['description']
            }
        )


def remove_fees(apps, schema_editor):
    InspectionFee = apps.get_model('main', 'InspectionFee')
    InspectionFee.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_inspection_fee_model'),
    ]

    operations = [
        migrations.RunPython(populate_default_fees, remove_fees),
    ]
