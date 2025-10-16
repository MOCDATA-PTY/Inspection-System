from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings
from datetime import date
import re
from django.utils import timezone

# Add role field to existing User model
User.add_to_class('role', models.CharField(
    max_length=20,
    choices=[
        ('inspector', 'Inspector'),
        ('admin', 'HR/Admin Staff'),
        ('super_admin', 'Super Admin'),
        ('financial', 'Financial'),
        ('scientist', 'Scientist'),
        ('developer', 'Developer'),
    ],
    default='inspector',
    help_text="User role in the system"
))

User.add_to_class('phone_number', models.CharField(max_length=20, blank=True, null=True))
User.add_to_class('department', models.CharField(max_length=100, blank=True, null=True))
User.add_to_class('employee_id', models.CharField(max_length=50, blank=True, null=True, unique=True))

# Add properties to User model
@property
def is_inspector(self):
    return getattr(self, 'role', 'inspector') == 'inspector'

@property
def is_admin(self):
    return getattr(self, 'role', 'inspector') == 'admin'

@property
def is_super_admin(self):
    return getattr(self, 'role', 'inspector') == 'super_admin'

@property
def is_financial(self):
    return getattr(self, 'role', 'inspector') == 'financial'

@property
def is_scientist(self):
    return getattr(self, 'role', 'inspector') == 'scientist'

