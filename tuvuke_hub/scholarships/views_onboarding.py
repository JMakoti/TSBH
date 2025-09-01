"""
Multi-step onboarding views for student registration.
Handles the step-by-step registration process with form validation and data persistence.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import json

from .models import Student, County
from .forms_onboarding import (
    OnboardingStep1Form, OnboardingStep2Form, OnboardingStep3Form,
    OnboardingStep4Form, OnboardingStep5Form, OnboardingProgressForm
)


@method_decorator(csrf_protect, name='dispatch')
class StudentOnboardingView(View):
    """
    Multi-step student onboarding view.
    
    Handles 5 steps of registration:
    1. Personal Information
    2. Contact Information  
    3. Education Information
    4. Family & Financial Information
    5. Account Setup & Completion
    """
    
    template_name = 'scholarships/onboarding.html'
    session_key = 'student_onboarding_data'
    
    # Define form classes for each step
    form_classes = {
        1: OnboardingStep1Form,
        2: OnboardingStep2Form,
        3: OnboardingStep3Form,
        4: OnboardingStep4Form,
        5: OnboardingStep5Form,
    }
    
    # Step configuration
    step_config = {
        1: {
            'title': 'Personal Information',
            'description': 'Tell us about yourself',
            'icon': 'fas fa-user',
            'progress': 20
        },
        2: {
            'title': 'Contact Information',
            'description': 'How can we reach you?',
            'icon': 'fas fa-phone',
            'progress': 40
        },
        3: {
            'title': 'Education Details',
            'description': 'Your academic background',
            'icon': 'fas fa-graduation-cap',
            'progress': 60
        },
        4: {
            'title': 'Family & Financial',
            'description': 'Family and financial information',
            'icon': 'fas fa-home',
            'progress': 80
        },
        5: {
            'title': 'Account Setup',
            'description': 'Create your account',
            'icon': 'fas fa-check-circle',
            'progress': 100
        }
    }
    
    def get(self, request):
        """Handle GET request - display current step"""
        current_step = self.get_current_step(request)
        
        # Redirect to dashboard if user is already authenticated
        if request.user.is_authenticated:
            messages.info(request, 'You are already registered and logged in.')
            return redirect('scholarships:student_dashboard')
        
        # Get form for current step
        form_class = self.form_classes[current_step]
        
        # Pre-populate form with session data
        initial_data = self.get_session_data(request)
        form = form_class(initial=initial_data)
        
        # Get progress form for hidden fields
        progress_form = OnboardingProgressForm(initial={
            'current_step': current_step,
            **initial_data
        })
        
        context = self.get_context_data(
            form=form,
            progress_form=progress_form,
            current_step=current_step
        )
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Handle POST request - process form submission"""
        current_step = int(request.POST.get('current_step', 1))
        
        # Get form class for current step
        form_class = self.form_classes[current_step]
        form = form_class(request.POST, request.FILES)
        
        # Get progress form
        progress_form = OnboardingProgressForm(request.POST)
        
        if form.is_valid():
            # Save form data to session
            form_data = form.cleaned_data
            self.save_step_data(request, current_step, form_data)
            
            # Check if this is the final step
            if current_step == 5:
                # Create user and student profile
                return self.complete_registration(request)
            else:
                # Move to next step
                next_step = current_step + 1
                self.set_current_step(request, next_step)
                
                messages.success(
                    request,
                    f'Step {current_step} completed successfully!'
                )
                
                return redirect('scholarships:student_onboarding')
        else:
            # Form has errors
            messages.error(
                request,
                'Please correct the errors below and try again.'
            )
        
        # If form is invalid, redisplay with errors
        context = self.get_context_data(
            form=form,
            progress_form=progress_form,
            current_step=current_step
        )
        
        return render(request, self.template_name, context)
    
    def get_current_step(self, request):
        """Get current step from session or default to 1"""
        return request.session.get(f'{self.session_key}_step', 1)
    
    def set_current_step(self, request, step):
        """Set current step in session"""
        request.session[f'{self.session_key}_step'] = step
    
    def get_session_data(self, request):
        """Get all collected data from session"""
        return request.session.get(self.session_key, {})
    
    def save_step_data(self, request, step, data):
        """Save step data to session"""
        session_data = self.get_session_data(request)
        session_data.update(data)
        
        # Handle special cases for foreign keys
        if 'county' in data and data['county']:
            session_data['county_id'] = data['county'].id
        
        request.session[self.session_key] = session_data
        request.session.modified = True
    
    def complete_registration(self, request):
        """Complete the registration process by creating User and Student"""
        try:
            # Get all collected data
            session_data = self.get_session_data(request)
            
            # Create User account
            user = User.objects.create(
                username=session_data['username'],
                email=session_data['email'],
                first_name=session_data['first_name'],
                last_name=session_data['last_name'],
                password=make_password(session_data['password1'])
            )
            
            # Get county object
            county = None
            if session_data.get('county_id'):
                try:
                    county = County.objects.get(id=session_data['county_id'])
                except County.DoesNotExist:
                    pass
            
            # Create Student profile
            student = Student.objects.create(
                user=user,
                first_name=session_data['first_name'],
                last_name=session_data['last_name'],
                other_names=session_data.get('other_names', ''),
                date_of_birth=session_data['date_of_birth'],
                gender=session_data['gender'],
                national_id=session_data['national_id'],
                phone_number=session_data['phone_number'],
                alternative_phone=session_data.get('alternative_phone', ''),
                email=session_data['email'],
                county=county,
                sub_county=session_data['sub_county'],
                ward=session_data['ward'],
                location=session_data.get('location', ''),
                current_education_level=session_data['current_education_level'],
                current_institution=session_data['current_institution'],
                course_of_study=session_data['course_of_study'],
                year_of_study=session_data['year_of_study'],
                expected_graduation_year=session_data['expected_graduation_year'],
                previous_gpa=session_data.get('previous_gpa'),
                previous_percentage=session_data.get('previous_percentage'),
                family_income_annual=session_data['family_income_annual'],
                number_of_dependents=session_data['number_of_dependents'],
                is_orphan=session_data.get('is_orphan', False),
                is_single_parent_child=session_data.get('is_single_parent_child', False),
                is_child_headed_household=session_data.get('is_child_headed_household', False),
                disability_status=session_data.get('disability_status', 'none'),
                special_needs_description=session_data.get('special_needs_description', ''),
                profile_photo=session_data.get('profile_photo'),
                is_verified=False,  # Will be verified later
                created_at=timezone.now()
            )
            
            # Log in the user with specified backend
            login(request, user, backend='scholarships.backends.MultiFieldAuthBackend')
            
            # Clear session data
            self.clear_session_data(request)
            
            # Success message
            messages.success(
                request,
                f'Welcome {user.first_name}! Your account has been created successfully. '
                f'You can now apply for scholarships.'
            )
            
            # Redirect to dashboard
            return redirect('scholarships:student_dashboard')
            
        except Exception as e:
            # Handle any errors during user creation
            messages.error(
                request,
                f'An error occurred while creating your account: {str(e)}. '
                f'Please try again or contact support.'
            )
            
            # Return to current step
            return redirect('scholarships:student_onboarding')
    
    def clear_session_data(self, request):
        """Clear onboarding session data"""
        if self.session_key in request.session:
            del request.session[self.session_key]
        if f'{self.session_key}_step' in request.session:
            del request.session[f'{self.session_key}_step']
        request.session.modified = True
    
    def get_context_data(self, form, progress_form, current_step):
        """Prepare context data for template"""
        return {
            'form': form,
            'progress_form': progress_form,
            'current_step': current_step,
            'total_steps': len(self.form_classes),
            'step_config': self.step_config[current_step],
            'all_steps': self.step_config,
            'is_final_step': current_step == len(self.form_classes),
            'progress_percentage': self.step_config[current_step]['progress'],
            'page_title': f'Registration - {self.step_config[current_step]["title"]}',
            # For navigation
            'can_go_back': current_step > 1,
            'next_step': current_step + 1 if current_step < len(self.form_classes) else None,
            'prev_step': current_step - 1 if current_step > 1 else None,
        }
