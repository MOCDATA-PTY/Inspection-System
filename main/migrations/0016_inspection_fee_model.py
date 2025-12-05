# Generated migration for InspectionFee model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0015_add_composite_key_workaround'),
    ]

    operations = [
        migrations.CreateModel(
            name='InspectionFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fee_code', models.CharField(help_text="Unique code for the fee (e.g., 'inspection_hour_rate')", max_length=50, unique=True)),
                ('fee_name', models.CharField(help_text='Display name for the fee', max_length=200)),
                ('rate', models.DecimalField(decimal_places=2, help_text='Fee rate amount', max_digits=10)),
                ('description', models.TextField(blank=True, help_text='Description of the fee', null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Inspection Fee',
                'verbose_name_plural': 'Inspection Fees',
                'db_table': 'inspection_fees',
                'ordering': ['fee_code'],
            },
        ),
    ]