def has_role_permission(self, required_role):
    """Check if user has the required role or higher"""
    role_hierarchy = {
        'inspector': 1,
        'admin': 2,
        'financial': 3,
        'scientist': 3,
        'super_admin': 4,
        'developer': 5,
    }
    
    user_level = role_hierarchy.get(getattr(self, 'role', 'inspector'), 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level

User.add_to_class('is_inspector', is_inspector)
User.add_to_class('is_admin', is_admin)
User.add_to_class('is_super_admin', is_super_admin)
User.add_to_class('is_financial', is_financial)
User.add_to_class('is_scientist', is_scientist)
User.add_to_class('has_role_permission', has_role_permission)

class ClientManager(models.Manager):
    def get_next_client_id(self):
        """Generate next sequential client ID (CL00001, CL00002, etc.)"""
        last_client = self.order_by('-id').first()
        if last_client:
            last_id = int(last_client.client_id[2:])
            return f"CL{(last_id + 1):05d}"
        else:
            return "CL00001"

class InspectorMapping(models.Model):
    """Model to store inspector ID mappings for the server"""
    inspector_id = models.IntegerField(unique=True, help_text="Server inspector ID (e.g., 1234567)")
    inspector_name = models.CharField(max_length=100, help_text="Human-readable inspector name (e.g., Ethan)")
    is_active = models.BooleanField(default=True, help_text="Whether this inspector is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inspector_mappings'
        ordering = ['inspector_name']
        verbose_name = "Inspector Mapping"
        verbose_name_plural = "Inspector Mappings"
        indexes = [
            models.Index(fields=['inspector_id']),
            models.Index(fields=['inspector_name']),
        ]
    
    def __str__(self):
        return f"{self.inspector_name} (ID: {self.inspector_id})"


class SystemSettings(models.Model):
    """System settings for automatic synchronization and preferences."""
    
    # Auto Sync Settings
    auto_sync_enabled = models.BooleanField(default=False, verbose_name="Enable Auto Sync")
    backup_frequency_days = models.IntegerField(default=7, verbose_name="Backup Frequency (days)")
    session_timeout_minutes = models.IntegerField(default=30, verbose_name="Session Timeout (minutes)")
    
    # Data Sync Settings
    google_sheets_enabled = models.BooleanField(default=True, verbose_name="Google Sheets Integration")
    sql_server_enabled = models.BooleanField(default=True, verbose_name="SQL Server Integration")
    sync_interval_hours = models.FloatField(default=24.0, verbose_name="Sync Interval (hours)")
    
    # Compliance Documents Settings
    compliance_sync_enabled = models.BooleanField(default=True, verbose_name="Enable Automatic Compliance Sync")
    compliance_sync_interval_hours = models.IntegerField(default=24, verbose_name="Compliance Sync Interval (hours)")
    compliance_processing_mode = models.CharField(
        max_length=20,
        default='incremental',
        choices=[
            ('all_at_once', 'Process ALL at Once'),
            ('incremental', 'Incremental Processing'),
            ('manual', 'Manual Processing Only')
        ],
        verbose_name="Processing Mode"
    )
    
    # Performance Optimization Settings
    compliance_daily_sync_enabled = models.BooleanField(default=True, verbose_name="Enable Daily Compliance Sync")
    compliance_last_processed_date = models.DateTimeField(null=True, blank=True, verbose_name="Last Compliance Process Date")
    compliance_skip_processed = models.BooleanField(default=True, verbose_name="Skip Already Processed Documents")
    
    # Priority Refresh Settings
    priority_1_interval = models.IntegerField(default=1, verbose_name="First 2 Months Refresh Interval")
    priority_1_unit = models.CharField(max_length=10, default='hours', verbose_name="First 2 Months Unit")
    priority_2_interval = models.IntegerField(default=2, verbose_name="Last 2 Months Refresh Interval")
    priority_2_unit = models.CharField(max_length=10, default='hours', verbose_name="Last 2 Months Unit")
    
    # OneDrive Settings
    onedrive_enabled = models.BooleanField(default=True, verbose_name="OneDrive Integration")
    onedrive_local_caching = models.BooleanField(default=True, verbose_name="Enable Local File Caching")
    onedrive_cache_days = models.IntegerField(default=60, verbose_name="Cache Duration (Days)")
    onedrive_auto_sync = models.BooleanField(default=True, verbose_name="Enable Auto Sync")
    onedrive_sync_interval_hours = models.IntegerField(default=2, verbose_name="Sync Interval (Hours)")
    onedrive_upload_delay_days = models.IntegerField(default=3, verbose_name="Upload Delay (Days)")
    onedrive_upload_delay_unit = models.CharField(
        max_length=10,
        default='days',
        choices=[
            ('hours', 'Hours'),
            ('days', 'Days'),
            ('weeks', 'Weeks'),
            ('months', 'Months'),
            ('years', 'Years')
        ],
        verbose_name="Upload Delay Unit"
    )
    
    # Theme Settings
    theme_mode = models.CharField(
        max_length=10,
        default='light',
        choices=[
            ('light', 'Light Mode'),
            ('dark', 'Dark Mode'),
            ('auto', 'Auto')
        ],
        verbose_name="Theme Mode"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return f"System Settings (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"
    
    def save(self, *args, **kwargs):
        # Ensure only one system settings record exists
        if not self.pk:
            SystemSettings.objects.all().delete()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create system settings."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class Client(models.Model):
    """General clients table"""
    client_id = models.CharField(max_length=200, unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True, verbose_name="Client Name")
    internal_account_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Internal Account Code", help_text="From Google Sheets Column H")
    email = models.EmailField(blank=True, null=True, verbose_name="Client Email", help_text="From Google Sheets Column K")
    manual_email = models.EmailField(blank=True, null=True, verbose_name="Manual Email Override", help_text="Manually added email that persists across syncs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ClientManager()
    
    class Meta:
        db_table = 'food_safety_agency_clients'
        ordering = ['name']
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        indexes = [
            models.Index(fields=['client_id']),
            models.Index(fields=['name']),
            models.Index(fields=['internal_account_code']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.client_id})"
    
    def save(self, *args, **kwargs):
        if not self.client_id:
            self.client_id = Client.objects.get_next_client_id()
        super().save(*args, **kwargs)


class ClientEmail(models.Model):
    """Additional emails linked to a client (persists across syncs)."""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='additional_emails')
    email = models.EmailField()
    label = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'food_safety_agency_client_emails'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['client']),
        ]

    def __str__(self):
        return f"{self.email} -> {self.client.client_id}"

class Inspection(models.Model):
    """Inspection data model based on the provided structure"""
    
    # Inspector information
    inspector = models.CharField(max_length=100, help_text="Inspector name (e.g., Cinga Ngongo)")
    inspection_number = models.PositiveIntegerField(help_text="Sequential inspection number")
    
    # Basic inspection details
    inspection_date = models.DateField(help_text="Date of inspection")
    facility_client_name = models.CharField(max_length=200, help_text="Facility or client name")
    town = models.CharField(max_length=100, blank=True, null=True, help_text="Town/location")
    
    # Product information
    commodity = models.CharField(max_length=50, blank=True, null=True, help_text="Commodity type (e.g., RAW)")
    product_name = models.CharField(max_length=100, blank=True, null=True, help_text="Product name (e.g., Mince, Mildwors)")
    product_class = models.CharField(max_length=100, blank=True, null=True, help_text="Product class (e.g., Raw species sausage / wors)")
    
    # Inspection activities
    inspected = models.BooleanField(default=False, help_text="Was inspection conducted?")
    sampled = models.BooleanField(default=False, help_text="Was sampling conducted?")
    
    # Operational details
    normal_hours = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, help_text="Normal hours worked")
    kilometres_traveled = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True, help_text="Kilometres traveled")
    
    # Testing parameters
    fat = models.BooleanField(default=False, help_text="Fat testing required")
    protein = models.BooleanField(default=False, help_text="Protein testing required")
    calcium = models.BooleanField(default=False, help_text="Calcium testing required")
    dna = models.BooleanField(default=False, help_text="DNA testing required")
    
    # Sample and lab information
    bought_sample_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Amount paid for sample")
    lab_used = models.CharField(max_length=100, blank=True, null=True, help_text="Laboratory used (e.g., Food Safety Laboratory)")
    
    # Documentation and follow-up
    follow_up = models.BooleanField(default=False, help_text="Follow-up required")
    occurrence_report = models.BooleanField(default=False, help_text="Occurrence report required")
    dispensation_application = models.BooleanField(default=False, help_text="Dispensation application required")
    
    # Comments and notes
    comments = models.TextField(blank=True, null=True, help_text="Additional comments or notes")
    
    # File uploads and references
    uploaded = models.BooleanField(default=False, help_text="Files uploaded")
    rfi_reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="RFI reference number")
    invoice_reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="Invoice reference number")
    lab_result_reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="Lab result reference number")
    
    # Re-testing information
    re_test = models.BooleanField(default=False, help_text="Re-test required")
    re_test_reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="Re-test reference number")
    
    # External testing and compliance
    verification_external_testing = models.BooleanField(default=False, help_text="External testing verification required")
    compliance_document = models.BooleanField(default=False, help_text="Compliance document required")
    direction_expiry_date = models.DateField(blank=True, null=True, help_text="Direction expiry date")
    
    # Contact information
    email = models.EmailField(blank=True, null=True, help_text="Primary email contact")
    additional_email_1 = models.EmailField(blank=True, null=True, help_text="Additional email contact 1")
    additional_email_2 = models.EmailField(blank=True, null=True, help_text="Additional email contact 2")
    additional_email_3 = models.EmailField(blank=True, null=True, help_text="Additional email contact 3")
    additional_email_4 = models.EmailField(blank=True, null=True, help_text="Additional email contact 4")
    
    # Communication tracking
    was_mail_sent = models.BooleanField(default=False, help_text="Was email sent?")
    compiled_supporting_documents = models.BooleanField(default=False, help_text="Supporting documents compiled")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inspections'
        ordering = ['-inspection_date', '-inspection_number']
        verbose_name = "Inspection"
        verbose_name_plural = "Inspections"
    
    def __str__(self):
        return f"{self.inspector} - {self.facility_client_name} - {self.inspection_date}"

