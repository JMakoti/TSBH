"""
Authentication views for TUVUKE Hub
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods

from .auth_forms import PhoneNumberLoginForm, StudentPhoneRegistrationForm, PasswordResetByPhoneForm
from .access_control import (
    is_student, is_provider, is_staff_or_admin,
    student_required, provider_required, staff_required
)
from .models import Student


class CustomLoginView(FormView):
    """
    Custom login view that supports phone number, email, and username authentication
    """
    template_name = 'auth/login.html'
    form_class = PhoneNumberLoginForm
    success_url = '/'
    
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Authenticate and login the user
        """
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        remember_me = form.cleaned_data.get('remember_me', False)
        
        user = authenticate(
            self.request,
            username=username,
            password=password
        )
        
        if user is not None:
            # Specify the backend when logging in to avoid multiple backend error
            login(self.request, user, backend='scholarships.backends.MultiFieldAuthBackend')
            
            # Set session expiry based on remember_me
            if remember_me:
                self.request.session.set_expiry(1209600)  # 2 weeks
            else:
                self.request.session.set_expiry(0)  # Browser session
            
            # Add success message
            messages.success(self.request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect based on user role
            return redirect(self.get_role_based_redirect_url(user))
        else:
            messages.error(self.request, 'Invalid login credentials.')
            return self.form_invalid(form)
    
    def get_role_based_redirect_url(self, user):
        """
        Get redirect URL based on user role
        """
        # Check if there's a 'next' parameter
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        
        # Role-based redirection
        if is_student(user):
            return reverse_lazy('scholarships:student_dashboard')
        elif is_provider(user):
            return reverse_lazy('scholarships:provider_dashboard')
        elif is_staff_or_admin(user):
            return reverse_lazy('admin:index')
        else:
            return reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login to TUVUKE Hub'
        context['subtitle'] = 'Access your scholarship management account'
        return context


@login_required
@require_http_methods(["GET", "POST"])
def custom_logout_view(request):
    """
    Custom logout view with role-specific messaging
    Handles both GET and POST requests
    """
    if request.user.is_authenticated:
        user_name = request.user.get_full_name() or request.user.username
        user_role = 'student' if is_student(request.user) else 'provider' if is_provider(request.user) else 'user'
        
        logout(request)
        
        messages.success(request, f'You have been successfully logged out. Thank you for using TUVUKE Hub!')
    
    return redirect('scholarships:search_homepage')


class StudentRegistrationView(FormView):
    """
    Student registration view using phone number as primary identifier
    """
    template_name = 'auth/student_register.html'
    form_class = StudentPhoneRegistrationForm
    success_url = reverse_lazy('auth:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You are already logged in.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Create user account and redirect to complete profile
        """
        try:
            user = form.save()
            
            # Create initial Student profile
            Student.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number'],
                email=form.cleaned_data['email'],
                # Other fields will be filled in the profile completion step
                first_name='',  # Will be updated in profile
                last_name='',   # Will be updated in profile
                date_of_birth='2000-01-01',  # Placeholder, will be updated
                gender='M',     # Placeholder, will be updated
                national_id='00000000',  # Placeholder, will be updated
                county_id=1,    # Placeholder, will be updated
                sub_county='',  # Will be updated
                ward='',        # Will be updated
                current_education_level='undergraduate',  # Placeholder
                current_institution='',  # Will be updated
                course_of_study='',  # Will be updated
                year_of_study=1,  # Placeholder
                expected_graduation_year=2025,  # Placeholder
                family_income_annual=0,  # Will be updated
            )
            
            messages.success(
                self.request,
                'Account created successfully! Please log in and complete your profile.'
            )
            
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, f'Error creating account: {str(e)}')
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Student Registration'
        context['subtitle'] = 'Create your student account to access scholarships'
        return context


class PasswordResetView(FormView):
    """
    Password reset view using phone number
    """
    template_name = 'auth/password_reset.html'
    form_class = PasswordResetByPhoneForm
    success_url = reverse_lazy('auth:password_reset_done')
    
    def form_valid(self, form):
        """
        Send password reset instructions
        """
        user = form.get_user()
        phone_number = form.cleaned_data['phone_number']
        
        # Here you would typically send an SMS with reset code
        # For now, we'll just show a success message
        messages.success(
            self.request,
            f'Password reset instructions have been sent to {phone_number}. '
            'Please check your SMS messages.'
        )
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reset Password'
        context['subtitle'] = 'Enter your phone number to reset your password'
        return context


class PasswordResetDoneView(TemplateView):
    """
    Password reset confirmation view
    """
    template_name = 'auth/password_reset_done.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Password Reset Sent'
        context['subtitle'] = 'Check your phone for reset instructions'
        return context


# Role-specific dashboard views

@student_required
def student_dashboard(request):
    """
    Student dashboard view - only accessible by students
    """
    student = request.user.student_profile
    
    # Get student's applications
    applications = student.applications.all()[:5]  # Latest 5 applications
    
    # Get recommended scholarships (basic implementation)
    recommended_scholarships = []
    # You can implement more sophisticated recommendation logic here
    
    context = {
        'title': 'Student Dashboard',
        'student': student,
        'applications': applications,
        'recommended_scholarships': recommended_scholarships,
    }
    
    return render(request, 'students/dashboard.html', context)


@provider_required
def provider_dashboard(request):
    """
    Provider dashboard view - only accessible by providers
    """
    # Get provider information
    # This assumes provider accounts are linked via email or special group membership
    
    context = {
        'title': 'Provider Dashboard',
        'user': request.user,
    }
    
    return render(request, 'providers/dashboard.html', context)


@staff_required
def admin_dashboard(request):
    """
    Admin dashboard view - only accessible by staff
    """
    context = {
        'title': 'Admin Dashboard',
        'user': request.user,
    }
    
    return render(request, 'admin/dashboard.html', context)


# API endpoint for checking phone number availability
def check_phone_availability(request):
    """
    AJAX endpoint to check if phone number is available
    """
    if request.method == 'GET':
        phone_number = request.GET.get('phone_number', '').strip()
        
        if not phone_number:
            return JsonResponse({'available': False, 'message': 'Phone number is required'})
        
        # Normalize phone number
        from .backends import PhoneNumberAuthBackend
        backend = PhoneNumberAuthBackend()
        normalized_phone = backend._normalize_phone_number(phone_number)
        
        if not normalized_phone:
            return JsonResponse({
                'available': False,
                'message': 'Please enter a valid Kenyan phone number'
            })
        
        # Check availability
        available = not Student.objects.filter(phone_number=normalized_phone).exists()
        
        return JsonResponse({
            'available': available,
            'message': 'Phone number is available' if available else 'Phone number already registered',
            'normalized': normalized_phone
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# Profile completion views

class StudentProfileMixin(LoginRequiredMixin):
    """
    Mixin to ensure only students can access profile views
    """
    def dispatch(self, request, *args, **kwargs):
        if not is_student(request.user):
            messages.error(request, 'Access denied. Student account required.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(student_required, name='dispatch')
class StudentProfileView(TemplateView):
    """
    Student profile view for completing registration
    """
    template_name = 'students/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Complete Your Profile'
        context['student'] = self.request.user.student_profile
        return context
