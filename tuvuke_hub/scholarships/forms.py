from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
import re

from .models import Student, County


class StudentRegistrationForm(UserCreationForm):
    """
    Extended user registration form that includes Student profile creation
    """
    # User fields
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        }),
        help_text="This will be your login email"
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )

    # Student-specific fields (Personal Information)
    other_names = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Other names (optional)'
        })
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'max': date.today().isoformat()
        }),
        help_text="You must be at least 15 years old to register"
    )
    gender = forms.ChoiceField(
        choices=Student.GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    national_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678',
            'pattern': '[0-9]{8}',
            'title': 'Enter 8-digit National ID number'
        }),
        help_text="Enter your 8-digit Kenyan National ID number"
    )

    # Contact Information
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254712345678',
            'pattern': r'^\+?254[0-9]{9}$',
            'title': 'Enter phone number in format +254XXXXXXXXX'
        }),
        help_text="Enter phone number in format +254XXXXXXXXX"
    )
    alternative_phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254712345678 (optional)',
            'pattern': r'^\+?254[0-9]{9}$',
            'title': 'Enter phone number in format +254XXXXXXXXX'
        })
    )

    # Location Information
    county = forms.ModelChoiceField(
        queryset=County.objects.all(),
        empty_label="Select your county",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    sub_county = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your sub-county'
        })
    )
    ward = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your ward'
        })
    )
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your location/village (optional)'
        })
    )
    postal_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter postal address (optional)'
        })
    )

    # Education Information
    current_education_level = forms.ChoiceField(
        choices=Student.EDUCATION_LEVEL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    current_institution = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current school/institution'
        })
    )
    course_of_study = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your course/program of study'
        })
    )
    year_of_study = forms.IntegerField(
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '10',
            'placeholder': 'Enter current year of study'
        })
    )
    expected_graduation_year = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': str(timezone.now().year),
            'max': str(timezone.now().year + 10),
            'placeholder': 'Enter expected graduation year'
        })
    )

    # Academic Performance
    previous_gpa = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        min_value=0,
        max_value=4.0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'max': '4.0',
            'placeholder': 'Enter GPA (0.0 - 4.0)'
        }),
        help_text="Enter GPA on a 4.0 scale (optional)"
    )
    previous_percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=100,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'max': '100',
            'placeholder': 'Enter percentage score'
        }),
        help_text="Enter percentage score (optional)"
    )

    # Financial Information
    family_income_annual = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': 'Enter annual family income in KES'
        }),
        help_text="Enter total annual family income in Kenyan Shillings"
    )
    number_of_dependents = forms.IntegerField(
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'placeholder': 'Enter number of dependents'
        }),
        help_text="Number of people dependent on family income"
    )

    # Special Circumstances
    disability_status = forms.ChoiceField(
        choices=Student.DISABILITY_STATUS_CHOICES,
        initial='none',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    is_orphan = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Check if you are an orphan"
    )
    is_single_parent_child = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Check if you are from a single-parent household"
    )
    is_child_headed_household = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Check if you are from a child-headed household"
    )

    # Profile Photo
    profile_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Upload a passport-size photo (optional)"
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password1', 'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize User fields
        self.fields['username'].help_text = "Choose a unique username for login"
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        
        # Set field order
        field_order = [
            # User Information
            'username', 'email', 'password1', 'password2',
            # Personal Information
            'first_name', 'last_name', 'other_names', 'date_of_birth', 'gender', 'national_id',
            # Contact Information
            'phone_number', 'alternative_phone',
            # Location Information
            'county', 'sub_county', 'ward', 'location', 'postal_address',
            # Education Information
            'current_education_level', 'current_institution', 'course_of_study',
            'year_of_study', 'expected_graduation_year',
            # Academic Performance
            'previous_gpa', 'previous_percentage',
            # Financial Information
            'family_income_annual', 'number_of_dependents',
            # Special Circumstances
            'disability_status', 'is_orphan', 'is_single_parent_child', 'is_child_headed_household',
            # Profile Photo
            'profile_photo'
        ]
        
        # Reorder fields - check if move_to_end method exists
        try:
            for field_name in reversed(field_order):
                if field_name in self.fields:
                    self.fields.move_to_end(field_name, last=False)
        except AttributeError:
            # Fallback for older Django versions where fields might be a regular dict
            from collections import OrderedDict
            if not isinstance(self.fields, OrderedDict):
                ordered_fields = OrderedDict()
                for field_name in field_order:
                    if field_name in self.fields:
                        ordered_fields[field_name] = self.fields[field_name]
                for field_name, field in self.fields.items():
                    if field_name not in ordered_fields:
                        ordered_fields[field_name] = field
                self.fields = ordered_fields

    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_national_id(self):
        """Validate National ID format and uniqueness"""
        national_id = self.cleaned_data.get('national_id')
        
        if national_id:
            # Check format (8 digits)
            if not re.match(r'^\d{8}$', national_id):
                raise ValidationError("National ID must be exactly 8 digits.")
            
            # Check uniqueness
            if Student.objects.filter(national_id=national_id).exists():
                raise ValidationError("A student with this National ID already exists.")
        
        return national_id

    def clean_phone_number(self):
        """Validate phone number format and uniqueness"""
        phone_number = self.cleaned_data.get('phone_number')
        
        if phone_number:
            # Normalize phone number format
            phone_number = self._normalize_phone_number(phone_number)
            
            # Check uniqueness
            if Student.objects.filter(phone_number=phone_number).exists():
                raise ValidationError("A student with this phone number already exists.")
        
        return phone_number

    def clean_alternative_phone(self):
        """Validate alternative phone number format"""
        alt_phone = self.cleaned_data.get('alternative_phone')
        
        if alt_phone:
            # Normalize phone number format
            alt_phone = self._normalize_phone_number(alt_phone)
            
            # Check it's different from primary phone
            primary_phone = self.cleaned_data.get('phone_number')
            if primary_phone and alt_phone == primary_phone:
                raise ValidationError("Alternative phone number must be different from primary phone number.")
        
        return alt_phone

    def clean_date_of_birth(self):
        """Validate age requirements"""
        date_of_birth = self.cleaned_data.get('date_of_birth')
        
        if date_of_birth:
            today = date.today()
            age = today.year - date_of_birth.year - (
                (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
            )
            
            if age < 15:
                raise ValidationError("You must be at least 15 years old to register.")
            
            if age > 100:
                raise ValidationError("Please enter a valid date of birth.")
        
        return date_of_birth

    def clean_expected_graduation_year(self):
        """Validate expected graduation year"""
        graduation_year = self.cleaned_data.get('expected_graduation_year')
        current_year = timezone.now().year
        
        if graduation_year:
            if graduation_year < current_year:
                raise ValidationError("Expected graduation year cannot be in the past.")
            
            if graduation_year > current_year + 10:
                raise ValidationError("Expected graduation year seems too far in the future.")
        
        return graduation_year

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        
        # Validate GPA and percentage - at least one should be provided for certain education levels
        education_level = cleaned_data.get('current_education_level')
        gpa = cleaned_data.get('previous_gpa')
        percentage = cleaned_data.get('previous_percentage')
        
        if education_level in ['undergraduate', 'postgraduate', 'phd']:
            if not gpa and not percentage:
                raise ValidationError(
                    "Please provide either GPA or percentage score for your education level."
                )
        
        # Validate year of study based on education level
        year_of_study = cleaned_data.get('year_of_study')
        if education_level and year_of_study:
            max_years = {
                'primary': 8,
                'secondary': 4,
                'certificate': 2,
                'diploma': 3,
                'undergraduate': 6,
                'postgraduate': 3,
                'phd': 8
            }
            
            if year_of_study > max_years.get(education_level, 10):
                raise ValidationError(
                    f"Year of study seems too high for {education_level} level."
                )
        
        return cleaned_data

    def _normalize_phone_number(self, phone_number):
        """Normalize phone number to standard format"""
        # Remove spaces and dashes
        phone_number = re.sub(r'[\s\-]', '', phone_number)
        
        # Convert to +254 format
        if phone_number.startswith('0'):
            phone_number = '+254' + phone_number[1:]
        elif phone_number.startswith('254'):
            phone_number = '+' + phone_number
        elif not phone_number.startswith('+254'):
            raise ValidationError("Phone number must be in format +254XXXXXXXXX")
        
        # Validate final format
        if not re.match(r'^\+254[0-9]{9}$', phone_number):
            raise ValidationError("Phone number must be in format +254XXXXXXXXX")
        
        return phone_number

    def save(self, commit=True):
        """Save user and create associated student profile"""
        # Save the User instance
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Create Student profile
            student = Student.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                other_names=self.cleaned_data.get('other_names', ''),
                date_of_birth=self.cleaned_data['date_of_birth'],
                gender=self.cleaned_data['gender'],
                national_id=self.cleaned_data['national_id'],
                phone_number=self.cleaned_data['phone_number'],
                email=self.cleaned_data['email'],
                alternative_phone=self.cleaned_data.get('alternative_phone', ''),
                county=self.cleaned_data['county'],
                sub_county=self.cleaned_data['sub_county'],
                ward=self.cleaned_data['ward'],
                location=self.cleaned_data.get('location', ''),
                postal_address=self.cleaned_data.get('postal_address', ''),
                current_education_level=self.cleaned_data['current_education_level'],
                current_institution=self.cleaned_data['current_institution'],
                course_of_study=self.cleaned_data['course_of_study'],
                year_of_study=self.cleaned_data['year_of_study'],
                expected_graduation_year=self.cleaned_data['expected_graduation_year'],
                previous_gpa=self.cleaned_data.get('previous_gpa'),
                previous_percentage=self.cleaned_data.get('previous_percentage'),
                family_income_annual=self.cleaned_data['family_income_annual'],
                number_of_dependents=self.cleaned_data['number_of_dependents'],
                disability_status=self.cleaned_data['disability_status'],
                is_orphan=self.cleaned_data.get('is_orphan', False),
                is_single_parent_child=self.cleaned_data.get('is_single_parent_child', False),
                is_child_headed_household=self.cleaned_data.get('is_child_headed_household', False),
                profile_photo=self.cleaned_data.get('profile_photo'),
            )
            
            return user
        
        return user