class FoodSafetyAgencyInspection(models.Model):
    """Food Safety Agency Inspection data copied from remote SQL Server"""
    
    # Basic inspection details
    commodity = models.CharField(max_length=50, blank=True, null=True, help_text="Commodity type (e.g., POULTRY, RAW, PMP, EGGS)")
    date_of_inspection = models.DateField(blank=True, null=True, help_text="Date of inspection")
    start_of_inspection = models.TimeField(blank=True, null=True, help_text="Start time of inspection")
    end_of_inspection = models.TimeField(blank=True, null=True, help_text="End time of inspection")
    
    # Location and inspection details
    inspection_location_type_id = models.IntegerField(blank=True, null=True, help_text="Inspection location type ID")
    is_direction_present_for_this_inspection = models.BooleanField(default=False, help_text="Direction present for this inspection")
    inspector_id = models.IntegerField(blank=True, null=True, help_text="Inspector ID from remote system")
    inspector_name = models.CharField(max_length=100, blank=True, null=True, help_text="Human-readable inspector name")
    
    # GPS coordinates
    latitude = models.CharField(max_length=20, blank=True, null=True, help_text="GPS Latitude")
    longitude = models.CharField(max_length=20, blank=True, null=True, help_text="GPS Longitude")
    
    # Product details (manual entry)
    product_name = models.CharField(max_length=150, blank=True, null=True, help_text="Product name (e.g., Mince, Burger, Boerewors)")
    product_class = models.CharField(max_length=150, blank=True, null=True, help_text="Product class/category")

    # Sample and travel information
    is_sample_taken = models.BooleanField(blank=True, null=True, help_text="Was sample taken during inspection")
    bought_sample = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Value of bought sample in Rand (ZAR)")
    inspection_travel_distance_km = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Travel distance in kilometers")
    
    # New fields for manual entry
    km_traveled = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Manual entry of kilometers traveled")
    hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Manual entry of hours worked")
    additional_email = models.EmailField(max_length=254, blank=True, null=True, help_text="Additional email for this specific inspection group")
    approved_status = models.CharField(max_length=10, blank=True, null=True, help_text="Approval status for this inspection group",
                                     choices=[
                                         ('PENDING', 'Pending'),
                                         ('APPROVED', 'Approved')
                                     ], default='PENDING')
    lab = models.CharField(max_length=20, blank=True, null=True, help_text="Laboratory used for testing",
                          choices=[
                              ('lab_a', 'Lab A'),
                              ('lab_b', 'Lab B'),
                              ('lab_c', 'Lab C'),
                              ('lab_d', 'Lab D'),
                              ('lab_e', 'Lab E'),
                              ('lab_f', 'Lab F')
                          ])
    
    # Reference information
    remote_id = models.IntegerField(blank=True, null=True, help_text="Original ID from remote system")
    client_name = models.CharField(max_length=200, blank=True, null=True, help_text="Client name from remote system")
    
    # Testing parameters
    fat = models.BooleanField(default=False, help_text="Fat testing required")
    protein = models.BooleanField(default=False, help_text="Protein testing required")
    calcium = models.BooleanField(default=False, help_text="Calcium testing required")
    dna = models.BooleanField(default=False, help_text="DNA testing required")
    needs_retest = models.CharField(max_length=3, blank=True, null=True, verbose_name='Needs Retest',
                                  choices=[('YES', 'Yes'), ('NO', 'No')], help_text="Whether this inspection needs retesting")
    
    # Document status tracking
    is_sent = models.BooleanField(default=False, help_text="Whether documents have been sent to client")
    sent_date = models.DateTimeField(blank=True, null=True, help_text="Date when documents were sent")
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='sent_inspections', help_text="User who marked documents as sent")
    
    # OneDrive upload tracking
    onedrive_uploaded = models.BooleanField(default=False, help_text="Whether files have been uploaded to OneDrive")
    onedrive_upload_date = models.DateTimeField(blank=True, null=True, help_text="Date when files were uploaded to OneDrive")
    onedrive_folder_id = models.CharField(max_length=255, blank=True, null=True, help_text="OneDrive folder ID where files are stored")
    
    # Document upload tracking
    rfi_uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='rfi_uploads', help_text="User who uploaded RFI document")
    rfi_uploaded_date = models.DateTimeField(blank=True, null=True, help_text="Date when RFI was uploaded")
    invoice_uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='invoice_uploads', help_text="User who uploaded Invoice document")
    invoice_uploaded_date = models.DateTimeField(blank=True, null=True, help_text="Date when Invoice was uploaded")
    lab_uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='lab_uploads', help_text="User who uploaded Lab document")
    lab_uploaded_date = models.DateTimeField(blank=True, null=True, help_text="Date when Lab document was uploaded")
    lab_form_uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='lab_form_uploads', help_text="User who uploaded Lab Form document")
    lab_form_uploaded_date = models.DateTimeField(blank=True, null=True, help_text="Date when Lab Form document was uploaded")
    retest_uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='retest_uploads', help_text="User who uploaded Retest document")
    retest_uploaded_date = models.DateTimeField(blank=True, null=True, help_text="Date when Retest document was uploaded")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'food_safety_agency_inspections'
        ordering = ['-date_of_inspection', '-created_at']
        verbose_name = "Food Safety Agency Inspection"
        verbose_name_plural = "Food Safety Agency Inspections"
        indexes = [
            models.Index(fields=['commodity']),
            models.Index(fields=['date_of_inspection']),
            models.Index(fields=['inspector_name']),
            models.Index(fields=['client_name']),
            models.Index(fields=['inspector_id']),
        ]
    
    def __str__(self):
        return f"{self.inspector_name} - {self.client_name} - {self.date_of_inspection} ({self.commodity})"

