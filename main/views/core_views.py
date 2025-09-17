from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..models import FoodSafetyAgencyInspection

@login_required
def update_product_name(request):
    """Update product_name for an inspection"""
    if request.method == 'POST':
        try:
            inspection_id = request.POST.get('inspection_id')
            value = request.POST.get('product_name', '')
            inspections = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id)
            inspection = inspections.first()
            if not inspection:
                return JsonResponse({'success': False, 'error': f'Inspection {inspection_id} not found'})
            inspection.product_name = value.strip() or None
            inspection.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def update_product_class(request):
    """Update product_class for an inspection"""
    if request.method == 'POST':
        try:
            inspection_id = request.POST.get('inspection_id')
            value = request.POST.get('product_class', '')
            inspections = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id)
            inspection = inspections.first()
            if not inspection:
                return JsonResponse({'success': False, 'error': f'Inspection {inspection_id} not found'})
            inspection.product_class = value.strip() or None
            inspection.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta, date, datetime
from decimal import Decimal
import calendar
import json
import requests
import os
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db.models import Q
from ..forms import LoginForm, RegisterForm, ClientForm, InspectionForm, InspectorMappingForm
from ..models import Client, Inspection, Shipment, Settings, FoodSafetyAgencyInspection, SystemLog, InspectorMapping
from django.views.decorators.csrf import csrf_exempt
from ..decorators import role_required, inspector_restricted, financial_only, scientist_only, inspector_only_inspections
@login_required
@role_required(['admin', 'super_admin', 'developer'])
def save_manual_client_email(request):
    """Persist a manual email override for a client (by business name)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
        client_name = (data.get('client_name') or '').strip()
        email = (data.get('email') or '').strip()
        if not client_name:
            return JsonResponse({'success': False, 'error': 'client_name is required'})
        if email and '@' not in email:
            return JsonResponse({'success': False, 'error': 'Invalid email format'})

        # Try multiple matching strategies to find the client
        client = Client.objects.filter(client_id__iexact=client_name).first()
        if not client:
            client = Client.objects.filter(name__iexact=client_name).first()
        if not client:
            client = Client.objects.filter(client_id__icontains=client_name).first()
        if not client:
            # Final fallback: normalized comparison in Python
            import re
            def _norm(txt: str) -> str:
                txt = (txt or '').lower().strip()
                txt = re.sub(r"[\(\)\[\]{}\\/._,-]", " ", txt)
                txt = re.sub(r"\s+", " ", txt)
                return txt
            norm_target = _norm(client_name)
            for c in Client.objects.only('id', 'client_id', 'name'):
                if _norm(c.client_id) == norm_target or _norm(c.name) == norm_target:
                    client = c
                    break
        # If no client found, create a minimal record with this business name
        if not client:
            client = Client.objects.create(client_id=client_name, name=client_name)
        # Save manual override and record additional email
        if email:
            client.manual_email = email
            client.save(update_fields=['manual_email'])
            try:
                from ..models import ClientEmail
                ClientEmail.objects.get_or_create(client=client, email=email)
            except Exception:
                pass
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@role_required(['admin', 'super_admin', 'developer'])
def delete_client_email(request):
    """Delete a removable client email (manual or additional)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
        client_name = (data.get('client_name') or '').strip()
        email = (data.get('email') or '').strip()
        if not (client_name and email):
            return JsonResponse({'success': False, 'error': 'client_name and email are required'})
        client = Client.objects.filter(client_id__iexact=client_name).first()
        if not client:
            return JsonResponse({'success': False, 'error': 'Client not found'})
        # If matches manual_email, clear it
        if client.manual_email and client.manual_email.lower() == email.lower():
            client.manual_email = None
            client.save(update_fields=['manual_email'])
            return JsonResponse({'success': True})
        # Otherwise try remove from additional emails
        try:
            from ..models import ClientEmail
            deleted, _ = ClientEmail.objects.filter(client=client, email__iexact=email).delete()
            if deleted:
                return JsonResponse({'success': True})
        except Exception:
            pass
        return JsonResponse({'success': False, 'error': 'Email not found or not removable'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
from .data_views import remote_sqlserver_data_view
from .utils import apply_filters, clear_messages
from ..services.google_drive_service import GoogleDriveService


# Global flag to track OneDrive operations during batch processing
onedrive_batch_processing = False

@login_required
def check_compliance_documents_batch(request):
    """Check compliance documents for multiple inspections after page loads."""
    global onedrive_batch_processing
    
    if request.method == 'POST':
        try:
            onedrive_batch_processing = True  # Start tracking OneDrive operations
            
            data = json.loads(request.body.decode('utf-8'))
            inspections_to_check = data.get('inspections', [])
            
            results = {}
            total_inspections = len(inspections_to_check)
            
            for i, inspection in enumerate(inspections_to_check):
                client_name = inspection.get('client_name')
                inspection_date = inspection.get('date_of_inspection')
                
                if client_name and inspection_date:
                    has_compliance = check_for_compliance_documents(client_name, inspection_date)
                    results[f"{client_name}_{inspection_date}"] = has_compliance
                    
                    # Log progress for debugging
                    print(f"Processed {i+1}/{total_inspections}: {client_name} - {inspection_date}")
            
            # Add a small delay to ensure all OneDrive operations complete
            import time
            time.sleep(2)
            
            onedrive_batch_processing = False  # Stop tracking OneDrive operations
            
            return JsonResponse({
                'success': True,
                'results': results,
                'total_processed': total_inspections
            })
        except Exception as e:
            onedrive_batch_processing = False  # Ensure flag is reset on error
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})





def index(request):
    """Redirect root URL to login page."""
    return redirect('login')


# =============================================================================
# AUTHENTICATION VIEWS
# =============================================================================

def user_login(request):
    """Handle user login with improved error handling and CSRF protection."""
    if request.method == 'POST':
        try:
            form = LoginForm(request, data=request.POST)
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            # Debug print
            print(f"Login attempt - Username: {username}")
            print(f"Password length: {len(password) if password else 0}")
            
            user = authenticate(request, username=username, password=password)
            print(f"Authentication result: {user}")
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Set initial last activity timestamp
                    from django.utils import timezone
                    request.session['last_activity'] = timezone.now().isoformat()
                    request.session.set_expiry(0)  # Expire session on browser close
                    # messages.success(request, f"Welcome back, {user.username}!")
                    
                    # Role-based redirect logic
                    user_role = getattr(user, 'role', 'inspector')
                    if user_role == 'admin':
                        # Redirect administrators to inspection page
                        return redirect('shipment_list')
                    else:
                        # All other users go to home page
                        return redirect('home')
                else:
                    messages.error(request, "Your account is disabled.")
            else:
                messages.error(request, "Invalid username or password. Please try again.")
        except Exception as e:
            # Handle CSRF and other errors gracefully
            print(f"Login error: {e}")
            if "CSRF" in str(e):
                messages.error(request, "Security token expired. Please refresh the page and try again.")
            else:
                messages.error(request, "An error occurred during login. Please try again.")
    else:
        form = LoginForm()

    response = render(request, 'main/login.html', {'form': form})
    response['Cache-Control'] = 'no-store'
    # Ensure CSRF cookie is set
    from django.middleware.csrf import get_token
    get_token(request)
    return response