class StudentProfileUpdateForm(forms.ModelForm):
    """
    Form for updating student profile information (excluding sensitive fields)
    """
    
    class Meta:
        model = Student
        fields = [
            'other_names', 'phone_number', 'alternative_phone',
            'county', 'sub_county', 'ward', 'location', 'postal_address',
            'current_institution', 'course_of_study', 'year_of_study',
            'expected_graduation_year', 'previous_gpa', 'previous_percentage',
            'family_income_annual', 'number_of_dependents',
            'disability_status', 'is_orphan', 'is_single_parent_child',
            'is_child_headed_household', 'profile_photo'
        ]
        widgets = {
            'other_names': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': r'^\+?254[0-9]{9}$'
            }),
            'alternative_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': r'^\+?254[0-9]{9}$'
            }),
            'county': forms.Select(attrs={'class': 'form-control'}),
            'sub_county': forms.TextInput(attrs={'class': 'form-control'}),
            'ward': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'current_institution': forms.TextInput(attrs={'class': 'form-control'}),
            'course_of_study': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
            'expected_graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'previous_gpa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '4.0'
            }),
            'previous_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'family_income_annual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'number_of_dependents': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'disability_status': forms.Select(attrs={'class': 'form-control'}),
            'is_orphan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_single_parent_child': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_child_headed_household': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_phone_number(self):
        """Validate phone number uniqueness for update"""
        phone_number = self.cleaned_data.get('phone_number')
        
        if phone_number:
            # Normalize phone number
            phone_number = self._normalize_phone_number(phone_number)
            
            # Check uniqueness (exclude current student)
            existing_student = Student.objects.filter(phone_number=phone_number).exclude(
                pk=self.instance.pk if self.instance else None
            ).first()
            
            if existing_student:
                raise ValidationError("A student with this phone number already exists.")
        
        return phone_number

    def clean_alternative_phone(self):
        """Validate alternative phone number"""
        alt_phone = self.cleaned_data.get('alternative_phone')
        
        if alt_phone:
            alt_phone = self._normalize_phone_number(alt_phone)
            
            primary_phone = self.cleaned_data.get('phone_number')
            if primary_phone and alt_phone == primary_phone:
                raise ValidationError("Alternative phone must be different from primary phone.")
        
        return alt_phone

    def _normalize_phone_number(self, phone_number):
        """Normalize phone number format"""
        phone_number = re.sub(r'[\s\-]', '', phone_number)
        
        if phone_number.startswith('0'):
            phone_number = '+254' + phone_number[1:]
        elif phone_number.startswith('254'):
            phone_number = '+' + phone_number
        elif not phone_number.startswith('+254'):
            raise ValidationError("Phone number must be in format +254XXXXXXXXX")
        
        if not re.match(r'^\+254[0-9]{9}$', phone_number):
            raise ValidationError("Phone number must be in format +254XXXXXXXXX")
        
        return phone_number