class Shipment(models.Model):
    """Shipment/Claim data model for legal system"""
    
    # Basic identification
    Claim_No = models.CharField(max_length=100, unique=True, verbose_name='Shipment Number')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='shipments')
    client_reference = models.CharField(max_length=50, blank=True, null=True, verbose_name='Client Reference', 
                                     help_text='Auto-generated client-specific reference (e.g., ClientName-1-20250601)')
    
    # Claim details
    Brand = models.CharField(max_length=100, blank=True, null=True, verbose_name='Brand')
    Claimant = models.CharField(max_length=200, blank=True, null=True, verbose_name='Claimant Name')
    
    # Intent to claim
    Intent_To_Claim = models.CharField(max_length=3, blank=True, null=True, verbose_name='Intent To Claim',
                                     choices=[('YES', 'Yes'), ('NO', 'No')])
    Intend_Claim_Date = models.DateField(blank=True, null=True, verbose_name='Intent To Claim Date')
    
    # Formal claim
    Formal_Claim_Received = models.CharField(max_length=3, blank=True, null=True, verbose_name='Formal Claim',
                                          choices=[('YES', 'Yes'), ('NO', 'No')])
    Formal_Claim_Date_Received = models.DateField(blank=True, null=True, verbose_name='Formal Claim Date')
    
    # Financial information
    Claimed_Amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Value')
    Amount_Paid_By_Carrier = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Paid By Carrier')
    Amount_Paid_By_Awa = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Paid By ISCM/AWA')
    Amount_Paid_By_Insurance = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Paid By Insurance')
    Total_Savings = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Total Savings')
    Financial_Exposure = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Financial Exposure')
    
    # Status and settlement
    Settlement_Status = models.CharField(max_length=15, blank=True, null=True, verbose_name='Settled or Not Settled',
                                       choices=[('SETTLED', 'Settled'), ('NOT_SETTLED', 'Not Settled'), ('PARTIAL', 'Partially Settled')])
    Status = models.CharField(max_length=15, default='OPEN', verbose_name='Status',
                            choices=[('OPEN', 'Open'), ('PENDING', 'Pending'), ('CLOSED', 'Closed'), ('REJECTED', 'Rejected'), ('UNDER_REVIEW', 'Under Review')])
    Closed_Date = models.DateField(blank=True, null=True, verbose_name='Closed Date')
    
    # Branch information
    Branch = models.CharField(max_length=3, choices=[
        ('ATL', 'ATL'), ('CMU', 'CMU'), ('CON', 'CON'), ('DOR', 'DOR'), 
        ('HEC', 'HEC'), ('HNL', 'HNL'), ('HOU', 'HOU'), ('ICS', 'ICS'), 
        ('IMP', 'IMP'), ('JFK', 'JFK'), ('LCL', 'LCL'), ('ORD', 'ORD'), ('PPG', 'PPG')
    ])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Shipment"
        verbose_name_plural = "Shipments"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['Claim_No']),
            models.Index(fields=['client']),
            models.Index(fields=['Status']),
            models.Index(fields=['Branch']),
            models.Index(fields=['client_reference']),
        ]
    
    def __str__(self):
        return f"{self.Claim_No} - {self.client.name if self.client else 'Unknown Client'}"
    
    def save(self, *args, **kwargs):
        # Generate client reference if not provided
        if not self.client_reference and self.client:
            # Get count of existing shipments for this client
            count = Shipment.objects.filter(client=self.client).count()
            # Format: ClientName-Count-Date
            date_str = self.created_at.strftime("%Y%m%d") if self.created_at else timezone.now().strftime("%Y%m%d")
            self.client_reference = f"{self.client.name.replace(' ', '')}-{count + 1}-{date_str}"
        
        super().save(*args, **kwargs)
    
    @property
    def is_closed(self):
        """Check if shipment is closed"""
        return self.Status == 'CLOSED'
    
    @property
    def total_paid(self):
        """Calculate total amount paid"""
        carrier = self.Amount_Paid_By_Carrier or 0
        awa = self.Amount_Paid_By_Awa or 0
        insurance = self.Amount_Paid_By_Insurance or 0
        return carrier + awa + insurance
    
    @property
    def net_exposure(self):
        """Calculate net financial exposure"""
        claimed = self.Claimed_Amount or 0
        total_paid = self.total_paid
        return claimed - total_paid