def register(request):
    """Handle new user registration and automatic login upon successful registration."""
    clear_messages(request)
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Log the user in immediately after registration
                user = authenticate(request, username=user.username, password=form.cleaned_data['password1'])
                if user:
                    login(request, user)
                    # Set initial last activity timestamp
                    from django.utils import timezone
                    request.session['last_activity'] = timezone.now().isoformat()
                    request.session.set_expiry(0)
                    messages.success(request, f"Registration successful! Welcome, {user.username}!")
                    return redirect('home')
                else:
                    messages.error(request, "Registration successful but login failed. Please try logging in manually.")
                    return redirect('login')
            except Exception as e:
                print(f"Registration error: {e}")
                messages.error(request, f"Registration failed: {str(e)}")
        else:
            # Debug: print form errors and add them as messages
            print("Form errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, f"{error}")
                    elif field == 'username':
                        messages.error(request, f"Username: {error}")
                    elif field == 'password1':
                        messages.error(request, f"Password: {error}")
                    elif field == 'password2':
                        messages.error(request, f"Password confirmation: {error}")
                    elif field == 'email':
                        messages.error(request, f"Email: {error}")
                    else:
                        messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = RegisterForm()

    return render(request, 'main/register.html', {'form': form})


def user_logout(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')


# =============================================================================
# CLIENT MANAGEMENT VIEWS
# =============================================================================

@login_required(login_url='login')
@inspector_only_inspections
def client_list(request):
    """Redirect to client_allocation since they serve the same purpose."""
    # Preserve any query parameters when redirecting
    query_string = request.GET.urlencode()
    if query_string:
        return redirect(f"{reverse('client_allocation')}?{query_string}")
    else:
        return redirect('client_allocation')


@login_required(login_url='login')
@inspector_only_inspections
def add_client(request):
    """Add a new client."""
    clear_messages(request)
    
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            try:
                client = form.save()
                messages.success(request, f"Client '{client.name}' added successfully!")
                return redirect('client_list')
            except Exception as e:
                messages.error(request, f"Error adding client: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = ClientForm()
    
    context = {
        'form': form,
        'action': 'Add'
    }
    
    return render(request, 'main/client_form.html', context)


@login_required(login_url='login')
@inspector_only_inspections
def edit_client(request, pk):
    """Edit an existing client."""
    clear_messages(request)
    
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            try:
                client = form.save()
                messages.success(request, f"Client '{client.name}' updated successfully!")
                return redirect('client_list')
            except Exception as e:
                messages.error(request, f"Error updating client: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = ClientForm(instance=client)
    
    context = {
        'form': form,
        'client': client,
        'action': 'Edit'
    }
    
    return render(request, 'main/client_form.html', context)


@login_required(login_url='login')
@inspector_only_inspections
def delete_client(request, pk):
    """Delete a client."""
    clear_messages(request)
    
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        try:
            client_name = client.name
            client.delete()
            messages.success(request, f"Client '{client_name}' deleted successfully!")
            return redirect('client_list')
        except Exception as e:
            messages.error(request, f"Error deleting client: {str(e)}")
            return redirect('client_list')
    
    context = {
        'client': client
    }
    
    return render(request, 'main/client_confirm_delete.html', context)


# =============================================================================
# INSPECTION MANAGEMENT VIEWS
# =============================================================================

@login_required(login_url='login')
def inspection_list(request):
    """Display list of all inspections."""
    clear_messages(request)
    
    # Get all inspections with optional search and filtering
    search_query = request.GET.get('search', '')
    inspector_filter = request.GET.get('inspector', '')
    town_filter = request.GET.get('town', '')
    commodity_filter = request.GET.get('commodity', '')
    
    inspections = Inspection.objects.all()
    
    if search_query:
        inspections = inspections.filter(
            models.Q(facility_client_name__icontains=search_query) |
            models.Q(inspector__icontains=search_query) |
            models.Q(product_name__icontains=search_query) |
            models.Q(comments__icontains=search_query)
        )
    
    if inspector_filter:
        inspections = inspections.filter(inspector=inspector_filter)
    
    if town_filter:
        inspections = inspections.filter(town=town_filter)
    
    if commodity_filter:
        inspections = inspections.filter(commodity=commodity_filter)
    
    # Get unique values for filters
    inspectors = Inspection.objects.values_list('inspector', flat=True).distinct().order_by('inspector')
    towns = Inspection.objects.values_list('town', flat=True).distinct().exclude(town__isnull=True).exclude(town='').order_by('town')
    commodities = Inspection.objects.values_list('commodity', flat=True).distinct().exclude(commodity__isnull=True).exclude(commodity='').order_by('commodity')
    
    context = {
        'inspections': inspections.order_by('-inspection_date', '-inspection_number'),
        'total_inspections': inspections.count(),
        'search_query': search_query,
        'inspector_filter': inspector_filter,
        'town_filter': town_filter,
        'commodity_filter': commodity_filter,
        'inspectors': inspectors,
        'towns': towns,
        'commodities': commodities
    }
    
    return render(request, 'main/inspection_list.html', context)


@login_required(login_url='login')
def add_inspection(request):
    """Add a new inspection."""
    clear_messages(request)
    
    if request.method == 'POST':
        form = InspectionForm(request.POST)
        if form.is_valid():
            try:
                inspection = form.save()
                messages.success(request, f"Inspection {inspection.inspection_number} for {inspection.facility_client_name} added successfully!")
                return redirect('inspection_list')
            except Exception as e:
                messages.error(request, f"Error adding inspection: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = InspectionForm()
    
    context = {
        'form': form,
        'action': 'Add'
    }
    
    return render(request, 'main/inspection_form.html', context)


@login_required(login_url='login')
def edit_inspection(request, pk):
    """Edit an existing inspection."""
    clear_messages(request)
    
    inspection = get_object_or_404(Inspection, pk=pk)
    
    if request.method == 'POST':
        form = InspectionForm(request.POST, instance=inspection)
        if form.is_valid():
            try:
                inspection = form.save()
                messages.success(request, f"Inspection {inspection.inspection_number} updated successfully!")
                return redirect('inspection_list')
            except Exception as e:
                messages.error(request, f"Error updating inspection: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = InspectionForm(instance=inspection)
    
    context = {
        'form': form,
        'inspection': inspection,
        'action': 'Edit'
    }
    
    return render(request, 'main/inspection_form.html', context)


@login_required(login_url='login')
def delete_inspection(request, pk):
    """Delete an inspection."""
    clear_messages(request)
    
    inspection = get_object_or_404(Inspection, pk=pk)
    
    if request.method == 'POST':
        try:
            inspection_info = f"{inspection.inspector} - {inspection.inspection_number} - {inspection.facility_client_name}"
            inspection.delete()
            messages.success(request, f"Inspection {inspection_info} deleted successfully!")
            return redirect('inspection_list')
        except Exception as e:
            messages.error(request, f"Error deleting inspection: {str(e)}")
            return redirect('inspection_list')
    
    context = {
        'inspection': inspection
    }
    
    return render(request, 'main/inspection_confirm_delete.html', context)


# =============================================================================
# SHIPMENT PAGE (EMPTY - NO DATA)
# =============================================================================

def check_compliance_documents_status(inspections, client_name, date_of_inspection):
    """Check compliance documents status for a group of inspections.
    
    Returns:
        dict: {
            'has_any_compliance': bool,  # True if at least one commodity has compliance docs
            'all_commodities_have_compliance': bool,  # True if every commodity has compliance docs
            'commodity_status': dict  # Status for each commodity
        }
    """
    import os
    from django.conf import settings
    from datetime import datetime
    import re
    import requests
    import json
    from django.core.cache import cache
    
    # Create cache key for this specific group
    cache_key = f"compliance_status_{client_name}_{date_of_inspection}"
    cached_status = cache.get(cache_key)
    
    if cached_status:
        return cached_status
    
    try:
        # First try to check OneDrive (since files are now uploaded there)
        onedrive_status = check_compliance_documents_status_onedrive(inspections, client_name, date_of_inspection)
        if onedrive_status:
            # Cache the result for 10 minutes
            cache.set(cache_key, onedrive_status, 600)
            return onedrive_status
        
        # Fallback to local media folder check (for backward compatibility)
        local_status = check_compliance_documents_status_local(inspections, client_name, date_of_inspection)
        # Cache the result for 10 minutes
        cache.set(cache_key, local_status, 600)
        return local_status
        
    except Exception as e:
        # If any error, return default status
        default_status = {
            'has_any_compliance': False,
            'all_commodities_have_compliance': False,
            'commodity_status': {}
        }
        # Cache the default result for 5 minutes
        cache.set(cache_key, default_status, 300)
        return default_status


def check_compliance_documents_status_onedrive(inspections, client_name, date_of_inspection):
    """Check compliance documents status in OneDrive."""
    try:
        import os
        from django.conf import settings
        from datetime import datetime
        import re
        import requests
        import json
        from django.core.cache import cache
        
        # Create cache key for OneDrive status
        cache_key = f"onedrive_compliance_{client_name}_{date_of_inspection}"
        cached_status = cache.get(cache_key)
        
        if cached_status:
            return cached_status
        
        # Load OneDrive tokens
        token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
        if not os.path.exists(token_file):
            return None  # No OneDrive tokens, fall back to local check
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        access_token = token_data.get('access_token')
        if not access_token:
            return None
        
        # Build OneDrive path
        year_folder = date_of_inspection.strftime("%Y")
        month_folder = date_of_inspection.strftime("%B")
        
        # Use original client name for OneDrive folder matching (folders now use original names)
        client_folder = client_name or 'Unknown Client'
        
        # Also try legacy variations for backwards compatibility
        client_folder_variations = [
            client_folder,  # Primary: original name
            # Legacy sanitized names for backwards compatibility
            re.sub(r'[^a-zA-Z0-9_]', '_', client_name).replace('_+', '_').strip('_'),
            re.sub(r'[^a-zA-Z0-9]', '', client_name),
            client_name.replace(' ', '_').replace('-', '_').replace("'", '').replace('"', ''),
        ]
        
        # Remove duplicates while preserving order
        client_folder_variations = list(dict.fromkeys(client_folder_variations))
        
        onedrive_base = getattr(settings, 'ONEDRIVE_FOLDER', 'FoodSafety Agency Inspections')
        
        # Get unique commodities from inspections
        commodities = set()
        for inspection in inspections:
            if inspection.commodity:
                commodities.add(str(inspection.commodity).upper().strip())
        
        commodity_status = {}
        has_any_compliance = False
        
        # Try each client folder variation
        for client_folder in client_folder_variations:
            base_path = f"{onedrive_base}/inspection/{year_folder}/{month_folder}/{client_folder}/Compliance"
            
            # Check each commodity folder in OneDrive
            for commodity in commodities:
                commodity_path = f"{base_path}/{commodity}"
                has_files = False
                
                # Check if commodity folder exists and has files
                check_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{commodity_path}:/children"
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(check_url, headers=headers)
                if response.status_code == 200:
                    files = response.json().get('value', [])
                    has_files = len(files) > 0
                    if has_files:
                        has_any_compliance = True
                
                commodity_status[commodity] = has_files
            
            # If we found any compliance documents, break out of the loop
            if has_any_compliance:
                break
        
        # Check if all commodities have compliance documents
        all_commodities_have_compliance = all(commodity_status.values()) if commodity_status else False
        
        result = {
            'has_any_compliance': has_any_compliance,
            'all_commodities_have_compliance': all_commodities_have_compliance,
            'commodity_status': commodity_status
        }
        
        # Cache the result for 15 minutes to reduce API calls
        cache.set(cache_key, result, 900)
        
        return result
        
    except Exception as e:
        return None  # Fall back to local check


def check_compliance_documents_status_local(inspections, client_name, date_of_inspection):
    """Check compliance documents status in local media folder (fallback)."""
    try:
        import os
        from django.conf import settings
        from datetime import datetime
        import re
        
        # Build base path: media/inspection/YYYY/Month/ClientName/Compliance/
        date_str = str(date_of_inspection).replace('-', '')
        year_folder = date_str[:4]
        month_num = int(date_str[4:6]) if len(date_str) >= 6 else int(datetime.now().strftime('%m'))
        year_num = int(year_folder)
        month_folder = datetime.strptime(f"{year_num}-{month_num:02d}-01", "%Y-%m-%d").strftime("%B")
        
        # Get unique commodities from inspections
        commodities = set()
        for inspection in inspections:
            if inspection.commodity:
                commodities.add(str(inspection.commodity).upper().strip())
        
        commodity_status = {}
        has_any_compliance = False
        
        # Use original client name for folder matching (folders now use original names)
        client_folder = client_name or 'Unknown Client'
        
        print(f"🔍 Checking compliance for client: {client_name}")
        print(f"   📁 Looking for folder: {client_folder}")
        
        # Check compliance folder with original client name
        base_path = os.path.join(settings.MEDIA_ROOT, 'inspection', year_folder, month_folder, client_folder, 'Compliance')
        print(f"   📂 Checking path: {base_path}")
        
        if os.path.exists(base_path):
            print(f"   ✅ Found compliance folder: {client_folder}")
            
            # Check each commodity folder
            for commodity in commodities:
                commodity_path = os.path.join(base_path, commodity)
                if os.path.exists(commodity_path):
                    files = os.listdir(commodity_path)
                    if files:
                        commodity_status[commodity] = True
                        has_any_compliance = True
                        print(f"   ✅ {commodity}: {len(files)} files")
                    else:
                        commodity_status[commodity] = False
                        print(f"   ❌ {commodity}: No files")
                else:
                    commodity_status[commodity] = False
                    print(f"   ❌ {commodity}: Folder not found")
            
            # Return results since we found the folder
            return {
                'has_any_compliance': has_any_compliance,
                'commodity_status': commodity_status,
                'client_folder_found': True
            }
        else:
            print(f"   ❌ Compliance folder not found: {base_path}")
            # Check if we need to try other variations for backwards compatibility
            client_folder_variations = [
                # Legacy sanitized names for backwards compatibility
                re.sub(r'[^a-zA-Z0-9_]', '_', client_name).replace('_+', '_').strip('_'),
                re.sub(r'[^a-zA-Z0-9]', '', client_name),
                client_name.replace(' ', '_').replace('-', '_').replace("'", '').replace('"', ''),
            ]
            
            # Remove duplicates while preserving order
            client_folder_variations = list(dict.fromkeys(client_folder_variations))
            
            print(f"   📁 Trying legacy folder variations: {client_folder_variations}")
            
            # Check each commodity folder for each client folder variation
            for legacy_client_folder in client_folder_variations:
                legacy_base_path = os.path.join(settings.MEDIA_ROOT, 'inspection', year_folder, month_folder, legacy_client_folder, 'Compliance')
                print(f"   📂 Checking legacy path: {legacy_base_path}")
                
                if os.path.exists(legacy_base_path):
                    print(f"   ✅ Found legacy compliance folder: {legacy_client_folder}")
                    
                    # Check each commodity folder
                    for commodity in commodities:
                        commodity_path = os.path.join(legacy_base_path, commodity)
                        has_files = False
                        
                        if os.path.isdir(commodity_path):
                            # Check if there are any files in the commodity folder
                            files = [f for f in os.listdir(commodity_path) if os.path.isfile(os.path.join(commodity_path, f))]
                            has_files = len(files) > 0
                            if has_files:
                                has_any_compliance = True
                                print(f"   📄 {commodity}: {len(files)} files found")
                            else:
                                print(f"   📄 {commodity}: No files")
                        else:
                            print(f"   📄 {commodity}: No folder")
                        
                        commodity_status[commodity] = has_files
                    
                    # If we found the folder, break out of the loop
                    break
                else:
                    print(f"   ❌ Legacy folder not found: {legacy_client_folder}")
        
        # Check if all commodities have compliance documents
        all_commodities_have_compliance = all(commodity_status.values()) if commodity_status else False
        
        print(f"   🎯 Final result: has_any_compliance={has_any_compliance}, all_commodities_have_compliance={all_commodities_have_compliance}")
        
        return {
            'has_any_compliance': has_any_compliance,
            'all_commodities_have_compliance': all_commodities_have_compliance,
            'commodity_status': commodity_status
        }
        
    except Exception as e:
        print(f"   ❌ Error checking compliance: {str(e)}")
        # If any error, return default status
        return {
            'has_any_compliance': False,
            'all_commodities_have_compliance': False,
            'commodity_status': {}
        }


@login_required(login_url='login')
def shipment_list(request):
    """Display Food Safety Agency inspections from local database on shipments page."""
    import time
    start_time = time.time()  # Track performance
    clear_messages(request)
    
    print("=" * 80)
    print("🚀🚀🚀 SHIPMENT_LIST VIEW CALLED - DEBUGGING INSPECTION ISSUES 🚀🚀🚀")
    print(f"👤 User: {request.user.username} (Role: {getattr(request.user, 'role', 'unknown')})")
    print("=" * 80)
    
    # Check for stored sync messages in cache and display them
    from django.core.cache import cache
    sync_success = cache.get('sync_success_message')
    sync_info_1 = cache.get('sync_info_message_1')
    sync_info_2 = cache.get('sync_info_message_2')
    
    if sync_success:
        messages.success(request, sync_success)
        cache.delete('sync_success_message')
    if sync_info_1:
        messages.info(request, sync_info_1)
        cache.delete('sync_info_message_1')
    if sync_info_2:
        messages.info(request, sync_info_2)
        cache.delete('sync_info_message_2')
    
    # Use caching to improve performance, but skip cache if filters are applied
    from django.core.cache import cache
    has_filters = any(request.GET.get(param) for param in ['claim_no', 'client', 'branch', 'inspection_date_from', 'inspection_date_to', 'sent_status', 'rfi_status', 'page'])
    
    cache_key = f"shipment_list_{request.user.id}_{request.user.role}"
    
    # FORCE CACHE CLEAR on every page load to prevent stale data issues
    print("🧹 CLEARING CACHE on page load to prevent stale data...")
    cache.delete(cache_key)
    cache.delete('drive_files_lookup_v2')
    cache.delete('page_clients_status_cache')
    print("✅ Cache cleared - fresh data will be loaded")
    
    # Check if we have cached data (only clear if needed)
    cached_data = cache.get(cache_key)
    
    # Get Food Safety Agency inspections from local database with MASSIVE OPTIMIZATION
    from ..models import FoodSafetyAgencyInspection, InspectorMapping
    from django.db.models import Prefetch, Q
    
    # Start with base queryset - only select needed fields to reduce memory usage
    inspections = FoodSafetyAgencyInspection.objects.select_related('rfi_uploaded_by', 'invoice_uploaded_by', 'sent_by').only(
        'client_name', 'date_of_inspection', 'inspector_name', 'inspector_id',
        'commodity', 'remote_id', 'is_sample_taken', 'needs_retest', 
        'product_name', 'product_class', 'fat', 'protein', 'calcium', 
        'dna', 'bought_sample', 'km_traveled', 'hours', 'lab', 'is_sent', 'sent_date', 'sent_by',
        'rfi_uploaded_by', 'rfi_uploaded_date', 'invoice_uploaded_by', 'invoice_uploaded_date',
        'rfi_uploaded_by__username', 'rfi_uploaded_by__first_name', 'rfi_uploaded_by__last_name',
        'invoice_uploaded_by__username', 'invoice_uploaded_by__first_name', 'invoice_uploaded_by__last_name',
        'sent_by__username', 'sent_by__first_name', 'sent_by__last_name'
    )
    
    # Filter to only show inspections from the last 6 months
    from datetime import datetime, timedelta
    six_months_ago = datetime.now() - timedelta(days=180)  # Approximately 6 months
    inspections = inspections.filter(date_of_inspection__gte=six_months_ago)
    
    # No automatic background fetching - only manual via settings button
    
    # Check compliance status for View Files button colors
    def check_compliance_status(client_name, inspection_date, inspection_count=None, products=None):
        """Check if compliance documents exist for View Files button color"""
        try:
            import os
            from datetime import datetime
            from django.conf import settings
            import re
            
            # Parse date and build folder path
            if isinstance(inspection_date, str):
                date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
            else:
                date_obj = inspection_date
                
            year_folder = date_obj.strftime('%Y')
            month_folder = date_obj.strftime('%B')
            
            # Use original client name for folder matching (folders now use original names)
            client_folder = client_name or 'Unknown Client'
            
            # Check compliance folder
            compliance_base = os.path.join(
                    settings.MEDIA_ROOT,
                    'inspection',
                    year_folder,
                    month_folder,
                    client_folder,
                    'Compliance'
                )
            
            if not os.path.exists(compliance_base):
                return 'no_compliance'
            
            # If this is a grouped inspection, check that ALL inspections have compliance docs
            if inspection_count and inspection_count > 1 and products:
                print(f"Checking grouped inspection: {client_name} with {inspection_count} inspections")
                
                # Count how many inspections have compliance documents
                inspections_with_compliance = 0
                total_inspections = len(products)
                
                for product in products:
                    commodity = product.get('commodity', '').strip().lower()
                    if commodity == 'eggs':
                        commodity = 'egg'
                    
                    if commodity:
                        # Check if this commodity has compliance documents
                        commodity_path = os.path.join(compliance_base, commodity.upper())
                        if os.path.exists(commodity_path):
                            files = [f for f in os.listdir(commodity_path) if os.path.isfile(os.path.join(commodity_path, f))]
                            if files:
                                inspections_with_compliance += 1
                                print(f"✅ {commodity.upper()} has {len(files)} compliance documents")
                            else:
                                print(f"❌ {commodity.upper()} has no compliance documents")
                        else:
                            print(f"❌ {commodity.upper()} folder does not exist")
                    else:
                        print(f"⚠️ Inspection has no commodity specified")
                
                print(f"Compliance status: {inspections_with_compliance}/{total_inspections} inspections have documents")
                
                # Only return 'has_compliance' if ALL inspections have their documents
                if inspections_with_compliance == total_inspections:
                    return 'has_compliance'
                elif inspections_with_compliance > 0:
                    return 'partial_compliance'
                else:
                    return 'no_compliance'
            else:
                # Single inspection - check if any commodity folders have files
                has_files = False
                for commodity_folder in os.listdir(compliance_base):
                    commodity_path = os.path.join(compliance_base, commodity_folder)
                    if os.path.isdir(commodity_path):
                        files = [f for f in os.listdir(commodity_path) if os.path.isfile(os.path.join(commodity_path, f))]
                        if files:
                            has_files = True
                            break
                
                if has_files:
                    return 'has_compliance'
                else:
                    return 'no_compliance'
                
        except Exception as e:
            print(f"Error checking compliance status: {e}")
            return 'no_compliance'
    
    # Filter inspections based on user role and inspector ID
    if request.user.role == 'inspector':
        # Get the inspector ID for the current user
        inspector_id = None
        try:
            inspector_mapping = InspectorMapping.objects.get(
                inspector_name=request.user.get_full_name() or request.user.username
            )
            inspector_id = inspector_mapping.inspector_id
        except InspectorMapping.DoesNotExist:
            # If no mapping found, try to find by username
            try:
                inspector_mapping = InspectorMapping.objects.get(
                    inspector_name=request.user.username
                )
                inspector_id = inspector_mapping.inspector_id
            except InspectorMapping.DoesNotExist:
                # If still no mapping, show no inspections
                inspector_id = None
        
        if inspector_id:
            # Filter inspections to only show those done by this inspector
            inspections = inspections.filter(inspector_id=inspector_id)
        else:
            # If no inspector ID found, show no inspections
            inspections = inspections.none()
    elif request.user.role == 'scientist':
        # Lab technicians can only see inspections where is_sample_taken is True
        inspections = inspections.filter(is_sample_taken=True)
    # For admin, super_admin, financial roles, show all inspections
    # (no filtering needed)
    
    # Apply filters if provided (but skip sent_status filter as it's handled at group level)
    sent_status_param = request.GET.get('sent_status')
    if sent_status_param:
        # Temporarily remove sent_status from request to avoid double filtering
        request.GET = request.GET.copy()
        request.GET.pop('sent_status', None)
        inspections = apply_fsa_inspection_filters(request, inspections)
        # Restore sent_status parameter
        request.GET['sent_status'] = sent_status_param
    else:
        inspections = apply_fsa_inspection_filters(request, inspections)
    
    # DATABASE-LEVEL PAGINATION: Only load data for current page
    from django.db.models import Count, Max, Min, Case, When, BooleanField
    from django.db.models.functions import TruncDate
    from django.core.paginator import Paginator
    import re
    
    # Function to sanitize group_id
    def sanitize_group_id(text):
        """Replace special characters with underscores to match frontend"""
        if not text:
            return ""
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized.strip('_')
    
    # Get page number first
    page_number = request.GET.get('page', 1)
    
    # Create the base queryset for groups
    groups_queryset = inspections.values(
        'client_name', 
        'date_of_inspection'
    ).annotate(
        inspection_count=Count('id'),
        latest_inspection_id=Max('id'),
        earliest_inspection_id=Min('id'),
        has_sent_inspections=Count('id', filter=Q(is_sent=True)),  # Count sent inspections in group
        has_unsent_inspections=Count('id', filter=Q(is_sent=False)),  # Count unsent inspections in group
        has_rfi_inspections=Count('id', filter=Q(rfi_uploaded_by__isnull=False)),  # Count inspections with RFI uploaded
        has_no_rfi_inspections=Count('id', filter=Q(rfi_uploaded_by__isnull=True))  # Count inspections without RFI uploaded
    ).order_by('-date_of_inspection', 'client_name')
    
    # FILTER GROUPS BY SENT STATUS: Apply sent status filter to groups, not individual inspections
    sent_status = request.GET.get('sent_status')
    if sent_status:
        if sent_status == 'YES':
            # Only show groups that have at least one sent inspection
            groups_queryset = groups_queryset.filter(has_sent_inspections__gt=0)
        elif sent_status == 'NO':
            # Only show groups that have at least one unsent inspection
            groups_queryset = groups_queryset.filter(has_unsent_inspections__gt=0)
    
    # FILTER GROUPS BY RFI STATUS: Apply RFI status filter to groups, not individual inspections
    rfi_status = request.GET.get('rfi_status')
    if rfi_status:
        if rfi_status == 'HAS_RFI':
            # Only show groups that have at least one inspection with RFI uploaded
            groups_queryset = groups_queryset.filter(has_rfi_inspections__gt=0)
        elif rfi_status == 'NO_RFI':
            # Only show groups that have at least one inspection without RFI uploaded
            groups_queryset = groups_queryset.filter(has_no_rfi_inspections__gt=0)
    
    # Apply database-level pagination
    paginator = Paginator(groups_queryset, 25)  # 25 groups per page
    page_obj = paginator.get_page(page_number)
    
    # Get only the groups for the current page
    client_date_groups = list(page_obj.object_list)
    
    # PERFORMANCE OPTIMIZATION: Simplified client data loading
    client_cache_key = "client_maps_simple"
    client_data = cache.get(client_cache_key)
    
    if not client_data:
        try:
            from ..models import Client as _Client
            _client_map = {}
            _client_id_map = {}
            
            # Simplified client loading - only get essential data
            for _c in _Client.objects.only('client_id', 'name', 'internal_account_code'):
                key_id = _norm(_c.client_id)
                key_name = _norm(_c.name)
                
                if key_id:
                    if _c.internal_account_code:
                        _client_map[key_id] = _c.internal_account_code
                    _client_id_map[key_id] = _c.client_id
                
                # Also map by name as fallback
                if key_name and key_name != key_id:
                    if _c.internal_account_code and key_name not in _client_map:
                        _client_map[key_name] = _c.internal_account_code
                    if key_name not in _client_id_map:
                        _client_id_map[key_name] = _c.client_id
            
            client_data = {
                'client_map': _client_map,
                'client_id_map': _client_id_map,
                'client_email_map': {}  # Simplified - no email processing for now
            }
            # Cache for 30 minutes (longer cache for better performance)
            cache.set(client_cache_key, client_data, 1800)
            
        except Exception:
            client_data = {
                'client_map': {},
                'client_id_map': {},
                'client_email_map': {}
            }
    
    _client_map = client_data['client_map']
    _client_id_map = client_data['client_id_map']
    _client_email_map = client_data['client_email_map']

    # Helper to fetch internal account code exactly like client-allocation page
    from ..models import Client as _Client
    def _get_internal_account_code(raw_name):
        try:
            # Prefer fast map by normalized key
            code = _client_map.get(_norm(raw_name))
            if code:
                return code
            # Exact DB lookups (case-insensitive) by client_id then name
            client = _Client.objects.filter(client_id__iexact=raw_name).only('internal_account_code').first()
            if client and client.internal_account_code:
                return client.internal_account_code
            client = _Client.objects.filter(name__iexact=raw_name).only('internal_account_code').first()
            if client and client.internal_account_code:
                return client.internal_account_code
        except Exception:
            pass
        return None

    # Helper: normalize names for matching (case-insensitive, collapse spaces, remove punctuation)
    def _norm(text):
        try:
            cleaned = re.sub(r"[\(\)\[\]{}\\/._,-]", " ", (text or ""))
            cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
            return cleaned
        except Exception:
            return (text or "").strip().lower()

    # PERFORMANCE OPTIMIZATION: Batch load all group data at once
    # Get all inspection IDs for the groups we're processing
    group_conditions = Q()
    for group in client_date_groups:
        group_conditions |= Q(
            client_name=group['client_name'],
            date_of_inspection=group['date_of_inspection']
        )
    
    # Load all inspections for these groups in one query
    all_group_inspections = inspections.filter(group_conditions).order_by('client_name', 'date_of_inspection', 'id')
    
    # Log potential data issues for debugging
    if len(all_group_inspections) == 0 and len(client_date_groups) > 0:
        print(f"⚠️  WARNING: No inspections found for {len(client_date_groups)} groups - may be permission filtering issue")
    
    # Group them by client_name and date_of_inspection
    from collections import defaultdict
    grouped_inspections_dict = defaultdict(list)
    for inspection in all_group_inspections:
        key = (inspection.client_name, inspection.date_of_inspection)
        grouped_inspections_dict[key].append(inspection)
    
    # Process grouped inspections efficiently - ONLY CREATE REPRESENTATIVE OBJECTS
    grouped_inspections = []
    print(f"🔄 Processing {len(client_date_groups)} groups...")
    for group in client_date_groups:
        client_name = group['client_name']
        date_of_inspection = group['date_of_inspection']
        inspection_count = group['inspection_count']
        
        print(f"🔍 Processing group: {client_name} - {date_of_inspection} (expected: {inspection_count})")
        
        # Get inspections from our pre-loaded dictionary
        group_inspections = grouped_inspections_dict.get((client_name, date_of_inspection), [])
        
        # Log when we have empty groups but expected products (potential data integrity issue)
        if not group_inspections and inspection_count > 0:
            print(f"⚠️  Data integrity issue: {client_name} on {date_of_inspection} has {inspection_count} expected but 0 loaded")
        
        # Get sample inspector from the group
        sample_inspection = group_inspections[0] if group_inspections else None
        inspector_name = sample_inspection.inspector_name if sample_inspection else None
        
        # Get aggregated km and hours for the group
        group_km_traveled = None
        group_hours = None
        group_is_sent = False
        
        # Get upload tracking information
        rfi_uploader = None
        rfi_upload_date = None
        invoice_uploader = None
        invoice_upload_date = None
        
        if sample_inspection:
            group_km_traveled = sample_inspection.km_traveled
            group_hours = sample_inspection.hours
            # Check if ANY inspection in the group is marked as sent
            group_is_sent = any(inspection.is_sent for inspection in group_inspections)
            
            
            # Get upload information from ANY inspection in group that has uploads
            # Check for RFI uploads across all inspections in the group
            for inspection in group_inspections:
                if inspection.rfi_uploaded_by:
                    rfi_uploader = inspection.rfi_uploaded_by.first_name or inspection.rfi_uploaded_by.username
                    rfi_upload_date = inspection.rfi_uploaded_date
                    break  # Use the first one found
            
            # Check for Invoice uploads across all inspections in the group
            for inspection in group_inspections:
                if inspection.invoice_uploaded_by:
                    invoice_uploader = inspection.invoice_uploaded_by.first_name or inspection.invoice_uploaded_by.username
                    invoice_upload_date = inspection.invoice_uploaded_date
                    break  # Use the first one found
        
        # Get all products for this group (simplified)
        products = []
        
        # If group_inspections is empty but we expected products, try a direct query as fallback
        if not group_inspections and inspection_count > 0:
            print(f"🔄 FALLBACK TRIGGERED: {client_name} on {date_of_inspection} - expected {inspection_count}, got 0")
            try:
                # Direct query without user-specific filters to handle permission issues
                fallback_inspections = FoodSafetyAgencyInspection.objects.filter(
                    client_name=client_name,
                    date_of_inspection=date_of_inspection
                ).order_by('id')
                
                print(f"🔍 Direct query found {fallback_inspections.count()} inspections for {client_name}")
                
                if fallback_inspections.exists():
                    group_inspections = list(fallback_inspections)
                    print(f"✅ Recovered {len(fallback_inspections)} inspections using direct query for {client_name}")
                else:
                    print(f"❌ No inspections found even with direct query for {client_name}")
            except Exception as e:
                print(f"❌ Fallback query failed for {client_name}: {e}")
        elif group_inspections:
            print(f"✅ Found {len(group_inspections)} inspections normally for {client_name}")
        else:
            print(f"ℹ️  No inspections expected for {client_name} (count: {inspection_count})")
        
        for inspection in group_inspections:
            product = {
                'remote_id': inspection.remote_id,
                'client_name': inspection.client_name,
                'internal_account_code': _get_internal_account_code(inspection.client_name),
                'commodity': inspection.commodity,
                'date_of_inspection': inspection.date_of_inspection,
                'is_sample_taken': inspection.is_sample_taken,
                'needs_retest': inspection.needs_retest,
                'product_name': inspection.product_name,
                'product_class': inspection.product_class,
                'fat': inspection.fat,
                'protein': inspection.protein,
                'calcium': inspection.calcium,
                'dna': inspection.dna,
                'bought_sample': inspection.bought_sample,
                'lab': inspection.lab,
                'is_complete': False  # Default to False
            }
            products.append(product)
        
        # Ensure products array is properly assigned
        if len(products) != inspection_count and inspection_count > 0:
            print(f"⚠️  Product count mismatch for {client_name}: expected {inspection_count}, got {len(products)}")
        
        print(f"📦 Final products for {client_name}: {len(products)} products")
        
        # Since we removed the logging system, set default values
        _cached_status = {
            'has_rfi': False,
            'has_invoice': False,
            'has_compliance_docs': False,
            'all_commodities_have_compliance': False,
            'has_any_compliance': False
        }
        
        has_compliance_documents = False
        
        # Check compliance documents status for color coding
        compliance_status_result = check_compliance_documents_status(group_inspections, client_name, date_of_inspection)
        
        # Also check for RFI and Invoice files to determine partial status
        has_rfi = rfi_uploader is not None
        has_invoice = invoice_uploader is not None
        has_compliance = compliance_status_result.get('has_any_compliance', False)
        
        # Determine compliance status for button coloring
        # Complete = has RFI + Invoice + Compliance docs
        # Partial = has any files but not all required
        # None = no files at all
        if has_rfi and has_invoice and has_compliance:
            compliance_status = 'complete'  # Green - all required files present
        elif has_rfi or has_invoice or has_compliance:
            compliance_status = 'partial'   # Yellow - some files present  
        else:
            compliance_status = 'no_compliance'  # Red - no files found
            
        print(f"🎨 COMPLIANCE STATUS DEBUG for {client_name}:")
        print(f"    RFI: {has_rfi} (uploader: {rfi_uploader})")
        print(f"    Invoice: {has_invoice} (uploader: {invoice_uploader})")
        print(f"    Compliance: {has_compliance}")
        print(f"    Final status: {compliance_status}")
        
        # Generate group_id
        sanitized_client = sanitize_group_id(client_name) if client_name else ""
        date_str = date_of_inspection.strftime('%Y%m%d') if date_of_inspection else "NO_DATE"
        group_id = f"{sanitized_client}_{date_str}" if sanitized_client and date_of_inspection else f"ERROR_client_{client_name}_date_{date_of_inspection}"
        
        
        # Create a simple dictionary instead of dynamic class object
        # This avoids pickling issues with Redis cache
        representative_inspection = {
            'client_name': client_name,
            'date_of_inspection': date_of_inspection,
            'inspection_count': inspection_count,
            'internal_account_code': _get_internal_account_code(client_name),
            'client_emails': _client_email_map.get(_norm(client_name), []),
            'is_complete': False,  # Default to False - will be checked on-demand
            'group_id': group_id,
            'inspector_name': inspector_name,
            'location': None,  # No location field in model
            'total_products': inspection_count,
            'km_traveled': group_km_traveled,  # From actual inspection data
            'hours': group_hours,  # From actual inspection data
            'is_sent': group_is_sent,  # From actual inspection data
            'sent_by': next((inspection.sent_by for inspection in group_inspections if inspection.is_sent), None),  # Who marked as sent
            'sent_date': next((inspection.sent_date for inspection in group_inspections if inspection.is_sent), None),  # When marked as sent
            'rfi_uploaded': _cached_status.get('has_rfi', False),
            'invoice_uploaded': _cached_status.get('has_invoice', False),
            'rfi_uploaded_by': rfi_uploader,  # Who uploaded RFI
            'rfi_uploaded_date': rfi_upload_date,  # When RFI was uploaded
            'invoice_uploaded_by': invoice_uploader,  # Who uploaded Invoice
            'invoice_uploaded_date': invoice_upload_date,  # When Invoice was uploaded
            'compliance_status': compliance_status,  # For View Files button color coding
            'compliance_documents_status': {
                'all_commodities_have_compliance': bool(compliance_status_result['all_commodities_have_compliance']),
                'has_any_compliance': bool(compliance_status_result['has_any_compliance'])
            },
            'products': products  # Now populated with actual inspection data
        }
        
        # DEBUG: Verify products are properly assigned
        print(f"🔗 Assigning {len(products)} products to shipment object for {client_name}")
        print(f"    Products in dict: {len(representative_inspection['products'])}")
        
        grouped_inspections.append(representative_inspection)
    
    # Cache filter options
    filter_cache_key = "filter_options"
    filter_data = cache.get(filter_cache_key)
    
    if not filter_data:
        # Get unique values for filters efficiently - LIMIT TO PREVENT LARGE RESPONSES
        inspectors = list(inspections.filter(inspector_name__isnull=False, inspector_name__gt='').values_list('inspector_name', flat=True).distinct().order_by('inspector_name')[:100])
        # Removed clients list since we now use search input instead of dropdown
        commodities = list(inspections.values_list('commodity', flat=True).distinct()[:50])
        
        filter_data = {
            'inspectors': inspectors,
            'commodities': commodities
        }
        # Cache for 5 minutes
        cache.set(filter_cache_key, filter_data, 300)
    
    # Get OneDrive delay settings for countdown display
    from ..models import SystemSettings
    system_settings = SystemSettings.get_settings()
    
    # Calculate delay in days for countdown display
    delay_days = system_settings.onedrive_upload_delay_days
    delay_unit = system_settings.onedrive_upload_delay_unit
    
    if delay_unit == 'hours':
        onedrive_delay_days = delay_days / 24
    elif delay_unit == 'days':
        onedrive_delay_days = delay_days
    elif delay_unit == 'weeks':
        onedrive_delay_days = delay_days * 7
    elif delay_unit == 'months':
        onedrive_delay_days = delay_days * 30
    elif delay_unit == 'years':
        onedrive_delay_days = delay_days * 365
    else:
        onedrive_delay_days = 3  # Default fallback
    
    # Get theme settings for template (from Settings model, not SystemSettings)
    try:
        from ..models import Settings
        settings_obj = Settings.get_settings()
        settings = {
            'dark_mode': settings_obj.dark_mode,
        }
        print(f"🎨 THEME DEBUG: dark_mode = {settings_obj.dark_mode}")
    except Exception as e:
        settings = {'dark_mode': False}
        print(f"🎨 THEME ERROR: {e}")

    # FIX: Use the enhanced grouped_inspections instead of the raw page_obj
    # The page_obj contains raw database results without products, but grouped_inspections has the enhanced data
    context = {
        'shipments': grouped_inspections,  # Use enhanced objects with products
        'inspectors': filter_data['inspectors'],
        'commodities': filter_data['commodities'],
        'total_inspections': len(grouped_inspections),
        'total_shipments': len(grouped_inspections),  # Add this for template compatibility
        'user_role': request.user.role,
        'user_name': request.user.get_full_name() or request.user.username,
        'user_message': None,  # Add this for template compatibility
        'paginator': paginator,
        'page_obj': page_obj,
        'show_all': False,  # Force pagination to prevent broken pipe
        'onedrive_delay_days': int(onedrive_delay_days),  # Add OneDrive delay for countdown
        'settings': settings,  # Add theme settings
    }
    
    # DEBUG: Check what's being sent to template
    print(f"📋 CONTEXT DEBUG (FIXED):")
    print(f"    Total shipments in context: {len(grouped_inspections)}")
    if len(grouped_inspections) > 0:
        first_shipment = grouped_inspections[0]
        print(f"    First shipment: {first_shipment.get('client_name', 'Unknown')}")
        print(f"    First shipment products: {len(first_shipment.get('products', []))}")
        print(f"    First shipment keys: {list(first_shipment.keys())}")
    print(f"    Context keys: {list(context.keys())}")
    print("🎉 PRODUCTS SHOULD NOW BE VISIBLE IN TEMPLATE!")
    
    # Cache the entire context for 5 minutes only if no filters applied
    if not has_filters:
        cache.set(cache_key, context, 300)
    
    # PERFORMANCE LOGGING: Track loading improvements
    import time
    load_time = time.time() - start_time if 'start_time' in locals() else 0
    print(f"⚡ PERFORMANCE: Loaded {len(page_obj)} groups in {load_time:.2f}s (page {page_obj.number} of {paginator.num_pages})")
    
    
    try:
        return render(request, 'main/shipment_list_clean.html', context)
    except BrokenPipeError:
        print("❌ Broken pipe error detected - client disconnected")
        # Return a minimal response to prevent server error
        return render(request, 'main/shipment_list_clean.html', {
            'shipments': [],
            'inspectors': [],
            'commodities': [],
            'total_inspections': 0,
            'total_shipments': 0,
            'user_role': request.user.role,
            'user_name': request.user.get_full_name() or request.user.username,
            'user_message': 'Connection interrupted. Please refresh the page.',
            'paginator': None,
            'page_obj': None,
            'show_all': False,
            'settings': settings,
        })
    except Exception as e:
        print(f"❌ Error rendering shipment list: {e}")
        # Return error page instead of crashing
        return render(request, 'main/shipment_list_clean.html', {
            'shipments': [],
            'inspectors': [],
            'commodities': [],
            'total_inspections': 0,
            'total_shipments': 0,
            'user_role': request.user.role,
            'user_name': request.user.get_full_name() or request.user.username,
            'user_message': f'Error loading data: {str(e)}',
            'paginator': None,
            'page_obj': None,
            'show_all': False,
            'settings': settings,
        })


def check_for_compliance_documents(client_name, inspection_date):
    """Check if compliance documents exist for a given client and date."""
    try:
        from django.conf import settings
        
        # Convert datetime.date to string format if needed
        if hasattr(inspection_date, 'strftime'):
            date_str = inspection_date.strftime('%Y-%m-%d')
        else:
            date_str = str(inspection_date)
        
        # Check OneDrive (preferred)
        onedrive_files = get_inspection_files_onedrive(client_name, date_str)
        if onedrive_files and 'compliance' in onedrive_files:
            compliance_files = onedrive_files['compliance']
            if compliance_files and len(compliance_files) > 0:
                return True

        # If we prefer OneDrive, skip local filesystem fallback entirely
        if getattr(settings, 'PREFER_ONEDRIVE', False):
            return False

        # Otherwise fall back to local files (legacy)
        local_files = get_inspection_files_local(client_name, date_str)
        if local_files and 'compliance' in local_files:
            compliance_files = local_files['compliance']
            if compliance_files and len(compliance_files) > 0:
                return True
        
        return False
    except Exception as e:
        print(f"Error checking compliance documents for {client_name}: {e}")
        return False


@login_required(login_url='login')
def delete_shipment(request, pk):
    """Delete a shipment entry."""
    clear_messages(request)
    shipment = get_object_or_404(Shipment, pk=pk)
    if request.method == 'POST':
        shipment.delete()
        messages.success(request, 'Shipment deleted successfully.')
    return redirect('shipment_list')


@login_required(login_url='login')
def edit_inspection(request, inspection_id):
    """Edit a Food Safety Agency inspection."""
    clear_messages(request)
    
    print(f"DEBUG: edit_inspection called with inspection_id: {inspection_id}")
    
    try:
        from ..models import FoodSafetyAgencyInspection, InspectorMapping
        inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id).first()
        if not inspection:
            messages.error(request, f'Inspection with ID {inspection_id} not found.')
            return redirect('shipment_list')
        print(f"DEBUG: Found inspection: {inspection.remote_id} for {inspection.client_name}")
        
        # Check if user has permission to edit this inspection
        if request.user.role == 'inspector':
            # Get the inspector ID for the current user
            inspector_id = None
            try:
                inspector_mapping = InspectorMapping.objects.get(
                    inspector_name=request.user.get_full_name() or request.user.username
                )
                inspector_id = inspector_mapping.inspector_id
            except InspectorMapping.DoesNotExist:
                try:
                    inspector_mapping = InspectorMapping.objects.get(
                        inspector_name=request.user.username
                    )
                    inspector_id = inspector_mapping.inspector_id
                except InspectorMapping.DoesNotExist:
                    inspector_id = None
            
            # Check if this inspection belongs to the current inspector
            if not inspector_id or inspection.inspector_id != inspector_id:
                messages.error(request, 'You can only edit your own inspections.')
                return redirect('shipment_list')
        
        # For admin, super_admin, financial, and scientist roles, allow editing any inspection
        # (no additional permission check needed)
        
        if request.method == 'POST':
            print(f"DEBUG: Processing POST request")
            # Handle form submission for editing inspection
            try:
                # Only update fields that won't be overwritten by server sync
                # Test result fields (these are local to our system)
                inspection.protein = 'protein_test' in request.POST
                inspection.fat = 'fat_test' in request.POST
                inspection.calcium = 'calcium_test' in request.POST
                inspection.dna = 'dna_test' in request.POST
                
                # Save the inspection
                inspection.save()
                print(f"DEBUG: Inspection saved successfully")
                messages.success(request, f"Inspection {inspection.remote_id} for {inspection.client_name} updated successfully!")
                return redirect('shipment_list')
                
            except Exception as e:
                print(f"DEBUG: Error updating inspection: {str(e)}")
                messages.error(request, f'Error updating inspection: {str(e)}')
                # Return to the form with error
                context = {
                    'inspection': inspection
                }
                return render(request, 'main/edit_inspection.html', context)
        else:
            print(f"DEBUG: Rendering edit form")
            # Render the edit form
            context = {
                'inspection': inspection
            }
            return render(request, 'main/edit_inspection.html', context)
            
    except Exception as e:
        print(f"DEBUG: Error in edit_inspection: {str(e)}")
        messages.error(request, f'Error editing inspection: {str(e)}')
        return redirect('shipment_list')

@login_required(login_url='login')
def delete_inspection(request, inspection_id):
    """Delete a Food Safety Agency inspection."""
    clear_messages(request)
    
    try:
        from ..models import FoodSafetyAgencyInspection, InspectorMapping
        inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id).first()
        if not inspection:
            messages.error(request, f'Inspection with ID {inspection_id} not found.')
            return redirect('shipment_list')
        
        # Check if user has permission to delete this inspection
        if request.user.role == 'inspector':
            # Get the inspector ID for the current user
            inspector_id = None
            try:
                inspector_mapping = InspectorMapping.objects.get(
                    inspector_name=request.user.get_full_name() or request.user.username
                )
                inspector_id = inspector_mapping.inspector_id
            except InspectorMapping.DoesNotExist:
                try:
                    inspector_mapping = InspectorMapping.objects.get(
                        inspector_name=request.user.username
                    )
                    inspector_id = inspector_mapping.inspector_id
                except InspectorMapping.DoesNotExist:
                    inspector_id = None
            
            # Check if this inspection belongs to the current inspector
            if not inspector_id or inspection.inspector_id != inspector_id:
                messages.error(request, 'You can only delete your own inspections.')
                return redirect('shipment_list')
        
        # For admin, super_admin, financial, and scientist roles, allow deleting any inspection
        # (no additional permission check needed)
        
        if request.method == 'POST':
            client_name = inspection.client_name
            inspection.delete()
            messages.success(request, f'Inspection {inspection_id} for {client_name} deleted successfully.')
        else:
            messages.error(request, 'Invalid request method.')
            
    except Exception as e:
        messages.error(request, f'Error deleting inspection: {str(e)}')
    
    return redirect('shipment_list')


@login_required(login_url='login')
def upload_document(request):
    """Handle document uploads for inspection groups and individual inspections."""
    if request.method == 'POST':
        # Check role-based restrictions for inspectors
        user_role = getattr(request.user, 'role', 'inspector')
        
        # Inspectors can only upload RFI documents
        if user_role == 'inspector':
            document_type = request.POST.get('document_type')
            allowed_document_types = ['rfi']
            if document_type not in allowed_document_types:
                return JsonResponse({
                    'success': False, 
                    'error': 'Access denied. Inspectors can only upload RFI documents.'
                })
        
        # Administrators can only upload invoice and RFI documents
        elif user_role == 'admin':
            document_type = request.POST.get('document_type')
            allowed_document_types = ['invoice', 'rfi']
            if document_type not in allowed_document_types:
                return JsonResponse({
                    'success': False, 
                    'error': 'Access denied. Administrators can only upload invoice and RFI documents.'
                })
        
        # Lab technicians can only upload lab-related documents
        elif user_role == 'scientist':
            document_type = request.POST.get('document_type')
            allowed_document_types = ['lab', 'lab_form', 'retest']
            if document_type not in allowed_document_types:
                return JsonResponse({
                    'success': False, 
                    'error': 'Access denied. Lab technicians can only upload lab results, lab forms, and retest documents.'
                })
        try:
            from ..models import FoodSafetyAgencyInspection
            from django.db import models
            import os
            from django.conf import settings
            from datetime import datetime
            import re
            
            # Get form data
            group_id = request.POST.get('group_id')
            inspection_id = request.POST.get('inspection_id')
            document_type = request.POST.get('document_type')
            inspection_number = request.POST.get('inspection_number')  # For individual inspection compliance files
            uploaded_file = request.FILES.get('file')
            
            # Debug logging
            print(f"Upload request - Group ID: '{group_id}', Inspection ID: '{inspection_id}', Document Type: '{document_type}'")
            print(f"Group ID type: {type(group_id)}, Inspection ID type: {type(inspection_id)}")
            print(f"Group ID length: {len(group_id) if group_id else 'None'}, Inspection ID length: {len(inspection_id) if inspection_id else 'None'}")
            print(f"POST data keys: {list(request.POST.keys())}")
            print(f"All POST data: {dict(request.POST)}")
            
            if not uploaded_file:
                return JsonResponse({'success': False, 'error': 'No file provided'})
            
            # RESTRICT TO PDF FILES ONLY
            file_extension = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else ''
            if file_extension != 'pdf':
                return JsonResponse({
                    'success': False, 
                    'error': f'Only PDF files are allowed. You uploaded a {file_extension.upper() if file_extension else "file without extension"}. Please convert your document to PDF and try again.'
                })
            
            # Validate file content type as additional security
            content_type = uploaded_file.content_type
            if content_type and not content_type.startswith('application/pdf'):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid file type. Only PDF documents are accepted.'
                })
            
            # Get inspection data to create proper folder structure
            if group_id:
                # Group-level upload (RFI, Invoice)
                # Parse group_id to get client name and date
                # group_id format: clientname_date (e.g., "3Amigos_20230530")
                parts = group_id.split('_')
                if len(parts) >= 2:
                    # Reconstruct client name (remove date part)
                    client_name = '_'.join(parts[:-1])
                    # Sanitize client name to match file lookup logic
                    import re
                    client_name = re.sub(r'[^a-zA-Z0-9_]', '_', client_name)
                    client_name = re.sub(r'_+', '_', client_name).strip('_')
                    date_str = parts[-1]
                    # Convert date format (e.g., 20230530 to 2023/May)
                    if len(date_str) == 8:
                        year = date_str[:4]
                        month_num = int(date_str[4:6])
                        month_name = datetime.strptime(f"2023-{month_num:02d}-01", "%Y-%m-%d").strftime("%B")
                        year_folder = year
                        month_folder = month_name
                    else:
                        year_folder = datetime.now().strftime("%Y")
                        month_folder = datetime.now().strftime("%B")
                else:
                    client_name = group_id
                    # Sanitize client name to match file lookup logic
                    import re
                    client_name = re.sub(r'[^a-zA-Z0-9_]', '_', client_name)
                    client_name = re.sub(r'_+', '_', client_name).strip('_')
                    year_folder = datetime.now().strftime("%Y")
                    month_folder = datetime.now().strftime("%B")
                
                identifier = group_id
                upload_type = 'group'
                
            elif inspection_id:
                # Individual inspection upload (Lab, Retest)
                # For lab results and retest, we should use the group's client name if available
                # to keep all documents for a group in the same folder
                if group_id and document_type in ['lab', 'lab_form', 'retest']:
                    # Use group's client name for lab results and retest to keep them organized together
                    parts = group_id.split('_')
                    if len(parts) >= 2:
                        client_name = '_'.join(parts[:-1])
                        date_str = parts[-1]
                        if len(date_str) == 8:
                            year = date_str[:4]
                            month_num = int(date_str[4:6])
                            month_name = datetime.strptime(f"2023-{month_num:02d}-01", "%Y-%m-%d").strftime("%B")
                            year_folder = year
                            month_folder = month_name
                        else:
                            year_folder = datetime.now().strftime("%Y")
                            month_folder = datetime.now().strftime("%B")
                    else:
                        client_name = group_id
                        # Sanitize client name to match file lookup logic
                        import re
                        client_name = re.sub(r'[^a-zA-Z0-9_]', '_', client_name)
                        client_name = re.sub(r'_+', '_', client_name).strip('_')
                        year_folder = datetime.now().strftime("%Y")
                        month_folder = datetime.now().strftime("%B")
                else:
                    # For other cases or when no group_id, use individual inspection's client name
                    try:
                        inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id).first()
                        if inspection:
                            client_name = inspection.client_name or "Unknown_Client"
                            if inspection.date_of_inspection:
                                year_folder = inspection.date_of_inspection.strftime("%Y")
                                month_folder = inspection.date_of_inspection.strftime("%B")
                            else:
                                year_folder = datetime.now().strftime("%Y")
                                month_folder = datetime.now().strftime("%B")
                        else:
                            client_name = "Unknown_Client"
                            year_folder = datetime.now().strftime("%Y")
                            month_folder = datetime.now().strftime("%B")
                    except:
                        client_name = "Unknown_Client"
                        year_folder = datetime.now().strftime("%Y")
                        month_folder = datetime.now().strftime("%B")
                
                identifier = inspection_id
                upload_type = 'inspection'
            else:
                return JsonResponse({'success': False, 'error': f'No group ID or inspection ID provided. Group ID: "{group_id}", Inspection ID: "{inspection_id}". Please refresh the page and try again.'})
            
            # Use original client name for folder structure (keep spaces and special characters)
            def create_folder_name(name):
                """Use original client name for folder names"""
                if not name:
                    return "Unknown Client"
                # Keep original name with spaces and special characters
                return name.strip()
            
            # Parse group_id to get the correct client name with spaces
            if group_id:
                parts = group_id.split('_')
                if len(parts) >= 2:
                    # Convert underscores back to spaces for client name
                    client_name = '_'.join(parts[:-1]).replace('_', ' ')
            
            client_folder = create_folder_name(client_name)
            
            # Create folder structure: inspection/Year/Month/client name/document_type/
            base_dir = os.path.join(settings.MEDIA_ROOT, 'inspection')
            year_dir = os.path.join(base_dir, year_folder)
            month_dir = os.path.join(year_dir, month_folder)
            client_dir = os.path.join(month_dir, client_folder)
            
            # For lab results and lab forms, create commodity-based subfolders
            if document_type in ['lab', 'lab_form'] and inspection_id:
                # Get the inspection by ID and date to ensure we get the correct one
                if group_id:
                    # Parse the date from group_id to get the correct inspection
                    parts = group_id.split('_')
                    if len(parts) >= 2:
                        date_str = parts[-1]
                        if len(date_str) == 8:
                            year = int(date_str[:4])
                            month = int(date_str[4:6])
                            day = int(date_str[6:8])
                            from datetime import date
                            group_date = date(year, month, day)
                            # Get inspection with matching remote_id AND date
                            inspection = FoodSafetyAgencyInspection.objects.filter(
                                remote_id=inspection_id,
                                date_of_inspection=group_date
                            ).first()
                        else:
                            inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id).first()
                    else:
                        inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id).first()
                else:
                    inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id).first()
                
                print(f"Debug - Inspection ID: {inspection_id}")
                print(f"Debug - Found inspection: {inspection}")
                if inspection:
                    print(f"Debug - Inspection client: {inspection.client_name}")
                    print(f"Debug - Inspection commodity: {inspection.commodity}")
                if inspection and inspection.commodity:
                    commodity = inspection.commodity.lower()
                    # Create lab results folder with commodity subfolder
                    lab_dir = os.path.join(client_dir, 'lab results')
                    document_dir = os.path.join(lab_dir, commodity)
                else:
                    # Fallback to default lab folder
                    document_dir = os.path.join(client_dir, 'lab results')
            elif document_type == 'compliance':
                # For compliance documents, create Compliance folder directly in client directory
                document_dir = os.path.join(client_dir, 'Compliance')
            else:
                # For other document types, use the standard structure
                document_dir = os.path.join(client_dir, document_type)
            
            # Create all directories
            os.makedirs(document_dir, exist_ok=True)
            
            # Log the folder structure for debugging
            print(f"Created folder structure: {document_dir}")
            print(f"Client: {client_name} -> {client_folder}")
            print(f"Year: {year_folder}, Month: {month_folder}")
            print(f"Document type: {document_type}")
            if document_type == 'lab' and inspection_id:
                inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id).first()
                if inspection and inspection.commodity:
                    print(f"Commodity: {inspection.commodity}")
            
            # Generate unique filename with timestamp
            file_extension = os.path.splitext(uploaded_file.name)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{identifier}_{document_type}_{timestamp}{file_extension}"
            
            # Log the filename for debugging
            print(f"Generated filename: {filename}")
            file_path = os.path.join(document_dir, filename)
            
            # Save file to local storage first (for OneDrive sync)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Update upload tracking in database
            from django.utils import timezone
            current_time = timezone.now()
            
            if upload_type == 'group':
                # Update all inspections in the group
                # Parse group_id to get client_name and date
                parts = group_id.split('_')
                if len(parts) >= 2:
                    # Convert underscores back to spaces for client name matching
                    client_name_from_group = '_'.join(parts[:-1]).replace('_', ' ')
                    date_str = parts[-1]
                    
                    # Convert date string to date object
                    if len(date_str) == 8:
                        try:
                            date_obj = datetime.strptime(date_str, '%Y%m%d').date()
                            
                            # Find all inspections for this client and date using exact matching
                            
                            print(f"🔍 DEBUG: Parsing group_id: {group_id}")
                            print(f"🔍 DEBUG: Client name from group: {client_name_from_group}")
                            print(f"🔍 DEBUG: Date object: {date_obj}")
                            
                            # Get all inspections for this date
                            candidate_inspections = FoodSafetyAgencyInspection.objects.filter(date_of_inspection=date_obj)
                            print(f"🔍 DEBUG: Found {candidate_inspections.count()} inspections for date {date_obj}")
                            
                            # Use exact client name matching (much more efficient)
                            matching_inspections = candidate_inspections.filter(
                                client_name=client_name_from_group
                            ).values_list('id', flat=True)
                            
                            print(f"✅ DEBUG: Found {len(matching_inspections)} matching inspections for '{client_name_from_group}'")
                            
                            # Update upload tracking fields for matching inspections
                            if matching_inspections:
                                group_inspections = FoodSafetyAgencyInspection.objects.filter(id__in=matching_inspections)
                                updated_count = 0
                                
                                if document_type == 'rfi':
                                    updated_count = group_inspections.update(
                                        rfi_uploaded_by=request.user,
                                        rfi_uploaded_date=current_time
                                    )
                                    print(f"✅ DEBUG: Updated RFI tracking for {updated_count} inspections")
                                elif document_type == 'invoice':
                                    updated_count = group_inspections.update(
                                        invoice_uploaded_by=request.user,
                                        invoice_uploaded_date=current_time
                                    )
                                    print(f"✅ DEBUG: Updated Invoice tracking for {updated_count} inspections")
                                
                                print(f"✅ Updated upload tracking for {updated_count} inspections in group {group_id}")
                                
                                # Clear only shipment list cache to ensure updated data is shown
                                from django.core.cache import cache
                                # Clear specific cache keys instead of all cache to avoid session issues
                                cache.delete(f"shipment_list_{request.user.id}_{request.user.role}")
                                cache.delete("filter_options")
                                # Clear file status cache for this client
                                # Construct inspection_date from group_id for cache clearing
                                if len(parts) >= 2 and len(parts[-1]) == 8:
                                    date_str = parts[-1]
                                    inspection_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                                    cache.delete(f"file_status_{client_name}_{inspection_date}")
                                print(f"🧹 Cleared shipment list cache after upload tracking update")
                                
                            else:
                                print(f"⚠️ No matching inspections found for group {group_id}")
                                print(f"⚠️ DEBUG: Available client names on {date_obj}:")
                                for inspection in candidate_inspections:
                                    print(f"   - '{inspection.client_name}'")
                                print(f"⚠️ DEBUG: Looking for client name: '{client_name_from_group}'")
                                
                        except ValueError:
                            print(f"⚠️ Could not parse date from group_id: {date_str}")
            
            elif upload_type == 'individual' and inspection_id:
                # Update individual inspection
                inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id).first()
                if inspection:
                    if document_type == 'rfi':
                        inspection.rfi_uploaded_by = request.user
                        inspection.rfi_uploaded_date = current_time
                        inspection.save(update_fields=['rfi_uploaded_by', 'rfi_uploaded_date'])
                        print(f"✅ DEBUG: Updated RFI tracking for individual inspection {inspection_id}")
                    elif document_type == 'invoice':
                        inspection.invoice_uploaded_by = request.user
                        inspection.invoice_uploaded_date = current_time
                        inspection.save(update_fields=['invoice_uploaded_by', 'invoice_uploaded_date'])
                        print(f"✅ DEBUG: Updated Invoice tracking for individual inspection {inspection_id}")
                    
                    # Clear cache after individual upload
                    from django.core.cache import cache
                    cache.delete(f"shipment_list_{request.user.id}_{request.user.role}")
                    cache.delete("filter_options")
                    # Clear file status cache for this client
                    cache.delete(f"file_status_{client_name}_{inspection_date}")
                    print(f"🧹 Cleared cache after individual upload tracking update")
            
            # Note: OneDrive sync is handled by the scheduled sync service after the configured delay period
            # Files are only uploaded to OneDrive after inspections are marked as "sent" and the delay period has passed
            print(f"📁 File saved locally: {filename} (OneDrive sync will occur after delay period)")
            
            # Log the file upload to system logs
            try:
                from ..models import SystemLog
                
                # Get client IP address
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip_address = x_forwarded_for.split(',')[0]
                else:
                    ip_address = request.META.get('REMOTE_ADDR')
                
                # Prepare log details
                log_details = {
                    'filename': uploaded_file.name,
                    'file_size': uploaded_file.size,
                    'document_type': document_type.upper(),
                    'upload_type': upload_type,
                    'file_path': file_path
                }
                
                if upload_type == 'group':
                    log_description = f"Uploaded {document_type.upper()} file '{uploaded_file.name}' for inspection group {group_id}"
                    log_details['group_id'] = group_id
                else:
                    log_description = f"Uploaded {document_type.upper()} file '{uploaded_file.name}' for inspection {inspection_id}"
                    log_details['inspection_id'] = inspection_id
                
                SystemLog.log_activity(
                    user=request.user,
                    action='FILE_UPLOAD',
                    page=request.path,
                    object_type='inspection_document',
                    object_id=group_id or inspection_id,
                    description=log_description,
                    details=log_details,
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
            except Exception as log_error:
                print(f"⚠️ Error logging file upload: {log_error}")
            
            # Return success message with user's first name
            user_first_name = request.user.first_name or request.user.username
            if upload_type == 'group':
                message = f'{document_type.upper()} uploaded successfully by {user_first_name} for group {group_id}'
            else:
                message = f'{document_type.upper()} uploaded successfully by {user_first_name} for inspection {inspection_id}'
            
            return JsonResponse({
                'success': True, 
                'message': message,
                'filename': filename,
                'file_path': file_path
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required(login_url='login')
def list_uploaded_files(request):
    """List uploaded files for a given inspection or group."""
    if request.method == 'GET':
        try:
            from ..models import FoodSafetyAgencyInspection
            import os
            from django.conf import settings
            from datetime import datetime
            
            group_id = request.GET.get('group_id')
            inspection_id = request.GET.get('inspection_id')
            
            if not group_id and not inspection_id:
                return JsonResponse({'success': False, 'error': f'No group ID or inspection ID provided. Group ID: "{group_id}", Inspection ID: "{inspection_id}". Please refresh the page and try again.'})
            
            # Get inspection data to determine folder path
            if group_id:
                # Parse group_id to get client name and date
                parts = group_id.split('_')
                if len(parts) >= 2:
                    # Reconstruct the original client name from group_id
                    # Group ID format: "Client_Name_20250912" -> Client Name
                    client_name_from_group = '_'.join(parts[:-1])
                    date_str = parts[-1]
                    
                    # Convert the group_id client name back to original format
                    # The sanitize_group_id function converts "Boxer - Heidedal" to "Boxer_Heidedal"
                    # So we need to convert it back to the original format
                    # Try different variations to find the actual folder name
                    possible_names = [
                        client_name_from_group.replace('_', ' - '),  # "Boxer - Heidedal" (most common)
                        client_name_from_group.replace('_', ' '),    # "Boxer Heidedal"
                        client_name_from_group.replace('_', '-'),    # "Boxer-Heidedal"
                        client_name_from_group,                      # "Boxer_Heidedal"
                    ]
                    
                    # We'll try to find the actual folder name by checking what exists
                    # For now, use the most likely format (with dashes)
                    original_client_name = possible_names[0]  # "Boxer - Heidedal"
                    
                    if len(date_str) == 8:
                        year = date_str[:4]
                        month_num = int(date_str[4:6])
                        month_name = datetime.strptime(f"2023-{month_num:02d}-01", "%Y-%m-%d").strftime("%B")
                        year_folder = year
                        month_folder = month_name
                    else:
                        year_folder = datetime.now().strftime("%Y")
                        month_folder = datetime.now().strftime("%B")
                else:
                    original_client_name = group_id
                    year_folder = datetime.now().strftime("%Y")
                    month_folder = datetime.now().strftime("%B")
                
                # Now create the proper folder variations using the original client name
                client_name = original_client_name
                
            else:
                # Individual inspection
                inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id).first()
                if inspection:
                    client_name = inspection.client_name or "Unknown_Client"
                    if inspection.date_of_inspection:
                        year_folder = inspection.date_of_inspection.strftime("%Y")
                        month_folder = inspection.date_of_inspection.strftime("%B")
                    else:
                        year_folder = datetime.now().strftime("%Y")
                        month_folder = datetime.now().strftime("%B")
                else:
                    client_name = "Unknown_Client"
                    year_folder = datetime.now().strftime("%Y")
                    month_folder = datetime.now().strftime("%B")
                
            # Use exact client name since folders now use original names
            import re
            parent_path = os.path.join(settings.MEDIA_ROOT, 'inspection', year_folder, month_folder)
            client_folder_variations = [client_name]
            
            # List files in document type folders (checking multiple folder variations)
            files_list = {}
            seen_files = set()  # Track files to avoid duplicates
            
            # Check all folder variations for files
            for folder_variation in client_folder_variations:
                test_path = os.path.join(parent_path, folder_variation)
                if not os.path.exists(test_path):
                    continue
                
                print(f"🔍 [DEBUG] Checking folder: {test_path}")
                
                # Check traditional document folders first (where files are actually uploaded)
                traditional_docs = ['rfi', 'invoice', 'lab', 'lab_form', 'retest']
                for doc_type in traditional_docs:
                    doc_path = os.path.join(test_path, doc_type)
                    if os.path.exists(doc_path):
                        print(f"🔍 [DEBUG] Found {doc_type} folder at: {doc_path}")
                        files = []
                        for filename in os.listdir(doc_path):
                            if os.path.isfile(os.path.join(doc_path, filename)):
                                file_path = os.path.join(doc_path, filename)
                                file_size = os.path.getsize(file_path)
                                
                                # Create unique key to avoid duplicates
                                unique_key = (filename, file_size, os.path.getmtime(file_path))
                                if unique_key not in seen_files:
                                    seen_files.add(unique_key)
                                    file_info = get_file_info(file_path, doc_type)
                                    files.append(file_info)
                                    print(f"✅ Added unique file: {filename}")
                                else:
                                    print(f"⚠️ Skipped duplicate file: {filename}")
                        
                        if files:
                            if doc_type not in files_list:
                                files_list[doc_type] = []
                            files_list[doc_type].extend(files)
                
                # Also check nested Inspection-XXXX folders for files
                try:
                    for item in os.listdir(test_path):
                        if item.startswith('Inspection-') and os.path.isdir(os.path.join(test_path, item)):
                            inspection_folder = os.path.join(test_path, item)
                            print(f"🔍 [DEBUG] Checking nested folder: {item}")
                            
                            # Check each document type in the nested folder
                            for doc_type in traditional_docs:
                                nested_doc_path = os.path.join(inspection_folder, doc_type)
                                if os.path.exists(nested_doc_path):
                                    print(f"🔍 [DEBUG] Found nested {doc_type} folder at: {nested_doc_path}")
                                    files = []
                                    for filename in os.listdir(nested_doc_path):
                                        if os.path.isfile(os.path.join(nested_doc_path, filename)):
                                            file_path = os.path.join(nested_doc_path, filename)
                                            file_size = os.path.getsize(file_path)
                                            
                                            # Create unique key to avoid duplicates
                                            unique_key = (filename, file_size, os.path.getmtime(file_path))
                                            if unique_key not in seen_files:
                                                seen_files.add(unique_key)
                                                file_info = get_file_info(file_path, f'{item}/{doc_type}')
                                                files.append(file_info)
                                                print(f"✅ Added unique nested file: {filename}")
                                            else:
                                                print(f"⚠️ Skipped duplicate nested file: {filename}")
                                    
                                    if files:
                                        if doc_type not in files_list:
                                            files_list[doc_type] = []
                                        files_list[doc_type].extend(files)
                            
                            # Check compliance folder in nested folder
                            nested_compliance_path = os.path.join(inspection_folder, 'Compliance')
                            if os.path.exists(nested_compliance_path):
                                print(f"🔍 [DEBUG] Found nested Compliance folder at: {nested_compliance_path}")
                                compliance_files = []
                                try:
                                    # Check for any commodity folders
                                    for commodity_folder in os.listdir(nested_compliance_path):
                                        commodity_path = os.path.join(nested_compliance_path, commodity_folder)
                                        if os.path.isdir(commodity_path):
                                            for filename in os.listdir(commodity_path):
                                                if os.path.isfile(os.path.join(commodity_path, filename)):
                                                    file_path = os.path.join(commodity_path, filename)
                                                    file_size = os.path.getsize(file_path)
                                                    
                                                    # Create unique key to avoid duplicates
                                                    unique_key = (filename, file_size, os.path.getmtime(file_path))
                                                    if unique_key not in seen_files:
                                                        seen_files.add(unique_key)
                                                        file_info = get_file_info(file_path, f'{item}/Compliance/{commodity_folder}')
                                                        compliance_files.append(file_info)
                                                        print(f"✅ Added unique nested compliance file: {filename}")
                                                    else:
                                                        print(f"⚠️ Skipped duplicate nested compliance file: {filename}")
                                except (OSError, PermissionError):
                                    print(f"⚠️ Error accessing nested compliance folder: {nested_compliance_path}")
                                    continue
                                
                                if compliance_files:
                                    if 'compliance' not in files_list:
                                        files_list['compliance'] = []
                                    files_list['compliance'].extend(compliance_files)
                except (OSError, PermissionError):
                    print(f"⚠️ Error accessing nested folders in: {test_path}")
            
            # Also check for compliance documents in the new folder structure
            for folder_variation in client_folder_variations:
                test_path = os.path.join(parent_path, folder_variation)
                if not os.path.exists(test_path):
                    continue
                
                compliance_path = os.path.join(test_path, 'Compliance')
                if os.path.exists(compliance_path):
                    print(f"🔍 [DEBUG] Found compliance folder at: {compliance_path}")
                    
                    # Get all commodity subfolders
                    for commodity_folder in os.listdir(compliance_path):
                        commodity_path = os.path.join(compliance_path, commodity_folder)
                        
                        if os.path.isdir(commodity_path):
                            print(f"Checking commodity folder: {commodity_folder}")
                            
                            # List all files in this commodity folder
                            files = []
                            for filename in os.listdir(commodity_path):
                                if os.path.isfile(os.path.join(commodity_path, filename)):
                                    file_path = os.path.join(commodity_path, filename)
                                    file_size = os.path.getsize(file_path)
                                    
                                    # Create unique key to avoid duplicates
                                    unique_key = (filename, file_size, os.path.getmtime(file_path))
                                    if unique_key not in seen_files:
                                        seen_files.add(unique_key)
                                        
                                        # Determine document type based on filename or folder
                                        doc_type = 'compliance'
                                        if 'rfi' in filename.lower():
                                            doc_type = 'rfi'
                                        elif 'invoice' in filename.lower():
                                            doc_type = 'invoice'
                                        elif 'lab' in filename.lower():
                                            doc_type = 'lab'
                                        elif 'retest' in filename.lower():
                                            doc_type = 'retest'
                                        
                                        file_info = get_file_info(file_path, doc_type)
                                        file_info['commodity'] = commodity_folder
                                        files.append(file_info)
                                        print(f"✅ Added compliance file: {filename}")
                            
                            if files:
                                if 'compliance' not in files_list:
                                    files_list['compliance'] = []
                                files_list['compliance'].extend(files)
                                print(f"Found {len(files)} compliance files in {commodity_folder}")
            
            # Log the results for debugging
            print(f"Files found for {inspection_id or group_id}: {files_list}")
            print(f"Group ID: {group_id}, Inspection ID: {inspection_id}")
            print(f"Parent path: {parent_path}")
            
            return JsonResponse({
                'success': True,
                'files': files_list,
                'base_path': parent_path
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required(login_url='login')
def edit_shipment(request, pk):
    """Edit an existing shipment."""
    clear_messages(request)
    shipment = get_object_or_404(Shipment, pk=pk)
    clients = Client.objects.all().order_by('name')
    
    # Check if this is a cancel/keep original request
    if request.method == 'POST' and 'keep_original' in request.POST:
        messages.info(request, 'No changes were made to the shipment.')
        return redirect('shipment_list')
    
    if request.method == 'POST':
        # For now, just redirect since we don't have the ShipmentForm
        messages.info(request, 'Edit functionality will be implemented with proper form.')
        return redirect('shipment_list')
    else:
        # For now, just show the shipment details
        return render(request, 'main/edit_shipment.html', {
            'shipment': shipment,
            'clients': clients
        })






def apply_inspection_filters(request, inspections):
    """Apply filters to the inspections queryset based on request parameters."""
    
    # Filter by inspection number
    inspection_no = request.GET.get('claim_no')  # Keep same parameter name for template compatibility
    if inspection_no:
        inspections = inspections.filter(inspection_number__icontains=inspection_no)
    
    # Filter by client name
    client_name = request.GET.get('client')
    if client_name:
        inspections = inspections.filter(facility_client_name__icontains=client_name)
    
    # Filter by inspector
    inspector = request.GET.get('branch')  # Keep same parameter name for template compatibility
    if inspector:
        inspections = inspections.filter(inspector__icontains=inspector)
    
    # Filter by inspection date range
    inspection_date_from = request.GET.get('inspection_date_from')
    if inspection_date_from:
        inspections = inspections.filter(inspection_date__gte=inspection_date_from)
    
    inspection_date_to = request.GET.get('inspection_date_to')
    if inspection_date_to:
        inspections = inspections.filter(inspection_date__lte=inspection_date_to)
    
    return inspections


def apply_fsa_inspection_filters(request, inspections):
    """Apply filters to the Food Safety Agency inspections queryset based on request parameters."""
    
    # Filter by inspection number (remote_id)
    inspection_no = request.GET.get('claim_no')  # Keep same parameter name for template compatibility
    if inspection_no:
        inspections = inspections.filter(remote_id__icontains=inspection_no)
    
    # Filter by client name
    client_name = request.GET.get('client')
    if client_name:
        inspections = inspections.filter(client_name__icontains=client_name)
    
    # Filter by inspector
    inspector = request.GET.get('branch')  # Keep same parameter name for template compatibility
    if inspector:
        inspections = inspections.filter(inspector_name__icontains=inspector)
    
    # Filter by inspection date range
    inspection_date_from = request.GET.get('inspection_date_from')
    if inspection_date_from:
        inspections = inspections.filter(date_of_inspection__gte=inspection_date_from)
    
    inspection_date_to = request.GET.get('inspection_date_to')
    if inspection_date_to:
        inspections = inspections.filter(date_of_inspection__lte=inspection_date_to)
    
    # Note: Sent status filtering is now handled at the group level in shipment_list view
    # to properly show groups that contain sent/unsent inspections
    
    return inspections


def apply_client_filters(request, clients):
    """Apply filters to the clients queryset based on request parameters."""
    
    # Filter by client ID
    client_id = request.GET.get('client_id')
    if client_id:
        clients = clients.filter(client_id__icontains=client_id)
    
    # Filter by client name
    client_name = request.GET.get('client')
    if client_name:
        clients = clients.filter(name__icontains=client_name)
    
    # Filter by account code
    account_code = request.GET.get('account_code')
    if account_code:
        clients = clients.filter(internal_account_code__icontains=account_code)
    
    # Filter by date range (using created_at field)
    date_from = request.GET.get('date_from')
    if date_from:
        clients = clients.filter(created_at__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        clients = clients.filter(created_at__lte=date_to)
    
    # Filter by status - since Client model doesn't have is_active field,
    # we'll filter by email presence as a proxy for "active" status
    status = request.GET.get('status')
    if status:
        if status == 'active':
            # Clients with email are considered "active"
            clients = clients.filter(
                models.Q(email__isnull=False) | models.Q(manual_email__isnull=False)
            ).exclude(email='').exclude(manual_email='')
        elif status == 'inactive':
            # Clients without email are considered "inactive"
            clients = clients.filter(
                models.Q(email__isnull=True) | models.Q(email=''),
                models.Q(manual_email__isnull=True) | models.Q(manual_email='')
            )
    
    return clients


# =============================================================================
# GOOGLE SHEETS INTEGRATION VIEWS
# =============================================================================


@login_required(login_url='login')
def client_allocation(request):
    """Client allocation view with local database clients."""
    clear_messages(request)
    
    try:
        from ..models import Client
        
        # Get clients from local database
        clients = Client.objects.all().order_by('name')
        
        # Apply comprehensive filters
        clients = apply_client_filters(request, clients)
        
        # Get total count before pagination
        total_clients = clients.count()
        
        # Check if user wants to see all clients
        show_all = request.GET.get('show_all', 'false').lower() == 'true'
        
        if show_all:
            # Show all clients without pagination
            clients_list = list(clients)
            page_obj = None
        else:
            # Use pagination
            from django.core.paginator import Paginator
            paginator = Paginator(clients, 25)  # Show 25 clients per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            clients_list = page_obj
        
        context = {
            'clients': clients_list,
            'page_obj': page_obj,
            'total_clients': total_clients,
            'show_all': show_all,
            'error': None
        }
        
    except Exception as e:
        context = {
            'clients': [],
            'page_obj': None,
            'total_clients': 0,
            'show_all': False,
            'error': f'Error fetching data: {str(e)}'
        }
    
    return render(request, 'main/client_allocation.html', context)


@login_required(login_url='login')
def refresh_clients(request):
    """Refresh the Food Safety Agency clients table with fresh data from Google Sheets."""
    clear_messages(request)
    
    if request.method == 'POST':
        print("\n" + "="*60)
        print("🔄 STARTING CLIENT SYNC OPERATION")
        print("="*60)
        
        try:
            from ..services.google_sheets_service import GoogleSheetsService
            
            print("📋 Step 1: Initializing Google Sheets Service...")
            sheets_service = GoogleSheetsService()
            print("✅ Google Sheets Service initialized successfully")
            
            print("\n📊 Step 2: Starting client table refresh...")
            
            # Force session save before long operation
            request.session.save()
            
            refresh_result = sheets_service.refresh_clients_table(request)

            # Detect AJAX request
            is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

            if refresh_result.get('success'):
                print(f"✅ CLIENT SYNC COMPLETED SUCCESSFULLY!")
                print(f"   📈 Deleted: {refresh_result['deleted_count']} old clients")
                print(f"   📈 Created: {refresh_result['clients_created']} new clients")
                print(f"   📈 Processed: {refresh_result['total_processed']} total rows from Google Sheets")

                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': True,
                        'message': f"Successfully synced clients! Deleted {refresh_result['deleted_count']} old clients and created {refresh_result['clients_created']} new clients from Google Sheets."
                    })
                else:
                    from django.contrib import messages
                    messages.success(request, f"Clients synced. Deleted {refresh_result['deleted_count']} old, created {refresh_result['clients_created']} new. Processed {refresh_result['total_processed']} rows.")
                    return redirect('client_allocation')
            else:
                print(f"❌ CLIENT SYNC FAILED!")
                print(f"   Error: {refresh_result.get('error', 'Unknown error')}")

                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'error': refresh_result.get('error', 'Unknown error')
                    })
                else:
                    from django.contrib import messages
                    messages.error(request, f"Client sync failed: {refresh_result.get('error', 'Unknown error')}")
                    return redirect('client_allocation')
                
        except Exception as e:
            print(f"❌ CLIENT SYNC EXCEPTION!")
            print(f"   Exception: {str(e)}")
            
            # Return JSON response for AJAX
            from django.http import JsonResponse
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        
        print("="*60)
        print("🔄 CLIENT SYNC OPERATION ENDED")
        print("="*60 + "\n")
    
    # If not POST, redirect back to client allocation page
    return redirect('client_allocation')


@login_required(login_url='login')
def refresh_inspections(request):
    """Refresh the Food Safety Agency inspections table with fresh data from SQL Server."""
    try:
        # Block administrators from accessing sync functionality
        if request.user.role == 'admin':
            messages.error(request, "Access denied. Administrators cannot sync inspections.")
            return redirect('home')
        
        clear_messages(request)
        
        # Ensure session is valid but don't modify it during long operations
        if not request.session.session_key:
            request.session.create()
        
        # Don't modify session during long operations to avoid cache conflicts
        # The session will be preserved as-is during the sync
        
        if request.method == 'POST':
            # For AJAX requests, return immediately and run sync in background
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                from django.core.cache import cache
                import threading
                
                # Store user info before starting background operation to avoid session issues
                user_id = request.user.id
                user_role = getattr(request.user, 'role', 'user')
                
                # Don't modify session for AJAX requests to avoid conflicts with middleware
                # The middleware will handle session timeout automatically
                
                # Start sync in background thread
                def run_sync():
                    try:
                        # Set a flag to prevent session modifications during sync
                        request._sync_in_progress = True
                        print("\n" + "="*60)
                        print("🔍 STARTING INSPECTION SYNC OPERATION (BACKGROUND)")
                        print("="*60)
                        
                        from ..services.google_sheets_service import GoogleSheetsService
                        
                        print("📋 Step 1: Initializing Google Sheets Service...")
                        sheets_service = GoogleSheetsService()
                        print("✅ Google Sheets Service initialized successfully")
                        
                        print("\n📊 Step 2: Starting inspection table refresh from SQL Server...")
                        refresh_result = sheets_service.populate_inspections_table(request)
                        
                        if refresh_result.get('success'):
                            print(f"✅ INSPECTION SYNC COMPLETED SUCCESSFULLY!")
                            print(f"   📈 Deleted: {refresh_result['deleted_count']} old inspections")
                            print(f"   📈 Created: {refresh_result['inspections_created']} new inspections")
                            print(f"   📈 Processed: {refresh_result['total_processed']} total records from SQL Server")
                            
                            # Clear cache to ensure fresh data is displayed
                            cache.clear()
                            print("   🗑️  Cache cleared to ensure fresh data display")
                            
                            # Store result in cache for frontend to check
                            cache.set('sync_result', {
                                'success': True,
                                'message': f'Successfully synced {refresh_result["inspections_created"]} inspections!',
                                'deleted_count': refresh_result['deleted_count'],
                                'created_count': refresh_result['inspections_created'],
                                'total_processed': refresh_result['total_processed']
                            }, 300)  # 5 minutes
                        else:
                            print(f"❌ INSPECTION SYNC FAILED!")
                            print(f"   Error: {refresh_result.get('error', 'Unknown error')}")
                            
                            # Store error in cache
                            cache.set('sync_result', {
                                'success': False,
                                'error': refresh_result.get('error', 'Unknown error')
                            }, 300)
                            
                    except Exception as e:
                        print(f"❌ INSPECTION SYNC EXCEPTION!")
                        print(f"   Exception: {str(e)}")
                        
                        # Store error in cache
                        cache.set('sync_result', {
                            'success': False,
                            'error': f'Error syncing inspections: {str(e)}'
                        }, 300)
                        
                    print("="*60)
                    print("🔍 INSPECTION SYNC OPERATION ENDED")
                    print("="*60 + "\n")
                
                # Start background thread
                thread = threading.Thread(target=run_sync)
                thread.daemon = True
                thread.start()
                
                # Return immediately
                return JsonResponse({
                    'success': True,
                    'message': 'Sync started in background. Please wait...',
                    'status': 'started'
                })
        
        # For non-AJAX requests, run sync normally
        print("\n" + "="*60)
        print("🔍 STARTING INSPECTION SYNC OPERATION")
        print("="*60)
        
        try:
            # Don't modify session expiry here to avoid conflicts with middleware
            # The middleware will handle session timeout automatically
            
            from ..services.google_sheets_service import GoogleSheetsService
            
            print("📋 Step 1: Initializing Google Sheets Service...")
            sheets_service = GoogleSheetsService()
            print("✅ Google Sheets Service initialized successfully")
            
            print("\n📊 Step 2: Starting inspection table refresh from SQL Server...")
            refresh_result = sheets_service.populate_inspections_table(request)
            
            if refresh_result.get('success'):
                print(f"✅ INSPECTION SYNC COMPLETED SUCCESSFULLY!")
                print(f"   📈 Deleted: {refresh_result['deleted_count']} old inspections")
                print(f"   📈 Created: {refresh_result['inspections_created']} new inspections")
                print(f"   📈 Processed: {refresh_result['total_processed']} total records from SQL Server")
                
                # Clear cache to ensure fresh data is displayed
                from django.core.cache import cache
                cache.clear()
                print("   🗑️  Cache cleared to ensure fresh data display")
                
                # Store messages in cache instead of session to avoid session conflicts
                from django.core.cache import cache
                cache.set('sync_success_message', f"Successfully synced inspections!", 300)  # 5 minutes
                cache.set('sync_info_message_1', f"Deleted {refresh_result['deleted_count']} old inspections and created {refresh_result['inspections_created']} new inspections from SQL Server.", 300)
                cache.set('sync_info_message_2', f"Processed {refresh_result['total_processed']} total records from SQL Server.", 300)
                
                # Return JSON response for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    response = JsonResponse({
                        'success': True,
                        'message': f'Successfully synced {refresh_result["inspections_created"]} inspections!',
                        'deleted_count': refresh_result['deleted_count'],
                        'created_count': refresh_result['inspections_created'],
                        'total_processed': refresh_result['total_processed']
                    })
                    # Prevent session save to avoid Redis conflicts
                    response._session_save = False
                    # Mark session as not modified to prevent save attempts
                    request.session.modified = False
                    return response
                
                # Redirect to inspections page after successful sync
                # Mark session as not modified to prevent save attempts
                request.session.modified = False
                return redirect('shipment_list')
            else:
                print(f"❌ INSPECTION SYNC FAILED!")
                print(f"   Error: {refresh_result.get('error', 'Unknown error')}")
                messages.error(request, f"Error syncing inspections: {refresh_result.get('error', 'Unknown error')}")
                
                # Return JSON response for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'error': refresh_result.get('error', 'Unknown error')
                    })
                
                # Redirect back to inspections page with error message
                return redirect('shipment_list')
                
        except Exception as e:
            print(f"❌ INSPECTION SYNC EXCEPTION!")
            print(f"   Exception: {str(e)}")
            messages.error(request, f"Error syncing inspections: {str(e)}")
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'error': f'Error syncing inspections: {str(e)}'
                })
            
            # Redirect back to inspections page with error message
            return redirect('shipment_list')
        
        print("="*60)
        print("🔍 INSPECTION SYNC OPERATION ENDED")
        print("="*60 + "\n")
        
        # If not POST, redirect back to shipment list page
        return redirect('shipment_list')
        
    except Exception as e:
        # Handle session interruption and other errors gracefully
        if 'SessionInterrupted' in str(type(e).__name__) or 'session' in str(e).lower():
            print(f"⚠️ Session interrupted: {e}")
            messages.warning(request, "Session was interrupted during sync. Please try again.")
            return redirect('shipment_list')
        elif 'UpdateError' in str(type(e).__name__):
            print(f"⚠️ Cache update error: {e}")
            messages.warning(request, "Cache error occurred. Please try again.")
            return redirect('shipment_list')
        else:
            print(f"❌ Unexpected error in refresh_inspections: {e}")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('shipment_list')


