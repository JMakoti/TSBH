"""
Access control decorators and mixins for TUVUKE Hub
Implements role-based access control for different user types
"""

from functools import wraps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from .models import Student, Provider


# =====================================================================
# UTILITY FUNCTIONS FOR USER ROLE CHECKING
# =====================================================================

def is_student(user):
    """
    Check if user is a student (has Student profile)
    
    Args:
        user: Django User object
        
    Returns:
        bool: True if user is a student, False otherwise
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        return hasattr(user, 'student_profile') and user.student_profile is not None
    except Exception:
        return False


def is_provider(user):
    """
    Check if user is a scholarship provider (has Provider profile)
    
    Args:
        user: Django User object
        
    Returns:
        bool: True if user is a provider, False otherwise
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        # Check if user has provider access via Provider model
        # This assumes providers have special group membership or staff status
        return (user.is_staff and 
                Provider.objects.filter(email=user.email).exists()) or user.groups.filter(name='Providers').exists()
    except Exception:
        return False


def is_staff_or_admin(user):
    """
    Check if user is staff or admin
    
    Args:
        user: Django User object
        
    Returns:
        bool: True if user is staff or admin, False otherwise
    """
    if not user or not user.is_authenticated:
        return False
    
    return user.is_staff or user.is_superuser


def is_verified_student(user):
    """
    Check if user is a verified student
    
    Args:
        user: Django User object
        
    Returns:
        bool: True if user is a verified student, False otherwise
    """
    if not is_student(user):
        return False
    
    try:
        return user.student_profile.is_verified
    except Exception:
        return False


def is_active_provider(user):
    """
    Check if user is an active provider
    
    Args:
        user: Django User object
        
    Returns:
        bool: True if user is an active provider, False otherwise
    """
    if not is_provider(user):
        return False
    
    try:
        provider = Provider.objects.get(email=user.email)
        return provider.is_active and provider.is_verified
    except Provider.DoesNotExist:
        return False


# =====================================================================
# FUNCTION-BASED VIEW DECORATORS
# =====================================================================

def student_required(view_func):
    """
    Decorator for views that require student access
    
    Usage:
        @student_required
        def student_dashboard(request):
            # Only students can access this view
            pass
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not is_student(request.user):
            messages.error(request, "Access denied. Student account required.")
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def provider_required(view_func):
    """
    Decorator for views that require provider access
    
    Usage:
        @provider_required
        def create_scholarship(request):
            # Only providers can access this view
            pass
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not is_provider(request.user):
            messages.error(request, "Access denied. Provider account required.")
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def staff_required(view_func):
    """
    Decorator for views that require staff access
    
    Usage:
        @staff_required
        def admin_panel(request):
            # Only staff can access this view
            pass
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not is_staff_or_admin(request.user):
            messages.error(request, "Access denied. Staff privileges required.")
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def verified_student_required(view_func):
    """
    Decorator for views that require verified student access
    
    Usage:
        @verified_student_required
        def apply_for_scholarship(request):
            # Only verified students can access this view
            pass
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not is_verified_student(request.user):
            if is_student(request.user):
                messages.warning(request, "Please verify your account to access this feature.")
                return redirect('student_profile')
            else:
                messages.error(request, "Access denied. Verified student account required.")
                return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def active_provider_required(view_func):
    """
    Decorator for views that require active provider access
    
    Usage:
        @active_provider_required
        def manage_scholarships(request):
            # Only active providers can access this view
            pass
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not is_active_provider(request.user):
            if is_provider(request.user):
                messages.warning(request, "Your provider account is pending verification.")
                return redirect('provider_profile')
            else:
                messages.error(request, "Access denied. Active provider account required.")
                return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# =====================================================================
# CLASS-BASED VIEW MIXINS
# =====================================================================

class StudentRequiredMixin(LoginRequiredMixin):
    """
    Mixin for class-based views that require student access
    
    Usage:
        class StudentDashboardView(StudentRequiredMixin, TemplateView):
            template_name = 'students/dashboard.html'
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not is_student(request.user):
            messages.error(request, "Access denied. Student account required.")
            return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)


