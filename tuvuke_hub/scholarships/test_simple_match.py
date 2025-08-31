"""
Simple test for the calculate_match_score method
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from .models import County, Student, Provider, Scholarship


class SimpleMatchScoreTest(TestCase):
    """Simple test for the match score calculation"""

    def test_basic_match_score(self):
        """Test basic match score calculation"""
        # Get existing county
        county = County.objects.get(code="047")  # Nairobi
        
        # Create minimal provider
        provider = Provider.objects.create(
            name="Test Foundation",
            slug="test-foundation",
            provider_type="foundation",
            funding_source="private",
            email="info@testfoundation.org",
            phone_number="+254712345678",
            physical_address="Test Address"
        )
        
        # Create minimal scholarship
        scholarship = Scholarship.objects.create(
            title="Test Scholarship",
            provider=provider,
            scholarship_type="academic",
            amount_per_beneficiary=Decimal('100000'),
            total_budget=Decimal('1000000'),
            number_of_awards=10,
            description="Test scholarship",
            application_start_date=timezone.now(),
            application_deadline=timezone.now() + timedelta(days=30)
        )
        
        # Test with None student (should return 0.0)
        score = scholarship.calculate_match_score(None)
        self.assertEqual(score, 0.0)
        
        # Create minimal user and student
        user = User.objects.create_user(
            username="teststudent",
            email="student@test.com",
            password="testpass123"
        )
        
        student = Student.objects.create(
            user=user,
            first_name="John",
            last_name="Doe",
            date_of_birth=date(2000, 1, 1),
            gender="M",
            national_id="12345678",
            phone_number="+254712345678",
            email="student@test.com",
            county=county,
            sub_county="Westlands",
            ward="Parklands",
            current_education_level="undergraduate",
            current_institution="University of Nairobi",
            course_of_study="Computer Science",
            year_of_study=3,
            expected_graduation_year=2025,
            family_income_annual=Decimal('500000'),
            physical_address="Test Address"
        )
        
        # Test with student (should return 100.0 for no criteria)
        score = scholarship.calculate_match_score(student)
        self.assertEqual(score, 100.0)