def check_sync_status(request):
    """Check the status of a background sync operation."""
    from django.http import JsonResponse
    from django.core.cache import cache
    
    if request.method == 'GET':
        sync_result = cache.get('sync_result')
        if sync_result:
            # Clear the result after retrieving it
            cache.delete('sync_result')
            return JsonResponse(sync_result)
        else:
            return JsonResponse({
                'success': False,
                'status': 'running',
                'message': 'Sync is still running...'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required(login_url='login')
def refresh_shipments(request):
    """Refresh the shipments table with fresh data from SQL Server."""
    clear_messages(request)
    
    if request.method == 'POST':
        print("\n" + "="*60)
        print("📦 STARTING SHIPMENT SYNC OPERATION")
        print("="*60)
        
        try:
            from ..services.google_sheets_service import GoogleSheetsService
            
            print("📋 Step 1: Initializing Google Sheets Service...")
            sheets_service = GoogleSheetsService()
            print("✅ Google Sheets Service initialized successfully")
            
            print("\n📊 Step 2: Starting shipment table refresh from SQL Server...")
            refresh_result = sheets_service.populate_shipments_table(request)
            
            if refresh_result.get('success'):
                print(f"✅ SHIPMENT SYNC COMPLETED SUCCESSFULLY!")
                print(f"   📈 Deleted: {refresh_result['deleted_count']} old shipments")
                print(f"   📈 Created: {refresh_result['shipments_created']} new shipments")
                print(f"   📈 Processed: {refresh_result['total_processed']} total records from SQL Server")
                
                messages.success(request, f"Successfully refreshed shipments table!")
                messages.info(request, f"Deleted {refresh_result['deleted_count']} old shipments and created {refresh_result['shipments_created']} new shipments from SQL Server.")
                messages.info(request, f"Processed {refresh_result['total_processed']} total records from SQL Server.")
            else:
                print(f"❌ SHIPMENT SYNC FAILED!")
                print(f"   Error: {refresh_result.get('error', 'Unknown error')}")
                messages.error(request, f"Error refreshing shipments: {refresh_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ SHIPMENT SYNC EXCEPTION!")
            print(f"   Exception: {str(e)}")
            messages.error(request, f"Error refreshing shipments: {str(e)}")
        
        print("="*60)
        print("📦 SHIPMENT SYNC OPERATION ENDED")
        print("="*60 + "\n")
    
    # Redirect back to shipments page
    return redirect('shipment_list')


def google_oauth_callback(request):
    """Handle OAuth callback from Google"""
    from django.http import HttpResponse
    
    # Get the authorization code from the URL
    code = request.GET.get('code')
    
    if code:
        # Store the code in session for the service to use
        request.session['google_auth_code'] = code
        
        # Redirect to client allocation page with success message
        from django.contrib import messages
        messages.success(request, 'Google authentication successful! You can now fetch data.')
        return redirect('client_allocation')
    else:
        # Handle error
        from django.contrib import messages
        messages.error(request, 'Google authentication failed. No authorization code received.')
        return redirect('client_allocation')


# =============================================================================
# DASHBOARD VIEWS
# =============================================================================

@login_required(login_url='login')
def dashboard(request):
    """Main dashboard view."""
    clear_messages(request)
    
    # Get system settings for theme - matching user_management approach
    try:
        from ..models import Settings
        system_settings = Settings.objects.first()
        if not system_settings:
            system_settings = Settings.objects.create()
        
        settings = type('Settings', (), {
            'dark_mode': system_settings.dark_mode,
        })()
    except Exception:
        settings = type('Settings', (), {'dark_mode': False})()
    
    # Handle theme saving via AJAX
    if request.method == 'POST' and request.POST.get('action') == 'save_theme':
        try:
            system_settings.dark_mode = 'theme_mode' in request.POST
            system_settings.save()
            
            # Log the activity
            try:
                SystemLog.log_activity(
                    user=request.user,
                    action='SETTINGS',
                    page=request.path,
                    description='Updated theme setting from dashboard',
                    details={'dark_mode': system_settings.dark_mode}
                )
            except Exception:
                pass
                
            return JsonResponse({'success': True, 'theme': 'dark' if system_settings.dark_mode else 'light'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Get summary statistics from the correct models
    total_clients = Client.objects.count()
    total_inspections = FoodSafetyAgencyInspection.objects.count()
    
    # Get recent inspections from FoodSafetyAgencyInspection
    recent_inspections = FoodSafetyAgencyInspection.objects.order_by('-created_at')[:5]
    
    # Get inspections by inspector from FoodSafetyAgencyInspection
    inspector_stats = FoodSafetyAgencyInspection.objects.values('inspector_name').annotate(
        count=models.Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'total_clients': total_clients,
        'total_inspections': total_inspections,
        'recent_inspections': recent_inspections,
        'inspector_stats': inspector_stats,
        'settings': settings
    }
    
    return render(request, 'main/dashboard.html', context)


@login_required(login_url='login')
@inspector_only_inspections
def home(request):
    """Home page view that requires login."""
    clear_messages(request)
    
    # Redirect administrators to inspection page since they're not allowed on home page
    if request.user.role == 'admin':
        messages.info(request, "Administrators are redirected to the inspection page.")
        return redirect('shipment_list')
    
    # Get system settings for theme - matching dashboard approach
    try:
        from ..models import Settings
        system_settings = Settings.objects.first()
        if not system_settings:
            system_settings = Settings.objects.create()
        
        settings = type('Settings', (), {
            'dark_mode': system_settings.dark_mode,
        })()
    except Exception:
        settings = type('Settings', (), {'dark_mode': False})()
    
    # Handle theme saving via AJAX
    if request.method == 'POST' and request.POST.get('action') == 'save_theme':
        try:
            system_settings.dark_mode = 'theme_mode' in request.POST
            system_settings.save()
            
            # Log the activity
            try:
                SystemLog.log_activity(
                    user=request.user,
                    action='SETTINGS',
                    page=request.path,
                    description='Updated theme setting from home',
                    details={'dark_mode': system_settings.dark_mode}
                )
            except Exception:
                pass
                
            return JsonResponse({'success': True, 'theme': 'dark' if system_settings.dark_mode else 'light'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Get summary statistics from the correct models
    total_clients = Client.objects.count()
    total_inspections = FoodSafetyAgencyInspection.objects.count()
    
    # Get recent inspections from FoodSafetyAgencyInspection
    recent_inspections = FoodSafetyAgencyInspection.objects.order_by('-created_at')[:5]
    
    # Get inspections by inspector from FoodSafetyAgencyInspection
    inspector_stats = FoodSafetyAgencyInspection.objects.values('inspector_name').annotate(
        count=models.Count('id')
    ).order_by('-count')[:5]
    
    # Get system status
    def check_database_status():
        """Check PostgreSQL database connectivity"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return True if result else False
        except Exception:
            return False
    
    def check_sql_server_status():
        """Check SQL Server database connectivity"""
        try:
            from django.db import connections
            with connections['sql_server'].cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return True if result else False
        except Exception:
            return False
    
    def check_google_sheets_status():
        """Check Google Sheets API connectivity"""
        try:
            from ..services.google_sheets_service import GoogleSheetsService
            service = GoogleSheetsService()
            # Try to authenticate without user interaction
            if os.path.exists(service.token_path):
                with open(service.token_path, 'rb') as token:
                    import pickle
                    creds = pickle.load(token)
                    if creds and creds.valid:
                        return True
            return False
        except Exception:
            return False
    
    
    def get_last_sync_status():
        """Get last sync status"""
        try:
            latest_inspection = FoodSafetyAgencyInspection.objects.order_by('-created_at').first()
            if latest_inspection:
                now = timezone.now()
                created_at = latest_inspection.created_at
                
                # Handle timezone-aware datetime comparison
                if timezone.is_aware(created_at) and not timezone.is_aware(now):
                    now = timezone.make_aware(now)
                elif not timezone.is_aware(created_at) and timezone.is_aware(now):
                    created_at = timezone.make_aware(created_at)
                
                time_diff = now - created_at
                if time_diff.total_seconds() < 3600:  # Less than 1 hour
                    return "Just now"
                elif time_diff.total_seconds() < 86400:  # Less than 1 day
                    hours = int(time_diff.total_seconds() / 3600)
                    return f"{hours} hour{'s' if hours > 1 else ''} ago"
                else:
                    days = int(time_diff.total_seconds() / 86400)
                    return f"{days} day{'s' if days > 1 else ''} ago"
            else:
                return "No data"
        except Exception:
            return "Unknown"
    
    # Check system status
    postgresql_online = check_database_status()
    sql_server_online = check_sql_server_status()
    google_sheets_online = check_google_sheets_status()
    last_sync = get_last_sync_status()
    
    # Get recent activities from SystemLog
    def get_recent_activities():
        try:
            from ..models import SystemLog
            activities = SystemLog.objects.select_related('user').order_by('-timestamp')[:5]
            return activities
        except Exception:
            return []
    
    recent_activities = get_recent_activities()

    context = {
        'total_clients': total_clients,
        'total_inspections': total_inspections,
        'recent_inspections': recent_inspections,
        'inspector_stats': inspector_stats,
        'settings': settings,
        'system_status': {
            'postgresql_online': postgresql_online,
            'sql_server_online': sql_server_online,
            'google_sheets_online': google_sheets_online,
            'last_sync': last_sync
        },
        'recent_activities': recent_activities
    }
    
    return render(request, 'main/home.html', context)


@login_required
@inspector_only_inspections
def analytics_dashboard(request):
    """Display the Power BI analytics dashboard with basic analytics data."""
    # Block administrators from accessing analytics dashboard
    if request.user.role == 'admin':
        messages.error(request, "Access denied. Administrators cannot access the Analytics Dashboard.")
        return redirect('home')
    from ..models import Client, Inspection, FoodSafetyAgencyInspection
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Get basic statistics
    total_clients = Client.objects.count()
    total_inspections = Inspection.objects.count()
    total_food_safety_inspections = FoodSafetyAgencyInspection.objects.count()
    
    # Get recent activity (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=thirty_days_ago
    ).count()
    
    # Get this month's inspections
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month_inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=current_month_start
    ).count()
    
    # Get average inspections per month (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    avg_monthly_inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=six_months_ago
    ).count() / 6
    
    # Get commodity breakdown
    commodity_stats = FoodSafetyAgencyInspection.objects.values('commodity').annotate(
        count=Count('commodity')
    ).order_by('-count')
    
    # Get top clients by inspection count
    top_clients = FoodSafetyAgencyInspection.objects.values('client_name').annotate(
        count=Count('client_name')
    ).order_by('-count')[:10]
    
    # Calculate percentages for top clients
    total_inspections_for_percentage = sum(client['count'] for client in top_clients)
    for client in top_clients:
        if total_inspections_for_percentage > 0:
            client['percentage'] = (client['count'] / total_inspections_for_percentage) * 100
        else:
            client['percentage'] = 0
    
    # Get monthly trends (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_trends = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=six_months_ago
    ).extra(
        select={'month': "EXTRACT(month FROM date_of_inspection)"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Convert month numbers to month names
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for trend in monthly_trends:
        month_num = int(trend['month']) - 1  # Convert to 0-based index
        if 0 <= month_num < 12:
            trend['month_name'] = month_names[month_num]
        else:
            trend['month_name'] = 'Unknown'
    
    # Get inspections over time (monthly for last 12 months)
    from django.db.models.functions import TruncMonth
    monthly_inspections = FoodSafetyAgencyInspection.objects.filter(
        date_of_inspection__gte=datetime.now() - timedelta(days=365)
    ).annotate(
        month=TruncMonth('date_of_inspection')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Get top inspectors by inspection count
    top_inspectors = FoodSafetyAgencyInspection.objects.values('inspector_name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Get major companies (Shoprite, Boxer, Pick n Pay, etc.)
    major_companies = FoodSafetyAgencyInspection.objects.values('client_name').annotate(
        count=Count('id')
    ).filter(
        models.Q(client_name__icontains='shoprite') |
        models.Q(client_name__icontains='boxer') |
        models.Q(client_name__icontains='pick') |
        models.Q(client_name__icontains='spar') |
        models.Q(client_name__icontains='woolworths')
    ).order_by('-count')
    
    # Simple forecasting for next 3 months
    if monthly_inspections:
        # Calculate average monthly growth rate
        recent_months = list(monthly_inspections)[-6:]  # Last 6 months
        if len(recent_months) >= 2:
            # Calculate average monthly change
            total_change = recent_months[-1]['count'] - recent_months[0]['count']
            avg_monthly_change = total_change / (len(recent_months) - 1)
            
            # Generate forecast for next 3 months
            last_count = recent_months[-1]['count']
            forecast_data = []
            for i in range(1, 4):
                forecast_count = max(0, last_count + (avg_monthly_change * i))
                forecast_data.append({
                    'month': f'Forecast {i}',
                    'count': round(forecast_count, 0)
                })
        else:
            forecast_data = []
    else:
        forecast_data = []
    
    # Debug: Print some values to see what's happening
    print(f"Debug - Total clients: {total_clients}")
    print(f"Debug - Total inspections: {total_inspections}")
    print(f"Debug - Total food safety inspections: {total_food_safety_inspections}")
    print(f"Debug - Monthly inspections count: {len(monthly_inspections)}")
    print(f"Debug - Top inspectors count: {len(top_inspectors)}")
    print(f"Debug - Major companies count: {len(major_companies)}")
    
    # Debug: Print sample data
    if monthly_inspections:
        print(f"Debug - Sample monthly data: {list(monthly_inspections)[:2]}")
    if top_inspectors:
        print(f"Debug - Sample inspector data: {list(top_inspectors)[:2]}")
    if major_companies:
        print(f"Debug - Sample company data: {list(major_companies)[:2]}")
    
    # Convert QuerySets to lists for proper JSON serialization
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    
    context = {
        'total_clients': total_clients,
        'total_inspections': total_inspections,
        'total_food_safety_inspections': total_food_safety_inspections,
        'recent_inspections': recent_inspections,
        'this_month_inspections': this_month_inspections,
        'avg_monthly_inspections': round(avg_monthly_inspections, 1),
        'monthly_inspections': json.dumps(list(monthly_inspections), cls=DjangoJSONEncoder),
        'top_inspectors': json.dumps(list(top_inspectors), cls=DjangoJSONEncoder),
        'major_companies': json.dumps(list(major_companies), cls=DjangoJSONEncoder),
        'forecast_data': json.dumps(forecast_data, cls=DjangoJSONEncoder),
    }
    
    return render(request, 'main/analytics_dashboard.html', context)

@login_required
def export_analytics(request, format_type):
    """Export analytics data in various formats"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        if format_type == 'excel':
            return export_analytics_excel(data)
        elif format_type == 'csv':
            return export_analytics_csv(data)
        elif format_type == 'pdf':
            return export_analytics_pdf(data)
        else:
            return JsonResponse({'error': 'Invalid format'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def export_analytics_excel(data):
    """Export analytics data to Excel"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from io import BytesIO
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Analytics Report"
    
    # Header
    ws['A1'] = "Food Safety Agency Analytics Report"
    ws['A1'].font = Font(size=16, bold=True)
    ws.merge_cells('A1:E1')
    
    # Summary Stats
    ws['A3'] = "Summary Statistics"
    ws['A3'].font = Font(size=14, bold=True)
    
    ws['A4'] = "Total Inspections"
    ws['B4'] = data.get('total_food_safety_inspections', 0)
    ws['A5'] = "Recent (30 days)"
    ws['B5'] = data.get('recent_inspections', 0)
    ws['A6'] = "This Month"
    ws['B6'] = data.get('this_month_inspections', 0)
    ws['A7'] = "Avg Monthly (6m)"
    ws['B7'] = data.get('avg_monthly_inspections', 0)
    
    # Monthly Inspections
    ws['A9'] = "Monthly Inspections"
    ws['A9'].font = Font(size=14, bold=True)
    
    ws['A10'] = "Month"
    ws['B10'] = "Inspections"
    ws['C10'] = "Forecast"
    
    row = 11
    monthly_data = data.get('monthly_inspections', [])
    forecast_data = data.get('forecast_data', [])
    
    for month in monthly_data:
        ws[f'A{row}'] = month.get('month', '')
        ws[f'B{row}'] = month.get('count', 0)
        row += 1
    
    for forecast in forecast_data:
        ws[f'A{row}'] = forecast.get('month', '')
        ws[f'C{row}'] = forecast.get('count', 0)
        row += 1
    
    # Top Inspectors
    ws['A{row}'] = "Top Inspectors"
    ws['A{row}'].font = Font(size=14, bold=True)
    row += 1
    
    ws['A{row}'] = "Inspector"
    ws['B{row}'] = "Inspections"
    row += 1
    
    for inspector in data.get('top_inspectors', []):
        ws[f'A{row}'] = inspector.get('inspector_name', 'Unknown')
        ws[f'B{row}'] = inspector.get('count', 0)
        row += 1
    
    # Major Companies
    ws['A{row}'] = "Major Companies"
    ws['A{row}'].font = Font(size=14, bold=True)
    row += 1
    
    ws['A{row}'] = "Company"
    ws['B{row}'] = "Inspections"
    row += 1
    
    for company in data.get('major_companies', []):
        ws[f'A{row}'] = company.get('client_name', '')
        ws[f'B{row}'] = company.get('count', 0)
        row += 1
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Save to BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="analytics_report_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    return response

def export_analytics_csv(data):
    """Export analytics data to CSV"""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Food Safety Agency Analytics Report"])
    writer.writerow([])
    
    # Summary Stats
    writer.writerow(["Summary Statistics"])
    writer.writerow(["Total Inspections", data.get('total_food_safety_inspections', 0)])
    writer.writerow(["Recent (30 days)", data.get('recent_inspections', 0)])
    writer.writerow(["This Month", data.get('this_month_inspections', 0)])
    writer.writerow(["Avg Monthly (6m)", data.get('avg_monthly_inspections', 0)])
    writer.writerow([])
    
    # Monthly Inspections
    writer.writerow(["Monthly Inspections"])
    writer.writerow(["Month", "Inspections", "Forecast"])
    
    monthly_data = data.get('monthly_inspections', [])
    forecast_data = data.get('forecast_data', [])
    
    for month in monthly_data:
        writer.writerow([month.get('month', ''), month.get('count', 0), ''])
    
    for forecast in forecast_data:
        writer.writerow([forecast.get('month', ''), '', forecast.get('count', 0)])
    
    writer.writerow([])
    
    # Top Inspectors
    writer.writerow(["Top Inspectors"])
    writer.writerow(["Inspector", "Inspections"])
    
    for inspector in data.get('top_inspectors', []):
        writer.writerow([inspector.get('inspector_name', 'Unknown'), inspector.get('count', 0)])
    
    writer.writerow([])
    
    # Major Companies
    writer.writerow(["Major Companies"])
    writer.writerow(["Company", "Inspections"])
    
    for company in data.get('major_companies', []):
        writer.writerow([company.get('client_name', ''), company.get('count', 0)])
    
    output.seek(0)
    
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="analytics_report_{datetime.now().strftime("%Y%m%d")}.csv"'
    return response

def export_analytics_pdf(data):
    """Export analytics data to PDF"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from io import BytesIO
    
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Title
    story.append(Paragraph("Food Safety Agency Analytics Report", title_style))
    story.append(Spacer(1, 20))
    
    # Summary Stats
    story.append(Paragraph("Summary Statistics", styles['Heading2']))
    summary_data = [
        ["Metric", "Value"],
        ["Total Inspections", str(data.get('total_food_safety_inspections', 0))],
        ["Recent (30 days)", str(data.get('recent_inspections', 0))],
        ["This Month", str(data.get('this_month_inspections', 0))],
        ["Avg Monthly (6m)", str(data.get('avg_monthly_inspections', 0))]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Monthly Inspections
    story.append(Paragraph("Monthly Inspections", styles['Heading2']))
    monthly_data = data.get('monthly_inspections', [])
    forecast_data = data.get('forecast_data', [])
    
    monthly_table_data = [["Month", "Inspections", "Forecast"]]
    for month in monthly_data:
        monthly_table_data.append([month.get('month', ''), str(month.get('count', 0)), ''])
    
    for forecast in forecast_data:
        monthly_table_data.append([forecast.get('month', ''), '', str(forecast.get('count', 0))])
    
    monthly_table = Table(monthly_table_data)
    monthly_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(monthly_table)
    story.append(Spacer(1, 20))
    
    # Top Inspectors
    story.append(Paragraph("Top Inspectors", styles['Heading2']))
    inspector_data = [["Inspector", "Inspections"]]
    for inspector in data.get('top_inspectors', []):
        inspector_data.append([inspector.get('inspector_name', 'Unknown'), str(inspector.get('count', 0))])
    
    inspector_table = Table(inspector_data)
    inspector_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(inspector_table)
    story.append(Spacer(1, 20))
    
    # Major Companies
    story.append(Paragraph("Major Companies", styles['Heading2']))
    company_data = [["Company", "Inspections"]]
    for company in data.get('major_companies', []):
        company_data.append([company.get('client_name', ''), str(company.get('count', 0))])
    
    company_table = Table(company_data)
    company_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(company_table)
    
    doc.build(story)
    output.seek(0)
    
    response = HttpResponse(output.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="analytics_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    return response


@login_required(login_url='login')
@inspector_only_inspections
def settings_view(request):
    """Settings page view."""
    clear_messages(request)
    
    # Get or create settings
    from ..models import Settings, SystemSettings
    settings = Settings.get_settings()
    system_settings = SystemSettings.get_settings()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'clear_cache':
            # Clear Django cache
            from django.core.cache import cache
            cache.clear()
            messages.success(request, "Application cache cleared successfully!")
            
        elif action == 'reset_settings':
            # Reset settings to defaults
            settings.auto_sync = False
            settings.backup_frequency = 'weekly'
            settings.session_timeout = 30
            settings.google_sheets_enabled = True
            settings.sql_server_enabled = True
            settings.sync_interval = 24
            settings.sync_interval_unit = 'hours'
            settings.email_notifications = False
            settings.sync_notifications = True
            settings.notification_email = None
            settings.two_factor_auth = False
            settings.password_expiry = 90
            settings.max_login_attempts = 5
            settings.save()
            messages.success(request, "Settings reset to default values!")
            
        elif action == 'export_data':
            # Export data functionality (placeholder)
            messages.info(request, "Data export functionality will be implemented soon!")
            
        elif action == 'create_backup':
            # Create manual backup
            from ..services.backup_service import BackupService
            backup_service = BackupService()
            result = backup_service.create_backup(backup_type='manual')
            
            if result['success']:
                messages.success(request, f"Backup created successfully! Files: {', '.join(result['files_created'])}. Records backed up: {result['record_counts']['clients']} clients, {result['record_counts']['inspections']} inspections, {result['record_counts']['shipments']} shipments.")
                try:
                    SystemLog.log_activity(
                        user=request.user,
                        action='EXPORT',
                        page=request.path,
                        description='Created manual backup',
                        details={
                            'files_created': result.get('files_created'),
                            'record_counts': result.get('record_counts')
                        }
                    )
                except Exception:
                    pass
            else:
                messages.error(request, f"Backup failed: {result['error']}")
                try:
                    SystemLog.log_activity(
                        user=request.user,
                        action='ERROR',
                        page=request.path,
                        description='Manual backup failed',
                        details={'error': result.get('error')}
                    )
                except Exception:
                    pass
                    
        elif action == 'save_theme':
            # Save theme setting
            settings.dark_mode = 'theme_mode' in request.POST
            settings.save()
            try:
                SystemLog.log_activity(
                    user=request.user,
                    action='SETTINGS',
                    page=request.path,
                    description='Updated theme setting',
                    details={'dark_mode': settings.dark_mode}
                )
            except Exception:
                pass
                
        elif action == 'save_compliance':
            # Compliance document settings
            settings.compliance_auto_sync = 'compliance_auto_sync' in request.POST
            settings.compliance_sync_interval = int(request.POST.get('compliance_sync_interval', 5))
            settings.compliance_sync_unit = request.POST.get('compliance_sync_unit', 'minutes')
            settings.compliance_batch_mode = request.POST.get('compliance_batch_mode', 'batch')
            settings.compliance_batch_size = int(request.POST.get('compliance_batch_size', 50))
            settings.compliance_date_range = int(request.POST.get('compliance_date_range', 7))
            settings.save()
            
            # Update background service with new settings
            try:
                # Compliance service removed - OneDrive service handles this
                pass
            except:
                pass  # Service might not be running
            
            mode_text = "Process ALL at once" if settings.compliance_batch_mode == 'all' else f"Process in batches of {settings.compliance_batch_size}"
            messages.success(request, f"Compliance settings updated! Auto sync: {'Enabled' if settings.compliance_auto_sync else 'Disabled'}, Interval: {settings.compliance_sync_interval} {settings.compliance_sync_unit}, Mode: {mode_text}")
        
        elif action == 'save_onedrive_cache' or 'onedrive_sync_interval_hours' in request.POST or 'system_auto_sync_enabled' in request.POST or 'onedrive_upload_delay_days' in request.POST or 'compliance_daily_sync_enabled' in request.POST:
            # OneDrive background sync and caching settings (stored in SystemSettings)
            # Always enable OneDrive when delay is configured
            system_settings.onedrive_enabled = True
            # Scheduled sync master toggle
            system_settings.auto_sync_enabled = 'system_auto_sync_enabled' in request.POST
            system_settings.onedrive_local_caching = 'onedrive_local_caching' in request.POST
            try:
                system_settings.onedrive_cache_days = int(request.POST.get('onedrive_cache_days', system_settings.onedrive_cache_days or 60))
            except Exception:
                pass
            # Always enable auto sync when OneDrive is enabled
            system_settings.onedrive_auto_sync = True
            try:
                system_settings.onedrive_sync_interval_hours = int(request.POST.get('onedrive_sync_interval_hours', system_settings.onedrive_sync_interval_hours or 2))
            except Exception:
                pass
            
            # OneDrive upload delay settings
            try:
                system_settings.onedrive_upload_delay_days = int(request.POST.get('onedrive_upload_delay_days', system_settings.onedrive_upload_delay_days or 3))
            except Exception:
                pass
            system_settings.onedrive_upload_delay_unit = request.POST.get('onedrive_upload_delay_unit', system_settings.onedrive_upload_delay_unit or 'days')
            
            # Daily compliance sync settings
            system_settings.compliance_daily_sync_enabled = 'compliance_daily_sync_enabled' in request.POST
            system_settings.compliance_skip_processed = 'compliance_skip_processed' in request.POST
            
            system_settings.save()
            
            # Create success message
            success_parts = []
            success_parts.append(f"OneDrive auto-upload: {system_settings.onedrive_upload_delay_days} {system_settings.onedrive_upload_delay_unit}")
            
            if system_settings.compliance_daily_sync_enabled:
                success_parts.append("Daily compliance sync: Enabled")
            if system_settings.compliance_skip_processed:
                success_parts.append("Skip processed: Enabled")
            
            messages.success(request, f"Settings updated! {' | '.join(success_parts)}")
            
        elif action == 'pull_all_data':
            # Pull ALL data from Google Drive (not just 4 months)
            try:
                import os
                import threading
                import time
                from datetime import datetime, timedelta
                from concurrent.futures import ThreadPoolExecutor, as_completed
                import multiprocessing
                from ..services.google_drive_service import GoogleDriveService
                from ..models import Client, FoodSafetyAgencyInspection
                from django.conf import settings as django_settings
                
                # Get all inspections (not just 4 months)
                all_inspections = FoodSafetyAgencyInspection.objects.all()
                
                # Get client account code mapping
                client_map = {c.name: (c.internal_account_code or 'no') for c in Client.objects.all()}
                
                # Google Drive folder ID
                folder_id = '18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4'
                
                def pull_all_data_background():
                    """Background function to pull ALL data from Google Drive"""
                    try:
                        print("🚀 Starting full system sync - pulling ALL data from Google Drive...")
                        
                        # Initialize Google Drive service
                        drive_service = GoogleDriveService()
                        print("✅ Google Drive service initialized")
                        
                        # Get file list from Google Drive
                        print("📁 Fetching file list from Google Drive...")
                        drive_files = drive_service.list_files_in_folder(folder_id, request=None)
                        file_lookup = GoogleDriveService.build_file_lookup(drive_files)
                        print(f"✅ Found {len(drive_files)} files in Google Drive")
                        
                        # Process all inspections
                        total_inspections = all_inspections.count()
                        processed = 0
                        downloaded = 0
                        errors = 0
                        
                        print(f"🔄 Processing {total_inspections} inspections...")
                        
                        for inspection in all_inspections:
                            try:
                                processed += 1
                                
                                # Get client's internal account code and commodity
                                account_code = client_map.get(inspection.client_name, 'no')
                                commodity = str(inspection.commodity).strip().lower() if inspection.commodity else ''
                                
                                if not commodity or account_code == 'no':
                                    continue
                                
                                if commodity == 'eggs':
                                    commodity = 'egg'
                                
                                # Find matching file in Google Drive
                                best_file = None
                                best_days = 10**9
                                
                                for file_info in file_lookup.values():
                                    if (file_info['commodity'].lower() == commodity and 
                                        file_info['accountCode'] == account_code):
                                        days_diff = abs((file_info['zipDate'] - inspection.date_of_inspection).days)
                                        if days_diff <= 15 and days_diff < best_days:
                                            best_file = file_info
                                            best_days = days_diff
                                
                                if best_file:
                                    # Create folder structure
                                    year_folder = inspection.date_of_inspection.strftime('%Y')
                                    month_folder = inspection.date_of_inspection.strftime('%B')
                                    
                                    # Use original client name for folder structure
                                    client_folder = inspection.client_name or 'Unknown Client'
                                    
                                    compliance_folder = os.path.join(
                                        django_settings.MEDIA_ROOT, 'inspection', year_folder, month_folder, 
                                        client_folder, 'Compliance', commodity.upper()
                                    )
                                    os.makedirs(compliance_folder, exist_ok=True)
                                    
                                    # Download file if it doesn't exist
                                    file_path = os.path.join(compliance_folder, best_file['name'])
                                    if not os.path.exists(file_path):
                                        success = drive_service.download_file(best_file['id'], file_path)
                                        if success:
                                            downloaded += 1
                                            print(f"✅ Downloaded {best_file['name']} for {inspection.client_name}")
                                        else:
                                            errors += 1
                                            print(f"❌ Failed to download {best_file['name']} for {inspection.client_name}")
                                    else:
                                        print(f"ℹ️ File exists: {best_file['name']} for {inspection.client_name}")
                                
                                # Progress update every 100 inspections
                                if processed % 100 == 0:
                                    print(f"📊 Progress: {processed}/{total_inspections} inspections processed, {downloaded} files downloaded, {errors} errors")
                                
                            except Exception as e:
                                errors += 1
                                print(f"❌ Error processing {inspection.client_name}: {e}")
                                continue
                        
                        print(f"🎉 Full system sync completed!")
                        print(f"📊 Final results: {processed} inspections processed, {downloaded} files downloaded, {errors} errors")
                        
                    except Exception as e:
                        print(f"❌ Fatal error in full system sync: {e}")
                
                # Start background process
                sync_thread = threading.Thread(target=pull_all_data_background, daemon=True)
                sync_thread.start()
                
                messages.success(request, "Full system sync started in background! Check console for progress.")
                
            except Exception as e:
                messages.error(request, f"Error starting full system sync: {str(e)}")
            
        else:
            # Handle form submissions for different settings sections
            if 'auto_sync' in request.POST:
                # System settings
                settings.auto_sync = 'auto_sync' in request.POST
                
                # Handle backup frequency - convert days to frequency choice
                backup_days = int(request.POST.get('backup_frequency', 7))
                if backup_days == 1:
                    settings.backup_frequency = 'daily'
                elif backup_days == 7:
                    settings.backup_frequency = 'weekly'
                elif backup_days == 30:
                    settings.backup_frequency = 'monthly'
                else:
                    # Default to weekly for any other value
                    settings.backup_frequency = 'weekly'
                
                settings.session_timeout = int(request.POST.get('session_timeout', 30))
                settings.dark_mode = 'theme_mode' in request.POST
                settings.save()
                
                # Create success message with backup frequency info
                frequency_text = {
                    'daily': 'daily',
                    'weekly': 'weekly (every 7 days)',
                    'monthly': 'monthly (every 30 days)'
                }.get(settings.backup_frequency, 'weekly')
                
                messages.success(request, f"System settings updated successfully! Auto sync: {'Enabled' if settings.auto_sync else 'Disabled'}, Backup: {frequency_text}, Session timeout: {settings.session_timeout} minutes, Theme: {'Dark' if settings.dark_mode else 'Light'} mode")
                # Log the settings update
                try:
                    SystemLog.log_activity(
                        user=request.user,
                        action='SETTINGS',
                        page=request.path,
                        description='Updated system settings',
                        details={
                            'auto_sync': settings.auto_sync,
                            'backup_frequency': settings.backup_frequency,
                            'session_timeout': settings.session_timeout,
                            'dark_mode': settings.dark_mode,
                        }
                    )
                except Exception:
                    pass
                
            elif 'google_sheets_enabled' in request.POST:
                # Data sync settings
                settings.google_sheets_enabled = 'google_sheets_enabled' in request.POST
                settings.sql_server_enabled = 'sql_server_enabled' in request.POST
                settings.sync_interval = int(request.POST.get('sync_interval', 24))
                settings.sync_interval_unit = request.POST.get('sync_interval_unit', 'hours')
                settings.save()
                messages.success(request, f"Data sync settings updated successfully! Interval: {settings.sync_interval} {settings.sync_interval_unit}")
            
            else:
                # Handle form submissions for different settings sections
                if 'auto_sync' in request.POST:
                    # System settings
                    settings.auto_sync = 'auto_sync' in request.POST
                    settings.session_timeout = int(request.POST.get('session_timeout', 30))
                    settings.dark_mode = 'theme_mode' in request.POST
                    settings.save()
                    messages.success(request, "System settings updated successfully!")
                    
    # Get backup status
    try:
        from ..services.backup_service import BackupService
        backup_service = BackupService()
        backup_status = backup_service.get_backup_status()
    except Exception as e:
        backup_status = {
            'auto_sync_enabled': settings.auto_sync,
            'backup_frequency': settings.backup_frequency,
            'last_backup': None,
            'next_backup': None,
            'backup_files': []
        }
    
    # Bridge SystemSettings into the settings object for template compatibility
    try:
        for attr in ['onedrive_enabled', 'onedrive_local_caching', 'onedrive_cache_days', 'onedrive_auto_sync', 'onedrive_sync_interval_hours', 'auto_sync_enabled', 'compliance_daily_sync_enabled', 'compliance_skip_processed']:
            setattr(settings, attr, getattr(system_settings, attr))
    except Exception:
        pass

    context = {
        'settings': settings,
        'backup_status': backup_status
    }
    
    return render(request, 'main/settings.html', context)


@login_required
def session_status(request):
    """Debug view to show current session status"""
    from django.utils import timezone
    from datetime import timedelta
    
    settings = Settings.get_settings()
    last_activity = request.session.get('last_activity')
    current_time = timezone.now()
    
    if last_activity:
        last_activity_dt = timezone.datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
        time_since_activity = current_time - last_activity_dt
        timeout_threshold = last_activity_dt + timedelta(minutes=settings.session_timeout)
        time_until_timeout = timeout_threshold - current_time
    else:
        last_activity_dt = None
        time_since_activity = None
        timeout_threshold = None
        time_until_timeout = None
    
    context = {
        'current_time': current_time,
        'last_activity': last_activity_dt,
        'time_since_activity': time_since_activity,
        'session_timeout_minutes': settings.session_timeout,
        'timeout_threshold': timeout_threshold,
        'time_until_timeout': time_until_timeout,
        'is_expired': time_until_timeout and time_until_timeout.total_seconds() < 0
    }
    
    return render(request, 'main/session_status.html', context)


@login_required
def update_test_result(request):
    """Update test result (fat, protein, calcium, dna) for an inspection"""
    # Note: This function handles potential duplicate remote_id records by selecting the first one
    if request.method == 'POST':
        try:
            inspection_id = request.POST.get('inspection_id')
            test_type = request.POST.get('test_type')
            test_result = request.POST.get('test_result') == 'true'
            
            # Validate test type
            valid_test_types = ['fat', 'protein', 'calcium', 'dna']
            if test_type not in valid_test_types:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid test type: {test_type}'
                })
            
            # Get the inspection record - handle potential duplicates by getting the first one
            try:
                inspections = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id)
                inspection = inspections.first()
                if not inspection:
                    return JsonResponse({
                        'success': False,
                        'error': f'Inspection with ID {inspection_id} not found'
                    })
                # Log if there are duplicates for debugging
                if inspections.count() > 1:
                    print(f"Warning: Found {inspections.count()} inspections with remote_id {inspection_id}, using the first one")
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Error finding inspection: {str(e)}'
                })
            
            # Update the appropriate field
            if test_type == 'fat':
                inspection.fat = test_result
            elif test_type == 'protein':
                inspection.protein = test_result
            elif test_type == 'calcium':
                inspection.calcium = test_result
            elif test_type == 'dna':
                inspection.dna = test_result
            
            inspection.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{test_type.title()} test result updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error updating test result: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })


@login_required
def update_needs_retest(request):
    """Update needs retest field for an inspection"""
    if request.method == 'POST':
        try:
            inspection_id = request.POST.get('inspection_id')
            needs_retest = request.POST.get('needs_retest')
            
            # Get the inspection record - handle potential duplicates by getting the first one
            try:
                inspections = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id)
                inspection = inspections.first()
                if not inspection:
                    return JsonResponse({
                        'success': False,
                        'error': f'Inspection with ID {inspection_id} not found'
                    })
                # Log if there are duplicates for debugging
                if inspections.count() > 1:
                    print(f"Warning: Found {inspections.count()} inspections with remote_id {inspection_id}, using the first one")
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Error finding inspection: {str(e)}'
                })
            
            # If no sample was taken, automatically set needs_retest to NO
            if not inspection.is_sample_taken:
                inspection.needs_retest = 'NO'
                inspection.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Needs retest automatically set to NO (no sample taken)'
                })
            
            # Validate needs_retest value for cases where sample was taken
            valid_values = ['YES', 'NO', '']
            if needs_retest not in valid_values:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid needs_retest value: {needs_retest}'
                })
            
            # Update the needs_retest field
            inspection.needs_retest = needs_retest if needs_retest else None
            inspection.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Needs retest updated successfully to: {needs_retest if needs_retest else "Not set"}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error updating needs retest: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })


