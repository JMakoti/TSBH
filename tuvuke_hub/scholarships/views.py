"""
Django views for student registration and profile management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, ListView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from decimal import Decimal
import json

from .forms import (
    StudentRegistrationForm, 
    StudentProfileUpdateForm, 
    QuickRegistrationForm, 
    StudentSearchForm
)
from .models import Student, County, Scholarship, Provider


@method_decorator(csrf_protect, name='dispatch')
class StudentRegistrationView(View):
    """
    Class-Based View for handling student registration.
    
    Handles both GET and POST requests:
    - GET: Display the registration form
    - POST: Process form submission, create user with hashed password, and log in
    """
    
    template_name = 'scholarships/register.html'
    form_class = StudentRegistrationForm
    
    def get(self, request):
        """Handle GET request - display registration form"""
        form = self.form_class()
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Handle POST request - process form submission"""
        form = self.form_class(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Save the form - this creates both User and Student profile
                # The form already handles password hashing in its save() method
                user = form.save()
                
                # Log in the user automatically
                login(request, user)
                
                # Add success message
                messages.success(
                    request, 
                    f'Welcome {user.first_name}! Your account has been created successfully. '
                    f'You can now apply for scholarships.'
                )
                
                # Redirect to dashboard
                return redirect('scholarships:student_dashboard')
                
            except Exception as e:
                # Handle any unexpected errors during save
                messages.error(
                    request, 
                    f'An error occurred while creating your account: {str(e)}. '
                    f'Please try again or contact support.'
                )
        else:
            # Form has validation errors
            messages.error(
                request, 
                'Please correct the errors below and try again.'
            )
        
        # If form is invalid or error occurred, redisplay form with errors
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)
    
    def get_context_data(self, form=None, **kwargs):
        """Prepare context data for template"""
        context = {
            'form': form or self.form_class(),
            'page_title': 'Student Registration',
            'submit_text': 'Create Account',
            'counties': County.objects.all().order_by('name'),
        }
        context.update(kwargs)
        return context


def register_student(request):
    """
    Handle student registration with comprehensive form validation.
    
    Features:
    - Creates both User and Student profile
    - Handles form validation errors
    - Automatic login after registration
    - Success/error messaging
    """
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Save the form - this creates both User and Student profile
                user = form.save()
                
                # Log in the user automatically
                login(request, user)
                
                # Add success message
                messages.success(
                    request, 
                    f'Welcome {user.first_name}! Your account has been created successfully. '
                    f'You can now apply for scholarships.'
                )
                
                # Redirect to dashboard or profile page
                return redirect('student_dashboard')
                
            except Exception as e:
                # Handle any unexpected errors during save
                messages.error(
                    request, 
                    f'An error occurred while creating your account: {str(e)}. '
                    f'Please try again or contact support.'
                )
        else:
            # Form has validation errors
            messages.error(
                request, 
                'Please correct the errors below and try again.'
            )
    else:
        form = StudentRegistrationForm()
    
    # Prepare context for template
    context = {
        'form': form,
        'page_title': 'Student Registration',
        'submit_text': 'Create Account',
        'counties': County.objects.all().order_by('name'),
    }
    
    return render(request, 'scholarships/register.html', context)


def quick_register_student(request):
    """
    Handle quick student registration with minimal fields.
    
    Features:
    - Simplified registration process
    - Essential fields only
    - Can complete profile later
    """
    if request.method == 'POST':
        form = QuickRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                # Create user and student profile
                user = form.save()
                
                # Log in the user
                login(request, user)
                
                messages.success(
                    request, 
                    f'Welcome {user.first_name}! Quick registration completed. '
                    f'Please complete your profile to access all features.'
                )
                
                # Redirect to profile completion
                return redirect('complete_profile')
                
            except Exception as e:
                messages.error(
                    request, 
                    f'Registration failed: {str(e)}. Please try again.'
                )
        else:
            messages.error(
                request, 
                'Please correct the errors below.'
            )
    else:
        form = QuickRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Quick Registration',
        'submit_text': 'Quick Register',
        'counties': County.objects.all().order_by('name'),
    }
    
    return render(request, 'scholarships/quick_register.html', context)


