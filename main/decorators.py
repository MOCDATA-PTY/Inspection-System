from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.contrib.auth.decorators import login_required

def role_required(allowed_roles):
    """
    Decorator to check if user has the required role(s).
    
    Usage:
    @role_required(['admin', 'super_admin'])
    @role_required(['financial'])
    @role_required(['inspector'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            user_role = getattr(request.user, 'role', 'inspector')
            
            # Check if user's role is in the allowed roles
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('home')
        
        return _wrapped_view
    return decorator

def inspector_restricted(view_func):
    """
    Decorator to restrict Inspector access to specific features.
    Inspectors cannot upload invoicing or lab results.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        user_role = getattr(request.user, 'role', 'inspector')
        
        # If user is an inspector, deny access
        if user_role == 'inspector':
            return redirect('home')
        
        # Allow access for all other roles
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def financial_only(view_func):
    """
    Decorator to restrict access to financial features only.
    Only financial, admin, and super_admin roles can access.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        user_role = getattr(request.user, 'role', 'inspector')
        allowed_roles = ['financial', 'admin', 'super_admin']
        
        if user_role in allowed_roles:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home')
    
    return _wrapped_view


def inspector_only_inspections(view_func):
    """
    Decorator to restrict Inspector and Lab Technician access to only the inspections page.
    Inspectors and Lab Technicians can only access the inspections page and related inspection functions.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        user_role = getattr(request.user, 'role', 'inspector')
        
        # If user is an inspector or scientist (lab technician), redirect to inspections page
        if user_role == 'inspector' or user_role == 'scientist':
            role_display = "Inspector" if user_role == 'inspector' else "Lab Technician"
            return redirect('shipment_list')
        
        # Allow access for all other roles
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def scientist_only(view_func):
    """
    Decorator to restrict access to scientist features only.
    Only scientist, admin, and super_admin roles can access.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        user_role = getattr(request.user, 'role', 'inspector')
        allowed_roles = ['scientist', 'admin', 'super_admin']
        
        if user_role in allowed_roles:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home')
    
    return _wrapped_view


def no_inspector_scientist(view_func):
    """
    Decorator to block inspector and scientist access to specific functions.
    Used for functions that should only be accessible by admin, super_admin, developer, and financial roles.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        user_role = getattr(request.user, 'role', 'inspector')
        
        # Block inspectors and scientists from accessing this function
        if user_role in ['inspector', 'scientist']:
            from django.http import JsonResponse
            return JsonResponse({
                'success': False, 
                'error': f'Access denied: {user_role.title()}s cannot perform this action'
            })
        
        # Allow access for all other roles
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view