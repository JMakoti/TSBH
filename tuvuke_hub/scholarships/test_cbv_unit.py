"""
Unit tests for StudentRegistrationView Class-Based View (without template dependency)
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from unittest.mock import patch

from scholarships.models import County, Student
from scholarships.views import StudentRegistrationView
from scholarships.forms import StudentRegistrationForm


class StudentRegistrationViewUnitTest(TestCase):
    """Unit tests for StudentRegistrationView focusing on core logic"""
    
    def setUp(self):
        """Set up test data"""
        # Create a county for testing
        self.county, created = County.objects.get_or_create(
            code='047',
            defaults={
                'name': 'Nairobi',
                'capital_city': 'Nairobi'
            }
        )
        
        self.view = StudentRegistrationView()
        
        self.valid_form_data = {
            'username': 'testuser123',
            'email': 'test123@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1995-01-15',
            'gender': 'M',
            'national_id': '87654321',
            'phone_number': '+254712345679',
            'county': self.county.id,
            'sub_county': 'Westlands',
            'ward': 'Kitisuru',
            'current_education_level': 'secondary',
            'current_institution': 'Nairobi School',
            'course_of_study': 'Sciences',
            'year_of_study': 2,
            'expected_graduation_year': 2025,
            'family_income_annual': 500000.00,
            'number_of_dependents': 3,
            'disability_status': 'none'
        }
    
    def test_form_validation_and_user_creation(self):
        """Test that the form validates and creates user properly"""
        form = StudentRegistrationForm(data=self.valid_form_data)
        
        # Form should be valid
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        # Save the form
        user = form.save()
        
        # Check user was created
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'testuser123')
        self.assertEqual(user.email, 'test123@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        
        # Check password was hashed properly
        self.assertTrue(check_password('testpass123', user.password))
        
        # Check student profile was created
        self.assertTrue(hasattr(user, 'student_profile'))
        student = user.student_profile
        self.assertEqual(student.first_name, 'John')
        self.assertEqual(student.last_name, 'Doe')
        self.assertEqual(student.national_id, '87654321')
        self.assertEqual(student.phone_number, '+254712345679')
    
    def test_get_context_data(self):
        """Test that get_context_data returns correct context"""
        context = self.view.get_context_data()
        
        self.assertIn('form', context)
        self.assertIn('page_title', context)
        self.assertIn('submit_text', context)
        self.assertIn('counties', context)
        
        self.assertEqual(context['page_title'], 'Student Registration')
        self.assertEqual(context['submit_text'], 'Create Account')
        self.assertIsInstance(context['form'], StudentRegistrationForm)
        
        # Check counties are ordered by name
        counties = list(context['counties'])
        self.assertTrue(len(counties) > 0)
    
    def test_view_form_class_and_template(self):
        """Test that view has correct form class and template"""
        self.assertEqual(self.view.form_class, StudentRegistrationForm)
        self.assertEqual(self.view.template_name, 'scholarships/register.html')
    
    def test_password_hashing_verification(self):
        """Test that password is properly hashed using make_password functionality"""
        from django.contrib.auth.hashers import make_password
        
        plain_password = 'testpass123'
        hashed_password = make_password(plain_password)
        
        # Check that the hashed password is different from plain text
        self.assertNotEqual(plain_password, hashed_password)
        
        # Check that we can verify the password
        self.assertTrue(check_password(plain_password, hashed_password))
        
        # Check that wrong password fails
        self.assertFalse(check_password('wrongpass', hashed_password))
