"""
Multi-step onboarding forms for student registration.
Each step is a separate form that collects specific information.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import date, timedelta
import re

from .models import Student, County


class OnboardingStep1Form(forms.Form):
    """
    Step 1: Basic Personal Information
    """
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'autocomplete': 'given-name'
        }),
        help_text='Your first name as it appears on official documents'
    )
    
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'autocomplete': 'family-name'
        }),
        help_text='Your surname/family name'
    )
    
    other_names = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Other names (optional)'
        }),
        help_text='Any middle names or other names'
    )
    
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'max': (date.today() - timedelta(days=15*365)).isoformat(),  # Min 15 years old
            'min': (date.today() - timedelta(days=35*365)).isoformat(),  # Max 35 years old
        }),
        help_text='Your date of birth'
    )
    
    gender = forms.ChoiceField(
        choices=[
            ('', 'Select your gender'),
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    national_id = forms.CharField(
        max_length=8,
        validators=[
            RegexValidator(
                regex=r'^\d{8}$',
                message='National ID must be exactly 8 digits'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678',
            'pattern': '[0-9]{8}',
            'title': 'Enter 8-digit National ID number'
        }),
        help_text='Your 8-digit National ID number'
    )
    
    def clean_date_of_birth(self):
        """Validate date of birth"""
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if age < 15:
                raise forms.ValidationError('You must be at least 15 years old to register.')
            if age > 35:
                raise forms.ValidationError('You must be younger than 35 years old to register.')
        
        return dob
    
    def clean_national_id(self):
        """Validate National ID uniqueness"""
        national_id = self.cleaned_data.get('national_id')
        if national_id and Student.objects.filter(national_id=national_id).exists():
            raise forms.ValidationError('A student with this National ID already exists.')
        return national_id


class OnboardingStep2Form(forms.Form):
    """
    Step 2: Contact Information
    """
    phone_number = forms.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+254[17][0-9]{8}$|^0[17][0-9]{8}$|^[17][0-9]{8}$',
                message='Enter a valid Kenyan phone number'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254712345678 or 0712345678',
            'pattern': r'(\+254|0)?[17][0-9]{8}',
            'title': 'Enter a valid Kenyan mobile number'
        }),
        help_text='Your primary mobile number'
    )
    
    alternative_phone = forms.CharField(
        max_length=15,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+254[17][0-9]{8}$|^0[17][0-9]{8}$|^[17][0-9]{8}$',
                message='Enter a valid Kenyan phone number'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Alternative phone (optional)'
        }),
        help_text='Alternative contact number (optional)'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'autocomplete': 'email'
        }),
        help_text='Your email address for notifications'
    )
    
    county = forms.ModelChoiceField(
        queryset=County.objects.all().order_by('name'),
        empty_label='Select your county',
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='The county where you currently reside'
    )
    
    sub_county = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your sub-county'
        }),
        help_text='Your sub-county/constituency'
    )
    
    ward = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your ward'
        }),
        help_text='Your ward'
    )
    
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Village/Estate/Location (optional)'
        }),
        help_text='Your specific location/village (optional)'
    )
    
    def clean_phone_number(self):
        """Normalize and validate phone number"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            normalized = self.normalize_phone_number(phone)
            if not normalized:
                raise forms.ValidationError('Enter a valid Kenyan phone number')
            
            # Check uniqueness
            if Student.objects.filter(phone_number=normalized).exists():
                raise forms.ValidationError('A student with this phone number already exists.')
            
            return normalized
        return phone
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email
    
    def normalize_phone_number(self, phone_number):
        """Normalize phone number to +254XXXXXXXXX format"""
        digits_only = re.sub(r'\D', '', phone_number)
        
        if digits_only.startswith('254') and len(digits_only) == 12:
            return '+' + digits_only
        elif digits_only.startswith('0') and len(digits_only) == 10:
            return '+254' + digits_only[1:]
        elif len(digits_only) == 9:
            return '+254' + digits_only
        
        return None


class OnboardingStep3Form(forms.Form):
    """
    Step 3: Education Information
    """
    current_education_level = forms.ChoiceField(
        choices=[
            ('', 'Select your education level'),
            ('primary', 'Primary School'),
            ('secondary', 'Secondary School'),
            ('college', 'College/Diploma'),
            ('undergraduate', 'Undergraduate'),
            ('postgraduate', 'Postgraduate'),
            ('masters', 'Masters'),
            ('phd', 'PhD'),
            ('professional', 'Professional Course'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Your current level of education'
    )
    
    current_institution = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name of your current school/college/university'
        }),
        help_text='Full name of your educational institution'
    )
    
    course_of_study = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Computer Science, Medicine, Business'
        }),
        help_text='Your field of study or course name'
    )
    
    year_of_study = forms.IntegerField(
        min_value=1,
        max_value=8,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1',
            'min': '1',
            'max': '8'
        }),
        help_text='Your current year of study (1-8)'
    )
    
    expected_graduation_year = forms.IntegerField(
        min_value=timezone.now().year,
        max_value=timezone.now().year + 10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': str(timezone.now().year + 2),
            'min': str(timezone.now().year),
            'max': str(timezone.now().year + 10)
        }),
        help_text='Year you expect to complete your studies'
    )
    
    previous_gpa = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        min_value=0.0,
        max_value=4.0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '3.50',
            'step': '0.01',
            'min': '0.00',
            'max': '4.00'
        }),
        help_text='Your GPA (if applicable, 0.00-4.00)'
    )
    
    previous_percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0.0,
        max_value=100.0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '85.50',
            'step': '0.01',
            'min': '0.00',
            'max': '100.00'
        }),
        help_text='Your percentage/grade (if applicable, 0-100%)'
    )
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        year_of_study = cleaned_data.get('year_of_study')
        expected_graduation = cleaned_data.get('expected_graduation_year')
        current_year = timezone.now().year
        
        if year_of_study and expected_graduation:
            if expected_graduation < current_year + (year_of_study - 1):
                raise forms.ValidationError(
                    'Expected graduation year should be realistic based on your current year of study.'
                )
        
        return cleaned_data