class QuickRegistrationForm(forms.Form):
    """
    Simplified form for quick student registration with minimal required fields
    """
    # Basic user information
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    # Essential student information
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    national_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678',
            'pattern': '[0-9]{8}'
        }),
        help_text="8-digit National ID"
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254712345678'
        })
    )
    county = forms.ModelChoiceField(
        queryset=County.objects.all(),
        empty_label="Select county",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    current_education_level = forms.ChoiceField(
        choices=Student.EDUCATION_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        return email

    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if not re.match(r'^\d{8}$', national_id):
            raise ValidationError("National ID must be 8 digits.")
        if Student.objects.filter(national_id=national_id).exists():
            raise ValidationError("National ID already registered.")
        return national_id

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Normalize phone number
        phone_number = re.sub(r'[\s\-]', '', phone_number)
        if phone_number.startswith('0'):
            phone_number = '+254' + phone_number[1:]
        elif phone_number.startswith('254'):
            phone_number = '+' + phone_number
        
        if not re.match(r'^\+254[0-9]{9}$', phone_number):
            raise ValidationError("Invalid phone number format.")
        
        if Student.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("Phone number already registered.")
        
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match.")
        
        return cleaned_data


class StudentSearchForm(forms.Form):
    """
    Form for searching students with various criteria
    """
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, or National ID...'
        })
    )
    county = forms.ModelChoiceField(
        queryset=County.objects.all(),
        required=False,
        empty_label="All counties",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    education_level = forms.ChoiceField(
        choices=[('', 'All levels')] + Student.EDUCATION_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    gender = forms.ChoiceField(
        choices=[('', 'All genders')] + Student.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_verified = forms.ChoiceField(
        choices=[
            ('', 'All students'),
            ('true', 'Verified only'),
            ('false', 'Unverified only')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    age_min = forms.IntegerField(
        required=False,
        min_value=15,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min age'
        })
    )
    age_max = forms.IntegerField(
        required=False,
        min_value=15,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max age'
        })
    )