@login_required
def student_profile_view(request):
    """
    Display student profile information.
    
    Features:
    - Shows complete profile
    - Links to edit profile
    - Profile completion status
    """
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(
            request, 
            'Student profile not found. Please contact support.'
        )
        return redirect('home')
    
    # Calculate profile completion percentage
    profile_completion = calculate_profile_completion(student)
    
    context = {
        'student': student,
        'profile_completion': profile_completion,
        'page_title': f'{student.get_full_name()} - Profile',
    }
    
    return render(request, 'scholarships/profile.html', context)


@login_required
def update_student_profile(request):
    """
    Handle student profile updates.
    
    Features:
    - Updates existing profile
    - Excludes sensitive fields
    - Validation for unique fields
    """
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(
            request, 
            'Student profile not found. Please contact support.'
        )
        return redirect('home')
    
    if request.method == 'POST':
        form = StudentProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=student
        )
        
        if form.is_valid():
            try:
                # Save the updated profile
                updated_student = form.save()
                
                messages.success(
                    request, 
                    'Your profile has been updated successfully!'
                )
                
                return redirect('student_profile')
                
            except Exception as e:
                messages.error(
                    request, 
                    f'Profile update failed: {str(e)}. Please try again.'
                )
        else:
            messages.error(
                request, 
                'Please correct the errors below.'
            )
    else:
        form = StudentProfileUpdateForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
        'page_title': 'Update Profile',
        'submit_text': 'Update Profile',
        'counties': County.objects.all().order_by('name'),
    }
    
    return render(request, 'scholarships/update_profile.html', context)


@login_required
def complete_profile(request):
    """
    Complete profile after quick registration.
    
    Features:
    - Shows remaining fields to complete
    - Uses update form with missing fields highlighted
    """
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(
            request, 
            'Student profile not found. Please contact support.'
        )
        return redirect('home')
    
    # Check if profile is already complete
    completion_percentage = calculate_profile_completion(student)
    if completion_percentage >= 80:
        messages.info(
            request, 
            'Your profile is already mostly complete!'
        )
        return redirect('student_profile')
    
    if request.method == 'POST':
        form = StudentProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=student
        )
        
        if form.is_valid():
            try:
                updated_student = form.save()
                
                # Check completion after update
                new_completion = calculate_profile_completion(updated_student)
                
                if new_completion >= 80:
                    messages.success(
                        request, 
                        'Congratulations! Your profile is now complete. '
                        'You can apply for scholarships.'
                    )
                    return redirect('student_dashboard')
                else:
                    messages.success(
                        request, 
                        f'Profile updated! Completion: {new_completion}%. '
                        f'Complete more fields to access all features.'
                    )
                
            except Exception as e:
                messages.error(
                    request, 
                    f'Profile update failed: {str(e)}'
                )
        else:
            messages.error(
                request, 
                'Please correct the errors below.'
            )
    else:
        form = StudentProfileUpdateForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
        'completion_percentage': completion_percentage,
        'page_title': 'Complete Your Profile',
        'submit_text': 'Save Progress',
        'counties': County.objects.all().order_by('name'),
    }
    
    return render(request, 'scholarships/complete_profile.html', context)


