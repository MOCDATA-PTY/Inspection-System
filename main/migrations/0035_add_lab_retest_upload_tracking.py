# Generated migration to add Lab, Lab Form, and Retest upload tracking fields

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0034_change_sync_interval_to_float'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodsafetyagencyinspection',
            name='lab_uploaded_by',
            field=models.ForeignKey(blank=True, help_text='User who uploaded Lab document', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lab_uploads', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='foodsafetyagencyinspection',
            name='lab_uploaded_date',
            field=models.DateTimeField(blank=True, help_text='Date when Lab document was uploaded', null=True),
        ),
        migrations.AddField(
            model_name='foodsafetyagencyinspection',
            name='lab_form_uploaded_by',
            field=models.ForeignKey(blank=True, help_text='User who uploaded Lab Form document', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lab_form_uploads', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='foodsafetyagencyinspection',
            name='lab_form_uploaded_date',
            field=models.DateTimeField(blank=True, help_text='Date when Lab Form document was uploaded', null=True),
        ),
        migrations.AddField(
            model_name='foodsafetyagencyinspection',
            name='retest_uploaded_by',
            field=models.ForeignKey(blank=True, help_text='User who uploaded Retest document', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='retest_uploads', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='foodsafetyagencyinspection',
            name='retest_uploaded_date',
            field=models.DateTimeField(blank=True, help_text='Date when Retest document was uploaded', null=True),
        ),
    ]
