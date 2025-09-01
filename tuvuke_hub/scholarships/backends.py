"""
Custom authentication backends for TUVUKE Hub
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Student, Provider


class PhoneNumberAuthBackend(BaseBackend):
    """
    Custom authentication backend that allows users to login with their phone number
    instead of username. Uses the phone_number field from the Student model.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using phone number or username
        
        Args:
            request: HTTP request object
            username: Can be username, email, or phone number
            password: User's password
            **kwargs: Additional keyword arguments
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        if username is None or password is None:
            return None
        
        try:
            # First try to find user by phone number in Student profile
            if username.startswith('+254') or username.startswith('254') or username.startswith('0'):
                # Normalize phone number format
                phone_number = self._normalize_phone_number(username)
                if phone_number:
                    try:
                        student = Student.objects.select_related('user').get(
                            phone_number=phone_number
                        )
                        user = student.user
                    except Student.DoesNotExist:
                        return None
                else:
                    return None
            else:
                # Try to find user by username or email
                try:
                    user = User.objects.get(
                        Q(username=username) | Q(email=username)
                    )
                except User.DoesNotExist:
                    return None
            
            # Check password
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
                
        except Exception:
            return None
        
        return None
    
    def user_can_authenticate(self, user):
        """
        Check if user account is active
        """
        return getattr(user, 'is_active', True)
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    
    def _normalize_phone_number(self, phone_number):
        """
        Normalize phone number to +254XXXXXXXXX format
        
        Args:
            phone_number: Raw phone number string
            
        Returns:
            Normalized phone number string or None if invalid
        """
        if not phone_number:
            return None
        
        # Remove all non-digit characters except +
        cleaned = ''.join(char for char in phone_number if char.isdigit() or char == '+')
        
        # Handle different formats
        if cleaned.startswith('+254'):
            if len(cleaned) == 13:  # +254XXXXXXXXX
                return cleaned
        elif cleaned.startswith('254'):
            if len(cleaned) == 12:  # 254XXXXXXXXX
                return f'+{cleaned}'
        elif cleaned.startswith('0'):
            if len(cleaned) == 10:  # 0XXXXXXXXX
                return f'+254{cleaned[1:]}'
        elif len(cleaned) == 9:  # XXXXXXXXX (without leading 0)
            return f'+254{cleaned}'
        
        return None


class EmailAuthBackend(BaseBackend):
    """
    Authentication backend for email-based login
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using email address
        """
        if username is None or password is None:
            return None
        
        try:
            # Check if username is email format
            if '@' in username:
                user = User.objects.get(email=username)
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
        except User.DoesNotExist:
            pass
        
        return None
    
    def user_can_authenticate(self, user):
        """
        Check if user account is active
        """
        return getattr(user, 'is_active', True)
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class MultiFieldAuthBackend(BaseBackend):
    """
    Combined authentication backend that supports username, email, and phone number
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using username, email, or phone number
        """
        if username is None or password is None:
            return None
        
        # Try phone number authentication first
        phone_backend = PhoneNumberAuthBackend()
        user = phone_backend.authenticate(request, username, password, **kwargs)
        if user:
            return user
        
        # Try email authentication
        email_backend = EmailAuthBackend()
        user = email_backend.authenticate(request, username, password, **kwargs)
        if user:
            return user
        
        # Finally try standard username authentication
        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            pass
        
        return None
    
    def user_can_authenticate(self, user):
        """
        Check if user account is active
        """
        return getattr(user, 'is_active', True)
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
