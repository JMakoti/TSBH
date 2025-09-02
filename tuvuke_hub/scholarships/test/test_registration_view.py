"""
Test cases for StudentRegistrationView Class-Based View
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

from scholarships.models import County, Student


class StudentRegistrationViewTest(TestCase):
    """Test the StudentRegistrationView Class-Based View"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create a county for testing
        self.county, created = County.objects.get_or_create(
            code='047',
            defaults={
                'name': 'Nairobi',
                'capital_city': 'Nairobi'
            }
        )
        
        self.registration_url = reverse('scholarships:register_student')
        
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
    
    def test_get_registration_page(self):
        """Test GET request returns registration form"""
        response = self.client.get(self.registration_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student Registration')
        self.assertContains(response, 'form')
        self.assertContains(response, 'Create Account')
    
    def test_post_valid_registration(self):
        """Test POST request with valid data creates user and logs them in"""
        response = self.client.post(self.registration_url, self.valid_form_data)
        
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='testuser123').exists())
        user = User.objects.get(username='testuser123')
        
        # Check password was hashed properly
        self.assertTrue(check_password('testpass123', user.password))
        
        # Check student profile was created
        self.assertTrue(hasattr(user, 'student_profile'))
        student = user.student_profile
        self.assertEqual(student.first_name, 'John')
        self.assertEqual(student.last_name, 'Doe')
        self.assertEqual(student.national_id, '87654321')
        
        # Check user is logged in (session should contain user_id)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)
    
    def test_post_invalid_registration(self):
        """Test POST request with invalid data returns form with errors"""
        invalid_data = self.valid_form_data.copy()
        invalid_data['email'] = 'invalid-email'  # Invalid email format
        invalid_data['national_id'] = '123'  # Too short
        
        response = self.client.post(self.registration_url, invalid_data)
        
        # Should return form with errors (status 200)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the errors')
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='testuser123').exists())
    
    def test_duplicate_registration_prevented(self):
        """Test that duplicate registrations are prevented"""
        # Create first user
        response1 = self.client.post(self.registration_url, self.valid_form_data)
        self.assertEqual(response1.status_code, 302)
        
        # Try to create second user with same data
        response2 = self.client.post(self.registration_url, self.valid_form_data)
        
        # Should return form with errors
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, 'Please correct the errors')
        
        # Should only have one user
        self.assertEqual(User.objects.filter(username='testuser123').count(), 1)