class OnboardingStep4Form(forms.Form):
    """
    Step 4: Family and Financial Information
    """
    family_income_annual = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '500000',
            'step': '1000'
        }),
        help_text='Total annual family income in KES'
    )
    
    number_of_dependents = forms.IntegerField(
        min_value=0,
        max_value=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '3',
            'min': '0',
            'max': '20'
        }),
        help_text='Number of people depending on family income'
    )
    
    is_orphan = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I am an orphan (lost one or both parents)'
    )
    
    is_single_parent_child = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I am from a single-parent family'
    )
    
    is_child_headed_household = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I am the head of my household'
    )
    
    disability_status = forms.ChoiceField(
        choices=[
            ('none', 'No disability'),
            ('physical', 'Physical disability'),
            ('visual', 'Visual impairment'),
            ('hearing', 'Hearing impairment'),
            ('intellectual', 'Intellectual disability'),
            ('multiple', 'Multiple disabilities'),
            ('other', 'Other disability'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Select if you have any disability'
    )
    
    special_needs_description = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describe any special needs or circumstances...',
            'rows': 3
        }),
        help_text='Additional information about special circumstances (optional)'
    )


class OnboardingStep5Form(forms.Form):
    """
    Step 5: Account Setup
    """
    username = forms.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Username can only contain letters, numbers, and @/./+/-/_ characters.'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'autocomplete': 'username'
        }),
        help_text='Choose a unique username for your account'
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a strong password',
            'autocomplete': 'new-password'
        }),
        help_text='Your password must be at least 8 characters long'
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        }),
        help_text='Enter the same password as before, for verification'
    )
    
    profile_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text='Upload a profile photo (optional, max 5MB)'
    )
    
    terms_accepted = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I accept the Terms and Conditions and Privacy Policy',
        error_messages={
            'required': 'You must accept the terms and conditions to proceed.'
        }
    )
    
    def clean_username(self):
        """Validate username uniqueness"""
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with this username already exists.')
        return username
    
    def clean_password1(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password1')
        if password:
            if len(password) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')
            
            # Check for at least one letter and one number
            if not re.search(r'[A-Za-z]', password):
                raise forms.ValidationError('Password must contain at least one letter.')
            if not re.search(r'\d', password):
                raise forms.ValidationError('Password must contain at least one number.')
        
        return password
    
    def clean(self):
        """Validate password confirmation"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        
        return cleaned_data
    
    def clean_profile_photo(self):
        """Validate profile photo"""
        photo = self.cleaned_data.get('profile_photo')
        if photo:
            # Check file size (5MB max)
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Profile photo must be smaller than 5MB.')
            
            # Check file type
            if not photo.content_type.startswith('image/'):
                raise forms.ValidationError('Please upload a valid image file.')
        
        return photo


class OnboardingProgressForm(forms.Form):
    """
    Hidden form to track onboarding progress and store data between steps.
    This form contains all the data collected from previous steps.
    """
    # Step tracking
    current_step = forms.IntegerField(widget=forms.HiddenInput())
    
    # Step 1 data
    first_name = forms.CharField(max_length=100, widget=forms.HiddenInput(), required=False)
    last_name = forms.CharField(max_length=100, widget=forms.HiddenInput(), required=False)
    other_names = forms.CharField(max_length=100, widget=forms.HiddenInput(), required=False)
    date_of_birth = forms.DateField(widget=forms.HiddenInput(), required=False)
    gender = forms.CharField(max_length=1, widget=forms.HiddenInput(), required=False)
    national_id = forms.CharField(max_length=8, widget=forms.HiddenInput(), required=False)
    
    # Step 2 data
    phone_number = forms.CharField(max_length=15, widget=forms.HiddenInput(), required=False)
    alternative_phone = forms.CharField(max_length=15, widget=forms.HiddenInput(), required=False)
    email = forms.EmailField(widget=forms.HiddenInput(), required=False)
    county_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    sub_county = forms.CharField(max_length=100, widget=forms.HiddenInput(), required=False)
    ward = forms.CharField(max_length=100, widget=forms.HiddenInput(), required=False)
    location = forms.CharField(max_length=100, widget=forms.HiddenInput(), required=False)
    
    # Step 3 data
    current_education_level = forms.CharField(max_length=50, widget=forms.HiddenInput(), required=False)
    current_institution = forms.CharField(max_length=200, widget=forms.HiddenInput(), required=False)
    course_of_study = forms.CharField(max_length=200, widget=forms.HiddenInput(), required=False)
    year_of_study = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    expected_graduation_year = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    previous_gpa = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    previous_percentage = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    
    # Step 4 data
    family_income_annual = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    number_of_dependents = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    is_orphan = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    is_single_parent_child = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    is_child_headed_household = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    disability_status = forms.CharField(max_length=50, widget=forms.HiddenInput(), required=False)
    special_needs_description = forms.CharField(widget=forms.HiddenInput(), required=False)