def search_students(request):
    """
    Search students with multiple criteria.
    
    Features:
    - Text search across multiple fields
    - Filter by county, education level, gender
    - Age range filtering
    - Verification status filtering
    - Pagination for results
    """
    form = StudentSearchForm(request.GET or None)
    students = Student.objects.select_related('county', 'user').all()
    
    # Apply search filters
    if form.is_valid():
        cleaned_data = form.cleaned_data
        
        # Text search across multiple fields
        if cleaned_data.get('search_query'):
            query = cleaned_data['search_query']
            students = students.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(other_names__icontains=query) |
                Q(national_id__icontains=query) |
                Q(user__email__icontains=query) |
                Q(current_institution__icontains=query) |
                Q(course_of_study__icontains=query)
            )
        
        # County filter
        if cleaned_data.get('county'):
            students = students.filter(county=cleaned_data['county'])
        
        # Education level filter
        if cleaned_data.get('education_level'):
            students = students.filter(
                current_education_level=cleaned_data['education_level']
            )
        
        # Gender filter
        if cleaned_data.get('gender'):
            students = students.filter(gender=cleaned_data['gender'])
        
        # Age range filters
        if cleaned_data.get('min_age'):
            from datetime import date, timedelta
            max_birth_date = date.today() - timedelta(days=cleaned_data['min_age'] * 365)
            students = students.filter(date_of_birth__lte=max_birth_date)
        
        if cleaned_data.get('max_age'):
            from datetime import date, timedelta
            min_birth_date = date.today() - timedelta(days=cleaned_data['max_age'] * 365)
            students = students.filter(date_of_birth__gte=min_birth_date)
        
        # Verification status filter
        if cleaned_data.get('is_verified') is not None:
            students = students.filter(is_verified=cleaned_data['is_verified'])
    
    # Order results
    students = students.order_by('-created_at', 'last_name', 'first_name')
    
    # Pagination
    paginator = Paginator(students, 20)  # 20 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'students': page_obj,
        'total_students': paginator.count,
        'page_title': 'Search Students',
    }
    
    return render(request, 'scholarships/search_students.html', context)


@login_required
def student_dashboard(request):
    """
    Comprehensive student dashboard with profile summary, applications, and recommendations.
    
    Features:
    - Profile information display
    - Application tracking with status badges
    - Personalized scholarship recommendations using match scores
    - Quick actions and statistics
    """
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        student = None
    
    # Initialize context variables
    applications = []
    applications_count = 0
    recommended_scholarships = []
    recommended_count = 0
    
    if student:
        # Get user's applications with related scholarship data
        from .models import Application
        applications = Application.objects.filter(
            student=student
        ).select_related(
            'scholarship', 
            'scholarship__provider'
        ).order_by('-application_date')[:10]
        
        applications_count = applications.count()
        
        # Get personalized scholarship recommendations
        active_scholarships = Scholarship.objects.filter(
            is_active=True,
            application_deadline__gte=timezone.now().date()
        ).select_related('provider').prefetch_related('target_counties')
        
        # Calculate match scores and filter recommendations
        recommendations_with_scores = []
        for scholarship in active_scholarships:
            try:
                match_score = student.calculate_match_score(scholarship)
                if match_score >= 40:  # Only show scholarships with decent match
                    recommendations_with_scores.append({
                        'scholarship': scholarship,
                        'match_score': match_score
                    })
            except Exception as e:
                # Skip scholarships that cause calculation errors
                continue
        
        # Sort by match score (highest first) and limit to top 8
        recommended_scholarships = sorted(
            recommendations_with_scores, 
            key=lambda x: x['match_score'], 
            reverse=True
        )[:8]
        
        recommended_count = len(recommended_scholarships)
    
    context = {
        'student': student,
        'applications': applications,
        'applications_count': applications_count,
        'recommended_scholarships': recommended_scholarships,
        'recommended_count': recommended_count,
        'page_title': f'Dashboard - {request.user.get_full_name() or request.user.username}',
    }
    
    return render(request, 'scholarships/dashboard.html', context)


def calculate_profile_completion(student):
    """
    Calculate profile completion percentage based on filled fields.
    
    Args:
        student: Student instance
        
    Returns:
        int: Completion percentage (0-100)
    """
    total_fields = 25  # Total important fields to track
    completed_fields = 0
    
    # Check essential fields
    if student.first_name:
        completed_fields += 1
    if student.last_name:
        completed_fields += 1
    if student.date_of_birth:
        completed_fields += 1
    if student.gender:
        completed_fields += 1
    if student.national_id:
        completed_fields += 1
    if student.phone_number:
        completed_fields += 1
    if student.county:
        completed_fields += 1
    if student.sub_county:
        completed_fields += 1
    if student.ward:
        completed_fields += 1
    if student.current_education_level:
        completed_fields += 1
    if student.current_institution:
        completed_fields += 1
    if student.course_of_study:
        completed_fields += 1
    if student.year_of_study:
        completed_fields += 1
    if student.expected_graduation_year:
        completed_fields += 1
    if student.family_income_annual:
        completed_fields += 1
    if student.number_of_dependents is not None:
        completed_fields += 1
    
    # Optional but important fields
    if student.other_names:
        completed_fields += 1
    if student.alternative_phone:
        completed_fields += 1
    if student.location:
        completed_fields += 1
    if student.postal_address:
        completed_fields += 1
    if student.previous_gpa or student.previous_percentage:
        completed_fields += 1
    if student.profile_photo:
        completed_fields += 1
    
    # Special circumstances (count as 3 fields)
    if (student.disability_status or student.is_orphan or 
        student.is_single_parent_child or student.is_child_headed_household):
        completed_fields += 3
    
    return int((completed_fields / total_fields) * 100)