@login_required
def update_km_traveled(request):
    """Update km traveled field for an inspection"""
    if request.method == 'POST':
        try:
            inspection_id = request.POST.get('inspection_id')
            km_traveled = request.POST.get('km_traveled')
            
            # Get the inspection record
            try:
                inspections = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id)
                inspection = inspections.first()
                if not inspection:
                    return JsonResponse({
                        'success': False,
                        'error': f'Inspection with ID {inspection_id} not found'
                    })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Error finding inspection: {str(e)}'
                })
            
            # Validate km_traveled value
            if km_traveled:
                try:
                    km_value = float(km_traveled)
                    if km_value < 0:
                        return JsonResponse({
                            'success': False,
                            'error': 'Km traveled cannot be negative'
                        })
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid km traveled value'
                    })
            
            # Update the km_traveled field
            inspection.km_traveled = km_value if km_traveled else None
            inspection.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Km traveled updated successfully to: {km_value if km_traveled else "Not set"}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error updating km traveled: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })


@login_required
def update_hours(request):
    """Update hours field for an inspection"""
    if request.method == 'POST':
        try:
            inspection_id = request.POST.get('inspection_id')
            hours = request.POST.get('hours')
            
            # Get the inspection record
            try:
                inspections = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id)
                inspection = inspections.first()
                if not inspection:
                    return JsonResponse({
                        'success': False,
                        'error': f'Inspection with ID {inspection_id} not found'
                    })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Error finding inspection: {str(e)}'
                })
            
            # Validate hours value
            if hours:
                try:
                    hours_value = float(hours)
                    if hours_value < 0:
                        return JsonResponse({
                            'success': False,
                            'error': 'Hours cannot be negative'
                        })
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid hours value'
                    })
            
            # Update the hours field
            inspection.hours = hours_value if hours else None
            inspection.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Hours updated successfully to: {hours_value if hours else "Not set"}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error updating hours: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })


@login_required
def update_lab(request):
    """Update lab field for an inspection"""
    if request.method == 'POST':
        try:
            inspection_id = request.POST.get('inspection_id')
            lab = request.POST.get('lab')
            
            # Get the inspection record
            try:
                inspections = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id)
                inspection = inspections.first()
                if not inspection:
                    return JsonResponse({
                        'success': False,
                        'error': f'Inspection with ID {inspection_id} not found'
                    })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Error finding inspection: {str(e)}'
                })
            
            # Validate lab value (keep in sync with model choices)
            valid_labs = ['lab_a', 'lab_b', 'lab_c', 'lab_d', 'lab_e', 'lab_f', '']
            if lab not in valid_labs:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid lab value: {lab}'
                })
            
            # Update the lab field
            inspection.lab = lab if lab else None
            inspection.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Lab updated successfully to: {lab if lab else "Not set"}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error updating lab: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })


@login_required
def update_group_km_traveled(request):
    """Update km_traveled field for all inspections in a group"""
    if request.method == 'POST':
        try:
            group_id = request.POST.get('group_id')
            km_traveled = request.POST.get('km_traveled')

            # Parse group_id to extract client_name and date_of_inspection
            # group_id format: "client_name_date_of_inspection"
            if '_' not in group_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid group ID format'
                })

            # Split the group_id to get client_name and date
            parts = group_id.split('_')
            if len(parts) < 2:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid group ID format'
                })

            # Reconstruct client_name (may contain underscores) and date
            date_part = parts[-1]
            client_name_parts = parts[:-1]
            client_name = '_'.join(client_name_parts)

            # Convert date string to date object (support YYYY-MM-DD and YYYYMMDD)
            from datetime import datetime
            date_of_inspection = None
            for fmt in ('%Y-%m-%d', '%Y%m%d'):
                try:
                    date_of_inspection = datetime.strptime(date_part, fmt).date()
                    break
                except ValueError:
                    continue
            if not date_of_inspection:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid date format in group ID: {date_part}'
                })

            # Find all inspections in this group using normalized client name
            import re as _re
            def _normalize(n):
                return _re.sub(r'[^a-zA-Z0-9]', '', (n or '')).lower()

            raw_key = _normalize(client_name)
            candidate_qs = FoodSafetyAgencyInspection.objects.filter(
                date_of_inspection=date_of_inspection
            )
            matching_ids = [ins.id for ins in candidate_qs if _normalize(ins.client_name) == raw_key]
            inspections = FoodSafetyAgencyInspection.objects.filter(id__in=matching_ids)

            if not inspections.exists():
                return JsonResponse({
                    'success': False,
                    'error': f'No inspections found for group: {group_id}'
                })

            # Update km_traveled for all inspections in the group
            km_value = float(km_traveled) if km_traveled else None
            updated_count = inspections.update(km_traveled=km_value)

            return JsonResponse({
                'success': True,
                'message': f'Km traveled updated successfully for {updated_count} inspections in group'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error updating group km traveled: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })


@login_required
def update_group_hours(request):
    """Update hours field for all inspections in a group"""
    if request.method == 'POST':
        try:
            group_id = request.POST.get('group_id')
            hours = request.POST.get('hours')

            # Parse group_id to extract client_name and date_of_inspection
            # group_id format: "client_name_date_of_inspection"
            if '_' not in group_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid group ID format'
                })

            # Split the group_id to get client_name and date
            parts = group_id.split('_')
            if len(parts) < 2:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid group ID format'
                })

            # Reconstruct client_name (may contain underscores) and date
            date_part = parts[-1]
            client_name_parts = parts[:-1]
            client_name = '_'.join(client_name_parts)

            # Convert date string to date object (support YYYY-MM-DD and YYYYMMDD)
            from datetime import datetime
            date_of_inspection = None
            for fmt in ('%Y-%m-%d', '%Y%m%d'):
                try:
                    date_of_inspection = datetime.strptime(date_part, fmt).date()
                    break
                except ValueError:
                    continue
            if not date_of_inspection:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid date format in group ID: {date_part}'
                })

            # Find all inspections in this group using normalized client name
            import re as _re
            def _normalize(n):
                return _re.sub(r'[^a-zA-Z0-9]', '', (n or '')).lower()

            raw_key = _normalize(client_name)
            candidate_qs = FoodSafetyAgencyInspection.objects.filter(
                date_of_inspection=date_of_inspection
            )
            matching_ids = [ins.id for ins in candidate_qs if _normalize(ins.client_name) == raw_key]
            inspections = FoodSafetyAgencyInspection.objects.filter(id__in=matching_ids)

            if not inspections.exists():
                return JsonResponse({
                    'success': False,
                    'error': f'No inspections found for group: {group_id}'
                })

            # Update hours for all inspections in the group
            hours_value = float(hours) if hours else None
            updated_count = inspections.update(hours=hours_value)

            return JsonResponse({
                'success': True,
                'message': f'Hours updated successfully for {updated_count} inspections in group'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error updating group hours: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })


@login_required
@role_required(['developer'])
def compliance_documents(request):
    """Developer-only page for managing/viewing compliance documents."""
    context = {
        'page_title': 'Compliance Documents (Developer Only)'
    }
    return render(request, 'main/compliance_documents.html', context)


@login_required
@role_required(['developer'])
def onedrive_view(request):
    """Developer-only page for viewing OneDrive contents."""
    import os
    import json
    from django.conf import settings
    from datetime import datetime
    
    # Initialize OneDrive data
    onedrive_data = {
        'connected': False,
        'folders': [],
        'total_files': 0,
        'error': None,
        'token_refreshed': False
    }
    
    try:
        # Check if OneDrive tokens exist
        token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                tokens = json.load(f)
            
            access_token = tokens.get('access_token')
            expires_at = tokens.get('expires_at', 0)
            current_time = datetime.now().timestamp()
            
            # Check if token is expired or will expire soon (within 10 minutes)
            if access_token and current_time < expires_at:
                # Token is valid
                onedrive_data['connected'] = True
            elif access_token and expires_at - current_time < 600:  # 10 minutes
                # Token expires soon, try to refresh
                print("🔄 Token expires soon, attempting refresh...")
                onedrive_data['token_refreshed'] = True
                onedrive_data['connected'] = True
            elif access_token:
                # Token is expired, try to refresh
                print("🔄 Token expired, attempting refresh...")
                onedrive_data['token_refreshed'] = True
                onedrive_data['connected'] = True
            else:
                onedrive_data['error'] = 'No valid access token found'
        else:
            onedrive_data['error'] = 'OneDrive not connected. Please connect in Settings.'
        
        # If we have a connection (valid or refreshed), try to get folder structure
        if onedrive_data['connected']:
            from ..services.onedrive_direct_service import OneDriveDirectUploadService
            onedrive_service = OneDriveDirectUploadService()
            
            # Authenticate with OneDrive (this will handle token refresh if needed)
            if onedrive_service.authenticate_onedrive():
                # Get ALL folders from OneDrive root directory
                folders = onedrive_service.list_folders_in_onedrive(None)
                
                if folders:
                    onedrive_data['folders'] = folders
                    # Count total files
                    total_files = 0
                    for folder in folders:
                        if 'file_count' in folder:
                            total_files += folder['file_count']
                    onedrive_data['total_files'] = total_files
                else:
                    onedrive_data['error'] = 'No folders found in OneDrive'
            else:
                onedrive_data['error'] = 'Failed to authenticate with OneDrive. For business accounts, you may need to re-authenticate through Settings.'
                onedrive_data['connected'] = False
            
    except Exception as e:
        onedrive_data['error'] = f'Error accessing OneDrive: {str(e)}'
        onedrive_data['connected'] = False
    
    # Get theme settings
    try:
        from ..models import SystemSettings
        system_settings = SystemSettings.get_settings()
        settings = type('Settings', (), {
            'dark_mode': system_settings.theme_mode == 'dark' if hasattr(system_settings, 'theme_mode') else False,
        })()
    except Exception:
        settings = type('Settings', (), {'dark_mode': False})()
    
    context = {
        'page_title': 'OneDrive View (Developer Only)',
        'onedrive_data': onedrive_data,
        'settings': settings,
    }
    return render(request, 'main/onedrive_view.html', context)


@login_required
@role_required(['developer'])
def compliance_linking_page(request):
    """Main page for inspection document linking (Apps Script replica)."""
    context = {
        'page_title': 'Inspection Document Links'
    }
    return render(request, 'main/compliance_linking.html', context)