class Settings(models.Model):
    """Application settings model"""
    
    # System Settings
    auto_sync = models.BooleanField(default=False, help_text="Automatically sync data every 24 hours")
    backup_frequency = models.CharField(max_length=20, default='weekly', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], help_text="Backup frequency")
    session_timeout = models.IntegerField(default=30, help_text="Session timeout in minutes")
    dark_mode = models.BooleanField(default=False, help_text="Enable dark mode theme")
    
    # Data Sync Settings
    google_sheets_enabled = models.BooleanField(default=True, help_text="Enable Google Sheets integration")
    sql_server_enabled = models.BooleanField(default=True, help_text="Enable SQL Server integration")
    sync_interval = models.IntegerField(default=24, help_text="Sync interval value")
    sync_interval_unit = models.CharField(max_length=10, default='hours', choices=[
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days')
    ], help_text="Sync interval unit")
    
    # Notification Settings
    email_notifications = models.BooleanField(default=False, help_text="Enable email notifications")
    sync_notifications = models.BooleanField(default=True, help_text="Notify when data synchronization completes")
    notification_email = models.EmailField(blank=True, null=True, help_text="Email address for notifications")
    
    # Security Settings
    two_factor_auth = models.BooleanField(default=False, help_text="Enable two-factor authentication")
    password_expiry = models.IntegerField(default=90, help_text="Password expiry in days")
    max_login_attempts = models.IntegerField(default=5, help_text="Maximum login attempts")
    
    # Compliance Document Settings
    compliance_auto_sync = models.BooleanField(default=False, help_text="Enable automatic compliance document syncing")
    compliance_sync_interval = models.IntegerField(default=5, help_text="Compliance sync interval value")
    compliance_sync_unit = models.CharField(max_length=10, default='minutes', choices=[
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days')
    ], help_text="Compliance sync interval unit")
    compliance_batch_mode = models.CharField(max_length=20, default='batch', choices=[
        ('batch', 'Process in Batches'),
        ('all', 'Process ALL at Once')
    ], help_text="Processing mode: batches or all documents at once")
    compliance_batch_size = models.IntegerField(default=50, help_text="Number of inspections to process per batch (only for batch mode)")
    compliance_date_range = models.IntegerField(default=7, help_text="Process inspections from last N days (only for batch mode)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"
    
    def __str__(self):
        return "Application Settings"
    
    @classmethod
    def get_settings(cls):
        """Get or create settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

class SystemLog(models.Model):
    """System log to track user activities"""
    
    # User information
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='system_logs', verbose_name="User")
    
    # Activity details
    action = models.CharField(max_length=50, choices=[
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('CREATE', 'Create Record'),
        ('UPDATE', 'Update Record'),
        ('DELETE', 'Delete Record'),
        ('VIEW', 'View Page'),
        ('NAVIGATE', 'Navigate'),
        ('SYNC', 'Data Sync'),
        ('SETTINGS', 'Settings Change'),
        ('USER_MANAGEMENT', 'User Management'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('FILE_UPLOAD', 'File Upload'),
        ('EXPORT', 'Data Export'),
        ('IMPORT', 'Data Import'),
        ('SEARCH', 'Search'),
        ('FILTER', 'Filter'),
        ('ERROR', 'Error'),
        ('WARNING', 'Warning'),
        ('INFO', 'Information'),
    ], verbose_name="Action Type")
    
    # Page and object information
    page = models.CharField(max_length=100, blank=True, null=True, verbose_name="Page/URL")
    object_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Object Type")
    object_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Object ID")
    
    # Details and metadata
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    details = models.JSONField(blank=True, null=True, verbose_name="Additional Details")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP Address")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    
    class Meta:
        db_table = 'system_logs'
        ordering = ['-timestamp']
        verbose_name = "System Log"
        verbose_name_plural = "System Logs"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['page']),
            models.Index(fields=['object_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @classmethod
    def log_activity(cls, user, action, page=None, object_type=None, object_id=None, 
                   description=None, details=None, ip_address=None, user_agent=None):
        """Convenience method to log user activity"""
        return cls.objects.create(
            user=user,
            action=action,
            page=page,
            object_type=object_type,
            object_id=object_id,
            description=description,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )

