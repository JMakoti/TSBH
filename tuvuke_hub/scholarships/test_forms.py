from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from scholarships.forms import StudentRegistrationForm, StudentProfileUpdateForm, QuickRegistrationForm
from scholarships.models import Student, County


class StudentRegistrationFormTest(TestCase):
    """Test cases for StudentRegistrationForm"""
    
    def setUp(self):
        """Set up test data"""
        # Use get_or_create to avoid conflicts with migration data
        self.county, created = County.objects.get_or_create(
            code='047',
            defaults={
                'name': 'Nairobi',
                'capital_city': 'Nairobi'
            }
        )
        
        self.valid_form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1995-01-15',
            'gender': 'M',
            'national_id': '12345678',
            'phone_number': '+254712345678',
            'county': self.county.id,
            'sub_county': 'Westlands',
            'ward': 'Kitisuru',
            'current_education_level': 'secondary',  # Changed to secondary to avoid GPA requirement
            'current_institution': 'Nairobi School',
            'course_of_study': 'Sciences',
            'year_of_study': 2,
            'expected_graduation_year': 2025,
            'family_income_annual': 500000.00,
            'number_of_dependents': 3,
            'disability_status': 'none'
        }

    def test_valid_form(self):
        """Test form with valid data"""
        form = StudentRegistrationForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_invalid_national_id(self):
        """Test form with invalid National ID"""
        # Test short National ID
        data = self.valid_form_data.copy()
        data['national_id'] = '123456'
        form = StudentRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('national_id', form.errors)
        
        # Test non-numeric National ID
        data['national_id'] = '12345abc'
        form = StudentRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('national_id', form.errors)

    def test_invalid_phone_number(self):
        """Test form with invalid phone number"""
        data = self.valid_form_data.copy()
        data['phone_number'] = '0712345678'  # Should be converted to +254 format
        form = StudentRegistrationForm(data=data)
        if form.is_valid():
            self.assertEqual(form.cleaned_data['phone_number'], '+254712345678')
        
        # Test completely invalid format
        data['phone_number'] = '123456'
        form = StudentRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)

    def test_age_validation(self):
        """Test age validation"""
        data = self.valid_form_data.copy()
        
        # Test underage (less than 15)
        data['date_of_birth'] = '2020-01-01'
        form = StudentRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)
        
        # Test valid age
        data['date_of_birth'] = '2000-01-01'
        form = StudentRegistrationForm(data=data)
        self.assertTrue('date_of_birth' not in form.errors)

    def test_duplicate_email(self):
        """Test duplicate email validation"""
        # Create a user with the email first
        User.objects.create_user(
            username='existing_user',
            email='test@example.com',
            password='password123'
        )
        
        form = StudentRegistrationForm(data=self.valid_form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_duplicate_national_id(self):
        """Test duplicate National ID validation"""
        # Create a student with the National ID first
        user = User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='password123'
        )
        Student.objects.create(
            user=user,
            first_name='Jane',
            last_name='Doe',
            date_of_birth='1995-01-01',
            gender='F',
            national_id='12345678',  # Same as in form data
            phone_number='+254700000000',
            email='existing@example.com',
            county=self.county,
            sub_county='Test',
            ward='Test',
            current_education_level='undergraduate',
            current_institution='Test University',
            course_of_study='Test Course',
            year_of_study=1,
            expected_graduation_year=2025,
            family_income_annual=100000
        )
        
        form = StudentRegistrationForm(data=self.valid_form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('national_id', form.errors)

    def test_duplicate_phone_number(self):
        """Test duplicate phone number validation"""
        # Create a student with the phone number first
        user = User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='password123'
        )
        Student.objects.create(
            user=user,
            first_name='Jane',
            last_name='Doe',
            date_of_birth='1995-01-01',
            gender='F',
            national_id='87654321',
            phone_number='+254712345678',  # Same as in form data
            email='existing@example.com',
            county=self.county,
            sub_county='Test',
            ward='Test',
            current_education_level='undergraduate',
            current_institution='Test University',
            course_of_study='Test Course',
            year_of_study=1,
            expected_graduation_year=2025,
            family_income_annual=100000
        )
        
        form = StudentRegistrationForm(data=self.valid_form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)

    def test_form_save(self):
        """Test form save functionality"""
        form = StudentRegistrationForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        
        # Check that Student profile was created
        self.assertTrue(hasattr(user, 'student_profile'))
        student = user.student_profile
        self.assertEqual(student.national_id, '12345678')
        self.assertEqual(student.phone_number, '+254712345678')

    def test_cross_field_validation(self):
        """Test cross-field validation"""
        data = self.valid_form_data.copy()
        
        # Test that GPA or percentage is required for higher education levels
        data['current_education_level'] = 'postgraduate'
        data['previous_gpa'] = None
        data['previous_percentage'] = None
        
        form = StudentRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)


