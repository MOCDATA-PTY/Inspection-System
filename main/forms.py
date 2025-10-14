from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Client, Inspection, InspectorMapping

class ClientForm(forms.ModelForm):
    """Form for creating/editing clients"""
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Client name'
        })
    )
    
    internal_account_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Internal account code (from Google Sheets Column H)'
        })
    )
    
    class Meta:
        model = Client
        fields = ['name', 'internal_account_code']
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("Client name is required.")
        return name

class InspectionForm(forms.ModelForm):
    """Form for creating/editing inspections"""
    
    inspection_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    direction_expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    bought_sample_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'class': 'form-control',
            'placeholder': '0.00'
        })
    )
    
    normal_hours = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'step': '0.1',
            'class': 'form-control',
            'placeholder': '0.0'
        })
    )
    
    kilometres_traveled = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'step': '0.1',
            'class': 'form-control',
            'placeholder': '0.0'
        })
    )
    
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional comments or notes...'
        })
    )
    
    class Meta:
        model = Inspection
        fields = [
            'inspector', 'inspection_number', 'inspection_date', 'facility_client_name', 'town',
            'commodity', 'product_name', 'product_class', 'inspected', 'sampled',
            'normal_hours', 'kilometres_traveled', 'fat', 'protein', 'calcium', 'dna',
            'bought_sample_amount', 'lab_used', 'follow_up', 'occurrence_report',
            'dispensation_application', 'comments', 'uploaded', 'rfi_reference_number',
            'invoice_reference_number', 'lab_result_reference_number', 're_test',
            're_test_reference_number', 'verification_external_testing', 'compliance_document',
            'direction_expiry_date', 'email', 'additional_email_1', 'additional_email_2',
            'additional_email_3', 'additional_email_4', 'was_mail_sent', 'compiled_supporting_documents'
        ]
        widgets = {
            'inspector': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Inspector name'}),
            'inspection_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Inspection number'}),
            'facility_client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Facility or client name'}),
            'town': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Town/location'}),
            'commodity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., RAW'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'product_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product class'}),
            'lab_used': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Food Safety Laboratory'}),
            'rfi_reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RFI reference'}),
            'invoice_reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Invoice reference'}),
            'lab_result_reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lab result reference'}),
            're_test_reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Re-test reference'}),
            'compliance_document': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Compliance document'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Primary email'}),
            'additional_email_1': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Additional email 1'}),
            'additional_email_2': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Additional email 2'}),
            'additional_email_3': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Additional email 3'}),
            'additional_email_4': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Additional email 4'}),
            'compiled_supporting_documents': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supporting documents'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure required fields are provided
        if not cleaned_data.get('inspector'):
            self.add_error('inspector', 'Inspector name is required.')
        if not cleaned_data.get('inspection_number'):
            self.add_error('inspection_number', 'Inspection number is required.')
        if not cleaned_data.get('inspection_date'):
            self.add_error('inspection_date', 'Inspection date is required.')
        if not cleaned_data.get('facility_client_name'):
            self.add_error('facility_client_name', 'Facility/client name is required.')
        
        # Check for duplicate inspection numbers for the same inspector
        inspector = cleaned_data.get('inspector')
        inspection_number = cleaned_data.get('inspection_number')
        
        if inspector and inspection_number:
            existing = Inspection.objects.filter(
                inspector=inspector,
                inspection_number=inspection_number
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                self.add_error('inspection_number', f'Inspection number {inspection_number} already exists for inspector {inspector}.')
        
        return cleaned_data

# User management forms

class RegisterForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off',
            'placeholder': 'Email address'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
            'placeholder': 'Confirm password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    """Form for user login"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password',
            'placeholder': 'Password'
        })
    )


class InspectorMappingForm(forms.ModelForm):
    """Form for creating/editing inspector mappings"""
    inspector_id = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Server inspector ID (e.g., 1234567)',
            'min': '1'
        })
    )
    
    inspector_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Inspector name (e.g., Ethan)'
        })
    )
    
    class Meta:
        model = InspectorMapping
        fields = ['inspector_id', 'inspector_name', 'is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def clean_inspector_id(self):
        inspector_id = self.cleaned_data.get('inspector_id')
        if inspector_id:
            # Check if this ID already exists (excluding current instance if editing)
            existing = InspectorMapping.objects.filter(inspector_id=inspector_id)
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(f"Inspector ID {inspector_id} is already assigned to another inspector.")
        
        return inspector_id
    
    def clean_inspector_name(self):
        inspector_name = self.cleaned_data.get('inspector_name')
        if not inspector_name:
            raise ValidationError("Inspector name is required.")
        return inspector_name