# AJAX Views for dynamic form behavior

@require_http_methods(["GET"])
def get_sub_counties(request):
    """
    AJAX endpoint to get sub-counties for a selected county.
    
    Returns:
        JsonResponse: List of sub-counties for the county
    """
    county_id = request.GET.get('county_id')
    
    if not county_id:
        return JsonResponse({'error': 'County ID is required'}, status=400)
    
    try:
        county = get_object_or_404(County, id=county_id)
        
        # This would require a SubCounty model or data
        # For now, return sample data
        sub_counties = [
            {'id': 1, 'name': 'Central'},
            {'id': 2, 'name': 'East'},
            {'id': 3, 'name': 'West'},
            {'id': 4, 'name': 'North'},
            {'id': 5, 'name': 'South'},
        ]
        
        return JsonResponse({
            'sub_counties': sub_counties,
            'county_name': county.name
        })
        
    except County.DoesNotExist:
        return JsonResponse({'error': 'County not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def validate_national_id(request):
    """
    AJAX endpoint to validate National ID uniqueness.
    
    Returns:
        JsonResponse: Validation result
    """
    try:
        data = json.loads(request.body)
        national_id = data.get('national_id', '').strip()
        student_id = data.get('student_id')  # For updates
        
        if not national_id:
            return JsonResponse({
                'valid': False, 
                'message': 'National ID is required'
            })
        
        # Check format (8 digits)
        if not national_id.isdigit() or len(national_id) != 8:
            return JsonResponse({
                'valid': False,
                'message': 'National ID must be exactly 8 digits'
            })
        
        # Check uniqueness
        query = Student.objects.filter(national_id=national_id)
        if student_id:
            query = query.exclude(id=student_id)
        
        if query.exists():
            return JsonResponse({
                'valid': False,
                'message': 'A student with this National ID already exists'
            })
        
        return JsonResponse({
            'valid': True,
            'message': 'National ID is available'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def validate_phone_number(request):
    """
    AJAX endpoint to validate phone number format and uniqueness.
    
    Returns:
        JsonResponse: Validation result with normalized phone number
    """
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number', '').strip()
        student_id = data.get('student_id')  # For updates
        
        if not phone_number:
            return JsonResponse({
                'valid': False,
                'message': 'Phone number is required'
            })
        
        # Normalize phone number (reuse logic from form)
        normalized_phone = normalize_phone_number(phone_number)
        
        if not normalized_phone:
            return JsonResponse({
                'valid': False,
                'message': 'Phone number must be in format +254XXXXXXXXX'
            })
        
        # Check uniqueness
        query = Student.objects.filter(phone_number=normalized_phone)
        if student_id:
            query = query.exclude(id=student_id)
        
        if query.exists():
            return JsonResponse({
                'valid': False,
                'message': 'A student with this phone number already exists'
            })
        
        return JsonResponse({
            'valid': True,
            'message': 'Phone number is available',
            'normalized_phone': normalized_phone
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def normalize_phone_number(phone_number):
    """
    Normalize phone number to international format (+254XXXXXXXXX).
    
    Args:
        phone_number: Raw phone number string
        
    Returns:
        str: Normalized phone number or None if invalid
    """
    import re
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone_number)
    
    # Handle different formats
    if digits_only.startswith('254') and len(digits_only) == 12:
        # Already in 254 format
        normalized = '+' + digits_only
    elif digits_only.startswith('0') and len(digits_only) == 10:
        # Local format (0712345678)
        normalized = '+254' + digits_only[1:]
    elif len(digits_only) == 9:
        # Missing leading zero (712345678)
        normalized = '+254' + digits_only
    else:
        # Invalid format
        return None
    
    # Validate the final format
    phone_pattern = r'^\+254[17][0-9]{8}$'
    if re.match(phone_pattern, normalized):
        return normalized
    
    return None


class ScholarshipListView(ListView):
    """
    Class-Based View for displaying and filtering scholarships.
    
    Features:
    - Displays active scholarships
    - Supports multiple filtering options via GET parameters
    - Pagination support
    - Search functionality
    - Ordering options
    - Match score calculation for logged-in students
    """
    
    model = Scholarship
    template_name = 'scholarships/scholarship_list.html'
    context_object_name = 'scholarships'
    paginate_by = 12  # Show 12 scholarships per page
    
    def get_queryset(self):
        """
        Filter scholarships based on GET parameters.
        
        Supported filters:
        - county: Filter by target county
        - education_level: Filter by target education level
        - scholarship_type: Filter by scholarship type
        - provider: Filter by provider
        - search: Text search in title and description
        - min_amount: Minimum scholarship amount
        - max_amount: Maximum scholarship amount
        - status: Scholarship status
        - for_orphans: Scholarships for orphans only
        - for_disabled: Scholarships for disabled students only
        - gender: Gender-specific scholarships
        - sort: Sorting option
        """
        # Start with active scholarships by default
        queryset = Scholarship.objects.select_related('provider').prefetch_related('target_counties')
        
        # Filter by status (default to active)
        status = self.request.GET.get('status', 'active')
        if status and status != 'all':
            queryset = queryset.filter(status=status)
        
        # Only show scholarships with future or current deadlines (unless admin)
        if not self.request.user.is_staff:
            queryset = queryset.filter(application_deadline__gte=timezone.now())
        
        # County filter
        county_id = self.request.GET.get('county')
        if county_id:
            try:
                county_id = int(county_id)
                queryset = queryset.filter(
                    Q(target_counties__id=county_id) | 
                    Q(target_counties__isnull=True)  # Include scholarships with no county restrictions
                )
            except (ValueError, TypeError):
                pass
        
        # Education level filter
        education_level = self.request.GET.get('education_level')
        if education_level:
            queryset = queryset.filter(
                Q(target_education_levels__contains=[education_level]) |
                Q(target_education_levels__contains=['all_levels'])
            )
        
        # Scholarship type filter
        scholarship_type = self.request.GET.get('scholarship_type')
        if scholarship_type:
            queryset = queryset.filter(scholarship_type=scholarship_type)
        
        # Provider filter
        provider_id = self.request.GET.get('provider')
        if provider_id:
            try:
                provider_id = int(provider_id)
                queryset = queryset.filter(provider_id=provider_id)
            except (ValueError, TypeError):
                pass
        
        # Text search in title and description
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(provider__name__icontains=search_query)
            )
        
        # Amount range filters
        min_amount = self.request.GET.get('min_amount')
        if min_amount:
            try:
                min_amount = Decimal(min_amount)
                queryset = queryset.filter(amount_per_beneficiary__gte=min_amount)
            except (ValueError, TypeError, Exception):
                pass
        
        max_amount = self.request.GET.get('max_amount')
        if max_amount:
            try:
                max_amount = Decimal(max_amount)
                queryset = queryset.filter(amount_per_beneficiary__lte=max_amount)
            except (ValueError, TypeError, Exception):
                pass
        
        # Special requirements filters
        if self.request.GET.get('for_orphans') == 'true':
            queryset = queryset.filter(for_orphans_only=True)
        
        if self.request.GET.get('for_disabled') == 'true':
            queryset = queryset.filter(for_disabled_only=True)
        
        # Gender filter
        gender = self.request.GET.get('gender')
        if gender == 'male':
            queryset = queryset.filter(for_males_only=True)
        elif gender == 'female':
            queryset = queryset.filter(for_females_only=True)
        elif gender == 'any':
            queryset = queryset.filter(for_males_only=False, for_females_only=False)
        
        # Field of study filter
        field_of_study = self.request.GET.get('field_of_study')
        if field_of_study:
            queryset = queryset.filter(target_fields_of_study__contains=[field_of_study])
        
        # Renewable scholarships only
        if self.request.GET.get('renewable') == 'true':
            queryset = queryset.filter(renewable=True)
        
        # Application method filter
        application_method = self.request.GET.get('application_method')
        if application_method:
            queryset = queryset.filter(application_method=application_method)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sort_options = [
            'title', '-title',
            'amount_per_beneficiary', '-amount_per_beneficiary',
            'application_deadline', '-application_deadline',
            'created_at', '-created_at',
            'provider__name', '-provider__name',
            'number_of_awards', '-number_of_awards'
        ]
        
        if sort_by in valid_sort_options:
            queryset = queryset.order_by(sort_by)
        else:
            # Default sorting: featured first, then by deadline, then by creation date
            queryset = queryset.order_by('-is_featured', 'application_deadline', '-created_at')
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        """Add additional context for the template."""
        context = super().get_context_data(**kwargs)
        
        # Add filter options for the template
        context.update({
            'counties': County.objects.all().order_by('name'),
            'providers': Provider.objects.filter(is_active=True).order_by('name'),
            'scholarship_types': Scholarship.SCHOLARSHIP_TYPE_CHOICES,
            'education_levels': Scholarship.EDUCATION_LEVEL_CHOICES,
            'status_choices': Scholarship.SCHOLARSHIP_STATUS_CHOICES,
            'coverage_types': Scholarship.COVERAGE_TYPE_CHOICES,
            
            # Current filter values (to maintain state in form)
            'current_filters': {
                'county': self.request.GET.get('county', ''),
                'education_level': self.request.GET.get('education_level', ''),
                'scholarship_type': self.request.GET.get('scholarship_type', ''),
                'provider': self.request.GET.get('provider', ''),
                'search': self.request.GET.get('search', ''),
                'min_amount': self.request.GET.get('min_amount', ''),
                'max_amount': self.request.GET.get('max_amount', ''),
                'status': self.request.GET.get('status', 'active'),
                'for_orphans': self.request.GET.get('for_orphans', ''),
                'for_disabled': self.request.GET.get('for_disabled', ''),
                'gender': self.request.GET.get('gender', ''),
                'field_of_study': self.request.GET.get('field_of_study', ''),
                'renewable': self.request.GET.get('renewable', ''),
                'application_method': self.request.GET.get('application_method', ''),
                'sort': self.request.GET.get('sort', '-created_at'),
            },
            
            # Statistics
            'total_scholarships': self.get_queryset().count(),
            'active_scholarships': Scholarship.objects.filter(
                status='active',
                application_deadline__gte=timezone.now()
            ).count(),
            
            # Page title
            'page_title': 'Available Scholarships',
            
            # Sorting options for template
            'sort_options': [
                ('title', 'Title (A-Z)'),
                ('-title', 'Title (Z-A)'),
                ('-amount_per_beneficiary', 'Amount (High to Low)'),
                ('amount_per_beneficiary', 'Amount (Low to High)'),
                ('application_deadline', 'Deadline (Earliest First)'),
                ('-application_deadline', 'Deadline (Latest First)'),
                ('-created_at', 'Newest First'),
                ('created_at', 'Oldest First'),
                ('provider__name', 'Provider (A-Z)'),
                ('-provider__name', 'Provider (Z-A)'),
            ],
            
            # Featured scholarships for sidebar
            'featured_scholarships': Scholarship.objects.filter(
                is_featured=True,
                status='active',
                application_deadline__gte=timezone.now()
            )[:5],
        })
        
        # Add user-specific context if logged in
        if self.request.user.is_authenticated:
            try:
                student = self.request.user.student_profile
                # Calculate match scores for scholarships if student exists
                scholarships_with_scores = []
                for scholarship in context['scholarships']:
                    match_score = scholarship.calculate_match_score(student)
                    scholarships_with_scores.append({
                        'scholarship': scholarship,
                        'match_score': match_score
                    })
                context['scholarships_with_scores'] = scholarships_with_scores
                context['has_student_profile'] = True
            except:
                context['has_student_profile'] = False
        else:
            context['has_student_profile'] = False
        
        return context
