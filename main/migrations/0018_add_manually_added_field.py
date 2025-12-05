# Generated migration for manually_added field in ClientAllocation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_populate_default_fees'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientallocation',
            name='manually_added',
            field=models.BooleanField(default=False, help_text='True if added manually via UI, False if synced from sheets', verbose_name='Manually Added'),
        ),
    ]