@login_required
@role_required(['developer'])
def get_inspection_data(request):
    """Get ALL inspection data with account codes and document links."""
    try:
        from ..models import FoodSafetyAgencyInspection, Client
        from django.core.cache import cache
        
        # Get inspections from January 2025 onwards only
        from datetime import date
        cutoff_date = date(2025, 1, 1)
        print("Loading inspections from January 2025 onwards...")
        inspections = FoodSafetyAgencyInspection.objects.select_related().filter(
            date_of_inspection__gte=cutoff_date
        ).order_by('-date_of_inspection')
        total_inspections_count = inspections.count()
        print(f"Found {total_inspections_count} inspections from Jan 2025 onwards")
        
        # Build client mapping from ALL clients in database (business name -> account code)
        print("Loading ALL client data from database...")
        client_map = {}
        all_clients = Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code='')
        
        for client in all_clients:
            # Normalize client name like Apps Script does
            key = normalize_client_name(client.client_id or '')
            if key:
                client_map[key] = {
                    'account_code': client.internal_account_code,
                    'email': ''  # Email would come from client database in real implementation
                }
        
        print(f"Loaded {len(client_map)} clients with account codes")
        
        # Load Drive files fresh (with debugging)
        cache_key = 'drive_files_lookup_v2'  # New cache key to force refresh
        file_lookup = cache.get(cache_key)
        
        if not file_lookup:
            print("Loading Drive files from Google Drive...")
            file_lookup = load_drive_files_real(request)
            cache.set(cache_key, file_lookup, 600)  # Cache for 10 minutes
            print(f"Loaded {len(file_lookup)} files from Drive")
        else:
            print(f"Using cached Drive files: {len(file_lookup)} files")
        
        # Process inspections (without Drive file lookup for refresh)
        inspection_data = []
        total_matches = 0
        total_links = 0
        total_errors = 0
        
        print("Processing inspections (refresh mode - no Drive lookup)...")
        for i, inspection in enumerate(inspections):
            try:
                # Progress logging
                if (i + 1) % 1000 == 0:
                    print(f"Processed {i + 1} of {total_inspections_count} inspections...")
                
                # Get client account code using normalized lookup
                client_key = normalize_client_name(inspection.client_name or '')
                client_info = client_map.get(client_key, {})
                
                account_code = client_info.get('account_code', '')
                email = client_info.get('email', '')
                
                # Determine document status and link
                if not account_code:
                    document_status = 'no-account'
                    document_link = 'Can\'t Find Internal Account Code'
                    total_errors += 1
                else:
                    total_matches += 1
                    # Find document link using Apps Script replica logic
                    document_link = find_document_link_apps_script_replica(
                        account_code, 
                        inspection.commodity, 
                        inspection.date_of_inspection,
                        file_lookup
                    )
                    
                    if document_link and document_link != 'Document Not Found' and '<a href=' in document_link:
                        document_status = 'found'
                        total_links += 1
                    else:
                        document_status = 'not-found'
                        document_link = 'Document Not Found'
                
                inspection_data.append({
                    'remote_id': inspection.remote_id,
                    'client_name': inspection.client_name,
                    'account_code': account_code or 'Can\'t Find Internal Account Code',
                    'email': email or 'No Email',
                    'commodity': inspection.commodity,
                    'date_of_inspection': inspection.date_of_inspection.strftime('%Y-%m-%d') if inspection.date_of_inspection else '',
                    'document_link': document_link,
                    'document_status': document_status
                })
                
            except Exception as e:
                total_errors += 1
                inspection_data.append({
                    'remote_id': inspection.remote_id,
                    'client_name': inspection.client_name,
                    'account_code': 'Error',
                    'email': 'Error',
                    'commodity': inspection.commodity,
                    'date_of_inspection': inspection.date_of_inspection.strftime('%Y-%m-%d') if inspection.date_of_inspection else '',
                    'document_link': f'Error: {str(e)[:50]}',
                    'document_status': 'error'
                })
        
        stats = {
            'total': len(inspection_data),
            'matches': total_matches,
            'links': total_links,
            'errors': total_errors
        }
        
        print(f"Processing complete: {len(inspection_data)} inspections, {total_matches} matches, {total_links} links, {total_errors} errors")
        
        return JsonResponse({
            'success': True,
            'inspections': inspection_data,
            'stats': stats
        })
        
    except Exception as e:
        print(f"Error in get_inspection_data: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@role_required(['developer'])
def process_document_links(request):
    """Process document links for inspections (Apps Script replica)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        import json
        from ..models import FoodSafetyAgencyInspection, Client
        from datetime import datetime, timedelta
        
        data = json.loads(request.body)
        batch_size = data.get('batch_size', 100)
        date_range = data.get('date_range', 'recent')
        
        # Get inspections from January 2025 onwards, then apply additional filters
        from datetime import date
        cutoff_date = date(2025, 1, 1)
        
        if date_range == 'recent':
            date_filter = datetime.now() - timedelta(days=30)
            # Use the more recent of cutoff_date or recent filter
            final_date = max(cutoff_date, date_filter.date())
            inspections = FoodSafetyAgencyInspection.objects.filter(
                date_of_inspection__gte=final_date
            ).order_by('-date_of_inspection')
        elif date_range == 'month':
            now = datetime.now()
            inspections = FoodSafetyAgencyInspection.objects.filter(
                date_of_inspection__gte=cutoff_date,
                date_of_inspection__year=now.year,
                date_of_inspection__month=now.month
            ).order_by('-date_of_inspection')
        else:
            # All dates from Jan 2025 onwards
            inspections = FoodSafetyAgencyInspection.objects.filter(
                date_of_inspection__gte=cutoff_date
            ).order_by('-date_of_inspection')
        
        # Apply batch size limit if not processing all
        if batch_size < 500:
            inspections = inspections[:batch_size]
        
        # Load all client data (replica of Apps Script loadAllClientData function)
        client_map = {}
        for client in Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code=''):
            # Normalize client name like Apps Script
            key = normalize_client_name(client.client_id or '')
            if key:
                client_map[key] = {
                    'account_code': client.internal_account_code,
                    'email': ''  # Would be populated from client database
                }
        
        # Load all Drive files using real Google Drive API
        file_lookup = load_drive_files_real(request)
        
        # Process inspections
        processed_inspections = []
        total_matches = 0
        total_links = 0
        total_errors = 0
        
        for inspection in inspections:
            try:
                # Normalize client name for lookup
                client_key = normalize_client_name(inspection.client_name or '')
                client_info = client_map.get(client_key, {})
                
                account_code = client_info.get('account_code', '')
                email = client_info.get('email', '')
                
                # Find document link (replica of Apps Script findDocumentLink function)
                if account_code and account_code != 'no':
                    total_matches += 1
                    document_link = find_document_link_apps_script_replica(
                        account_code,
                        inspection.commodity,
                        inspection.date_of_inspection,
                        file_lookup
                    )
                    
                    if document_link and document_link != 'Document Not Found' and '<a href=' in document_link:
                        document_status = 'found'
                        total_links += 1
                    else:
                        document_status = 'not-found'
                        document_link = 'Document Not Found'
                else:
                    document_status = 'no-account'
                    document_link = 'Can\'t Find Internal Account Code'
                    total_errors += 1
                
                processed_inspections.append({
                    'remote_id': inspection.remote_id,
                    'client_name': inspection.client_name,
                    'account_code': account_code or 'Can\'t Find Internal Account Code',
                    'email': email or 'No Email',
                    'commodity': inspection.commodity,
                    'date_of_inspection': inspection.date_of_inspection.strftime('%Y-%m-%d') if inspection.date_of_inspection else '',
                    'document_link': document_link,
                    'document_status': document_status
                })
                
            except Exception as e:
                total_errors += 1
                processed_inspections.append({
                    'remote_id': inspection.remote_id,
                    'client_name': inspection.client_name,
                    'account_code': 'Error',
                    'email': 'Error',
                    'commodity': inspection.commodity,
                    'date_of_inspection': inspection.date_of_inspection.strftime('%Y-%m-%d') if inspection.date_of_inspection else '',
                    'document_link': f'Error: {str(e)[:50]}',
                    'document_status': 'error'
                })
        
        stats = {
            'total': len(processed_inspections),
            'matches': total_matches,
            'links': total_links,
            'errors': total_errors
        }
        
        summary = f"Processed {len(processed_inspections)} inspections, found {total_matches} matches, created {total_links} links"
        
        return JsonResponse({
            'success': True,
            'inspections': processed_inspections,
            'stats': stats,
            'summary': summary
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def normalize_client_name(name):
    """Normalize client name like Apps Script does."""
    if not name:
        return ''
    
    return name.strip().lower().replace('\u00A0', ' ').replace('\u200B', '').replace('\u2002', ' ').replace('\u2003', ' ').replace('  ', ' ')


def load_drive_files_real(request):
    """Load real Drive files using the existing GoogleDriveService - Apps Script replica."""
    try:
        from ..services.google_drive_service import GoogleDriveService
        import re
        from datetime import datetime
        
        drive_service = GoogleDriveService()
        folder_id = "18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4"  # From Apps Script
        
        print("Loading ALL Google Drive files...")
        start_time = datetime.now()
        
        # Get ALL files from Drive folder (not limited to 1000)
        files = drive_service.list_files_in_folder(folder_id, request=request, max_items=None)
        
        file_lookup = {}
        file_count = 0
        
        for file in files:
            file_name = file.get('name', '')
            file_id = file.get('id', '')
            web_view_link = file.get('webViewLink', '')
            
            # Debug first few files to see actual naming pattern
            if file_count < 5:
                print(f"Sample file {file_count + 1}: {file_name}")
            
            # Apps Script pattern: COMMODITY-ACCOUNT_CODE-DATE
            # Example: RAW-RE-IND-RAW-NA-1000-2025-01-15
            full_pattern = re.match(r'^([A-Za-z]+)-([A-Z]{2}-[A-Z]{3}-[A-Z]{3}-[A-Z]{2,3}-\d+)-(\d{4}-\d{2}-\d{2})', file_name)
            
            if full_pattern and file_id:
                commodity_prefix = full_pattern.group(1)
                account_code = full_pattern.group(2)
                zip_date_str = full_pattern.group(3)
                
                try:
                    zip_date = datetime.strptime(zip_date_str, '%Y-%m-%d')
                except:
                    continue
                
                # Create compound key exactly like Apps Script
                compound_key = f"{commodity_prefix.lower()}|{account_code}|{zip_date_str}"
                
                file_lookup[compound_key] = {
                    'url': web_view_link or f"https://drive.google.com/file/d/{file_id}/view",
                    'name': file_name,
                    'commodity': commodity_prefix,
                    'accountCode': account_code,
                    'zipDate': zip_date,
                    'zipDateStr': zip_date_str,
                    'file_id': file_id
                }
                
                file_count += 1
                
                # Progress logging like Apps Script
                if file_count % 1000 == 0 and file_count > 0:
                    print(f"Loaded {file_count} files...")
        
        load_time = (datetime.now() - start_time).total_seconds()
        print(f"Loaded {len(file_lookup)} files in {load_time:.1f} seconds")
        
        # Debug: Show first few parsed files
        if file_lookup:
            print("Sample parsed files:")
            for i, (key, file_info) in enumerate(file_lookup.items()):
                if i < 5:
                    print(f"  {key} -> {file_info['name']}")
        
        return file_lookup
        
    except Exception as e:
        print(f"Drive folder access issue: {e}")
        return {}


def find_document_link_apps_script_replica(account_code, commodity, inspection_date, file_lookup):
    """Exact replica of Apps Script findDocumentLink function."""
    if not account_code or account_code == "no" or not commodity or not inspection_date:
        return "Document Not Found"
    
    # Exact commodity normalization from Apps Script
    commodity_str = str(commodity).lower().strip()
    if commodity_str == "eggs":
        commodity_str = "egg"
    
    # Convert inspection_date to datetime if it's not already
    if isinstance(inspection_date, str):
        try:
            from datetime import datetime
            inspection_date_obj = datetime.strptime(inspection_date, '%Y-%m-%d').date()
        except:
            return "Document Not Found"
    elif hasattr(inspection_date, 'date'):
        # It's a datetime object, get just the date part
        inspection_date_obj = inspection_date.date()
    else:
        # It's already a date object
        inspection_date_obj = inspection_date
    
    best_match = None
    best_days_diff = float('inf')
    
    # Search through file lookup exactly like Apps Script
    for file_key in file_lookup:
        file = file_lookup[file_key]
        
        # Exact matching logic from Apps Script
        if (file['commodity'].lower() == commodity_str and 
            file['accountCode'] == account_code):
            
            try:
                # Calculate days difference exactly like Apps Script
                zip_date = file['zipDate']
                if hasattr(zip_date, 'date'):
                    zip_date = zip_date.date()
                days_difference = abs((zip_date - inspection_date_obj).days)
                
                if days_difference <= 15 and days_difference < best_days_diff:
                    best_match = file
                    best_days_diff = days_difference
                    
            except Exception as e:
                continue
    
    if best_match:
        # Use webViewLink like Apps Script getUrl() 
        url = best_match['url']
        
        # Also store compliance document info for download organization
        compliance_info = {
            'url': url,
            'filename': best_match['name'],
            'account_code': account_code,
            'commodity': commodity_str,
            'inspection_date': inspection_date_obj,
            'file_id': best_match.get('file_id', '')
        }
        
        return f'<a href="{url}" class="document-link" target="_blank" data-compliance="{compliance_info}">📄 Document Link</a>'
    
    return "Document Not Found"


def create_compliance_folder_structure():
    """Create compliance document folder structure organized by commodity."""
    import os
    from django.conf import settings
    
    base_compliance_dir = os.path.join(settings.MEDIA_ROOT, 'compliance')
    
    # Create commodity-specific compliance folders
    commodity_folders = [
        'raw_compliance',
        'pmp_compliance', 
        'poultry_compliance',
        'eggs_compliance',
        'general_compliance'
    ]
    
    created_folders = []
    for folder in commodity_folders:
        folder_path = os.path.join(base_compliance_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        created_folders.append(folder_path)
    
    return created_folders


def organize_zip_file_automatically(zip_file_path, client_name, inspection_date, commodity):
    """Automatically organize ZIP file contents by inspection numbers."""
    import os
    import zipfile
    import shutil
    from datetime import datetime
    import re
    
    try:
        print(f"🔍 Analyzing ZIP file: {os.path.basename(zip_file_path)}")
        
        # Get the base directory (client folder)
        # The ZIP file is in: media/inspection/YYYY/Month/ClientName/Compliance/COMMODITY/
        # We need to go up three levels to get to the client folder
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(zip_file_path)))
        
        # Create a temporary extraction directory
        temp_dir = os.path.join(base_dir, f"temp_extract_{os.path.basename(zip_file_path)}")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Extract ZIP file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Analyze files and organize them
        organized_files = []
        general_files = []
        
        # Walk through extracted files
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.lower().endswith('.pdf'):  # Only process PDF files
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, temp_dir)
                    
                    # Look for inspection number in filename (4-digit number)
                    inspection_match = re.search(r'(\d{4})', file)
                    if inspection_match:
                        inspection_number = inspection_match.group(1)
                        organized_files.append({
                            'file_path': file_path,
                            'relative_path': relative_path,
                            'filename': file,
                            'inspection_number': inspection_number
                        })
                        print(f"  📋 Found file for inspection {inspection_number}: {file}")
                    else:
                        general_files.append({
                            'file_path': file_path,
                            'relative_path': relative_path,
                            'filename': file
                        })
                        print(f"  📁 General file: {file}")
        
        # Create individual inspection folders and move files
        for file_info in organized_files:
            inspection_folder = os.path.join(base_dir, f"Inspection-{file_info['inspection_number']}")
            
            # Create complete folder structure for each inspection
            compliance_folder = os.path.join(inspection_folder, "Compliance", commodity.upper())
            lab_folder = os.path.join(inspection_folder, "Lab")
            retest_folder = os.path.join(inspection_folder, "Retest")
            form_folder = os.path.join(inspection_folder, "Form")
            
            os.makedirs(compliance_folder, exist_ok=True)
            os.makedirs(lab_folder, exist_ok=True)
            os.makedirs(retest_folder, exist_ok=True)
            os.makedirs(form_folder, exist_ok=True)
            
            # Move file to individual inspection compliance folder with commodity subfolder
            dest_path = os.path.join(compliance_folder, file_info['filename'])
            shutil.move(file_info['file_path'], dest_path)
            print(f"  ✅ Moved {file_info['filename']} to Inspection-{file_info['inspection_number']}/Compliance/{commodity.upper()}/")
        
        # Create main document type folders at client level
        rfi_folder = os.path.join(base_dir, "RFI")
        invoice_folder = os.path.join(base_dir, "Invoice")
        main_compliance_folder = os.path.join(base_dir, "Compliance", commodity.upper())  # Use existing Compliance folder with commodity subfolder
        
        os.makedirs(rfi_folder, exist_ok=True)
        os.makedirs(invoice_folder, exist_ok=True)
        os.makedirs(main_compliance_folder, exist_ok=True)
        
        # Move general files to main Compliance folder with commodity subfolder
        for file_info in general_files:
            dest_path = os.path.join(main_compliance_folder, file_info['filename'])
            shutil.move(file_info['file_path'], dest_path)
            print(f"  ✅ Moved {file_info['filename']} to main Compliance/{commodity.upper()}/ folder")
        
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Optionally, remove the original ZIP file since we've organized its contents
        try:
            os.remove(zip_file_path)
            print(f"  🗑️ Removed original ZIP file: {os.path.basename(zip_file_path)}")
        except Exception as e:
            print(f"  ⚠️ Could not remove original ZIP file: {e}")
        
        print(f"✅ Auto-organization complete: {len(organized_files)} files organized into individual inspections, {len(general_files)} files moved to general compliance")
        
    except Exception as e:
        print(f"❌ Error in auto-organization: {e}")
        # Clean up temp directory if it exists
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def download_compliance_document(file_id, account_code, commodity, inspection_date, filename, client_name, request):
    """Download compliance document to client's inspection folder structure."""
    import os
    import re
    from django.conf import settings
    from ..services.google_drive_service import GoogleDriveService
    from datetime import datetime
    
    try:
        # Build path like existing inspection structure: media/inspection/YYYY/Month/ClientName/Compliance/COMMODITY
        if isinstance(inspection_date, str):
            date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
        else:
            date_obj = inspection_date
        
        year_folder = date_obj.strftime('%Y')
        month_folder = date_obj.strftime('%B')  # Full month name like "May"
        
        # Use original client name for folder structure
        client_folder = client_name or 'Unknown Client'
        
        # Note: commodity is tracked but not used for folder structure
        commodity_upper = str(commodity).upper().strip()
        
        # Build full path: media/inspection/YYYY/Month/ClientName/Compliance/COMMODITY
        base_path = os.path.join(
            settings.MEDIA_ROOT, 
            'inspection', 
            year_folder, 
            month_folder, 
            client_folder,
            'Compliance',
            commodity_upper
        )
        os.makedirs(base_path, exist_ok=True)
        
        # Keep original filename - don't rename compliance documents
        safe_filename = filename
        file_path = os.path.join(base_path, safe_filename)
        
        # Download file if it doesn't exist
        if not os.path.exists(file_path):
            drive_service = GoogleDriveService()
            drive_service.download_file(file_id, file_path, request=request)
            
            # Check if downloaded file is a ZIP and organize it automatically
            if filename.lower().endswith('.zip'):
                # Check if auto-organization is enabled
                auto_organize_enabled = getattr(settings, 'AUTO_ORGANIZE_ZIP_FILES', True)
                if auto_organize_enabled:
                    print(f"🗂️ Auto-organizing ZIP file: {filename}")
                    try:
                        organize_zip_file_automatically(file_path, client_name, inspection_date, commodity_upper)
                    except Exception as e:
                        print(f"⚠️ Auto-organization failed for {filename}: {e}")
                        # Continue anyway - the ZIP file is still downloaded
                else:
                    print(f"📦 ZIP file downloaded but auto-organization is disabled: {filename}")
            
            return file_path
        else:
            return file_path  # Already exists
            
    except Exception as e:
        print(f"Error downloading compliance document: {e}")
        return None


@login_required
@role_required(['developer'])
def download_compliance_documents(request):
    """Download compliance documents with found links to organized folders."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        import json
        from ..models import FoodSafetyAgencyInspection, Client
        from datetime import date
        
        data = json.loads(request.body)
        commodity_filter = data.get('commodity', 'all')
        date_range = data.get('date_range', 'recent')
        download_all = data.get('download_all', False)
        
        # Get inspections with links found
        cutoff_date = date(2025, 1, 1)
        inspections = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection__gte=cutoff_date
        ).order_by('-date_of_inspection')
        
        if commodity_filter != 'all':
            inspections = inspections.filter(commodity__iexact=commodity_filter)
        
        # Build client mapping - use client name instead of client_id
        client_map = {}
        for client in Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code=''):
            key = normalize_client_name(client.name or '')  # Use client.name instead of client.client_id
            if key:
                client_map[key] = client.internal_account_code
        
        # Load Drive files
        file_lookup = load_drive_files_real(request)
        
        # Create compliance folder structure
        create_compliance_folder_structure()
        
        # Process and download documents
        downloaded_count = 0
        error_count = 0
        processed_count = 0
        
        # Process ALL inspections if download_all is True, otherwise limit to 100
        inspection_limit = None if download_all else 100
        inspections_to_process = inspections[:inspection_limit] if inspection_limit else inspections
        
        for inspection in inspections_to_process:
            try:
                processed_count += 1
                
                # Get account code
                client_key = normalize_client_name(inspection.client_name or '')
                account_code = client_map.get(client_key, '')
                
                if account_code:
                    # Find document link
                    document_link = find_document_link_apps_script_replica(
                        account_code,
                        inspection.commodity,
                        inspection.date_of_inspection,
                        file_lookup
                    )
                    
                    # If link found, extract file info and download
                    if document_link and '<a href=' in document_link:
                        # Extract file info from the link
                        for file_key, file_info in file_lookup.items():
                            if (file_info['commodity'].lower() == str(inspection.commodity).lower().strip() and
                                file_info['accountCode'] == account_code):
                                
                                # Extract file ID from URL
                                file_id = file_info['url'].split('/d/')[1].split('/')[0] if '/d/' in file_info['url'] else None
                                
                                if file_id:
                                    # Download to compliance folder
                                    downloaded_path = download_compliance_document(
                                        file_id,
                                        account_code,
                                        inspection.commodity,
                                        inspection.date_of_inspection,
                                        file_info['name'],
                                        inspection.client_name,
                                        request
                                    )
                                    
                                    if downloaded_path:
                                        downloaded_count += 1
                                        print(f"     ✅ Downloaded: {downloaded_path}")
                                    else:
                                        print(f"     ❌ Download failed")
                                else:
                                    print(f"     ❌ Could not extract file ID from URL")
                                break
                
            except Exception as e:
                error_count += 1
                print(f"Error processing inspection {inspection.remote_id}: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'Downloaded {downloaded_count} compliance documents from {processed_count} inspections',
            'processed': processed_count,
            'downloaded': downloaded_count,
            'errors': error_count,
            'folders_created': len(client_map)  # Approximate folder count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@role_required(['developer'])
def start_compliance_document_download(request):
    """Start background compliance document downloading."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        # Compliance service removed - OneDrive service handles this
        return JsonResponse({
            'success': False,
            'message': 'Compliance service has been removed. Use OneDrive service instead.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@role_required(['developer'])
def start_compliance_background(request):
    """Start background compliance document processing."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        # Compliance service removed - OneDrive service handles this
        return JsonResponse({
            'success': False,
            'message': 'Compliance service has been removed. Use OneDrive service instead.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@role_required(['developer'])
def stop_compliance_background(request):
    """Stop background compliance document processing."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        # Compliance service removed - OneDrive service handles this
        return JsonResponse({
            'success': False,
            'message': 'Compliance service has been removed. Use OneDrive service instead.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@role_required(['developer'])
def compliance_background_status(request):
    """Get status of background compliance processing."""
    try:
        # Compliance service removed - OneDrive service handles this
        return JsonResponse({
            'success': False,
            'message': 'Compliance service has been removed. Use OneDrive service instead.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@role_required(['developer'])
def process_all_compliance_documents(request):
    """Process ALL compliance documents at once with comprehensive logging."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        # Compliance service removed - OneDrive service handles this
        return JsonResponse({
            'success': False,
            'message': 'Compliance service has been removed. Use OneDrive service instead.',
            'processed': 0,
            'downloaded': 0,
            'folders_created': 0,
            'processing_time': '0',
            'errors': 0
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e),
            'processed': 0,
            'downloaded': 0,
            'folders_created': 0,
            'processing_time': '0',
            'errors': 1
        })


@login_required
def scheduled_sync_service_status(request):
    """Get scheduled sync service status."""
    try:
        from ..services.scheduled_sync_service import get_scheduled_sync_service_status
        
        status = get_scheduled_sync_service_status()
        return JsonResponse(status)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def start_scheduled_sync_service(request):
    """Start the scheduled sync service."""
    try:
        from ..services.scheduled_sync_service import start_scheduled_sync_service
        
        success, message = start_scheduled_sync_service()
        return JsonResponse({'success': success, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def stop_scheduled_sync_service(request):
    """Stop the scheduled sync service."""
    try:
        from ..services.scheduled_sync_service import stop_scheduled_sync_service
        
        success, message = stop_scheduled_sync_service()
        return JsonResponse({'success': success, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def run_manual_sync(request):
    """Run a manual sync of a specific type."""
    try:
        import json
        
        data = json.loads(request.body)
        sync_type = data.get('sync_type', '')
        
        if not sync_type:
            return JsonResponse({'success': False, 'error': 'Sync type not specified'})
        
        from ..services.scheduled_sync_service import run_manual_sync
        
        success, message = run_manual_sync(sync_type)
        return JsonResponse({'success': success, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def save_system_settings(request):
    """Save system settings."""
    try:
        import json
        from ..models import SystemSettings
        
        data = json.loads(request.body)
        
        # Get or create settings
        settings = SystemSettings.get_settings()
        
        # Update settings
        settings.auto_sync_enabled = data.get('auto_sync_enabled', False)
        settings.backup_frequency_days = data.get('backup_frequency_days', 7)
        settings.session_timeout_minutes = data.get('session_timeout_minutes', 30)
        settings.google_sheets_enabled = data.get('google_sheets_enabled', True)
        settings.sql_server_enabled = data.get('sql_server_enabled', True)
        settings.sync_interval_hours = data.get('sync_interval_hours', 24)
        settings.onedrive_enabled = data.get('onedrive_enabled', True)
        settings.onedrive_local_caching = data.get('onedrive_local_caching', True)
        settings.onedrive_cache_days = data.get('onedrive_cache_days', 60)
        settings.onedrive_auto_sync = data.get('onedrive_auto_sync', True)
        settings.onedrive_sync_interval_hours = data.get('onedrive_sync_interval_hours', 2)
        settings.onedrive_upload_delay_days = data.get('onedrive_upload_delay_days', 3)
        settings.onedrive_upload_delay_unit = data.get('onedrive_upload_delay_unit', 'days')
        settings.theme_mode = data.get('theme_mode', 'light')
        
        # Compliance settings
        settings.compliance_daily_sync_enabled = data.get('compliance_daily_sync_enabled', True)
        settings.compliance_skip_processed = data.get('compliance_skip_processed', True)
        
        settings.save()
        
        return JsonResponse({'success': True, 'message': 'System settings saved successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def start_daily_compliance_sync(request):
    """Start the daily compliance sync service."""
    try:
        from ..services.daily_compliance_sync import daily_sync_service
        
        if daily_sync_service.is_running:
            return JsonResponse({'success': False, 'message': 'Daily compliance sync is already running.'})
        
        daily_sync_service.start_daily_sync(manual_start=True)
        return JsonResponse({'success': True, 'message': 'Daily compliance sync started successfully.'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def stop_daily_compliance_sync(request):
    """Stop the daily compliance sync service."""
    try:
        from ..services.daily_compliance_sync import daily_sync_service
        
        if not daily_sync_service.is_running:
            return JsonResponse({'success': False, 'message': 'Daily compliance sync is not running.'})
        
        daily_sync_service.stop_daily_sync()
        return JsonResponse({'success': True, 'message': 'Daily compliance sync stopped successfully.'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def daily_compliance_sync_status(request):
    """Get the status of the daily compliance sync service."""
    try:
        from ..services.daily_compliance_sync import daily_sync_service
        
        status = daily_sync_service.get_status()
        return JsonResponse({'success': True, 'status': status})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_system_settings(request):
    """Get current system settings."""
    try:
        from ..models import SystemSettings
        
        settings = SystemSettings.get_settings()
        
        return JsonResponse({
            'success': True,
            'settings': {
                'auto_sync_enabled': settings.auto_sync_enabled,
                'backup_frequency_days': settings.backup_frequency_days,
                'session_timeout_minutes': settings.session_timeout_minutes,
                'google_sheets_enabled': settings.google_sheets_enabled,
                'sql_server_enabled': settings.sql_server_enabled,
                'sync_interval_hours': settings.sync_interval_hours,
                'compliance_sync_enabled': settings.compliance_sync_enabled,
                'compliance_sync_interval_hours': settings.compliance_sync_interval_hours,
                'compliance_processing_mode': settings.compliance_processing_mode,
                'compliance_daily_sync_enabled': settings.compliance_daily_sync_enabled,
                'compliance_skip_processed': settings.compliance_skip_processed,
                'compliance_last_processed_date': settings.compliance_last_processed_date.isoformat() if settings.compliance_last_processed_date else None,
                'onedrive_enabled': settings.onedrive_enabled,
                'onedrive_local_caching': settings.onedrive_local_caching,
                'onedrive_cache_days': settings.onedrive_cache_days,
                'onedrive_auto_sync': settings.onedrive_auto_sync,
                'onedrive_sync_interval_hours': settings.onedrive_sync_interval_hours,
                'onedrive_upload_delay_days': settings.onedrive_upload_delay_days,
                'onedrive_upload_delay_unit': settings.onedrive_upload_delay_unit,
                'theme_mode': settings.theme_mode
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_inspection_files_onedrive(client_name, inspection_date):
    """Get inspection files from OneDrive with Redis caching."""
    try:
        import os
        import json
        import requests
        from datetime import datetime
        from django.conf import settings
        from django.core.cache import cache
        import re
        
        # Parse date
        date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
        year_folder = date_obj.strftime('%Y')
        month_folder = date_obj.strftime('%B')
        
        # Use original client name for folder matching (folders now use original names)
        client_folder = client_name or 'Unknown Client'
        
        # First try to get from Redis cache (fastest)
        cache_key = f"client_files:{client_folder}:{year_folder}:{month_folder}"
        cached_files = cache.get(cache_key)
        
        if cached_files:
            print(f"🚀 Using cached files for {client_name} ({len(cached_files)} files)")
            return organize_cached_files(cached_files)
        
        # If not in cache, check local files first (faster than OneDrive API)
        local_files = get_inspection_files_local(client_name, inspection_date)
        if local_files and any(local_files.values()):
            print(f"💾 Using local files for {client_name}")
            return local_files
        
        # Finally, fall back to OneDrive API (slowest)
        print(f"☁️ Fetching from OneDrive for {client_name}")
        return get_inspection_files_onedrive_api(client_name, inspection_date)
        
    except Exception as e:
        print(f"❌ Error getting files: {e}")
        return None


def organize_cached_files(cached_files):
    """Organize cached files into categories."""
    try:
        files_by_category = {
            'rfi': [],
            'invoice': [],
            'lab': [],
            'retest': [],
            'compliance': []
        }
        
        for file_metadata in cached_files:
            if isinstance(file_metadata, str):
                # Parse JSON string
                file_metadata = json.loads(file_metadata)
            
            # Determine category based on path
            if 'Compliance' in file_metadata.get('local_path', ''):
                files_by_category['compliance'].append({
                    'name': file_metadata['name'],
                    'size': file_metadata['size'],
                    'url': file_metadata.get('onedrive_path', ''),
                    'relative_path': file_metadata['local_path'],
                    'source': file_metadata.get('source', 'onedrive'),
                    'modified': file_metadata.get('cached_at', '')
                })
            else:
                # For other categories, we'd need to determine from path
                # For now, add to compliance if it's a compliance file
                files_by_category['compliance'].append({
                    'name': file_metadata['name'],
                    'size': file_metadata['size'],
                    'url': file_metadata.get('onedrive_path', ''),
                    'relative_path': file_metadata['local_path'],
                    'source': file_metadata.get('source', 'onedrive'),
                    'modified': file_metadata.get('cached_at', '')
                })
        
        return files_by_category
        
    except Exception as e:
        print(f"❌ Error organizing cached files: {e}")
        return {}


def get_inspection_files_onedrive_api(client_name, inspection_date):
    """Get inspection files from OneDrive API (slow method)."""
    try:
        import os
        import json
        import requests
        from datetime import datetime
        from django.conf import settings
        import re
        
        # Load OneDrive tokens
        token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
        if not os.path.exists(token_file):
            return None
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        access_token = token_data.get('access_token')
        if not access_token:
            return None
        
        # Build OneDrive path
        date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
        year_folder = date_obj.strftime('%Y')
        month_folder = date_obj.strftime('%B')
        
        # Use original client name for folder matching (folders now use original names)
        client_folder = client_name or 'Unknown Client'
        
        onedrive_base = getattr(settings, 'ONEDRIVE_FOLDER', 'FoodSafety Agency Inspections')
        base_path = f"{onedrive_base}/inspection/{year_folder}/{month_folder}/{client_folder}"
        
        # Define file categories
        categories = {
            'rfi': 'rfi',
            'invoice': 'invoice',
            'lab': 'lab results',
            'retest': 'retest',
            'compliance': 'Compliance'
        }
        
        files_by_category = {}
        
        for category_key, folder_name in categories.items():
            files_by_category[category_key] = []
            
            if category_key == 'compliance':
                # Check compliance subfolders
                compliance_base = f"{base_path}/Compliance"
                for commodity in ['RAW', 'PMP', 'POULTRY', 'EGGS']:
                    commodity_path = f"{compliance_base}/{commodity}"
                    
                    # Get files from OneDrive
                    check_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{commodity_path}:/children"
                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    }
                    
                    response = requests.get(check_url, headers=headers)
                    if response.status_code == 200:
                        files = response.json().get('value', [])
                        for file_info in files:
                            if file_info.get('file'):
                                file_data = {
                                    'name': file_info['name'],
                                    'size': file_info.get('size', 0),
                                    'url': file_info.get('@microsoft.graph.downloadUrl', ''),
                                    'relative_path': f'Compliance/{commodity}/{file_info["name"]}',
                                    'onedrive_id': file_info.get('id', ''),
                                    'source': 'onedrive'
                                }
                                files_by_category[category_key].append(file_data)
            else:
                # Check regular category folder
                category_path = f"{base_path}/{folder_name}"
                
                # Get files from OneDrive
                check_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{category_path}:/children"
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(check_url, headers=headers)
                if response.status_code == 200:
                    files = response.json().get('value', [])
                    for file_info in files:
                        if file_info.get('file'):
                            file_data = {
                                'name': file_info['name'],
                                'size': file_info.get('size', 0),
                                'url': file_info.get('@microsoft.graph.downloadUrl', ''),
                                'relative_path': f'{folder_name}/{file_info["name"]}',
                                'onedrive_id': file_info.get('id', ''),
                                'source': 'onedrive'
                            }
                            files_by_category[category_key].append(file_data)
        
        return files_by_category
        
    except Exception as e:
        return None


def get_inspection_files_local(client_name, inspection_date):
    """Get inspection files from local media folder using optimized structure with caching."""
    # FORCE CACHE CLEAR to prevent stale file data
    from django.core.cache import cache
    cache.delete('inspection_files_cache')
    print(f"🧹 [BACKEND] Cleared inspection files cache for {client_name}")
    
    try:
        import os
        from datetime import datetime
        from django.conf import settings
        from django.core.cache import cache
        import re
        
        # Parse date and build folder path
        date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
        year_folder = date_obj.strftime('%Y')
        month_folder = date_obj.strftime('%B')
        
        # Use original client name for folder matching (folders now use original names)
        client_folder = client_name or 'Unknown Client'
        
        # Create cache key for this specific client/date combination
        cache_key = f"local_files:{client_folder}:{year_folder}:{month_folder}"
        
        # Try to get from cache first (fastest - 10 minute cache)
        cached_files = cache.get(cache_key)
        if cached_files:
            total_cached = sum(len(files) for files in cached_files.values())
            print(f"🚀 Using cached local files for {client_name} ({total_cached} files)")
            return cached_files
        
        print(f"🔍 Scanning files for: {client_name} ({inspection_date})")
        
        # Base client path - use correct structure: media/inspection/YYYY/Month/ClientName/
        client_base_path = os.path.join(
                settings.MEDIA_ROOT,
                'inspection',
                year_folder,
                month_folder,
                client_folder
            )
        
        # Define file categories
        categories = {
            'rfi': 'rfi',
            'invoice': 'invoice',
            'lab': 'lab results',
            'retest': 'retest',
            'compliance': 'Compliance'
        }
        
        files_by_category = {}
        
        # Initialize categories
        for category_key in categories.keys():
            files_by_category[category_key] = []
        
        # Find the actual client path (optimized with early exit)
        actual_client_path = None
        
        # First try the exact path
        if os.path.exists(client_base_path):
            actual_client_path = client_base_path
        else:
            # Try to find client folder with optimized search
            month_path = os.path.join(settings.MEDIA_ROOT, 'inspection', year_folder, month_folder)
            if os.path.exists(month_path):
                try:
                    # Use listdir with error handling and early exit
                    for folder_name in os.listdir(month_path):
                        folder_path = os.path.join(month_path, folder_name)
                        if os.path.isdir(folder_path):
                            # Use exact matching since folders now use original client names
                            if folder_name == client_folder:
                                actual_client_path = folder_path
                                break
                except (OSError, PermissionError):
                    print(f"❌ Error accessing month folder: {month_path}")
                    # Cache empty result to avoid repeated failed scans
                    cache.set(cache_key, files_by_category, 300)  # Cache for 5 minutes
                    return files_by_category
        
        if not actual_client_path:
            print(f"❌ No client folder found for: {client_folder}")
            # Cache empty result to avoid repeated failed scans
            cache.set(cache_key, files_by_category, 300)  # Cache for 5 minutes
            return files_by_category
        
        # Scan for files in each category (optimized with error handling)
        # Use only one folder structure to avoid duplicates
        folder_structures = [
            {'rfi': 'rfi', 'invoice': 'invoice', 'lab': 'lab results', 'retest': 'retest', 'compliance': 'Compliance'}
        ]
        
        # First check top-level folders
        for structure in folder_structures:
            for category_key, folder_name in structure.items():
                if category_key == 'compliance':
                    # Check compliance subfolders for all commodities
                    compliance_base = os.path.join(actual_client_path, 'Compliance')
                    if os.path.exists(compliance_base):
                        try:
                            # Check for any commodity folders
                            for commodity_folder in os.listdir(compliance_base):
                                commodity_path = os.path.join(compliance_base, commodity_folder)
                                if os.path.isdir(commodity_path):
                                    for filename in os.listdir(commodity_path):
                                        file_path = os.path.join(commodity_path, filename)
                                        if os.path.isfile(file_path):
                                            file_info = get_file_info(file_path, f'Compliance/{commodity_folder}')
                                            files_by_category[category_key].append(file_info)
                        except (OSError, PermissionError):
                            print(f"⚠️ Error accessing compliance folder: {compliance_base}")
                            continue
                else:
                    # Check regular category folder
                    category_path = os.path.join(actual_client_path, folder_name)
                    if os.path.exists(category_path):
                        try:
                            # Use listdir with error handling
                            for filename in os.listdir(category_path):
                                file_path = os.path.join(category_path, filename)
                                if os.path.isfile(file_path):
                                    file_info = get_file_info(file_path, folder_name)
                                    files_by_category[category_key].append(file_info)
                        except (OSError, PermissionError):
                            print(f"⚠️ Error accessing category folder: {category_path}")
                            continue
        
        # Also check nested Inspection-XXXX folders for files
        try:
            for item in os.listdir(actual_client_path):
                if item.startswith('Inspection-') and os.path.isdir(os.path.join(actual_client_path, item)):
                    inspection_folder = os.path.join(actual_client_path, item)
                    print(f"🔍 [FILES] Checking nested folder: {item}")
                    
                    # Check each category in the nested folder
                    for structure in folder_structures:
                        for category_key, folder_name in structure.items():
                            if category_key == 'compliance':
                                # Check compliance subfolders in nested folder
                                nested_compliance_base = os.path.join(inspection_folder, 'Compliance')
                                if os.path.exists(nested_compliance_base):
                                    try:
                                        # Check for any commodity folders
                                        for commodity_folder in os.listdir(nested_compliance_base):
                                            commodity_path = os.path.join(nested_compliance_base, commodity_folder)
                                            if os.path.isdir(commodity_path):
                                                for filename in os.listdir(commodity_path):
                                                    file_path = os.path.join(commodity_path, filename)
                                                    if os.path.isfile(file_path):
                                                        file_info = get_file_info(file_path, f'{item}/Compliance/{commodity_folder}')
                                                        files_by_category[category_key].append(file_info)
                                                        print(f"✅ [FILES] Found compliance file in nested folder: {filename}")
                                    except (OSError, PermissionError):
                                        print(f"⚠️ Error accessing nested compliance folder: {nested_compliance_base}")
                                        continue
                            else:
                                # Check regular category folder in nested folder
                                nested_category_path = os.path.join(inspection_folder, folder_name)
                                if os.path.exists(nested_category_path):
                                    try:
                                        for filename in os.listdir(nested_category_path):
                                            file_path = os.path.join(nested_category_path, filename)
                                            if os.path.isfile(file_path):
                                                file_info = get_file_info(file_path, f'{item}/{folder_name}')
                                                files_by_category[category_key].append(file_info)
                                                print(f"✅ [FILES] Found {category_key} file in nested folder: {filename}")
                                    except (OSError, PermissionError):
                                        print(f"⚠️ Error accessing nested category folder: {nested_category_path}")
                                        continue
        except (OSError, PermissionError):
            print(f"⚠️ Error accessing nested folders in: {actual_client_path}")
        
        # Cache the results for 10 minutes to improve performance
        cache.set(cache_key, files_by_category, 600)
        
        # Debug: Print summary
        total_files = sum(len(files) for files in files_by_category.values())
        print(f"📊 Total files found: {total_files} (cached for 10 minutes)")
        
        return files_by_category
        
    except Exception as e:
        print(f"❌ Error in get_inspection_files_local: {e}")
        return {}


@login_required
def populate_six_month_files(request):
    """Populate files for all inspections in the last 6 months."""
    try:
        from datetime import datetime, timedelta
        import os
        from ..models import FoodSafetyAgencyInspection
        
        # Get inspections from last 6 months
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_inspections = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection__gte=six_months_ago
        ).values('client_name', 'date_of_inspection').distinct()
        
        # Use the correct inspection structure: media/inspection/YYYY/Month/ClientName/
        total_folders_created = 0
        
        for inspection in recent_inspections:
            try:
                # Create folder structure using the correct format
                year_folder = inspection['date_of_inspection'].strftime('%Y')
                month_folder = inspection['date_of_inspection'].strftime('%B')
                
                # Use original client name for folder structure (folders now use original names)
                client_folder = inspection['client_name'] or 'Unknown Client'
                
                folder_path = os.path.join(
                    settings.MEDIA_ROOT, 
                    'inspection', 
                    year_folder, 
                    month_folder, 
                    client_folder
                )
                os.makedirs(folder_path, exist_ok=True)
                total_folders_created += 1
                
                # Try to fetch files for this inspection
                try:
                    files = get_inspection_files_local(inspection['client_name'], inspection['date_of_inspection'].strftime('%Y-%m-%d'))
                    if files:
                        print(f"Found {len(files)} files for {inspection['client_name']} - {inspection['date_of_inspection']}")
                except Exception as e:
                    print(f"Error fetching files for {inspection['client_name']}: {e}")
                    
            except Exception as e:
                print(f"Error creating folder for {inspection['client_name']}: {e}")
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Created {total_folders_created} inspection folders for the last 6 months',
            'folders_created': total_folders_created
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def pull_six_month_data_from_google_drive(request):
    """Pull ALL 6-Month Data from Google Drive and store locally."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        from datetime import datetime, timedelta
        from ..models import FoodSafetyAgencyInspection, Client
        from ..services.google_drive_service import GoogleDriveService
        import os
        import re
        
        print("🚀 STARTING 6-MONTH GOOGLE DRIVE DATA PULL")
        print("=" * 60)
        
        # Get inspections from last 6 months
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_inspections = FoodSafetyAgencyInspection.objects.filter(
            date_of_inspection__gte=six_months_ago
        ).order_by('-date_of_inspection')
        
        total_inspections = recent_inspections.count()
        print(f"📊 Found {total_inspections:,} inspections from the last 6 months")
        
        if total_inspections == 0:
            return JsonResponse({
                'success': True,
                'message': 'No inspections found in the last 6 months',
                'files_downloaded': 0,
                'folders_created': 0
            })
        
        # Build client mapping
        client_map = {}
        for client in Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code=''):
            key = normalize_client_name(client.name or '')
            if key:
                client_map[key] = client.internal_account_code
        
        print(f"👥 Loaded {len(client_map):,} client mappings")
        
        # Initialize Google Drive service
        drive_service = GoogleDriveService()
        if not drive_service.authenticate(request):
            return JsonResponse({
                'success': False,
                'error': 'Failed to authenticate with Google Drive. Please check your credentials.'
            })
        
        # Load Drive files
        print("☁️ Loading Google Drive files...")
        file_lookup = load_drive_files_real(request)
        print(f"📁 Loaded {len(file_lookup):,} files from Google Drive")
        
        # Track statistics
        files_downloaded = 0
        folders_created = 0
        errors = 0
        processed_count = 0
        
        # Process each inspection
        for inspection in recent_inspections:
            try:
                processed_count += 1
                
                # Progress logging every 50 inspections
                if processed_count % 50 == 0:
                    print(f"⏳ Progress: {processed_count:,}/{total_inspections:,} ({(processed_count/total_inspections*100):.1f}%) - Downloaded: {files_downloaded:,}")
                
                # Get account code for this client
                client_key = normalize_client_name(inspection.client_name or '')
                account_code = client_map.get(client_key, '')
                
                if not account_code:
                    continue
                
                # Find matching files in Google Drive
                matching_files = []
                for file_key, file_info in file_lookup.items():
                    if (file_info['commodity'].lower() == str(inspection.commodity).lower().strip() and
                        file_info['accountCode'] == account_code):
                        matching_files.append(file_info)
                
                if not matching_files:
                    continue
                
                # Create folder structure for this inspection
                year_folder = inspection.date_of_inspection.strftime("%Y")
                month_folder = inspection.date_of_inspection.strftime("%B")
                
                # Use original client name for folder structure
                client_folder = inspection.client_name or 'Unknown Client'
                
                # Create base folder structure
                base_path = os.path.join(
                    settings.MEDIA_ROOT,
                    'inspection',
                    year_folder,
                    month_folder,
                    client_folder,
                    'Compliance',
                    str(inspection.commodity).upper()
                )
                os.makedirs(base_path, exist_ok=True)
                folders_created += 1
                
                # Download each matching file
                for file_info in matching_files:
                    try:
                        # Extract file ID from URL
                        file_id = file_info.get('file_id') or file_info.get('url', '').split('/d/')[1].split('/')[0] if '/d/' in file_info.get('url', '') else None
                        
                        if not file_id:
                            continue
                        
                        # Keep original filename - don't rename compliance documents
                        safe_filename = file_info['name']
                        file_path = os.path.join(base_path, safe_filename)
                        
                        # Download file if it doesn't exist
                        if not os.path.exists(file_path):
                            success = drive_service.download_file(file_id, file_path, request)
                            if success:
                                files_downloaded += 1
                                if files_downloaded % 10 == 0:
                                    print(f"📤 Downloaded {files_downloaded:,} files so far...")
                            else:
                                errors += 1
                        else:
                            # File already exists, count as downloaded
                            files_downloaded += 1
                            
                    except Exception as e:
                        errors += 1
                        print(f"❌ Error downloading file {file_info.get('name', 'unknown')}: {e}")
                
            except Exception as e:
                errors += 1
                print(f"❌ Error processing inspection {inspection.remote_id}: {e}")
        
        # Final statistics
        print("=" * 60)
        print("🎯 6-MONTH GOOGLE DRIVE PULL COMPLETE")
        print(f"📊 Total Inspections Processed: {processed_count:,}")
        print(f"📁 Folders Created: {folders_created:,}")
        print(f"📤 Files Downloaded: {files_downloaded:,}")
        print(f"❌ Errors: {errors:,}")
        print("=" * 60)
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully pulled 6-month data from Google Drive! Downloaded {files_downloaded:,} files and created {folders_created:,} folders.',
            'files_downloaded': files_downloaded,
            'folders_created': folders_created,
            'inspections_processed': processed_count,
            'errors': errors
        })
        
    except Exception as e:
        print(f"❌ Fatal error in 6-month data pull: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Fatal error: {str(e)}'
        })


@login_required
def get_inspection_files(request):
    """Get all files for a specific grouped inspection (client + date) and store them locally."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        import json
        import os
        from datetime import datetime, timedelta
        from django.conf import settings
        from ..models import FoodSafetyAgencyInspection
        
        data = json.loads(request.body)
        group_id = data.get('group_id', '')
        client_name = data.get('client_name', '')
        inspection_date = data.get('inspection_date', '')
        
        # Create media folder structure for this inspection using correct format
        from datetime import datetime
        import re
        
        # Parse date and build folder path
        date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
        year_folder = date_obj.strftime('%Y')
        month_folder = date_obj.strftime('%B')
        
        # Use original client name for folder structure (folders now use original names)
        client_folder = client_name or 'Unknown Client'
        
        inspection_folder = os.path.join(
            settings.MEDIA_ROOT, 
            'inspection', 
            year_folder, 
            month_folder, 
            client_folder
        )
        os.makedirs(inspection_folder, exist_ok=True)
        
        # Get files from local storage
        local_files = get_inspection_files_local(client_name, inspection_date)
        
        # Since files are now fetched in the background when the inspections page loads,
        # we just return the local files that are already available
        # Check if there are actually any files (not just empty arrays)
        has_files = local_files and any(file_list for file_list in local_files.values() if file_list)
        if not has_files:
            return JsonResponse({
                'success': True,
                'files': [],
                'client_name': client_name,
                'inspection_date': inspection_date,
                'source': 'local',
                'message': 'Files are being fetched in the background for all 6-month inspections. Check back in a few minutes.'
            })
        
        return JsonResponse({
            'success': True,
            'files': local_files,
            'client_name': client_name,
            'inspection_date': inspection_date,
            'source': 'local'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def delete_inspection_file(request):
    """Delete a specific file from an inspection."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        import json
        import os
        import re
        from django.conf import settings
        from django.core.cache import cache
        
        data = json.loads(request.body)
        file_path = data.get('file_path', '')
        client_name = data.get('client_name', '')
        inspection_date = data.get('inspection_date', '')
        
        print(f"🗑️ Delete request: file_path={file_path}, client_name={client_name}, inspection_date={inspection_date}")
        
        if not file_path or not client_name or not inspection_date:
            return JsonResponse({'success': False, 'error': 'Missing required parameters'})
        
        # Prevent deletion of compliance documents
        if '/Compliance/' in file_path or file_path.lower().startswith('compliance/'):
            print(f"🚫 BLOCKED: Attempted to delete compliance document: {file_path}")
            return JsonResponse({
                'success': False, 
                'error': 'Compliance documents cannot be deleted for security and audit purposes.'
            })
        
        # Security check: ensure the file path is within the media directory
        media_root = settings.MEDIA_ROOT
        
        print(f"🗑️ Media root: {media_root}")
        print(f"🗑️ Requested file path: {file_path}")
        print(f"🗑️ Client name: {client_name}")
        print(f"🗑️ Inspection date: {inspection_date}")
        
        # Parse inspection date to get year and month
        from datetime import datetime
        try:
            date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
            year = date_obj.strftime('%Y')
            month = date_obj.strftime('%B')
        except:
            return JsonResponse({'success': False, 'error': 'Invalid inspection date format'})
        
        # Use original client name for folder matching (folders now use original names)
        client_folder_pattern = client_name or 'Unknown Client'
        
        print(f"🗑️ Parsed date: year={year}, month={month}")
        print(f"🗑️ Client folder pattern: {client_folder_pattern}")
        
        # Try to find the file using the provided information
        full_file_path = None
        
        # First, try the exact path if it looks like a full path
        if file_path.startswith('inspection/'):
            potential_path = os.path.join(media_root, file_path)
            if os.path.exists(potential_path):
                full_file_path = potential_path
                print(f"🗑️ Found file using exact path: {full_file_path}")
            else:
                # Try alternative path construction (same as file display)
                alternative_path = os.path.join(media_root, 'inspection', year, month, client_folder_pattern, file_path.split('/')[-2], file_path.split('/')[-1])
                if os.path.exists(alternative_path):
                    full_file_path = alternative_path
                    print(f"🗑️ Found file using alternative path: {full_file_path}")
        
        # If not found, search for the file using client name and date
        if not full_file_path:
            print(f"🗑️ Searching for file using client name and date...")
            
            # Build the expected path structure
            month_path = os.path.join(media_root, 'inspection', year, month)
            print(f"🗑️ Month path: {month_path}")
            
            if os.path.exists(month_path):
                try:
                    # Find client folder
                    for folder_name in os.listdir(month_path):
                        folder_path = os.path.join(month_path, folder_name)
                        if os.path.isdir(folder_path):
                            # Check if folder name matches client pattern
                            folder_pattern = re.sub(r'[^a-zA-Z0-9_]', '', folder_name).lower()
                            client_pattern = client_folder_pattern.lower()
                            
                            if (folder_pattern == client_pattern or 
                                client_pattern in folder_pattern or
                                folder_pattern in client_pattern):
                                print(f"🗑️ Found matching client folder: {folder_name}")
                                
                                # Search for the file in this folder
                                print(f"🗑️ Searching in folder: {folder_path}")
                                print(f"🗑️ Looking for filename: {os.path.basename(file_path)}")
                                
                                for root, dirs, files in os.walk(folder_path):
                                    print(f"🗑️ Checking directory: {root}")
                                    print(f"🗑️ Files in directory: {files}")
                                    
                                    for file in files:
                                        if file == os.path.basename(file_path):
                                            full_file_path = os.path.join(root, file)
                                            print(f"🗑️ Found file at: {full_file_path}")
                                            break
                                    if full_file_path is not None:
                                        break
                                if full_file_path is not None:
                                    break
                except (OSError, PermissionError) as e:
                    print(f"❌ Error accessing month folder: {e}")
        
        if not full_file_path:
            print(f"❌ Could not find file: {file_path}")
            return JsonResponse({'success': False, 'error': 'File not found'})
        
        # Normalize paths to prevent directory traversal attacks
        full_file_path = os.path.normpath(full_file_path)
        media_root = os.path.normpath(media_root)
        
        print(f"🗑️ Final normalized full path: {full_file_path}")
        print(f"🗑️ Final normalized media root: {media_root}")
        
        if not full_file_path.startswith(media_root):
            print(f"❌ Delete 404: Invalid file path - not within media root")
            return JsonResponse({'success': False, 'error': 'Invalid file path'})
        
        # Check if file exists (should already be confirmed above)
        print(f"🗑️ Final check - file exists: {os.path.exists(full_file_path)}")
        
        # Delete the file
        try:
            os.remove(full_file_path)
            print(f"🗑️ Deleted file: {file_path}")
            
            # Clear database upload records based on file type
            from ..models import FoodSafetyAgencyInspection
            from datetime import datetime
            
            try:
                # Parse the inspection date
                date_obj = datetime.strptime(inspection_date, '%Y-%m-%d').date()
                
                # Find matching inspections
                inspections = FoodSafetyAgencyInspection.objects.filter(
                    client_name=client_name,
                    date_of_inspection=date_obj
                )
                
                # Determine document type and clear appropriate fields
                if '/rfi/' in file_path.lower():
                    inspections.update(rfi_uploaded_by=None, rfi_uploaded_date=None)
                    print(f"🔄 Cleared RFI upload records for {inspections.count()} inspections")
                elif '/invoice/' in file_path.lower():
                    inspections.update(invoice_uploaded_by=None, invoice_uploaded_date=None)
                    print(f"🔄 Cleared Invoice upload records for {inspections.count()} inspections")
                elif '/lab/' in file_path.lower():
                    inspections.update(lab_uploaded_by=None, lab_uploaded_date=None)
                    print(f"🔄 Cleared Lab upload records for {inspections.count()} inspections")
                    
            except Exception as db_error:
                print(f"⚠️ Warning: Could not update database records: {db_error}")
                # Continue with file deletion success even if DB update fails
            
            # Clear relevant caches
            cache.delete(f"shipment_list_{request.user.id}_{request.user.role}")
            cache.delete("filter_options")
            
            return JsonResponse({
                'success': True, 
                'message': f'File {os.path.basename(file_path)} deleted successfully',
                'database_updated': True
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Failed to delete file: {str(e)}'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_client_all_files(request):
    """Get ALL files for a client across all their inspections from local PC."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        import json
        import os
        from datetime import datetime
        from django.conf import settings
        from ..models import FoodSafetyAgencyInspection
        import re
        
        data = json.loads(request.body)
        client_name = data.get('client_name', '')
        
        if not client_name:
            return JsonResponse({'success': False, 'error': 'Client name is required'})
        
        print(f"🔍 Getting ALL files for client: {client_name}")
        
        # Use exact client name for matching (folders now use original names)
        client_folder_pattern = client_name
        
        print(f"🔍 Looking for client folder: {client_folder_pattern}")
        
        # Base inspection path
        inspection_base = os.path.join(settings.MEDIA_ROOT, 'inspection')
        
        if not os.path.exists(inspection_base):
            return JsonResponse({
                'success': True,
                'files': {},
                'client_name': client_name,
                'message': 'No inspection folder found. Run the 6-month data pull first.'
            })
        
        # Define file categories
        categories = {
            'rfi': 'rfi',
            'invoice': 'invoice', 
            'lab': 'lab results',
            'retest': 'retest',
            'compliance': 'Compliance'
        }
        
        files_by_category = {key: [] for key in categories.keys()}
        total_files = 0
        inspections_found = []
        added_files = {}  # Track added files to avoid true duplicates (filename + size)
        
        # Search through all year/month folders
        for year_folder in os.listdir(inspection_base):
            year_path = os.path.join(inspection_base, year_folder)
            if not os.path.isdir(year_path):
                continue
                
            for month_folder in os.listdir(year_path):
                month_path = os.path.join(year_path, month_folder)
                if not os.path.isdir(month_path):
                    continue
                
                # Look for client folder (exact match or similar)
                for folder_name in os.listdir(month_path):
                    folder_path = os.path.join(month_path, folder_name)
                    if not os.path.isdir(folder_path):
                        continue
                    
                    # Use exact matching since folders now use original client names
                    if folder_name == client_folder_pattern:
                        
                        print(f"✅ Found client folder: {folder_name} in {year_folder}/{month_folder}")
                        inspections_found.append(f"{year_folder}/{month_folder}")
                        
                        # Search for files in this client folder
                        for category_key, category_name in categories.items():
                            if category_key == 'compliance':
                                # Check compliance subfolders for all commodities
                                compliance_base = os.path.join(folder_path, 'Compliance')
                                if os.path.exists(compliance_base):
                                    for commodity_folder in os.listdir(compliance_base):
                                        commodity_path = os.path.join(compliance_base, commodity_folder)
                                        if os.path.isdir(commodity_path):
                                            for filename in os.listdir(commodity_path):
                                                file_path = os.path.join(commodity_path, filename)
                                                if os.path.isfile(file_path):
                                                    # Get file info
                                                    file_info = get_file_info(file_path, f'Compliance/{commodity_folder}')
                                                    
                                                    # Check for duplicates using filename + size
                                                    file_key = f"{filename}_{file_info.get('size', 0)}"
                                                    
                                                    if file_key not in added_files:
                                                        file_info['inspection_period'] = f"{year_folder}/{month_folder}"
                                                        file_info['commodity'] = commodity_folder
                                                        files_by_category[category_key].append(file_info)
                                                        added_files[file_key] = True
                                                        total_files += 1
                                                        print(f"   Added compliance: {filename} ({file_info.get('size', 0)} bytes)")
                                                    else:
                                                        print(f"   Skipped compliance (duplicate): {filename} (same name and size already added)")
                            else:
                                # Check regular category folder
                                category_path = os.path.join(folder_path, category_key)
                                if os.path.exists(category_path):
                                    for filename in os.listdir(category_path):
                                        file_path = os.path.join(category_path, filename)
                                        if os.path.isfile(file_path):
                                            file_info = get_file_info(file_path, category_key)
                                            file_info['inspection_period'] = f"{year_folder}/{month_folder}"
                                            files_by_category[category_key].append(file_info)
                                            total_files += 1
        
        # Sort files by date (newest first)
        for category_key in files_by_category:
            files_by_category[category_key].sort(key=lambda x: x.get('modified_time', 0), reverse=True)
        
        print(f"📊 Found {total_files} total files across {len(inspections_found)} inspection periods")
        for category, files in files_by_category.items():
            print(f"  {categories[category]}: {len(files)} files")
        
        return JsonResponse({
            'success': True,
            'files': files_by_category,
            'client_name': client_name,
            'total_files': total_files,
            'inspections_found': inspections_found,
            'categories': categories,
            'source': 'local'
        })
        
    except Exception as e:
        print(f"❌ Error in get_client_all_files: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_page_clients_files(request):
    """Get files for multiple clients from current page only - optimized for pagination."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        import json
        import os
        from datetime import datetime
        from django.conf import settings
        import re
        
        data = json.loads(request.body)
        client_names = data.get('client_names', [])
        target_client = data.get('target_client', '')
        
        if not client_names:
            return JsonResponse({'success': False, 'error': 'Client names list is required'})
        
        if not target_client:
            return JsonResponse({'success': False, 'error': 'Target client name is required'})
        
        print(f"🔍 Getting files for target client: {target_client}")
        print(f"📄 Checking only {len(client_names)} clients from current page")
        
        # Use exact client name for matching (folders now use original names)
        target_client_pattern = target_client
        
        # Sanitize all client names for comparison
        client_patterns = []
        for client_name in client_names:
            pattern = re.sub(r'[^a-zA-Z0-9_]', '_', client_name)
            pattern = re.sub(r'_+', '_', pattern).strip('_')
            client_patterns.append(pattern.lower())
        
        print(f"🔍 Looking for target client folder: {target_client_pattern}")
        print(f"📋 Client patterns to check: {client_patterns}")
        
        # Base inspection path
        inspection_base = os.path.join(settings.MEDIA_ROOT, 'inspection')
        
        if not os.path.exists(inspection_base):
            return JsonResponse({
                'success': True,
                'files': {},
                'client_name': target_client,
                'message': 'No inspection folder found. Run the 6-month data pull first.'
            })
        
        # Define file categories
        categories = {
            'rfi': 'rfi',
            'invoice': 'invoice', 
            'lab': 'lab results',
            'retest': 'retest',
            'compliance': 'Compliance'
        }
        
        files_by_category = {key: [] for key in categories.keys()}
        total_files = 0
        inspections_found = []
        
        # Search through all year/month folders - but only check folders that match our client list
        for year_folder in os.listdir(inspection_base):
            year_path = os.path.join(inspection_base, year_folder)
            if not os.path.isdir(year_path):
                continue
                
            for month_folder in os.listdir(year_path):
                month_path = os.path.join(year_path, month_folder)
                if not os.path.isdir(month_path):
                    continue
                
                # Look for client folders that match our target client
                for folder_name in os.listdir(month_path):
                    folder_path = os.path.join(month_path, folder_name)
                    if not os.path.isdir(folder_path):
                        continue
                    
                    # Use exact matching since folders now use original client names
                    if folder_name == target_client_pattern:
                        
                        print(f"✅ Found target client folder: {folder_name} in {year_folder}/{month_folder}")
                        inspections_found.append(f"{year_folder}/{month_folder}")
                        
                        # Search for files in this client folder
                        for category_key, category_name in categories.items():
                            if category_key == 'compliance':
                                # Check compliance subfolders for all commodities
                                compliance_base = os.path.join(folder_path, 'Compliance')
                                if os.path.exists(compliance_base):
                                    for commodity_folder in os.listdir(compliance_base):
                                        commodity_path = os.path.join(compliance_base, commodity_folder)
                                        if os.path.isdir(commodity_path):
                                            for filename in os.listdir(commodity_path):
                                                file_path = os.path.join(commodity_path, filename)
                                                if os.path.isfile(file_path):
                                                    file_info = get_file_info(file_path, f'Compliance/{commodity_folder}')
                                                    file_info['inspection_period'] = f"{year_folder}/{month_folder}"
                                                    file_info['commodity'] = commodity_folder
                                                    files_by_category[category_key].append(file_info)
                                                    total_files += 1
                            else:
                                # Check regular category folder
                                category_path = os.path.join(folder_path, category_key)
                                if os.path.exists(category_path):
                                    for filename in os.listdir(category_path):
                                        file_path = os.path.join(category_path, filename)
                                        if os.path.isfile(file_path):
                                            file_info = get_file_info(file_path, category_key)
                                            file_info['inspection_period'] = f"{year_folder}/{month_folder}"
                                            files_by_category[category_key].append(file_info)
                                            total_files += 1
        
        # Sort files by date (newest first)
        for category_key in files_by_category:
            files_by_category[category_key].sort(key=lambda x: x.get('modified_time', 0), reverse=True)
        
        # Determine file status for color coding
        has_rfi = len(files_by_category.get('rfi', [])) > 0
        has_invoice = len(files_by_category.get('invoice', [])) > 0
        has_lab = len(files_by_category.get('lab', [])) > 0
        has_retest = len(files_by_category.get('retest', [])) > 0
        has_compliance = len(files_by_category.get('compliance', [])) > 0
        
        # Determine status based on user requirements:
        # Green: ALL required documents (RFI, Invoice, Lab, Compliance) exist
        # Orange: Only compliance document exists (or compliance + some others but not all)
        # Blue: Has RFI/Invoice/Lab but no compliance documents
        # Red: No files at all
        if total_files == 0:
            file_status = 'no_files'  # Red - no files at all
        elif has_rfi and has_invoice and has_lab and has_compliance:
            file_status = 'all_files'  # Green - all required documents exist
        elif has_compliance:
            file_status = 'compliance_only'  # Orange - compliance exists (with or without other docs)
        elif has_rfi or has_invoice or has_lab or has_retest:
            file_status = 'partial_files'  # Blue - has some files but no compliance
        else:
            file_status = 'no_files'  # Red - no files at all
        
        print(f"📊 Found {total_files} total files across {len(inspections_found)} inspection periods")
        print(f"🎨 File status: {file_status}")
        for category, files in files_by_category.items():
            print(f"  {categories[category]}: {len(files)} files")
        
        return JsonResponse({
            'success': True,
            'files': files_by_category,
            'client_name': target_client,
            'total_files': total_files,
            'inspections_found': inspections_found,
            'categories': categories,
            'source': 'local',
            'optimized': True,
            'clients_checked': len(client_names),
            'file_status': file_status,
            'has_rfi': has_rfi,
            'has_invoice': has_invoice,
            'has_lab': has_lab,
            'has_retest': has_retest,
            'has_compliance': has_compliance
        })
        
    except Exception as e:
        print(f"❌ Error in get_page_clients_files: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_page_clients_file_status(request):
    """Get file status for multiple clients from current page - optimized for bulk checking."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    # FORCE CACHE CLEAR to prevent stale file status data
    from django.core.cache import cache
    cache.delete('page_clients_status_cache')
    print("🧹 [BACKEND] Cleared file status cache to prevent stale data")
    
    # Add small delay to ensure files are fully written before detection
    import time
    time.sleep(0.5)  # 500ms delay to ensure file system is updated
    print("⏳ [BACKEND] Added delay to ensure files are fully written")
    
    try:
        import json
        import os
        from datetime import datetime
        from django.conf import settings
        import re
        
        data = json.loads(request.body)
        
        # Support both old and new formats for backwards compatibility
        client_date_combinations = data.get('client_date_combinations', [])
        
        # Legacy format support
        if not client_date_combinations:
            client_names = data.get('client_names', [])
            inspection_dates = data.get('inspection_dates', {})
            
            if client_names:
                # Convert legacy format to new format
                for client_name in client_names:
                    dates = inspection_dates.get(client_name, [])
                    if isinstance(dates, list):
                        for date in dates:
                            client_date_combinations.append({
                                'client_name': client_name,
                                'inspection_date': date,
                                'unique_key': f"{client_name}_{date}"
                            })
        
        if not client_date_combinations:
            return JsonResponse({'success': False, 'error': 'Client date combinations are required'})
        
        # Limit to reasonable number of combinations per request (prevent abuse)
        if len(client_date_combinations) > 50:
            client_date_combinations = client_date_combinations[:50]
            print(f"⚠️ [TERMINAL] Limited to first 50 combinations to prevent performance issues")
        
        print(f"🔍 [TERMINAL] Checking file status for {len(client_date_combinations)} client+date combinations")
        print(f"📋 [TERMINAL] Combinations: {[c.get('unique_key', 'unknown') for c in client_date_combinations[:5]]}...")  # Show first 5
        
        # Check cache first for bulk results (updated for new format)
        from django.core.cache import cache
        combination_keys = [c.get('unique_key', '') for c in client_date_combinations]
        cache_key = f"combination_status:{hash(tuple(sorted(combination_keys)))}"
        cached_result = cache.get(cache_key)
        if cached_result:
            print(f"🚀 [TERMINAL] Using cached status for {len(client_date_combinations)} combinations")
            return JsonResponse(cached_result)
        
        # Base inspection path
        inspection_base = os.path.join(settings.MEDIA_ROOT, 'inspection')
        
        if not os.path.exists(inspection_base):
            return JsonResponse({
                'success': True,
                'combination_statuses': {},
                'message': 'No inspection folder found. Run the 6-month data pull first.'
            })
        
        # Define file categories
        categories = ['rfi', 'invoice', 'lab', 'retest', 'compliance']
        
        combination_statuses = {}
        
        # Process each client+date combination individually
        for combination in client_date_combinations:
            client_name = combination.get('client_name')
            inspection_date = combination.get('inspection_date')
            unique_key = combination.get('unique_key')
            
            if not client_name or not inspection_date or not unique_key:
                print(f"⚠️ Invalid combination data: {combination}")
                continue
            try:
                print(f"🔍 [BUTTON] Checking {unique_key}: {client_name} on {inspection_date}")
                
                # Initialize results for this specific combination
                has_rfi = has_invoice = has_lab = has_retest = has_compliance = False
                file_status = 'no_files'
                
                # OPTIMIZATION 1: Database check first (fastest - no file system access)
                date_obj = datetime.strptime(str(inspection_date), '%Y-%m-%d').date()
                inspections = FoodSafetyAgencyInspection.objects.filter(
                    client_name=client_name,
                    date_of_inspection=date_obj
                )
                
                # Check database for upload records (super fast)
                has_rfi_db = inspections.filter(rfi_uploaded_by__isnull=False).exists()
                has_invoice_db = inspections.filter(invoice_uploaded_by__isnull=False).exists()
                # Note: lab_uploaded_by field doesn't exist in database, rely on directory check only
                
                # OPTIMIZATION 2: Try multiple folder variations (consistent with list_uploaded_files)
                year = date_obj.strftime('%Y')
                month = date_obj.strftime('%B')
                
                # Use exact client name since folders now use original names
                client_folder_variations = [client_name]
                
                # Check all folder variations for files for this specific date
                has_rfi_dir = has_invoice_dir = has_lab_dir = has_retest_dir = has_compliance_dir = False
                
                parent_path = os.path.join(inspection_base, year, month)
                if os.path.exists(parent_path):
                    for folder_variation in client_folder_variations:
                        test_path = os.path.join(parent_path, folder_variation)
                        if os.path.exists(test_path):
                            print(f"🔍 [BUTTON] Checking path for {inspection_date}: {test_path}")
                            
                            # Check for files in each document type folder (not just directory existence)
                            # Check both top-level and nested Inspection-XXXX folders
                            
                            # Check RFI files (check both uppercase and lowercase)
                            if not has_rfi_dir:
                                # Check top-level RFI folder (uppercase)
                                rfi_path = os.path.join(test_path, 'RFI')
                                has_rfi_dir = os.path.exists(rfi_path) and any(os.path.isfile(os.path.join(rfi_path, f)) for f in os.listdir(rfi_path)) if os.path.exists(rfi_path) else False
                                
                                # Check top-level rfi folder (lowercase)
                                if not has_rfi_dir:
                                    rfi_path = os.path.join(test_path, 'rfi')
                                    has_rfi_dir = os.path.exists(rfi_path) and any(os.path.isfile(os.path.join(rfi_path, f)) for f in os.listdir(rfi_path)) if os.path.exists(rfi_path) else False
                                    if has_rfi_dir:
                                        print(f"✅ [BUTTON] Found RFI files in lowercase folder: {rfi_path}")
                                    else:
                                        print(f"❌ [BUTTON] No RFI files in lowercase folder: {rfi_path}")
                                
                                # Also check nested Inspection-XXXX folders
                                if not has_rfi_dir:
                                    for item in os.listdir(test_path):
                                        if item.startswith('Inspection-') and os.path.isdir(os.path.join(test_path, item)):
                                            # Check both uppercase and lowercase
                                            nested_rfi_path = os.path.join(test_path, item, 'RFI')
                                            if not os.path.exists(nested_rfi_path):
                                                nested_rfi_path = os.path.join(test_path, item, 'rfi')
                                            if os.path.exists(nested_rfi_path) and any(os.path.isfile(os.path.join(nested_rfi_path, f)) for f in os.listdir(nested_rfi_path)):
                                                has_rfi_dir = True
                                                print(f"✅ [BUTTON] Found RFI files in nested folder {item}")
                                                break
                            
                            # Check Invoice files (check both uppercase and lowercase)
                            if not has_invoice_dir:
                                # Check top-level Invoice folder (uppercase)
                                invoice_path = os.path.join(test_path, 'Invoice')
                                has_invoice_dir = os.path.exists(invoice_path) and any(os.path.isfile(os.path.join(invoice_path, f)) for f in os.listdir(invoice_path)) if os.path.exists(invoice_path) else False
                                
                                # Check top-level invoice folder (lowercase)
                                if not has_invoice_dir:
                                    invoice_path = os.path.join(test_path, 'invoice')
                                    has_invoice_dir = os.path.exists(invoice_path) and any(os.path.isfile(os.path.join(invoice_path, f)) for f in os.listdir(invoice_path)) if os.path.exists(invoice_path) else False
                                    if has_invoice_dir:
                                        print(f"✅ [BUTTON] Found Invoice files in lowercase folder: {invoice_path}")
                                    else:
                                        print(f"❌ [BUTTON] No Invoice files in lowercase folder: {invoice_path}")
                                
                                # Also check nested Inspection-XXXX folders
                                if not has_invoice_dir:
                                    for item in os.listdir(test_path):
                                        if item.startswith('Inspection-') and os.path.isdir(os.path.join(test_path, item)):
                                            # Check both uppercase and lowercase
                                            nested_invoice_path = os.path.join(test_path, item, 'Invoice')
                                            if not os.path.exists(nested_invoice_path):
                                                nested_invoice_path = os.path.join(test_path, item, 'invoice')
                                            if os.path.exists(nested_invoice_path) and any(os.path.isfile(os.path.join(nested_invoice_path, f)) for f in os.listdir(nested_invoice_path)):
                                                has_invoice_dir = True
                                                print(f"✅ [BUTTON] Found Invoice files in nested folder {item}")
                                                break
                            
                            # Check Lab files (check multiple folder name variations)
                            if not has_lab_dir:
                                # Check top-level Lab folder (uppercase)
                                lab_path = os.path.join(test_path, 'Lab')
                                has_lab_dir = os.path.exists(lab_path) and any(os.path.isfile(os.path.join(lab_path, f)) for f in os.listdir(lab_path)) if os.path.exists(lab_path) else False
                                
                                # Check top-level lab results folder (with space)
                                if not has_lab_dir:
                                    lab_path = os.path.join(test_path, 'lab results')
                                    has_lab_dir = os.path.exists(lab_path) and any(os.path.isfile(os.path.join(lab_path, f)) for f in os.listdir(lab_path)) if os.path.exists(lab_path) else False
                                
                                # Check top-level lab folder (lowercase)
                                if not has_lab_dir:
                                    lab_path = os.path.join(test_path, 'lab')
                                    has_lab_dir = os.path.exists(lab_path) and any(os.path.isfile(os.path.join(lab_path, f)) for f in os.listdir(lab_path)) if os.path.exists(lab_path) else False
                                
                                # Also check nested Inspection-XXXX folders
                                if not has_lab_dir:
                                    for item in os.listdir(test_path):
                                        if item.startswith('Inspection-') and os.path.isdir(os.path.join(test_path, item)):
                                            # Check multiple variations
                                            nested_lab_path = os.path.join(test_path, item, 'Lab')
                                            if not os.path.exists(nested_lab_path):
                                                nested_lab_path = os.path.join(test_path, item, 'lab results')
                                            if not os.path.exists(nested_lab_path):
                                                nested_lab_path = os.path.join(test_path, item, 'lab')
                                            if os.path.exists(nested_lab_path) and any(os.path.isfile(os.path.join(nested_lab_path, f)) for f in os.listdir(nested_lab_path)):
                                                has_lab_dir = True
                                                print(f"✅ [BUTTON] Found Lab files in nested folder {item}")
                                                break
                            
                            # Check Retest files (check both uppercase and lowercase)
                            if not has_retest_dir:
                                # Check top-level Retest folder (uppercase)
                                retest_path = os.path.join(test_path, 'Retest')
                                has_retest_dir = os.path.exists(retest_path) and any(os.path.isfile(os.path.join(retest_path, f)) for f in os.listdir(retest_path)) if os.path.exists(retest_path) else False
                                
                                # Check top-level retest folder (lowercase)
                                if not has_retest_dir:
                                    retest_path = os.path.join(test_path, 'retest')
                                    has_retest_dir = os.path.exists(retest_path) and any(os.path.isfile(os.path.join(retest_path, f)) for f in os.listdir(retest_path)) if os.path.exists(retest_path) else False
                                
                                # Also check nested Inspection-XXXX folders
                                if not has_retest_dir:
                                    for item in os.listdir(test_path):
                                        if item.startswith('Inspection-') and os.path.isdir(os.path.join(test_path, item)):
                                            # Check both uppercase and lowercase
                                            nested_retest_path = os.path.join(test_path, item, 'Retest')
                                            if not os.path.exists(nested_retest_path):
                                                nested_retest_path = os.path.join(test_path, item, 'retest')
                                            if os.path.exists(nested_retest_path) and any(os.path.isfile(os.path.join(nested_retest_path, f)) for f in os.listdir(nested_retest_path)):
                                                has_retest_dir = True
                                                print(f"✅ [BUTTON] Found Retest files in nested folder {item}")
                                                break
                            
                            if not has_compliance_dir:
                                # Check top-level Compliance folder
                                compliance_path = os.path.join(test_path, 'Compliance')
                                if os.path.exists(compliance_path):
                                    # Check for files in commodity subfolders
                                    for commodity_folder in os.listdir(compliance_path):
                                        commodity_path = os.path.join(compliance_path, commodity_folder)
                                        if os.path.isdir(commodity_path):
                                            if any(os.path.isfile(os.path.join(commodity_path, f)) for f in os.listdir(commodity_path)):
                                                has_compliance_dir = True
                                                print(f"✅ [BUTTON] Found compliance files in top-level folder for {inspection_date}")
                                                break
                                
                                # Also check nested Inspection-XXXX folders for compliance files
                                if not has_compliance_dir:
                                    for item in os.listdir(test_path):
                                        if item.lower().startswith('inspection-') and os.path.isdir(os.path.join(test_path, item)):
                                            inspection_folder = os.path.join(test_path, item)
                                            # Check both uppercase and lowercase compliance folders
                                            nested_compliance_path = os.path.join(inspection_folder, 'Compliance')
                                            if not os.path.exists(nested_compliance_path):
                                                nested_compliance_path = os.path.join(inspection_folder, 'compliance')
                                            if os.path.exists(nested_compliance_path):
                                                # Check for files in commodity subfolders
                                                for commodity_folder in os.listdir(nested_compliance_path):
                                                    commodity_path = os.path.join(nested_compliance_path, commodity_folder)
                                                    if os.path.isdir(commodity_path):
                                                        if any(os.path.isfile(os.path.join(commodity_path, f)) for f in os.listdir(commodity_path)):
                                                            has_compliance_dir = True
                                                            print(f"✅ [BUTTON] Found compliance files in nested folder {item} for {inspection_date}")
                                                            break
                                                if has_compliance_dir:
                                                    break
                
                # Check actual file existence on disk AND sync database records
                # If files exist on disk but database doesn't have uploader info, update database
                has_rfi = has_rfi_dir
                has_invoice = has_invoice_dir
                has_lab = has_lab_dir
                has_retest = has_retest_dir
                
                # SYNC DATABASE: Update database records to match actual files on disk
                if has_rfi or has_invoice or has_lab or has_retest:
                    # Find matching inspections for this client and date
                    matching_inspections = FoodSafetyAgencyInspection.objects.filter(
                        client_name=client_name,
                        date_of_inspection=date_obj
                    )
                    
                    if matching_inspections.exists():
                        from django.utils import timezone
                        current_time = timezone.now()
                        
                        # Update database to reflect actual file status
                        if has_rfi and not matching_inspections.filter(rfi_uploaded_by__isnull=False).exists():
                            # Files exist but database doesn't have uploader info - set to system user
                            matching_inspections.update(
                                rfi_uploaded_by_id=1,  # System user
                                rfi_uploaded_date=current_time
                            )
                            print(f"🔄 [SYNC] Updated RFI database records for {client_name} - files exist on disk")
                        
                        if has_invoice and not matching_inspections.filter(invoice_uploaded_by__isnull=False).exists():
                            # Files exist but database doesn't have uploader info - set to system user
                            matching_inspections.update(
                                invoice_uploaded_by_id=1,  # System user
                                invoice_uploaded_date=current_time
                            )
                            print(f"🔄 [SYNC] Updated Invoice database records for {client_name} - files exist on disk")
                        
                        if has_lab and not matching_inspections.filter(lab_uploaded_by__isnull=False).exists():
                            # Files exist but database doesn't have uploader info - set to system user
                            matching_inspections.update(
                                lab_uploaded_by_id=1,  # System user
                                lab_uploaded_date=current_time
                            )
                            print(f"🔄 [SYNC] Updated Lab database records for {client_name} - files exist on disk")
                        
                        if has_retest and not matching_inspections.filter(retest_uploaded_by__isnull=False).exists():
                            # Files exist but database doesn't have uploader info - set to system user
                            matching_inspections.update(
                                retest_uploaded_by_id=1,  # System user
                                retest_uploaded_date=current_time
                            )
                            print(f"🔄 [SYNC] Updated Retest database records for {client_name} - files exist on disk")
                has_compliance = has_compliance_dir
                
                # Determine status for this specific client+date combination
                if has_rfi and has_invoice and has_lab and has_compliance:
                    file_status = 'all_files'  # Green
                elif has_compliance:
                    file_status = 'compliance_only'  # Orange
                elif has_rfi or has_invoice or has_lab or has_retest:
                    file_status = 'partial_files'  # Blue
                else:
                    file_status = 'no_files'  # Red
                
                print(f"📊 [BUTTON] {unique_key}: RFI:{has_rfi} (disk), Invoice:{has_invoice} (disk), Lab:{has_lab} (disk), Compliance:{has_compliance} (disk)")
                print(f"🎯 [BUTTON] Final status for {unique_key}: {file_status} (based on actual files only)")
                        
            except ValueError:
                print(f"⚠️ Invalid date format for {unique_key}: {inspection_date}")
                has_rfi = has_invoice = has_lab = has_retest = has_compliance = False
                file_status = 'no_files'
                
            except Exception as e:
                print(f"❌ Error checking files for {unique_key}: {e}")
                has_rfi = has_invoice = has_lab = has_retest = has_compliance = False
                file_status = 'error'
            
            # Store optimized status for this specific combination (common for all cases)
            combination_statuses[unique_key] = {
                'file_status': file_status,
                'client_name': client_name,
                'inspection_date': inspection_date,
                'has_rfi': has_rfi,
                'has_invoice': has_invoice,
                'has_lab': has_lab,
                'has_retest': has_retest,
                'has_compliance': has_compliance
            }
            
            print(f"✅ {unique_key}: {file_status}")
        
        print(f"📊 Completed status check for {len(combination_statuses)} combinations")
        
        # Prepare optimized response
        result_data = {
            'success': True,
            'combination_statuses': combination_statuses,
            'total_checked': len(client_date_combinations),
            'source': 'local',
            'optimized': True
        }
        cache.set(cache_key, result_data, 300)  # Cache for 5 minutes
        
        return JsonResponse(result_data)
        
    except Exception as e:
        print(f"❌ Error in get_page_clients_file_status: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def download_all_inspection_files(request):
    """Download all files for a grouped inspection as a ZIP."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        import json
        import os
        import zipfile
        import tempfile
        from django.http import HttpResponse
        from django.conf import settings
        from datetime import datetime
        import re
        
        data = json.loads(request.body)
        client_name = data.get('client_name')
        inspection_date = data.get('inspection_date')
        group_id = data.get('group_id')
        
        if not client_name or not inspection_date:
            return JsonResponse({'success': False, 'error': 'Client name and inspection date are required'})
        
        print(f"🗂️ Creating ZIP for {client_name} on {inspection_date}")
        
        # Parse date and build folder path
        if isinstance(inspection_date, str):
            date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
        else:
            date_obj = inspection_date
        
        def is_file_for_inspection_date(filename, target_date):
            """Check if a file belongs to the specific inspection date"""
            try:
                import re
                target_date_obj = datetime.strptime(target_date, '%Y-%m-%d') if isinstance(target_date, str) else target_date
                target_date_str = target_date_obj.strftime('%Y-%m-%d')
                target_date_compact = target_date_obj.strftime('%Y%m%d')
                
                # Check for YYYY-MM-DD format (compliance files) - must be exact match
                # Look for the date pattern with non-alphanumeric boundaries
                date_pattern_str = r'(?:^|[^0-9])' + re.escape(target_date_str) + r'(?:[^0-9]|$)'
                if re.search(date_pattern_str, filename):
                    return True
                
                # Check for YYYYMMDD format (uploaded files) - must be exact match
                # Look for the date pattern with non-alphanumeric boundaries
                date_pattern_compact = r'(?:^|[^0-9])' + re.escape(target_date_compact) + r'(?:[^0-9]|$)'
                if re.search(date_pattern_compact, filename):
                    return True
                
                # If no date pattern found, include the file anyway
                # This is more permissive and includes files without dates in their names
                print(f"   📄 Including file without date pattern: {filename}")
                return True
                
            except Exception as e:
                print(f"⚠️ Error checking file date for {filename}: {e}")
                # If there's an error, include the file to be safe
                return True
            
        year_folder = date_obj.strftime('%Y')
        month_folder = date_obj.strftime('%B')
        
        # Find the actual client folder using the same logic as file listing
        # Check multiple possible client folder variations
        inspection_base = os.path.join(settings.MEDIA_ROOT, 'inspection')
        
        if not os.path.exists(inspection_base):
            return JsonResponse({'success': False, 'error': 'No inspection folder found'})
        
        # Use exact client name for matching (folders now use original names)
        client_folder_pattern = client_name
        
        print(f"🔍 Looking for client folder: {client_folder_pattern}")
        
        # Find all matching client folders across all months (like file listing does)
        matching_folders = []
        
        # Search through all year/month folders
        for year_folder_search in os.listdir(inspection_base):
            year_path = os.path.join(inspection_base, year_folder_search)
            if not os.path.isdir(year_path):
                continue
                
            for month_folder_search in os.listdir(year_path):
                month_path = os.path.join(year_path, month_folder_search)
                if not os.path.isdir(month_path):
                    continue
                
                # Look for client folder in this year/month
                for folder_name in os.listdir(month_path):
                    folder_path = os.path.join(month_path, folder_name)
                    if not os.path.isdir(folder_path):
                        continue
                    
                    # Normalize folder name for comparison
                    normalized_folder = re.sub(r'[^a-zA-Z0-9_]', '_', folder_name)
                    normalized_folder = re.sub(r'_+', '_', normalized_folder).strip('_')
                    
                    # Use exact matching since folders now use original client names
                    is_match = (folder_name == client_folder_pattern)
                    
                    if is_match:
                        print(f"   ✅ Exact match: {folder_name} in {year_folder_search}/{month_folder_search}")
                    else:
                        print(f"   ❌ No match: {folder_name} in {year_folder_search}/{month_folder_search}")
                    
                    if is_match:
                        matching_folders.append(folder_path)
                        print(f"✅ Found matching client folder: {folder_name} in {year_folder_search}/{month_folder_search}")
        
        if not matching_folders:
            return JsonResponse({'success': False, 'error': f'No client folders found for {client_name}. Searched in {inspection_base}'})
        
        # Create temporary ZIP file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        try:
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                files_added = 0
                added_files = {}  # Track added files by filename + size + modified time to avoid true duplicates
                
                # Process all matching client folders
                for base_path in matching_folders:
                    folder_name = os.path.basename(base_path)
                    print(f"📁 Processing folder: {folder_name} at {base_path}")
                    
                    # Check what's actually in this folder
                    if os.path.exists(base_path):
                        folder_contents = os.listdir(base_path)
                        print(f"📁 Folder contents: {folder_contents}")
                    
                    # Define categories to check
                    categories = ['rfi', 'invoice', 'lab', 'retest']
                    
                    # Check each category folder
                    for category in categories:
                        category_path = os.path.join(base_path, category)
                        if os.path.exists(category_path):
                            print(f"📂 Found {category} folder")
                            for filename in os.listdir(category_path):
                                file_path = os.path.join(category_path, filename)
                                if os.path.isfile(file_path):
                                    # Filter files by inspection date to avoid mixing different dates
                                    if is_file_for_inspection_date(filename, inspection_date):
                                        arcname = f"{category}/{filename}"
                                        
                                        # Get file stats for duplicate detection
                                        try:
                                            stat = os.stat(file_path)
                                            file_size = stat.st_size
                                            file_modified = stat.st_mtime
                                            file_key = f"{arcname}_{file_size}_{file_modified}"
                                            
                                            # Check if we've already added this exact file (same name, size, and modified time)
                                            if file_key not in added_files:
                                                zip_file.write(file_path, arcname)
                                                added_files[file_key] = arcname
                                                files_added += 1
                                                print(f"   Added {category}: {arcname} ({file_size} bytes)")
                                            else:
                                                print(f"   Skipped {category} (exact duplicate): {arcname}")
                                        except Exception as e:
                                            print(f"   Error getting file stats for {file_path}: {e}")
                                            # If we can't get stats, include the file to be safe
                                            zip_file.write(file_path, arcname)
                                            files_added += 1
                                            print(f"   Added {category}: {arcname} (no stats)")
                                    else:
                                        print(f"   Skipped {category} (wrong date): {filename}")
                        else:
                            print(f"⚠️ No {category} folder found")
                    
                    # Check for compliance documents
                    compliance_base = os.path.join(base_path, 'Compliance')
                    if os.path.exists(compliance_base):
                        print(f"📋 Found Compliance folder: {compliance_base}")
                        compliance_contents = os.listdir(compliance_base)
                        print(f"📋 Compliance folder contents: {compliance_contents}")
                        
                        # Check all commodity subfolders
                        for commodity_folder in compliance_contents:
                            commodity_path = os.path.join(compliance_base, commodity_folder)
                            if os.path.isdir(commodity_path):
                                print(f"📋 Checking commodity folder: {commodity_folder}")
                                commodity_files = os.listdir(commodity_path)
                                print(f"📋 Commodity {commodity_folder} files: {commodity_files}")
                                
                                for filename in commodity_files:
                                    file_path = os.path.join(commodity_path, filename)
                                    if os.path.isfile(file_path):
                                        # Filter compliance files by inspection date
                                        if is_file_for_inspection_date(filename, inspection_date):
                                            arcname = f"Compliance/{commodity_folder}/{filename}"
                                            
                                            # Get file stats for duplicate detection
                                            try:
                                                stat = os.stat(file_path)
                                                file_size = stat.st_size
                                                file_modified = stat.st_mtime
                                                
                                                # For compliance files, use filename + size for duplicate detection
                                                # This allows multiple files with same name but different sizes (different inspections)
                                                # but prevents true duplicates (same name AND same size)
                                                file_key = f"{filename}_{file_size}"
                                                
                                                # Check if we've already added this exact file (same name and size)
                                                if file_key not in added_files:
                                                    zip_file.write(file_path, arcname)
                                                    added_files[file_key] = arcname
                                                    files_added += 1
                                                    print(f"   Added compliance: {arcname} ({file_size} bytes)")
                                                else:
                                                    print(f"   Skipped compliance (exact duplicate): {arcname} (same name and size already added)")
                                            except Exception as e:
                                                print(f"   Error getting file stats for {file_path}: {e}")
                                                # If we can't get stats, include the file to be safe
                                                zip_file.write(file_path, arcname)
                                                files_added += 1
                                                print(f"   Added compliance: {arcname} (no stats)")
                                        else:
                                            print(f"   Skipped compliance (wrong date): {filename}")
                    else:
                        print(f"⚠️ No Compliance folder found at: {compliance_base}")
                
                if files_added == 0:
                    return JsonResponse({'success': False, 'error': 'No files found to download'})
            
            # Prepare response
            zip_filename = f"{client_name}_{inspection_date}_inspection_files.zip"
            zip_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', zip_filename)
            
            # Read ZIP file content
            with open(temp_zip.name, 'rb') as zip_file:
                zip_content = zip_file.read()
            
            # Create HTTP response
            response = HttpResponse(zip_content, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
            response['Content-Length'] = len(zip_content)
            
            print(f"✅ ZIP created successfully: {zip_filename} ({files_added} files)")
            return response
            
        finally:
            # Cleanup temporary file
            try:
                os.unlink(temp_zip.name)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Error creating ZIP: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def update_sent_status(request):
    """Update sent status for inspection group and mark as complete if sent."""
    print(f"🔄 UPDATE_SENT_STATUS called - Method: {request.method}")
    print(f"📋 POST data: {dict(request.POST)}")
    
    if request.method != 'POST':
        print(f"❌ Invalid method: {request.method}")
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        group_id = request.POST.get('group_id')
        sent_status = request.POST.get('sent_status')
        
        print(f"📧 Group ID: '{group_id}', Status: '{sent_status}'")
        
        if not group_id:
            print("❌ No group ID provided")
            return JsonResponse({'success': False, 'error': 'Group ID is required'})
        
        print(f"📧 Updating sent status for group {group_id}: {sent_status}")
        
        # Parse group_id to get client_name and date
        # group_id format: "ClientName_YYYYMMDD"
        parts = group_id.rsplit('_', 1)
        if len(parts) != 2:
            return JsonResponse({'success': False, 'error': 'Invalid group ID format'})
        
        client_name_sanitized = parts[0]
        date_str = parts[1]
        
        # Parse date
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date_str, '%Y%m%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid date format in group ID'})
        
        # Find all inspections in this group and update their sent status
        from ..models import FoodSafetyAgencyInspection
        
        # We need to find the original client name from the sanitized version
        # Get all inspections for this date and find matching client
        inspections = FoodSafetyAgencyInspection.objects.filter(date_of_inspection=date_obj)
        
        # Find inspections where sanitized client name matches
        import re
        matching_inspections = []
        for inspection in inspections:
            if inspection.client_name:
                # Use the same sanitization logic as group ID creation (frontend logic)
                sanitized_client = re.sub(r'[^a-zA-Z0-9_]', '_', inspection.client_name)
                sanitized_client = re.sub(r'_+', '_', sanitized_client)
                sanitized_client = sanitized_client.strip('_')
                
                if sanitized_client.lower() == client_name_sanitized.lower():
                    matching_inspections.append(inspection)
        
        if not matching_inspections:
            return JsonResponse({'success': False, 'error': 'No inspections found for this group'})
        
        # Update sent status for all inspections in the group
        is_sent = sent_status == 'YES' if sent_status else False
        
        from django.utils import timezone
        sent_date = timezone.now() if is_sent else None
        sent_by = request.user if is_sent else None
        
        updated_count = 0
        for inspection in matching_inspections:
            inspection.is_sent = is_sent
            inspection.sent_date = sent_date
            inspection.sent_by = sent_by
            inspection.save(update_fields=['is_sent', 'sent_date', 'sent_by'])
            updated_count += 1
        
        print(f"✅ Updated sent status for {updated_count} inspections in group {group_id}")
        
        # Log the sent status change to system logs
        try:
            # Get client name from the first matching inspection
            client_name = matching_inspections[0].client_name if matching_inspections else 'Unknown'
            
            # Get user IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # Create descriptive log message
            status_text = {
                'YES': 'Sent',
                'NO': 'Not Sent',
                '': 'Not Sent (cleared)'
            }.get(sent_status, sent_status)
            
            description = f"Changed sent status to '{status_text}' for {client_name} inspection group on {date_obj.strftime('%Y-%m-%d')}"
            
            # Log the activity
            SystemLog.log_activity(
                user=request.user,
                action='UPDATE',
                page='/inspections/',
                object_type='inspection_group',
                object_id=group_id,
                description=description,
                details={
                    'client_name': client_name,
                    'inspection_date': date_obj.strftime('%Y-%m-%d'),
                    'sent_status': sent_status,
                    'status_text': status_text,
                    'inspections_affected': updated_count,
                    'group_id': group_id
                },
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            print(f"📝 Logged sent status change: {request.user.username} set {client_name} to '{status_text}'")
            
        except Exception as e:
            print(f"⚠️ Error logging sent status change: {e}")
            # Don't fail the main operation if logging fails
        
        return JsonResponse({
            'success': True,
            'message': f'Sent status updated for {updated_count} inspections',
            'sent_status': sent_status,
            'is_complete': is_sent,
            'sent_by_username': request.user.username,
            'sent_date': sent_date.isoformat() if sent_date else None
        })
        
    except Exception as e:
        print(f"❌ Error updating sent status: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def download_inspection_file(request):
    """Secure file download for inspection files."""
    try:
        import os
        from django.http import FileResponse, Http404, HttpResponseRedirect
        from django.conf import settings
        from urllib.parse import unquote
        
        file_param = request.GET.get('file', '')
        source = request.GET.get('source', 'local')  # 'local' or 'onedrive'
        
        if not file_param:
            raise Http404("File not specified")
        
        # Decode URL-encoded filename
        relative_path = unquote(file_param)
        
        if source == 'onedrive':
            # Handle OneDrive file download
            return download_onedrive_file(request, relative_path)
        else:
            # Handle local file download (existing logic)
            return download_local_file(request, relative_path)
        
    except Exception as e:
        raise Http404(f"Error serving file: {str(e)}")


def download_onedrive_file(request, relative_path):
    """Download file from OneDrive."""
    try:
        import os
        import json
        import requests
        from django.http import HttpResponseRedirect
        
        # Load OneDrive tokens
        token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
        if not os.path.exists(token_file):
            raise Http404("OneDrive not configured")
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        access_token = token_data.get('access_token')
        if not access_token:
            raise Http404("OneDrive not authenticated")
        
        # Build OneDrive path
        onedrive_base = getattr(settings, 'ONEDRIVE_FOLDER', 'FoodSafety Agency Inspections')
        onedrive_path = f"{onedrive_base}/inspection/{relative_path}"
        
        # Get file download URL from OneDrive
        check_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{onedrive_path}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(check_url, headers=headers)
        if response.status_code != 200:
            raise Http404("File not found in OneDrive")
        
        file_info = response.json()
        download_url = file_info.get('@microsoft.graph.downloadUrl')
        
        if not download_url:
            raise Http404("Download URL not available")
        
        # Redirect to OneDrive download URL
        return HttpResponseRedirect(download_url)
        
    except Exception as e:
        raise Http404(f"Error downloading from OneDrive: {str(e)}")


def download_local_file(request, relative_path):
    """Download file from local media folder."""
    try:
        import os
        from django.http import FileResponse, Http404
        from django.conf import settings
        
        print(f"🔍 Download request: {relative_path}")
        
        # Security: Ensure file is within MEDIA_ROOT/inspection
        if not relative_path.startswith('inspection/'):
            print(f"❌ Download 404: Access denied - path doesn't start with 'inspection/': {relative_path}")
            raise Http404("Access denied")
        
        # Build full file path - normalize path separators for Windows
        normalized_path = relative_path.replace('/', os.sep)
        file_path = os.path.join(settings.MEDIA_ROOT, normalized_path)
        
        # Security: Ensure file exists and is within allowed directory
        if not os.path.exists(file_path):
            print(f"❌ Download 404: File does not exist: {file_path}")
            raise Http404(f"File not found: {relative_path}")
        
        if not os.path.isfile(file_path):
            print(f"❌ Download 404: Path is not a file: {file_path}")
            raise Http404(f"Path is not a file: {relative_path}")
        
        # Additional security: Ensure resolved path is still within MEDIA_ROOT
        real_path = os.path.realpath(file_path)
        media_root_real = os.path.realpath(settings.MEDIA_ROOT)
        if not real_path.startswith(media_root_real):
            raise Http404("Access denied")
        
        # Determine content type
        content_type = 'application/octet-stream'
        filename = os.path.basename(file_path)
        ext = filename.split('.')[-1].lower()
        
        content_types = {
            'pdf': 'application/pdf',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xls': 'application/vnd.ms-excel',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'zip': 'application/zip'
        }
        
        content_type = content_types.get(ext, content_type)
        
        # Create file response with proper download headers
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type,
            as_attachment=True,
            filename=filename
        )
        
        # Set headers for download
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        raise Http404(f"Error serving file: {str(e)}")


@login_required
def get_zip_contents(request):
    """Get contents of a ZIP file for preview."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        import json
        import os
        import zipfile
        from django.conf import settings
        from urllib.parse import unquote
        
        data = json.loads(request.body)
        relative_path = data.get('file_path', '')
        
        if not relative_path:
            return JsonResponse({'success': False, 'error': 'File path not specified'})
        
        # Security: Ensure file is within MEDIA_ROOT/inspection
        if not relative_path.startswith('inspection/'):
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        # Build full file path
        file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        
        # Security checks
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return JsonResponse({'success': False, 'error': 'File not found'})
        
        # Read ZIP contents
        contents = []
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                for info in zip_file.infolist():
                    if not info.is_dir():  # Only show files, not directories
                        contents.append({
                            'name': info.filename,
                            'size': info.file_size,
                            'compressed_size': info.compress_size,
                            'modified': info.date_time
                        })
        except zipfile.BadZipFile:
            return JsonResponse({'success': False, 'error': 'Invalid ZIP file'})
        
        return JsonResponse({
            'success': True,
            'contents': contents,
            'total_files': len(contents),
            'zip_name': os.path.basename(file_path)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def send_group_documents(request):
    """Send all documents for a grouped inspection via email."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        import json
        import os
        from datetime import datetime
        from django.conf import settings
        from django.core.mail import EmailMessage
        
        data = json.loads(request.body)
        group_id = data.get('group_id', '')
        client_name = data.get('client_name', '')
        inspection_date = data.get('inspection_date', '')
        
        # Parse date and build folder path
        date_obj = datetime.strptime(inspection_date, '%Y-%m-%d')
        year_folder = date_obj.strftime('%Y')
        month_folder = date_obj.strftime('%B')
        
        # Use original client name for folder structure (folders now use original names)
        client_folder = client_name or 'Unknown Client'
        
        # Base client path
        client_base_path = os.path.join(
            settings.MEDIA_ROOT,
            'inspection',
            year_folder,
            month_folder,
            client_folder
        )
        
        # Collect all available documents
        document_categories = ['rfi', 'invoice', 'lab', 'retest']
        attachments = []
        documents_found = []
        
        for category in document_categories:
            category_path = os.path.join(client_base_path, category)
            if os.path.exists(category_path):
                for filename in os.listdir(category_path):
                    file_path = os.path.join(category_path, filename)
                    if os.path.isfile(file_path) and filename.lower().endswith('.pdf'):
                        attachments.append(file_path)
                        documents_found.append(f"{category.upper()}: {filename}")
        
        # Also check compliance documents
        compliance_path = os.path.join(client_base_path, 'Compliance')
        if os.path.exists(compliance_path):
            for commodity in ['RAW', 'PMP', 'POULTRY', 'EGGS']:
                commodity_path = os.path.join(compliance_path, commodity)
                if os.path.exists(commodity_path):
                    for filename in os.listdir(commodity_path):
                        file_path = os.path.join(commodity_path, filename)
                        if os.path.isfile(file_path):
                            attachments.append(file_path)
                            documents_found.append(f"Compliance/{commodity}: {filename}")
        
        if not attachments:
            return JsonResponse({
                'success': False,
                'error': 'No documents found to send. Please upload RFI, Invoice, Lab results, or other documents first.'
            })
        
        # Get client email (you'll need to implement client email lookup)
        # For now, using a placeholder - you can extend this to get actual client emails
        recipient_email = get_client_email(client_name)  # Function to implement
        
        if not recipient_email:
            return JsonResponse({
                'success': False,
                'error': f'No email address found for {client_name}. Please add client email in the system.'
            })
        
        # Create email
        subject = f'Inspection Documents - {client_name} - {inspection_date}'
        message = f"""
Dear {client_name},

Please find attached the inspection documents for the inspection conducted on {inspection_date}.

Documents included:
{chr(10).join('• ' + doc for doc in documents_found)}

Best regards,
Food Safety Agency (Pty) Ltd
        """.strip()
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
            reply_to=[settings.DEFAULT_FROM_EMAIL]
        )
        
        # Attach all documents
        for file_path in attachments:
            email.attach_file(file_path)
        
        # Send email
            email.send()
        
        # Log the activity
        from ..models import SystemLog
        SystemLog.log_activity(
            user=request.user,
            action='EMAIL',
            page='inspections',
            object_type='group_documents',
            object_id=group_id,
            description=f'Sent {len(attachments)} documents for {client_name}',
            details={
                'client_name': client_name,
                'inspection_date': inspection_date,
                'documents_sent': documents_found,
                'recipient': recipient_email
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Documents sent successfully to {recipient_email}',
            'recipients': recipient_email,
            'documents_sent': len(attachments),
            'email_id': f'inspection_{group_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_client_email(client_name):
    """Get client email address from database (manual override preferred)."""
    try:
        from ..models import Client
        
        # Try to find client by business name (client_id field)
        client = Client.objects.filter(client_id__iexact=client_name).first()
        
        if client:
            return client.manual_email or client.email
        
        # If no email found, return None for now
        return None
        
    except Exception:
        return None


@login_required
@role_required(['admin', 'super_admin', 'developer'])
def sync_client_emails_from_sheets(request):
    """Sync client emails from Google Sheets column K."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    # Check if user has required permissions
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    # Check user role
    user_role = getattr(request.user, 'role', None)
    if user_role not in ['admin', 'super_admin', 'developer']:
        return JsonResponse({'success': False, 'error': f'Insufficient permissions. Your role: {user_role}'})
    
    try:
        from ..services.google_sheets_service import GoogleSheetsService
        from ..models import Client
        import re
        
        # Initialize Google Sheets service
        try:
            sheets_service = GoogleSheetsService()
            print("Google Sheets service initialized successfully")
            
            # Authenticate the service
            print("Authenticating with Google Sheets...")
            sheets_service.authenticate(request)
            print("Google Sheets authentication completed")
            
        except Exception as e:
            print(f"Error initializing Google Sheets service: {e}")
            return JsonResponse({'success': False, 'error': f'Failed to initialize Google Sheets service: {str(e)}'})
        
        # Get data from the client database sheet
        # CLIENT_DATABASE_URL from your Apps Script: 1iNULGBAzJ9n2ZulxwP8ZZZbwcPhj7X6e6rPwYqtI_fM
        spreadsheet_id = '1iNULGBAzJ9n2ZulxwP8ZZZbwcPhj7X6e6rPwYqtI_fM'
        sheet_name = 'Internal Account Code Generator'
        
        print(f"Attempting to access spreadsheet: {spreadsheet_id}")
        print(f"Sheet name: {sheet_name}")
        
        # Get data from columns H (account code), J (client name), K (email)
        # Starting from row 2 as per your request
        range_name = f'{sheet_name}!H2:K'
        print(f"Range: {range_name}")
        
        try:
            result = sheets_service.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return JsonResponse({'success': False, 'error': 'No data found in Google Sheets'})
            
            print(f"Found {len(values)} rows in Google Sheets")
            print(f"Sample row: {values[0] if values else 'No data'}")
            
            updated_count = 0
            created_count = 0
            error_count = 0
            
            for row in values:
                try:
                    # Extract data from columns H, I, J, K
                    account_code = row[0] if len(row) > 0 else ''  # Column H
                    # Skip column I
                    client_name = row[2] if len(row) > 2 else ''   # Column J  
                    email = row[3] if len(row) > 3 else ''         # Column K
                    
                    if not client_name or not account_code:
                        continue
                    
                    # Clean email (remove whitespace, validate basic format)
                    email = email.strip() if email else ''
                    if email and '@' not in email:
                        email = ''  # Invalid email format
                    
                    # Convert "None" to null/empty string
                    if email.lower() == 'none':
                        email = ''
                    
                    # Find client by internal account code first, then by client_id
                    client = None
                    if account_code:
                        client = Client.objects.filter(internal_account_code=account_code).first()
                    
                    if not client and client_name:
                        client = Client.objects.filter(client_id=client_name).first()
                    
                    if client:  # Update all clients, even with empty emails; do not override manual_email
                        if not client.manual_email and client.email != (email if email else None):
                            client.email = email if email else None
                            client.save()
                            updated_count += 1
                            print(f"Updated {client.client_id} with email: {email if email else 'null'}")
                    
                except Exception as e:
                    error_count += 1
                    print(f"Error processing row {row}: {e}")
            
            return JsonResponse({
                'success': True,
                'message': f'Client email sync completed: {created_count} created, {updated_count} updated, {error_count} errors',
                'created': created_count,
                'updated': updated_count,
                'errors': error_count,
                'total_processed': len(values)
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error accessing Google Sheets: {str(e)}'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_file_info(file_path, category):
    """Get file information for display."""
    import os
    from datetime import datetime
    from django.conf import settings
    from django.urls import reverse
    
    try:
        stat = os.stat(file_path)
        filename = os.path.basename(file_path)
        
        # Create proper relative path for URL (handle Windows paths)
        relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
        # Normalize path separators for URL
        relative_path = relative_path.replace('\\', '/')
        
        # Create proper media URLs
        file_url = f'/media/{relative_path}'
        
        # Create download URL with proper headers
        download_url = f'/inspections/download-file/?file={relative_path}'
        
        return {
            'name': filename,
            'size': stat.st_size,
            'modified_time': stat.st_mtime,  # Return timestamp for frontend
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),  # Keep formatted string too
            'url': file_url,
            'download_url': download_url,
            'category': category,
            'relative_path': relative_path
        }
    except Exception as e:
        return {
            'name': os.path.basename(file_path),
            'size': 0,
            'modified': 'Unknown',
            'url': '#',
            'download_url': '#',
            'category': category,
            'relative_path': ''
        }


def find_document_link_simulation(account_code, commodity, inspection_date):
    """Simple simulation of document link finding."""
    if not account_code or not commodity:
        return 'Document Not Found'
    
    # Simulate finding a document 30% of the time
    import random
    if random.random() < 0.3:
        return f'<a href="https://drive.google.com/file/d/example_{account_code[:5]}/view" class="document-link" target="_blank">📄 Document Link</a>'
    
    return 'Document Not Found'


@login_required
@role_required(['developer'])
def start_compliance_linking(request):
    """Start the compliance document linking process."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        import json
        data = json.loads(request.body)
        batch_size = data.get('batch_size', 200)
        doc_types = data.get('doc_types', 'all')
        
        # Get total inspection count
        from ..models import FoodSafetyAgencyInspection
        total_inspections = FoodSafetyAgencyInspection.objects.count()
        total_batches = (total_inspections + batch_size - 1) // batch_size
        
        # Initialize or get current progress from cache/session
        from django.core.cache import cache
        progress_key = f'compliance_linking_progress_{request.user.id}'
        
        progress = cache.get(progress_key, {
            'current_round': 1,
            'current_batch': 1,
            'processed_count': 0,
            'linked_count': 0,
            'error_count': 0,
            'is_running': False,
            'batch_size': batch_size,
            'doc_types': doc_types
        })
        
        progress['is_running'] = True
        progress['batch_size'] = batch_size
        progress['doc_types'] = doc_types
        cache.set(progress_key, progress, 3600)  # Cache for 1 hour
        
        row_start = ((progress['current_round'] - 1) * batch_size) + 1
        row_end = min(row_start + batch_size - 1, total_inspections)
        
        return JsonResponse({
            'success': True,
            'message': f'Started processing batch {progress["current_batch"]} of {total_batches}',
            'current_round': progress['current_round'],
            'current_batch': progress['current_batch'],
            'total_batches': total_batches,
            'row_start': row_start,
            'row_end': row_end,
            'total_inspections': total_inspections
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@role_required(['developer'])
def pause_compliance_linking(request):
    """Pause the compliance document linking process."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        from django.core.cache import cache
        progress_key = f'compliance_linking_progress_{request.user.id}'
        progress = cache.get(progress_key, {})
        
        if progress:
            progress['is_running'] = False
            cache.set(progress_key, progress, 3600)
            return JsonResponse({'success': True, 'message': 'Processing paused'})
        else:
            return JsonResponse({'success': False, 'error': 'No active process found'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@role_required(['developer'])
def reset_compliance_progress(request):
    """Reset the compliance document linking progress."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        from django.core.cache import cache
        progress_key = f'compliance_linking_progress_{request.user.id}'
        cache.delete(progress_key)
        
        return JsonResponse({
            'success': True, 
            'message': 'Progress reset successfully. Next run will start from the beginning.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@role_required(['developer'])
def compliance_linking_status(request):
    """Get current status of compliance document linking."""
    try:
        from django.core.cache import cache
        from ..models import FoodSafetyAgencyInspection
        
        progress_key = f'compliance_linking_progress_{request.user.id}'
        progress = cache.get(progress_key, {
            'current_round': 1,
            'current_batch': 1,
            'processed_count': 0,
            'linked_count': 0,
            'error_count': 0,
            'is_running': False,
            'batch_size': 200,
            'doc_types': 'all'
        })
        
        total_inspections = FoodSafetyAgencyInspection.objects.count()
        total_batches = (total_inspections + progress['batch_size'] - 1) // progress['batch_size']
        
        row_start = ((progress['current_round'] - 1) * progress['batch_size']) + 1
        row_end = min(row_start + progress['batch_size'] - 1, total_inspections)
        
        progress_percentage = (progress['processed_count'] / total_inspections * 100) if total_inspections > 0 else 0
        
        # Check if processing is complete
        is_complete = progress['processed_count'] >= total_inspections or not progress['is_running']
        
        return JsonResponse({
            'success': True,
            'message': f"Round {progress['current_round']}, Batch {progress['current_batch']} of {total_batches}",
            'current_round': progress['current_round'],
            'current_batch': progress['current_batch'],
            'total_batches': total_batches,
            'row_start': row_start,
            'row_end': row_end,
            'processed_count': progress['processed_count'],
            'linked_count': progress['linked_count'],
            'error_count': progress['error_count'],
            'total_inspections': total_inspections,
            'progress_percentage': round(progress_percentage, 1),
            'is_running': progress['is_running'],
            'is_complete': is_complete
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@role_required(['developer'])
def process_compliance_batch(request):
    """Process a single batch of compliance document linking."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        from django.core.cache import cache
        from ..models import FoodSafetyAgencyInspection, Client
        from ..services.google_drive_service import GoogleDriveService
        import os
        from datetime import datetime
        
        progress_key = f'compliance_linking_progress_{request.user.id}'
        progress = cache.get(progress_key, {})
        
        if not progress or not progress.get('is_running'):
            return JsonResponse({'success': False, 'error': 'No active process found'})
        
        batch_size = progress['batch_size']
        doc_types = progress['doc_types']
        
        # Get current batch of inspections
        offset = (progress['current_round'] - 1) * batch_size
        inspections = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection')[offset:offset + batch_size]
        
        if not inspections:
            # No more inspections to process
            progress['is_running'] = False
            cache.set(progress_key, progress, 3600)
            return JsonResponse({
                'success': True,
                'message': 'All inspections processed',
                'is_complete': True
            })
        
        # Build client mapping (business name -> internal account code)
        client_map = {}
        for client in Client.objects.exclude(internal_account_code__isnull=True).exclude(internal_account_code=''):
            key = (client.client_id or '').strip().lower()
            if key:
                client_map[key] = client.internal_account_code
        
        # Initialize Google Drive service
        drive_service = GoogleDriveService()
        root_folder_id = '1nrODSMMhYQhMeX3gXLzoIV_65fC_pXnO'  # From the Apps Script
        
        processed_count = 0
        linked_count = 0
        error_count = 0
        
        for inspection in inspections:
            try:
                processed_count += 1
                
                # Get client account code
                client_key = (inspection.client_name or '').strip().lower()
                account_code = client_map.get(client_key, 'unknown')
                
                # Get month/year folder from inspection date
                if inspection.date_of_inspection:
                    month_year = inspection.date_of_inspection.strftime('%B %Y')
                    
                    # Find files for this inspection based on account code and date
                    # This is a simplified version - you'd need to implement the full
                    # folder traversal and file matching logic from the Apps Script
                    
                    # For now, just simulate the process
                    links_created = simulate_link_creation(inspection, account_code, doc_types)
                    linked_count += links_created
                    
            except Exception as e:
                error_count += 1
                print(f"Error processing inspection {inspection.remote_id}: {e}")
        
        # Update progress
        progress['processed_count'] += processed_count
        progress['linked_count'] += linked_count
        progress['error_count'] += error_count
        progress['current_round'] += 1
        
        # Check if we need to move to next batch
        total_inspections = FoodSafetyAgencyInspection.objects.count()
        if progress['processed_count'] >= total_inspections:
            progress['is_running'] = False
        
        cache.set(progress_key, progress, 3600)
        
        return JsonResponse({
            'success': True,
            'message': f'Processed {processed_count} inspections, created {linked_count} links',
            'processed_count': processed_count,
            'linked_count': linked_count,
            'error_count': error_count,
            'is_complete': not progress['is_running']
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def simulate_link_creation(inspection, account_code, doc_types):
    """Simulate link creation for testing purposes."""
    # This is a placeholder function that simulates the link creation process
    # In a real implementation, you would:
    # 1. Search for files in Google Drive based on reference patterns
    # 2. Create hyperlinks in the database or update inspection records
    # 3. Return the actual number of links created
    
    links_created = 0
    
    # Simulate different document types
    if doc_types == 'all' or doc_types == 'rfi':
        # Simulate RFI link creation
        if inspection.remote_id and account_code != 'unknown':
            links_created += 1
    
    if doc_types == 'all' or doc_types == 'invoice':
        # Simulate Invoice link creation
        if inspection.remote_id and account_code != 'unknown':
            links_created += 1
    
    if doc_types == 'all' or doc_types == 'coa':
        # Simulate COA link creation
        if inspection.remote_id and account_code != 'unknown':
            links_created += 1
    
    return links_created


@login_required
@role_required(['developer'])
def first_50_compliance_links(request):
    inspections = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection')[:50]
    # Map client -> internal account code
    from ..models import Client
    client_map = {c.name: (c.internal_account_code or 'no') for c in Client.objects.all()}

    # Load Drive files and build lookup
    folder_id = '18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4'
    drive = GoogleDriveService()
    files = drive.list_files_in_folder(folder_id, request=request, max_items=10)
    lookup = GoogleDriveService.build_file_lookup(files)

    results = []
    for ins in inspections:
        account_code = client_map.get(ins.client_name, 'no')
        url = GoogleDriveService.find_best_link(account_code, ins.commodity, ins.date_of_inspection, lookup)
        results.append({
            'remote_id': ins.remote_id,
            'client_name': ins.client_name,
            'commodity': ins.commodity,
            'date_of_inspection': ins.date_of_inspection,
            'account_code': account_code,
            'document_url': url or None,
        })
    return JsonResponse({'success': True, 'count': len(results), 'items': results})


@login_required
@role_required(['developer'])
def fetch_and_store_first_50_compliance_docs(request):
    import os
    from django.conf import settings as dj_settings
    inspections = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection')[:50]
    from ..models import Client
    client_map = {c.name: (c.internal_account_code or 'no') for c in Client.objects.all()}

    folder_id = '18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4'
    drive = GoogleDriveService()
    files = drive.list_files_in_folder(folder_id, request=request)
    lookup = GoogleDriveService.build_file_lookup(files)

    base_dir = os.path.join(dj_settings.MEDIA_ROOT, 'compliance_documents')
    os.makedirs(base_dir, exist_ok=True)

    saved = []
    for ins in inspections:
        account_code = client_map.get(ins.client_name, 'no')
        # Reuse link matcher but pull the file id by reverse searching the lookup
        best_id = None
        best_days = 10**9
        import datetime as _dt
        commodity = (ins.commodity or '').strip().lower()
        if commodity == 'eggs':
            commodity = 'egg'
        for f in lookup.values():
            if f['commodity'].lower() == commodity and f['accountCode'] == account_code:
                days = abs((f['zipDate'] - ins.date_of_inspection).days) if ins.date_of_inspection else 10**9
                if days <= 15 and days < best_days:
                    best_days = days
                    best_id = f['id']
                    best_name = f['name']
        if not best_id:
            continue
        client_folder = os.path.join(base_dir, (ins.client_name or 'Unknown').replace(' ', '_'))
        os.makedirs(client_folder, exist_ok=True)
        dest_path = os.path.join(client_folder, best_name)
        try:
            if not os.path.exists(dest_path):
                drive.download_file(best_id, dest_path, request=request)
            saved.append({'client_name': ins.client_name, 'file': dest_path})
        except Exception as e:
            saved.append({'client_name': ins.client_name, 'error': str(e)})

    return JsonResponse({'success': True, 'saved_count': len([s for s in saved if 'file' in s]), 'items': saved})


@login_required
@role_required(['developer'])
def list_any_50_drive_files(request):
    print("[View] list_any_50_drive_files: start")
    """List any 50 files from the specified Drive folder to validate access."""
    folder_id = '18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4'
    drive = GoogleDriveService()
    files = drive.list_files_in_folder(folder_id, request=request)
    print(f"[View] list_any_50_drive_files: got {len(files)} files, trimming to 10")
    items = [
        {
            'id': f.get('id'),
            'name': f.get('name'),
            'mimeType': f.get('mimeType'),
            'webViewLink': f.get('webViewLink')
        }
        for f in files[:10]
    ]
    print(f"[View] list_any_50_drive_files: returning {len(items)} items")
    return JsonResponse({'success': True, 'count': len(items), 'items': items})


@login_required
@role_required(['developer'])
def fetch_store_any_50_drive_files(request):
    print("[View] fetch_store_any_50_drive_files: start")
    """Download the first 50 files from the specified Drive folder into MEDIA for testing."""
    import os
    from django.conf import settings as dj_settings

    folder_id = '18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4'
    drive = GoogleDriveService()
    files = drive.list_files_in_folder(folder_id, request=request, max_items=10)
    print(f"[View] fetch_store_any_50_drive_files: will download {len(files)} files")

    base_dir = os.path.join(dj_settings.MEDIA_ROOT, 'compliance_documents', 'test_any_50')
    os.makedirs(base_dir, exist_ok=True)

    saved = []
    for f in files:
        file_id = f.get('id')
        name = f.get('name') or f'{file_id}.bin'
        dest_path = os.path.join(base_dir, name)
        try:
            if not os.path.exists(dest_path):
                drive.download_file(file_id, dest_path, request=request)
            saved.append({'id': file_id, 'file': dest_path})
        except Exception as e:
            print(f"[View] fetch_store_any_50_drive_files: error downloading {file_id}: {e}")
            saved.append({'id': file_id, 'error': str(e)})

    print(f"[View] fetch_store_any_50_drive_files: saved_count={len([s for s in saved if 'file' in s])}")
    return JsonResponse({'success': True, 'saved_count': len([s for s in saved if 'file' in s]), 'items': saved})


@login_required
@role_required(['developer'])
def drive_any10_page(request):
    print("[View] drive_any10_page: start")
    folder_id = '18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4'
    drive = GoogleDriveService()
    files = drive.list_files_in_folder(folder_id, request=request, max_items=10)
    context = {
        'page_title': 'Drive Test - Any 10 Files',
        'files': files,
    }
    return render(request, 'main/drive_any10.html', context)


@login_required
@role_required(['developer'])
def download_first_10_compliance_by_commodity(request):
    print("[View] download_first_10_compliance_by_commodity: start")
    import os
    from django.conf import settings as dj_settings

    # Prepare inspections and client account code map
    inspections = FoodSafetyAgencyInspection.objects.exclude(client_name__isnull=True).exclude(client_name__exact='').order_by('-date_of_inspection')[:10]
    from ..models import Client
    client_map = {c.name: (c.internal_account_code or 'no') for c in Client.objects.all()}

    # Load Drive files and build lookup
    folder_id = '18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4'
    drive = GoogleDriveService()
    print("[View] download_first_10_compliance_by_commodity: listing drive files")
    # Only list enough files to match quickly (cap 2000)
    files = drive.list_files_in_folder(folder_id, request=request, max_items=2000)
    lookup = GoogleDriveService.build_file_lookup(files)

    # Commodity grouping
    def _group_for_commodity(raw):
        s = (raw or '').strip().lower()
        if s == 'eggs' or s == 'egg':
            return 'egg'
        if 'pmp' in s:
            return 'pmp'
        if 'poultry' in s:
            return 'poultry'
        return 'raw' if 'raw' in s else (s or 'raw')

    saved = []
    base_dir = os.path.join(dj_settings.MEDIA_ROOT, 'compliance')
    os.makedirs(base_dir, exist_ok=True)

    for ins in inspections:
        account_code = client_map.get(ins.client_name, 'no')
        # Find best matching file id similar to earlier logic
        best = None
        best_days = 10**9
        import datetime as _dt
        commodity_norm = (ins.commodity or '').strip().lower()
        if commodity_norm == 'eggs':
            commodity_norm = 'egg'
        # Fast path: try a direct name contains search by account code to reduce scanning
        try:
            # Narrow search using tokens: account code plus commodity prefix
            tokens = [account_code, (ins.commodity or '').split()[0]]
            fast_candidates = drive.search_files_in_folder_by_tokens(folder_id, tokens, request=request, max_items=50)
            for fc in fast_candidates:
                name = fc.get('name') or ''
                import re as _re
                m = _re.match(r'^([A-Za-z]+)-([A-Z]{2}-[A-Z]{3}-[A-Z]{3}-[A-Z]{2,3}-\d+)-(\d{4}-\d{2}-\d{2})', name)
                if not m:
                    continue
                comm, acc, date_str = m.group(1), m.group(2), m.group(3)
                if acc != account_code:
                    continue
                if comm.lower() != commodity_norm:
                    continue
                try:
                    fdate = _dt.datetime.strptime(date_str, '%Y-%m-%d').date()
                except Exception:
                    continue
                days = abs((fdate - (ins.date_of_inspection or _dt.date.min)).days) if ins.date_of_inspection else 10**9
                if days <= 15 and days < best_days:
                    best_days = days
                    best = {'id': fc.get('id'), 'name': name}
        except Exception:
            pass
        if not best:
            for f in lookup.values():
                if f['commodity'].lower() == commodity_norm and f['accountCode'] == account_code:
                    # Enforce ±15 days window
                    days = abs((f['zipDate'] - (ins.date_of_inspection or _dt.date.min)).days) if ins.date_of_inspection else 10**9
                    if days <= 15 and days < best_days:
                        best_days = days
                        best = f
        if not best:
            saved.append({'client_name': ins.client_name, 'status': 'no_match'})
            continue
        group = _group_for_commodity(ins.commodity)
        client_folder = os.path.join(base_dir, group, (ins.client_name or 'Unknown').replace(' ', '_'))
        os.makedirs(client_folder, exist_ok=True)
        dest_path = os.path.join(client_folder, best['name'])
        try:
            if not os.path.exists(dest_path):
                drive.download_file(best['id'], dest_path, request=request)
            saved.append({'client_name': ins.client_name, 'group': group, 'file': dest_path})
        except Exception as e:
            saved.append({'client_name': ins.client_name, 'group': group, 'error': str(e)})

    saved_count = len([s for s in saved if 'file' in s])
    print(f"[View] download_first_10_compliance_by_commodity: saved_count={saved_count}")

    # If AJAX, return JSON, else render a simple page
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse({'success': True, 'saved_count': saved_count, 'items': saved})

    context = {
        'page_title': 'Downloaded Compliance Documents (First 10)',
        'saved_count': saved_count,
        'results': saved,
    }
    return render(request, 'main/download_first10_by_commodity.html', context)


@login_required
@role_required(['developer'])
def fetch_store_first_10_matched_docs(request):
    print("[View] fetch_store_first_10_matched_docs: start")
    import os
    import calendar
    from django.conf import settings as dj_settings
    from ..models import Client

    # Load first 10 inspections (most recent)
    inspections = FoodSafetyAgencyInspection.objects.order_by('-date_of_inspection')[:10]

    # Map client -> internal account code
    client_map = {c.name: (c.internal_account_code or 'no') for c in Client.objects.all()}

    # Drive files lookup
    folder_id = '18CbrhqSsZO53TM3D8hRxkVmZyRBF-Zi4'
    drive = GoogleDriveService()
    files = drive.list_files_in_folder(folder_id, request=request)
    lookup = GoogleDriveService.build_file_lookup(files)

    def classify_category(file_name: str) -> str:
        name = (file_name or '').lower()
        if 'invoice' in name:
            return 'invoice'
        if 'rfi' in name or 'request for information' in name:
            return 'rfi'
        if 'lab' in name:
            return 'lab results'
        if 'retest' in name:
            return 'retest'
        return 'compliance'

    def month_name(dt):
        return calendar.month_name[dt.month]

    saved = []
    for ins in inspections:
        account_code = client_map.get(ins.client_name, 'no')
        # Find best file id based on commodity/account/date like earlier function
        best = None
        best_days = 10**9
        commodity = (ins.commodity or '').strip().lower()
        if commodity == 'eggs':
            commodity = 'egg'
        for f in lookup.values():
            if f['commodity'].lower() == commodity and f['accountCode'] == account_code:
                days = abs((f['zipDate'] - (ins.date_of_inspection or f['zipDate'])).days)
                if days <= 15 and days < best_days:
                    best_days = days
                    best = f

        if not best:
            saved.append({'client_name': ins.client_name, 'status': 'no_match'})
            continue

        # Build folder path: media/inspection/YYYY/Month/ClientName/<category>/
        if not ins.date_of_inspection:
            saved.append({'client_name': ins.client_name, 'status': 'no_date'})
            continue
        year_str = f"{ins.date_of_inspection.year}"
        month_str = month_name(ins.date_of_inspection)
        client_folder_name = (ins.client_name or 'Unknown').replace(' ', '')
        category = classify_category(best['name'])

        dest_dir = os.path.join(
            dj_settings.MEDIA_ROOT,
            'inspection',
            year_str,
            month_str,
            client_folder_name,
            category
        )
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, best['name'])

        try:
            if not os.path.exists(dest_path):
                drive.download_file(best['id'], dest_path, request=request)
            saved.append({'client_name': ins.client_name, 'file': dest_path, 'category': category})
        except Exception as e:
            saved.append({'client_name': ins.client_name, 'error': str(e)})

    print(f"[View] fetch_store_first_10_matched_docs: saved_count={len([s for s in saved if 'file' in s])}")
    return JsonResponse({'success': True, 'saved_count': len([s for s in saved if 'file' in s]), 'items': saved})

@login_required
@role_required(['admin', 'super_admin', 'developer'])
def user_management(request):
    """User management page for administrators"""
    from main.models import InspectorMapping
    
    # Check if user has admin, super_admin, or developer role
    if not (request.user.has_role_permission('admin') or request.user.has_role_permission('super_admin') or request.user.has_role_permission('developer') or request.user.is_staff):
        messages.error(request, "You don't have permission to access user management.")
        return redirect('home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_user':
            # Add new user
            username = request.POST.get('new_username')
            email = request.POST.get('new_email')
            password1 = request.POST.get('new_password1')
            password2 = request.POST.get('new_password2')
            first_name = request.POST.get('new_first_name', '')
            last_name = request.POST.get('new_last_name', '')
            role = request.POST.get('new_role', 'inspector')
            inspector_id = request.POST.get('new_inspector_id', '')
            
            # Only developers can create other developers
            if role == 'developer' and request.user.role != 'developer':
                messages.error(request, "Only developers can create users with developer status.")
            # Validation
            elif not username or not email or not password1:
                messages.error(request, "Username, email, and password are required.")
            elif password1 != password2:
                messages.error(request, "Passwords do not match.")
            elif User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
            elif role == 'inspector' and inspector_id:
                # Check if inspector ID already exists
                if InspectorMapping.objects.filter(inspector_id=inspector_id).exists():
                    messages.error(request, f"Inspector ID {inspector_id} is already assigned to another inspector.")
                else:
                    try:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=password1,
                            first_name=first_name,
                            last_name=last_name
                        )
                        # Set role
                        user.role = role
                        user.save()
                        
                        # Create inspector mapping if inspector ID is provided
                        if inspector_id:
                            inspector_name = f"{first_name} {last_name}".strip() or username
                            InspectorMapping.objects.create(
                                inspector_id=int(inspector_id),
                                inspector_name=inspector_name,
                                is_active=True
                            )
                            messages.success(request, f"User '{username}' created successfully with role '{role}' and inspector ID '{inspector_id}'.")
                        else:
                            messages.success(request, f"User '{username}' created successfully with role '{role}'.")
                    except Exception as e:
                        messages.error(request, f"Error creating user: {str(e)}")
            else:
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password1,
                        first_name=first_name,
                        last_name=last_name
                    )
                    # Set role
                    user.role = role
                    user.save()
                    messages.success(request, f"User '{username}' created successfully with role '{role}'.")
                except Exception as e:
                    messages.error(request, f"Error creating user: {str(e)}")
        
        elif action == 'toggle_user_status':
            # Toggle user active status
            user_id = request.POST.get('user_id')
            print(f"🔄 Toggle user status - User ID: {user_id}")
            try:
                user = User.objects.get(id=user_id)
                old_status = user.is_active
                user.is_active = not user.is_active
                user.save()
                status = "activated" if user.is_active else "deactivated"
                print(f"✅ User '{user.username}' {status} successfully. Old: {old_status}, New: {user.is_active}")
                messages.success(request, f"User '{user.username}' {status} successfully.")
                # Redirect to refresh the page and show updated status
                return redirect('user_management')
            except User.DoesNotExist:
                print(f"❌ User not found with ID: {user_id}")
                messages.error(request, "User not found.")
            except Exception as e:
                print(f"❌ Error updating user status: {str(e)}")
                messages.error(request, f"Error updating user status: {str(e)}")
        
        elif action == 'reset_password':
            # Reset user password
            user_id = request.POST.get('user_id')
            new_password = request.POST.get('new_password')
            try:
                user = User.objects.get(id=user_id)
                user.password = make_password(new_password)
                user.save()
                messages.success(request, f"Password for user '{user.username}' reset successfully.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
            except Exception as e:
                messages.error(request, f"Error resetting password: {str(e)}")
        
        elif action == 'delete_user':
            # Delete user
            user_id = request.POST.get('user_id')
            try:
                user_to_delete = User.objects.get(id=user_id)
                
                # Only admin, super_admin, or developer users can delete other users
                if request.user.role not in ['admin', 'super_admin', 'developer']:
                    messages.error(request, "Only admin, super admin, or developer users can delete other users.")
                # Prevent self-deletion
                elif user_to_delete == request.user:
                    messages.error(request, "You cannot delete your own account.")
                # Prevent deletion of developer accounts
                elif user_to_delete.role == 'developer':
                    messages.error(request, "Cannot delete developer accounts.")
                # Allow admin to delete any non-developer user
                else:
                    username = user_to_delete.username
                    user_to_delete.delete()
                    messages.success(request, f"User '{username}' deleted successfully.")
                    
            except User.DoesNotExist:
                messages.error(request, "User not found.")
            except Exception as e:
                messages.error(request, f"Error deleting user: {str(e)}")
        
        elif action == 'edit_user':
            # Edit user information
            user_id = request.POST.get('user_id')
            try:
                user_to_edit = User.objects.get(id=user_id)
                
                # Only super_admin and developer users can edit user information
                if request.user.role not in ['super_admin', 'developer']:
                    messages.error(request, "Only super admin and developer users can edit user information.")
                else:
                    # Only developers can make other users developers
                    if role == 'developer' and request.user.role != 'developer':
                        messages.error(request, "Only developers can create or promote users to developer status.")
                        return redirect('user_management')
                    # Get form data
                    username = request.POST.get('edit_username', '').strip()
                    email = request.POST.get('edit_email', '').strip()
                    first_name = request.POST.get('edit_first_name', '').strip()
                    last_name = request.POST.get('edit_last_name', '').strip()
                    role = request.POST.get('edit_role', 'inspector')
                    phone_number = request.POST.get('edit_phone_number', '').strip()
                    department = request.POST.get('edit_department', '').strip()
                    employee_id = request.POST.get('edit_employee_id', '').strip()
                    inspector_id = request.POST.get('edit_inspector_id', '').strip()
                    password1 = request.POST.get('edit_password1', '').strip()
                    password2 = request.POST.get('edit_password2', '').strip()
                    
                    # Validation
                    if not username:
                        messages.error(request, "Username is required.")
                    elif not email:
                        messages.error(request, "Email is required.")
                    elif User.objects.filter(username=username).exclude(id=user_id).exists():
                        messages.error(request, "Username already exists for another user.")
                    elif User.objects.filter(email=email).exclude(id=user_id).exists():
                        messages.error(request, "Email already exists for another user.")
                    elif password1 and password1 != password2:
                        messages.error(request, "Passwords do not match.")
                    else:
                        # Update user information
                        user_to_edit.username = username
                        user_to_edit.email = email
                        user_to_edit.first_name = first_name
                        user_to_edit.last_name = last_name
                        user_to_edit.role = role
                        user_to_edit.phone_number = phone_number
                        user_to_edit.department = department
                        user_to_edit.employee_id = employee_id
                        
                        # Update password if provided
                        if password1:
                            user_to_edit.set_password(password1)
                        
                        user_to_edit.save()
                        
                        # Handle inspector ID if role is inspector
                        if role == 'inspector' and inspector_id:
                            # Update or create inspector mapping
                            full_name = f"{first_name} {last_name}".strip() or user_to_edit.username
                            mapping, created = InspectorMapping.objects.get_or_create(
                                inspector_name=full_name,
                                defaults={'inspector_id': int(inspector_id)}
                            )
                            if not created:
                                mapping.inspector_id = int(inspector_id)
                                mapping.save()
                        
                        messages.success(request, f"User '{user_to_edit.username}' information updated successfully.")
                        
            except User.DoesNotExist:
                messages.error(request, "User not found.")
            except ValueError as e:
                messages.error(request, f"Invalid inspector ID: {str(e)}")
            except Exception as e:
                messages.error(request, f"Error updating user: {str(e)}")
    
    # Get all users (including developers for super_admin and developer roles)
    if request.user.role in ['super_admin', 'developer']:
        users = User.objects.all().order_by('username')
    else:
        users = User.objects.exclude(role='developer').order_by('username')
    
    # Get all inspector mappings
    inspector_mappings = InspectorMapping.objects.all().order_by('inspector_name')
    
    # Create a dictionary to map user names to inspector IDs
    inspector_id_map = {}
    for mapping in inspector_mappings:
        inspector_id_map[mapping.inspector_name] = mapping.inspector_id
    
    # Add inspector_id to each user object for easy template access
    for user in users:
        if user.role == 'inspector':
            user.inspector_id = inspector_id_map.get(user.get_full_name() or user.username)
        else:
            user.inspector_id = None
    
            # Role choices for the form
        role_choices = [
            ('inspector', 'Inspector'),
            ('admin', 'HR/Admin Staff'),
            ('super_admin', 'Super Admin'),
            ('financial', 'Financial'),
            ('scientist', 'Scientist'),
            ('developer', 'Developer'),  # Hidden role
        ]
    
    # Get theme settings
    try:
        from ..models import SystemSettings
        system_settings = SystemSettings.get_settings()
        settings = type('Settings', (), {
            'dark_mode': system_settings.theme_mode == 'dark' if hasattr(system_settings, 'theme_mode') else False,
        })()
    except Exception:
        settings = type('Settings', (), {'dark_mode': False})()
    
    context = {
        'users': users,
        'inspector_mappings': inspector_mappings,
        'role_choices': role_choices,
        'settings': settings,
    }
    
    return render(request, 'main/user_management.html', context)

@login_required
@inspector_only_inspections
def system_logs(request):
    """Display system logs with filtering and pagination."""
    if not (request.user.is_staff or request.user.role in ['admin', 'super_admin', 'developer']):
        messages.error(request, "You don't have permission to access system logs.")
        return redirect('home')
    
    # Get filter parameters
    user_filter = request.GET.get('user', '')
    action_filter = request.GET.get('action', '')
    page_filter = request.GET.get('page', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    show_all = request.GET.get('show_all', 'false') == 'true'
    
    # Build query
    logs = SystemLog.objects.select_related('user').all()
    
    # Apply filters
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if page_filter:
        logs = logs.filter(page__icontains=page_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            logs = logs.filter(timestamp__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Get total count before pagination
    total_logs = logs.count()
    
    # Pagination
    if not show_all:
        paginator = Paginator(logs, 50)  # Show 50 logs per page
        page_number = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page_number)
            logs = page_obj.object_list
        except:
            page_obj = paginator.page(1)
            logs = page_obj.object_list
    else:
        page_obj = None
        logs = logs[:1000]  # Limit to 1000 logs when showing all
    
    # Get unique values for filter dropdowns
    users = User.objects.filter(system_logs__isnull=False).distinct().order_by('username')
    actions = SystemLog.objects.values_list('action', flat=True).distinct().order_by('action')
    pages = SystemLog.objects.values_list('page', flat=True).exclude(page__isnull=True).exclude(page='').distinct().order_by('page')
    
    # Get theme settings
    try:
        from ..models import SystemSettings
        system_settings = SystemSettings.get_settings()
        settings = type('Settings', (), {
            'dark_mode': system_settings.theme_mode == 'dark' if hasattr(system_settings, 'theme_mode') else False,
        })()
    except Exception:
        settings = type('Settings', (), {'dark_mode': False})()
    
    context = {
        'logs': logs,
        'page_obj': page_obj,
        'total_logs': total_logs,
        'users': users,
        'actions': actions,
        'pages': pages,
        'filters': {
            'user': user_filter,
            'action': action_filter,
            'page': page_filter,
            'date_from': date_from,
            'date_to': date_to,
            'show_all': show_all,
        },
        'settings': settings,
    }
    
    return render(request, 'main/system_logs.html', context)


# =============================================================================
# INSPECTOR MAPPING MANAGEMENT VIEWS
# =============================================================================

@login_required
@inspector_only_inspections
def inspector_mapping_list(request):
    """Display list of all inspector mappings."""
    clear_messages(request)
    
    # Get all inspector mappings
    mappings = InspectorMapping.objects.all().order_by('inspector_name')
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    active_filter = request.GET.get('active', '')
    
    # Apply filters
    if search_query:
        mappings = mappings.filter(
            Q(inspector_name__icontains=search_query) |
            Q(inspector_id__icontains=search_query)
        )
    
    if active_filter == 'true':
        mappings = mappings.filter(is_active=True)
    elif active_filter == 'false':
        mappings = mappings.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(mappings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'mappings': page_obj,
        'total_mappings': mappings.count(),
        'search_query': search_query,
        'active_filter': active_filter,
    }
    
    return render(request, 'main/inspector_mapping_list.html', context)


@login_required
@inspector_only_inspections
def add_inspector_mapping(request):
    """Add a new inspector mapping."""
    clear_messages(request)
    
    if request.method == 'POST':
        form = InspectorMappingForm(request.POST)
        if form.is_valid():
            try:
                mapping = form.save()
                messages.success(request, f"Inspector mapping '{mapping.inspector_name}' (ID: {mapping.inspector_id}) created successfully!")
                return redirect('inspector_mapping_list')
            except Exception as e:
                messages.error(request, f"Error creating inspector mapping: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = InspectorMappingForm()
    
    context = {
        'form': form,
        'action': 'Add'
    }
    
    return render(request, 'main/inspector_mapping_form.html', context)


@login_required
@inspector_only_inspections
def edit_inspector_mapping(request, pk):
    """Edit an existing inspector mapping."""
    clear_messages(request)
    
    mapping = get_object_or_404(InspectorMapping, pk=pk)
    
    if request.method == 'POST':
        form = InspectorMappingForm(request.POST, instance=mapping)
        if form.is_valid():
            try:
                mapping = form.save()
                messages.success(request, f"Inspector mapping '{mapping.inspector_name}' (ID: {mapping.inspector_id}) updated successfully!")
                return redirect('inspector_mapping_list')
            except Exception as e:
                messages.error(request, f"Error updating inspector mapping: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = InspectorMappingForm(instance=mapping)
    
    context = {
        'form': form,
        'mapping': mapping,
        'action': 'Edit'
    }
    
    return render(request, 'main/inspector_mapping_form.html', context)


@login_required
@inspector_only_inspections
def delete_inspector_mapping(request, pk):
    """Delete an inspector mapping."""
    clear_messages(request)
    
    mapping = get_object_or_404(InspectorMapping, pk=pk)
    
    if request.method == 'POST':
        try:
            inspector_name = mapping.inspector_name
            inspector_id = mapping.inspector_id
            mapping.delete()
            messages.success(request, f"Inspector mapping '{inspector_name}' (ID: {inspector_id}) deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting inspector mapping: {str(e)}")
    
    return redirect('inspector_mapping_list')

@login_required
def update_bought_sample(request):
    """Update bought sample value for an inspection."""
    if request.method == 'POST':
        try:
            from ..models import FoodSafetyAgencyInspection, InspectorMapping
            from django.http import JsonResponse
            
            inspection_id = request.POST.get('inspection_id')
            bought_sample_value = request.POST.get('bought_sample')
            
            if not inspection_id:
                return JsonResponse({'success': False, 'error': 'Inspection ID is required'})
            
            # Find the inspection
            inspection = FoodSafetyAgencyInspection.objects.filter(remote_id=inspection_id).first()
            if not inspection:
                return JsonResponse({'success': False, 'error': 'Inspection not found'})
            
            # Check if user has permission to edit this inspection
            if request.user.role == 'inspector':
                # Get the inspector ID for the current user
                inspector_id = None
                try:
                    inspector_mapping = InspectorMapping.objects.get(
                        inspector_name=request.user.get_full_name() or request.user.username
                    )
                    inspector_id = inspector_mapping.inspector_id
                except InspectorMapping.DoesNotExist:
                    try:
                        inspector_mapping = InspectorMapping.objects.get(
                            inspector_name=request.user.username
                        )
                        inspector_id = inspector_mapping.inspector_id
                    except InspectorMapping.DoesNotExist:
                        inspector_id = None
                
                # Check if this inspection belongs to the current inspector
                if not inspector_id or inspection.inspector_id != inspector_id:
                    return JsonResponse({'success': False, 'error': 'You can only edit your own inspections'})
            
            # For admin, super_admin, financial, and scientist roles, allow editing any inspection
            # (no additional permission check needed)
            
            # Update the bought sample value
            if bought_sample_value == '' or bought_sample_value is None:
                # If empty, set to None (will show as "No" in template)
                inspection.bought_sample = None
            else:
                try:
                    inspection.bought_sample = float(bought_sample_value)
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Invalid bought sample value'})
            
            inspection.save()
            
            return JsonResponse({'success': True, 'message': 'Bought sample updated successfully'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
def onedrive_callback(request):
    """Handle OneDrive OAuth callback."""
    from django.http import HttpResponse
    import requests
    import json
    import os
    from datetime import datetime
    from django.conf import settings
    
    # Get the authorization code from the URL
    code = request.GET.get('code')
    
    if code:
        print(f"✅ OneDrive authorization code received: {code}")
        
        try:
            # Exchange authorization code for access token
            token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            token_data = {
                'client_id': settings.ONEDRIVE_CLIENT_ID,
                'client_secret': settings.ONEDRIVE_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': settings.ONEDRIVE_REDIRECT_URI
            }
            
            response = requests.post(token_url, data=token_data)
            
            if response.status_code == 200:
                token_response = response.json()
                access_token = token_response.get('access_token')
                refresh_token = token_response.get('refresh_token')
                
                if access_token:
                    # Save tokens to file for the service to use
                    token_data = {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'expires_in': token_response.get('expires_in'),
                        'token_type': token_response.get('token_type'),
                        'expires_at': datetime.now().timestamp() + token_response.get('expires_in', 3600)
                    }
                    
                    token_file = os.path.join(settings.BASE_DIR, 'onedrive_tokens.json')
                    with open(token_file, 'w') as f:
                        json.dump(token_data, f, indent=2)
                    
                    print(f"✅ Tokens saved to: {token_file}")
                    print("✅ OneDrive authentication setup complete!")
                    
                    # Return success page
                    return HttpResponse(f"""
                    <html>
                    <head><title>OneDrive Authentication Success</title></head>
                    <body>
                    <h1>✅ OneDrive Authentication Successful!</h1>
                    <p>Authorization code received: {code}</p>
                    <p>✅ Access and refresh tokens have been saved!</p>
                    <p>You can now close this window and return to the application.</p>
                    <script>
                        // Auto-close after 3 seconds
                        setTimeout(function() {{
                            window.close();
                        }}, 3000);
                    </script>
                    </body>
                    </html>
                    """)
                else:
                    print("❌ No access token received")
                    return HttpResponse("❌ No access token received", status=400)
            else:
                print(f"❌ Token exchange failed: {response.status_code} - {response.text}")
                return HttpResponse(f"❌ Token exchange failed: {response.status_code}", status=400)
                
        except Exception as e:
            print(f"❌ Token exchange failed: {e}")
            return HttpResponse(f"❌ Token exchange failed: {e}", status=400)
    else:
        return HttpResponse("❌ No authorization code received", status=400)













@login_required(login_url='login')
@role_required(['developer'])
def performance_monitor(request):
    """Monitor performance metrics and cache statistics."""
    from django.core.cache import cache
    import time
    
    # Get cache statistics
    cache_stats = {
        'shipment_list_cache_hits': cache.get('shipment_list_cache_hits', 0),
        'compliance_status_cache_hits': cache.get('compliance_status_cache_hits', 0),
        'onedrive_compliance_cache_hits': cache.get('onedrive_compliance_cache_hits', 0),
        'client_maps_cache_hits': cache.get('client_maps_cache_hits', 0),
    }
    
    # Get recent performance data
    recent_load_times = cache.get('recent_load_times', [])
    
    # Get theme settings
    try:
        from ..models import SystemSettings
        system_settings = SystemSettings.get_settings()
        settings = type('Settings', (), {
            'dark_mode': system_settings.theme_mode == 'dark' if hasattr(system_settings, 'theme_mode') else False,
        })()
    except Exception:
        settings = type('Settings', (), {'dark_mode': False})()
    
    context = {
        'cache_stats': cache_stats,
        'recent_load_times': recent_load_times[-10:],  # Last 10 load times
        'average_load_time': sum(recent_load_times) / len(recent_load_times) if recent_load_times else 0,
        'settings': settings,
    }
    
    return render(request, 'main/performance_monitor.html', context)

@login_required(login_url='login')
def server_status(request):
    """Check server health and performance metrics."""
    from django.core.cache import cache
    from django.db import connection
    import psutil
    import os
    
    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Get database metrics
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM food_safety_agency_inspections")
        inspection_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM food_safety_agency_clients")
        client_count = cursor.fetchone()[0]
    
    # Get cache metrics
    cache_hits = cache.get('cache_hits', 0)
    cache_misses = cache.get('cache_misses', 0)
    cache_hit_rate = (cache_hits / (cache_hits + cache_misses)) * 100 if (cache_hits + cache_misses) > 0 else 0
    
    context = {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'memory_available': memory.available // (1024**3),  # GB
        'disk_percent': disk.percent,
        'disk_free': disk.free // (1024**3),  # GB
        'inspection_count': inspection_count,
        'client_count': client_count,
        'cache_hits': cache_hits,
        'cache_misses': cache_misses,
        'cache_hit_rate': cache_hit_rate,
        'server_uptime': time.time() - psutil.boot_time(),
    }
    
    return render(request, 'main/server_status.html', context)


# =============================================================================
# CLIENT AUTOCOMPLETE API
# =============================================================================

@login_required
def client_autocomplete_api(request):
    """API endpoint for client autocomplete suggestions."""
    from django.http import JsonResponse
    from ..models import Client, FoodSafetyAgencyInspection
    
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    try:
        # Get unique client names from both Client model and FoodSafetyAgencyInspection
        # This ensures we get all clients that have inspections
        client_suggestions = []
        
        # Get clients from Client model
        clients = Client.objects.filter(
            Q(client_id__icontains=query) | 
            Q(name__icontains=query)
        ).values('client_id', 'name', 'internal_account_code').distinct()[:10]
        
        for client in clients:
            client_name = client['name'] or client['client_id']
            if client_name:
                client_suggestions.append({
                    'name': client_name,
                    'account_code': client['internal_account_code'] or '',
                    'type': 'client'
                })
        
        # Get additional clients from inspection data that might not be in Client model
        inspection_clients = FoodSafetyAgencyInspection.objects.filter(
            client_name__icontains=query
        ).values_list('client_name', flat=True).distinct()[:10]
        
        for client_name in inspection_clients:
            if client_name and not any(s['name'] == client_name for s in client_suggestions):
                client_suggestions.append({
                    'name': client_name,
                    'account_code': '',
                    'type': 'inspection'
                })
        
        # Sort by name and limit to 15 total suggestions
        client_suggestions.sort(key=lambda x: x['name'].lower())
        client_suggestions = client_suggestions[:15]
        
        return JsonResponse({'suggestions': client_suggestions})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def scheduled_backup_service_status(request):
    """Get scheduled backup service status."""
    try:
        from ..services.scheduled_backup_service import get_scheduled_backup_service_status
        
        status = get_scheduled_backup_service_status()
        return JsonResponse(status)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def start_scheduled_backup_service(request):
    """Start the scheduled backup service."""
    try:
        from ..services.scheduled_backup_service import start_scheduled_backup_service
        
        success, message = start_scheduled_backup_service()
        return JsonResponse({'success': success, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def stop_scheduled_backup_service(request):
    """Stop the scheduled backup service."""
    try:
        from ..services.scheduled_backup_service import stop_scheduled_backup_service
        
        success, message = stop_scheduled_backup_service()
        return JsonResponse({'success': success, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def run_manual_backup(request):
    """Run a manual backup."""
    try:
        from ..services.scheduled_backup_service import run_manual_backup
        
        success, message = run_manual_backup()
        return JsonResponse({'success': success, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# MASTER SERVICE CONTROL
# =============================================================================

@login_required
def master_service_control_status(request):
    """Get the status of all background services."""
    try:
        services_status = {}
        
        # Daily Compliance Sync Service
        try:
            from ..services.daily_compliance_sync import daily_sync_service
            services_status['daily_compliance_sync'] = {
                'name': 'Daily Compliance Sync',
                'running': daily_sync_service.is_running,
                'status': {}
            }
        except Exception as e:
            services_status['daily_compliance_sync'] = {
                'name': 'Daily Compliance Sync',
                'running': False,
                'status': {'error': str(e)}
            }
        
        # Scheduled Sync Service
        try:
            from ..services.scheduled_sync_service import ScheduledSyncService
            sync_service = ScheduledSyncService()
            services_status['scheduled_sync'] = {
                'name': 'Scheduled Sync',
                'running': sync_service.is_running,
                'status': {}
            }
        except Exception as e:
            services_status['scheduled_sync'] = {
                'name': 'Scheduled Sync',
                'running': False,
                'status': {'error': str(e)}
            }
        
        # Scheduled Backup Service
        try:
            from ..services.scheduled_backup_service import ScheduledBackupService
            backup_service = ScheduledBackupService()
            services_status['scheduled_backup'] = {
                'name': 'Scheduled Backup',
                'running': backup_service.is_running,
                'status': {}
            }
        except Exception as e:
            services_status['scheduled_backup'] = {
                'name': 'Scheduled Backup',
                'running': False,
                'status': {'error': str(e)}
            }
        
        # OneDrive Upload Service (skip if there's an error)
        try:
            from ..services.onedrive_direct_service import OneDriveDirectUploadService, get_onedrive_direct_service_status
            onedrive_service = OneDriveDirectUploadService()
            service_status = get_onedrive_direct_service_status()
            
            # Check OneDrive connection status
            connection_status = onedrive_service.authenticate_onedrive()
            
            services_status['onedrive_upload'] = {
                'name': 'OneDrive Upload',
                'running': onedrive_service.is_running,
                'connected': connection_status,
                'status': service_status
            }
        except Exception as e:
            services_status['onedrive_upload'] = {
                'name': 'OneDrive Upload',
                'running': False,
                'connected': False,
                'status': {'error': 'Service unavailable', 'details': str(e)}
            }
        
        # Calculate overall status
        all_running = all(service['running'] for service in services_status.values())
        any_running = any(service['running'] for service in services_status.values())
        
        return JsonResponse({
            'success': True,
            'services': services_status,
            'all_running': all_running,
            'any_running': any_running,
            'total_services': len(services_status),
            'running_services': sum(1 for service in services_status.values() if service['running'])
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def start_all_services(request):
    """Start all background services."""
    try:
        results = {}
        errors = []
        
        # Start Daily Compliance Sync
        try:
            from ..services.daily_compliance_sync import daily_sync_service
            if not daily_sync_service.is_running:
                daily_sync_service.start_daily_sync(manual_start=True)
                results['daily_compliance_sync'] = 'Started successfully'
            else:
                results['daily_compliance_sync'] = 'Already running'
        except Exception as e:
            error_msg = f"Daily Compliance Sync: {str(e)}"
            errors.append(error_msg)
            results['daily_compliance_sync'] = f"Failed: {str(e)}"
        
        # Start Scheduled Sync Service
        try:
            from ..services.scheduled_sync_service import start_scheduled_sync_service
            success, message = start_scheduled_sync_service()
            results['scheduled_sync'] = message
            if not success:
                errors.append(f"Scheduled Sync: {message}")
        except Exception as e:
            error_msg = f"Scheduled Sync: {str(e)}"
            errors.append(error_msg)
            results['scheduled_sync'] = f"Failed: {str(e)}"
        
        # Start Scheduled Backup Service
        try:
            from ..services.scheduled_backup_service import start_scheduled_backup_service
            success, message = start_scheduled_backup_service()
            results['scheduled_backup'] = message
            if not success:
                errors.append(f"Scheduled Backup: {message}")
        except Exception as e:
            error_msg = f"Scheduled Backup: {str(e)}"
            errors.append(error_msg)
            results['scheduled_backup'] = f"Failed: {str(e)}"
        
        # Start OneDrive Upload Service (skip if unavailable)
        try:
            from ..services.onedrive_direct_service import OneDriveDirectUploadService
            onedrive_service = OneDriveDirectUploadService()
            success, message = onedrive_service.start_background_service()
            results['onedrive_upload'] = message
            if not success:
                errors.append(f"OneDrive Upload: {message}")
        except Exception as e:
            error_msg = f"OneDrive Upload: {str(e)}"
            errors.append(error_msg)
            results['onedrive_upload'] = f"Service unavailable"
        
        # Log the activity
        try:
            SystemLog.log_activity(
                user=request.user,
                action='SETTINGS',
                page=request.path,
                description='Started all background services via Master Service Control',
                details={'results': results, 'errors': errors}
            )
        except Exception:
            pass
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Some services failed to start',
                'results': results,
                'errors': errors
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'All services started successfully',
                'results': results
            })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def stop_all_services(request):
    """Stop all background services."""
    try:
        from ..services.daily_compliance_sync import daily_sync_service
        from ..services.scheduled_sync_service import stop_scheduled_sync_service
        from ..services.scheduled_backup_service import stop_scheduled_backup_service
        from ..services.onedrive_direct_service import OneDriveDirectUploadService
        
        results = {}
        errors = []
        
        # Stop Daily Compliance Sync
        try:
            if daily_sync_service.is_running:
                daily_sync_service.stop_daily_sync()
                results['daily_compliance_sync'] = 'Stopped successfully'
            else:
                results['daily_compliance_sync'] = 'Was not running'
        except Exception as e:
            error_msg = f"Daily Compliance Sync: {str(e)}"
            errors.append(error_msg)
            results['daily_compliance_sync'] = f"Failed: {str(e)}"
        
        # Stop Scheduled Sync Service
        try:
            success, message = stop_scheduled_sync_service()
            results['scheduled_sync'] = message
            if not success:
                errors.append(f"Scheduled Sync: {message}")
        except Exception as e:
            error_msg = f"Scheduled Sync: {str(e)}"
            errors.append(error_msg)
            results['scheduled_sync'] = f"Failed: {str(e)}"
        
        # Stop Scheduled Backup Service
        try:
            success, message = stop_scheduled_backup_service()
            results['scheduled_backup'] = message
            if not success:
                errors.append(f"Scheduled Backup: {message}")
        except Exception as e:
            error_msg = f"Scheduled Backup: {str(e)}"
            errors.append(error_msg)
            results['scheduled_backup'] = f"Failed: {str(e)}"
        
        # Stop OneDrive Upload Service
        try:
            onedrive_service = OneDriveDirectUploadService()
            success, message = onedrive_service.stop_background_service()
            results['onedrive_upload'] = message
            if not success:
                errors.append(f"OneDrive Upload: {message}")
        except Exception as e:
            error_msg = f"OneDrive Upload: {str(e)}"
            errors.append(error_msg)
            results['onedrive_upload'] = f"Failed: {str(e)}"
        
        # Log the activity
        try:
            SystemLog.log_activity(
                user=request.user,
                action='SETTINGS',
                page=request.path,
                description='Stopped all background services via Master Service Control',
                details={'results': results, 'errors': errors}
            )
        except Exception:
            pass
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': 'Some services failed to stop',
                'results': results,
                'errors': errors
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'All services stopped successfully',
                'results': results
            })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# ONEDRIVE SERVICE CONTROL
# =============================================================================

@login_required
def onedrive_service_status(request):
    """Get OneDrive service status and connection info."""
    try:
        from ..services.onedrive_direct_service import OneDriveDirectUploadService, get_onedrive_direct_service_status
        
        onedrive_service = OneDriveDirectUploadService()
        service_status = get_onedrive_direct_service_status()
        
        # Check OneDrive connection status
        connection_status = onedrive_service.authenticate_onedrive()
        
        # Get OneDrive settings
        from ..models import SystemSettings
        settings = SystemSettings.get_settings()
        upload_delay = getattr(settings, 'onedrive_upload_delay_days', 3)
        onedrive_enabled = getattr(settings, 'onedrive_enabled', False)
        
        return JsonResponse({
            'success': True,
            'service_running': onedrive_service.is_running,
            'connected': connection_status,
            'enabled': onedrive_enabled,
            'upload_delay_days': upload_delay,
            'status': service_status
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def start_onedrive_service(request):
    """Start OneDrive service."""
    try:
        from ..services.onedrive_direct_service import start_onedrive_direct_background_service
        
        success, message = start_onedrive_direct_background_service()
        
        # Log the activity
        try:
            SystemLog.log_activity(
                user=request.user,
                action='SETTINGS',
                page=request.path,
                description='Started OneDrive service via Master Service Control',
                details={'success': success, 'message': message}
            )
        except Exception:
            pass
        
        return JsonResponse({'success': success, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def stop_onedrive_service(request):
    """Stop OneDrive service."""
    try:
        from ..services.onedrive_direct_service import stop_onedrive_direct_background_service
        
        success, message = stop_onedrive_direct_background_service()
        
        # Log the activity
        try:
            SystemLog.log_activity(
                user=request.user,
                action='SETTINGS',
                page=request.path,
                description='Stopped OneDrive service via Master Service Control',
                details={'success': success, 'message': message}
            )
        except Exception:
            pass
        
        return JsonResponse({'success': success, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def test_onedrive_connection(request):
    """Test OneDrive connection."""
    try:
        from ..services.onedrive_direct_service import OneDriveDirectUploadService
        
        onedrive_service = OneDriveDirectUploadService()
        connection_status = onedrive_service.authenticate_onedrive()
        
        # Log the activity
        try:
            SystemLog.log_activity(
                user=request.user,
                action='SETTINGS',
                page=request.path,
                description='Tested OneDrive connection',
                details={'connected': connection_status}
            )
        except Exception:
            pass
        
        if connection_status:
            return JsonResponse({
                'success': True, 
                'message': 'OneDrive connection successful',
                'connected': True
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'OneDrive connection failed. Please check authentication.',
                'connected': False
            })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def reauthenticate_onedrive(request):
    """Re-authenticate OneDrive by generating authorization URL."""
    try:
        from django.conf import settings
        
        # Check if OneDrive is enabled
        if not getattr(settings, 'ONEDRIVE_ENABLED', False):
            return JsonResponse({
                'success': False, 
                'message': 'OneDrive integration is not enabled in settings',
                'requires_setup': True
            })
        
        # Generate authorization URL
        client_id = getattr(settings, 'ONEDRIVE_CLIENT_ID', '')
        redirect_uri = getattr(settings, 'ONEDRIVE_REDIRECT_URI', 'http://localhost:8000/onedrive/callback')
        
        if not client_id:
            return JsonResponse({
                'success': False, 
                'message': 'OneDrive Client ID not configured',
                'requires_setup': True
            })
        
        # Generate authorization URL - try common endpoint first (works for both org and consumer)
        auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        auth_params = {
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': 'Files.ReadWrite.All',
            'response_mode': 'query',
            'prompt': 'consent'  # Force consent to ensure refresh token is provided
        }
        
        # Build the authorization URL
        auth_url_with_params = f"{auth_url}?{'&'.join([f'{k}={v}' for k, v in auth_params.items()])}"
        
        # Log the activity
        try:
            SystemLog.log_activity(
                user=request.user,
                action='SETTINGS',
                page=request.path,
                description='Generated OneDrive authorization URL for re-authentication',
                details={'auth_url': auth_url_with_params}
            )
        except Exception:
            pass
        
        return JsonResponse({
            'success': True, 
            'message': 'Authorization URL generated. Please visit the URL to complete re-authentication.',
            'auth_url': auth_url_with_params,
            'instructions': [
                '1. Click the authorization URL below',
                '2. Sign in with your Microsoft account',
                '3. Grant permissions to the app',
                '4. You will be redirected back to the application',
                '5. The tokens will be automatically saved and refreshed'
            ]
        })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_onedrive_auth_url(request):
    """Get OneDrive authorization URL for manual authentication."""
    try:
        from django.conf import settings
        
        # Check if OneDrive is enabled
        if not getattr(settings, 'ONEDRIVE_ENABLED', False):
            return JsonResponse({
                'success': False, 
                'message': 'OneDrive integration is not enabled in settings'
            })
        
        # Generate authorization URL
        auth_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize"
        auth_params = {
            'client_id': settings.ONEDRIVE_CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': settings.ONEDRIVE_REDIRECT_URI,
            'scope': 'Files.ReadWrite.All',
            'response_mode': 'query'
        }
        
        # Build the authorization URL
        auth_url_with_params = f"{auth_url}?{'&'.join([f'{k}={v}' for k, v in auth_params.items()])}"
        
        return JsonResponse({
            'success': True,
            'auth_url': auth_url_with_params,
            'message': 'Click the URL to authenticate with OneDrive'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)  