class ProviderRequiredMixin(LoginRequiredMixin):
    """
    Mixin for class-based views that require provider access
    
    Usage:
        class CreateScholarshipView(ProviderRequiredMixin, CreateView):
            model = Scholarship
            # ... other view configuration
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not is_provider(request.user):
            messages.error(request, "Access denied. Provider account required.")
            return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)


class StaffRequiredMixin(LoginRequiredMixin):
    """
    Mixin for class-based views that require staff access
    
    Usage:
        class AdminPanelView(StaffRequiredMixin, TemplateView):
            template_name = 'admin/panel.html'
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not is_staff_or_admin(request.user):
            messages.error(request, "Access denied. Staff privileges required.")
            return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)


class VerifiedStudentRequiredMixin(LoginRequiredMixin):
    """
    Mixin for class-based views that require verified student access
    
    Usage:
        class ScholarshipApplicationView(VerifiedStudentRequiredMixin, CreateView):
            model = Application
            # ... other view configuration
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not is_verified_student(request.user):
            if is_student(request.user):
                messages.warning(request, "Please verify your account to access this feature.")
                return redirect('student_profile')
            else:
                messages.error(request, "Access denied. Verified student account required.")
                return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)


class ActiveProviderRequiredMixin(LoginRequiredMixin):
    """
    Mixin for class-based views that require active provider access
    
    Usage:
        class ManageScholarshipsView(ActiveProviderRequiredMixin, ListView):
            model = Scholarship
            # ... other view configuration
    """
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not is_active_provider(request.user):
            if is_provider(request.user):
                messages.warning(request, "Your provider account is pending verification.")
                return redirect('provider_profile')
            else:
                messages.error(request, "Access denied. Active provider account required.")
                return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)


class RoleBasedAccessMixin(LoginRequiredMixin):
    """
    Generic role-based access mixin that can be customized
    
    Usage:
        class CustomView(RoleBasedAccessMixin, TemplateView):
            allowed_roles = ['student', 'provider']  # Define allowed roles
            template_name = 'custom.html'
    """
    
    allowed_roles = []  # Override in subclasses
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        user_roles = self.get_user_roles(request.user)
        
        if not any(role in self.allowed_roles for role in user_roles):
            messages.error(request, "Access denied. Insufficient privileges.")
            return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_user_roles(self, user):
        """
        Get list of roles for the user
        
        Args:
            user: Django User object
            
        Returns:
            list: List of role strings
        """
        roles = []
        
        if is_student(user):
            roles.append('student')
            if is_verified_student(user):
                roles.append('verified_student')
        
        if is_provider(user):
            roles.append('provider')
            if is_active_provider(user):
                roles.append('active_provider')
        
        if is_staff_or_admin(user):
            roles.append('staff')
            if user.is_superuser:
                roles.append('admin')
        
        return roles


# =====================================================================
# DJANGO ADMIN ACCESS CONTROL
# =====================================================================

def admin_required(view_func):
    """
    Decorator for Django admin views that require superuser access
    
    Usage:
        @admin_required
        def custom_admin_view(request):
            # Only superusers can access this view
            pass
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('scholarships:login')
        
        if not request.user.is_superuser:
            return HttpResponseForbidden("Access denied. Superuser privileges required.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class AdminRequiredMixin(LoginRequiredMixin):
    """
    Mixin for class-based views that require admin access
    
    Usage:
        class AdminOnlyView(AdminRequiredMixin, TemplateView):
            template_name = 'admin_only.html'
    """
    
    login_url = reverse_lazy('scholarships:login')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.is_superuser:
            return HttpResponseForbidden("Access denied. Superuser privileges required.")
        
        return super().dispatch(request, *args, **kwargs)


# =====================================================================
# CONTEXT PROCESSORS
# =====================================================================

def user_roles_context(request):
    """
    Context processor to add user role information to all templates
    
    Usage in templates:
        {% if user_roles.is_student %}
            <!-- Student-specific content -->
        {% endif %}
    """
    if request.user.is_authenticated:
        return {
            'user_roles': {
                'is_student': is_student(request.user),
                'is_verified_student': is_verified_student(request.user),
                'is_provider': is_provider(request.user),
                'is_active_provider': is_active_provider(request.user),
                'is_staff': is_staff_or_admin(request.user),
                'is_admin': request.user.is_superuser,
            }
        }
    return {
        'user_roles': {
            'is_student': False,
            'is_verified_student': False,
            'is_provider': False,
            'is_active_provider': False,
            'is_staff': False,
            'is_admin': False,
        }
    }