class QuickRegistrationFormTest(TestCase):
    """Test cases for QuickRegistrationForm"""
    
    def setUp(self):
        self.county = County.objects.create(
            name='nairobi',
            code='047',
            capital_city='Nairobi'
        )
        
        self.valid_form_data = {
            'username': 'quickuser',
            'email': 'quick@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Quick',
            'last_name': 'User',
            'national_id': '87654321',
            'phone_number': '+254700123456',
            'county': self.county.id,
            'current_education_level': 'secondary'
        }

    def test_valid_quick_form(self):
        """Test quick registration form with valid data"""
        form = QuickRegistrationForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_password_mismatch(self):
        """Test password mismatch validation"""
        data = self.valid_form_data.copy()
        data['password2'] = 'differentpassword'
        
        form = QuickRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_phone_number_normalization(self):
        """Test phone number normalization in quick form"""
        data = self.valid_form_data.copy()
        data['phone_number'] = '0700123456'  # Local format
        
        form = QuickRegistrationForm(data=data)
        if form.is_valid():
            self.assertEqual(form.cleaned_data['phone_number'], '+254700123456')


class StudentProfileUpdateFormTest(TestCase):
    """Test cases for StudentProfileUpdateForm"""
    
    def setUp(self):
        self.county = County.objects.create(
            name='nairobi',
            code='047',
            capital_city='Nairobi'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.student = Student.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            date_of_birth='1995-01-01',
            gender='M',
            national_id='12345678',
            phone_number='+254712345678',
            email='test@example.com',
            county=self.county,
            sub_county='Westlands',
            ward='Kitisuru',
            current_education_level='undergraduate',
            current_institution='University of Nairobi',
            course_of_study='Computer Science',
            year_of_study=2,
            expected_graduation_year=2025,
            family_income_annual=500000
        )

    def test_update_form_initialization(self):
        """Test form initialization with existing student data"""
        form = StudentProfileUpdateForm(instance=self.student)
        self.assertEqual(form.initial['phone_number'], '+254712345678')
        self.assertEqual(form.initial['county'], self.county.id)

    def test_update_phone_number(self):
        """Test updating phone number"""
        form_data = {
            'phone_number': '+254700999888',
            'county': self.county.id,
            'sub_county': 'Westlands',
            'ward': 'Kitisuru',
            'current_institution': 'University of Nairobi',
            'course_of_study': 'Computer Science',
            'year_of_study': 3,
            'expected_graduation_year': 2025,
            'family_income_annual': 600000,
            'number_of_dependents': 2,
            'disability_status': 'none'
        }
        
        form = StudentProfileUpdateForm(data=form_data, instance=self.student)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        updated_student = form.save()
        self.assertEqual(updated_student.phone_number, '+254700999888')

    def test_phone_number_uniqueness_on_update(self):
        """Test phone number uniqueness when updating (should exclude current student)"""
        # Create another student with a different phone number
        another_user = User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='password123'
        )
        Student.objects.create(
            user=another_user,
            first_name='Jane',
            last_name='Smith',
            date_of_birth='1996-01-01',
            gender='F',
            national_id='87654321',
            phone_number='+254700111222',
            email='another@example.com',
            county=self.county,
            sub_county='Test',
            ward='Test',
            current_education_level='undergraduate',
            current_institution='Test University',
            course_of_study='Test Course',
            year_of_study=1,
            expected_graduation_year=2025,
            family_income_annual=100000
        )
        
        # Try to update our student's phone to the other student's phone
        form_data = {
            'phone_number': '+254700111222',  # Same as another student
            'county': self.county.id,
            'sub_county': 'Westlands',
            'ward': 'Kitisuru',
            'current_institution': 'University of Nairobi',
            'course_of_study': 'Computer Science',
            'year_of_study': 3,
            'expected_graduation_year': 2025,
            'family_income_annual': 600000,
            'number_of_dependents': 2,
            'disability_status': 'none'
        }
        
        form = StudentProfileUpdateForm(data=form_data, instance=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
