# Generated manually to recreate Ticket model after 0022_delete_ticket

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_populate_initial_fee_history'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Ticket title/summary', max_length=200)),
                ('description', models.TextField(help_text='Detailed description of the issue')),
                ('issue_type', models.CharField(blank=True, help_text='Type of issue (bug, feature, question, etc.)', max_length=50, null=True)),
                ('affected_area', models.CharField(blank=True, help_text='Affected module/area of the system', max_length=100, null=True)),
                ('steps_to_reproduce', models.TextField(blank=True, help_text='Steps to reproduce the issue', null=True)),
                ('expected_behavior', models.TextField(blank=True, help_text='What should happen', null=True)),
                ('actual_behavior', models.TextField(blank=True, help_text='What actually happened', null=True)),
                ('browser_info', models.CharField(blank=True, help_text='Browser/device information', max_length=200, null=True)),
                ('additional_notes', models.TextField(blank=True, help_text='Any other relevant details', null=True)),
                ('impact_users', models.CharField(blank=True, help_text='Number of affected users', max_length=50, null=True)),
                ('is_blocking', models.CharField(blank=True, help_text='Is this blocking work?', max_length=20, null=True)),
                ('status', models.CharField(choices=[('open', 'Open'), ('in-progress', 'In Progress'), ('resolved', 'Resolved'), ('closed', 'Closed')], default='open', help_text='Current status of the ticket', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', help_text='Priority level', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('due_date', models.DateField(blank=True, help_text='Target completion date', null=True)),
                ('assigned_to', models.ForeignKey(blank=True, help_text='User assigned to handle this ticket', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tickets', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(help_text='User who created the ticket', on_delete=django.db.models.deletion.CASCADE, related_name='created_tickets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ticket',
                'verbose_name_plural': 'Tickets',
                'db_table': 'fsa_tickets',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['status'], name='idx_ticket_status'),
                    models.Index(fields=['priority'], name='idx_ticket_priority'),
                    models.Index(fields=['created_by'], name='idx_ticket_creator'),
                    models.Index(fields=['assigned_to'], name='idx_ticket_assignee'),
                    models.Index(fields=['-created_at'], name='idx_ticket_created'),
                ],
            },
        ),
    ]
