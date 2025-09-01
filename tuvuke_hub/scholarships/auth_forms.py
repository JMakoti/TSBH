"""
Custom authentication forms for TUVUKE Hub
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Student
from .backends import PhoneNumberAuthBackend


class PhoneNumberLoginForm(AuthenticationForm):
    """
    Custom login form that supports phone number, email, or username authentication
    """
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number, email, or username',
            'autofocus': True,
        }),
        label='Phone Number / Email / Username',
        help_text='Enter your phone number (+254XXXXXXXXX), email address, or username'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }),
        label='Password'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label='Remember me'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the default username field error messages
        self.fields['username'].error_messages = {
            'required': 'Please enter your phone number, email, or username.',
        }
        self.fields['password'].error_messages = {
            'required': 'Please enter your password.',
        }
    
    def clean_username(self):
        """
        Clean and validate the username field
        """
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError('This field is required.')
        
        # Clean the input - remove extra spaces
        username = username.strip()
        
        # If it looks like a phone number, try to normalize it
        if any(char.isdigit() for char in username) and len(username) >= 9:
            backend = PhoneNumberAuthBackend()
            normalized_phone = backend._normalize_phone_number(username)
            if normalized_phone:
                # Check if a student with this phone number exists
                if Student.objects.filter(phone_number=normalized_phone).exists():
                    return normalized_phone
        
        return username
    
    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.
        """
        if not user.is_active:
            raise ValidationError(
                'This account is inactive. Please contact support.',
                code='inactive',
            )


class StudentPhoneRegistrationForm(forms.Form):
    """
    Initial registration form using phone number for students
    """
    
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254XXXXXXXXX',
            'pattern': r'^\+?254[0-9]{9}$',
        }),
        label='Phone Number',
        help_text='Enter your phone number in format +254XXXXXXXXX'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        }),
        label='Email Address',
        help_text='This will be used for account notifications'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }),
        label='Password',
        help_text='Password must be at least 8 characters long'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        }),
        label='Confirm Password'
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I agree to the Terms and Conditions and Privacy Policy'
    )
    
    def clean_phone_number(self):
        """
        Validate and normalize phone number
        """
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise ValidationError('Phone number is required.')
        
        # Normalize phone number
        backend = PhoneNumberAuthBackend()
        normalized_phone = backend._normalize_phone_number(phone_number)
        
        if not normalized_phone:
            raise ValidationError(
                'Please enter a valid Kenyan phone number in format +254XXXXXXXXX'
            )
        
        # Check if phone number already exists
        if Student.objects.filter(phone_number=normalized_phone).exists():
            raise ValidationError(
                'A student account with this phone number already exists.'
            )
        
        return normalized_phone
    
    def clean_email(self):
        """
        Validate email uniqueness
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError(
                'A user with this email address already exists.'
            )
        return email
    
    def clean(self):
        """
        Validate password confirmation
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("The two password fields didn't match.")
            
            # Basic password validation
            if len(password1) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
        
        return cleaned_data
    
    def save(self):
        """
        Create user account using phone number as username
        """
        cleaned_data = self.cleaned_data
        
        # Create username from phone number (remove + sign)
        username = cleaned_data['phone_number'].replace('+', '')
        
        # Create User account
        user = User.objects.create_user(
            username=username,
            email=cleaned_data['email'],
            password=cleaned_data['password1']
        )
        
        return user


class PasswordResetByPhoneForm(forms.Form):
    """
    Password reset form using phone number
    """
    
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254XXXXXXXXX',
            'pattern': r'^\+?254[0-9]{9}$',
        }),
        label='Phone Number',
        help_text='Enter the phone number associated with your account'
    )
    
    def clean_phone_number(self):
        """
        Validate phone number and check if account exists
        """
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise ValidationError('Phone number is required.')
        
        # Normalize phone number
        backend = PhoneNumberAuthBackend()
        normalized_phone = backend._normalize_phone_number(phone_number)
        
        if not normalized_phone:
            raise ValidationError(
                'Please enter a valid Kenyan phone number in format +254XXXXXXXXX'
            )
        
        # Check if phone number exists
        try:
            student = Student.objects.get(phone_number=normalized_phone)
            self.user = student.user
        except Student.DoesNotExist:
            raise ValidationError(
                'No account found with this phone number.'
            )
        
        return normalized_phone
    
    def get_user(self):
        """
        Return the user associated with the phone number
        """
        return getattr(self, 'user', None)
