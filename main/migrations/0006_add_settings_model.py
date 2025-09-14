# Generated manually to add Settings model only

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_add_food_safety_agency_inspection'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_sync', models.BooleanField(default=False, help_text='Automatically sync data every 24 hours')),
                ('backup_frequency', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='weekly', help_text='Backup frequency', max_length=20)),
                ('session_timeout', models.IntegerField(default=30, help_text='Session timeout in minutes')),
                ('google_sheets_enabled', models.BooleanField(default=True, help_text='Enable Google Sheets integration')),
                ('sql_server_enabled', models.BooleanField(default=True, help_text='Enable SQL Server integration')),
                ('sync_interval', models.IntegerField(default=24, help_text='Sync interval in hours')),
                ('email_notifications', models.BooleanField(default=False, help_text='Enable email notifications')),
                ('sync_notifications', models.BooleanField(default=True, help_text='Notify when data synchronization completes')),
                ('notification_email', models.EmailField(blank=True, help_text='Email address for notifications', max_length=254, null=True)),
                ('two_factor_auth', models.BooleanField(default=False, help_text='Enable two-factor authentication')),
                ('password_expiry', models.IntegerField(default=90, help_text='Password expiry in days')),
                ('max_login_attempts', models.IntegerField(default=5, help_text='Maximum login attempts')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Settings',
                'verbose_name_plural': 'Settings',
            },
        ),
    ]
