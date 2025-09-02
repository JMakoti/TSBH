"""
Tests for the calculate_match_score method on Scholarship model
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from .models import County, Student, Provider, Scholarship


class MatchScoreTestCase(TestCase):
    """Test cases for scholarship matching algorithm"""

    def setUp(self):
        """Set up test data"""
        # Get or create test county (Nairobi already exists from migration)
        self.county, created = County.objects.get_or_create(
            code="047",
            defaults={"name": "Nairobi"}
        )
        
        # Create test provider
        self.provider = Provider.objects.create(
            name="Test Foundation",
            slug="test-foundation",
            provider_type="foundation",
            funding_source="private",
            email="info@testfoundation.org",
            phone_number="+254712345678",
            physical_address="Test Address, Nairobi"
        )
        
        # Create test user and student
        self.user = User.objects.create_user(
            username="teststudent",
            email="student@test.com",
            password="testpass123"
        )
        
        self.student = Student.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            date_of_birth=date(2000, 1, 1),  # 24 years old
            gender="M",
            national_id="12345678",
            phone_number="+254712345678",
            email="student@test.com",
            county=self.county,
            sub_county="Westlands",
            ward="Parklands",
            current_education_level="undergraduate",
            current_institution="University of Nairobi",
            course_of_study="Computer Science",
            year_of_study=3,
            expected_graduation_year=2025,
            previous_gpa=Decimal('3.5'),
            previous_percentage=Decimal('75.0'),
            family_income_annual=Decimal('500000'),
            number_of_dependents=3,
            disability_status="none",
            is_orphan=False,
            is_single_parent_child=False,
            is_child_headed_household=False
        )

    def test_perfect_match_scholarship(self):
        """Test scholarship that perfectly matches the student"""
        scholarship = Scholarship.objects.create(
            title="Perfect Match Scholarship",
            provider=self.provider,
            scholarship_type="academic",
            amount_per_beneficiary=Decimal('100000'),
            description="A test scholarship for perfect matching",
            target_education_levels=["undergraduate"],
            minimum_gpa=Decimal('3.0'),
            minimum_age=18,
            maximum_age=30,
            maximum_family_income=Decimal('600000'),
            for_males_only=True,  # Changed from gender_restriction="male"
            target_fields_of_study=["Computer Science", "Engineering"],
            for_orphans_only=False,
            for_disabled_only=False,
            application_start_date=timezone.now(),
            application_deadline=timezone.now() + timedelta(days=30)
        )
        
        # Add target county
        scholarship.target_counties.add(self.county)
        
        # Calculate match score
        score = scholarship.calculate_match_score(self.student)
        
        # Should be 100% match
        self.assertEqual(score, 100.0)

    def test_partial_match_scholarship(self):
        """Test scholarship with partial match"""
        scholarship = Scholarship.objects.create(
            title="Partial Match Scholarship",
            provider=self.provider,
            scholarship_type="academic",
            amount_per_beneficiary=Decimal('100000'),
            description="A test scholarship for partial matching",
            target_education_levels=["postgraduate"],  # Student is undergraduate
            minimum_gpa=Decimal('3.0'),  # Student has 3.5, matches
            minimum_age=18,
            maximum_age=30,
            maximum_family_income=Decimal('400000'),  # Student has 500k, doesn't match
            for_males_only=True,  # Student is male, matches
            for_orphans_only=False,
            for_disabled_only=False,
            application_start_date=timezone.now(),
            application_deadline=timezone.now() + timedelta(days=30)
        )
        
        # Add target county (matches)
        scholarship.target_counties.add(self.county)
        
        # Calculate match score
        score = scholarship.calculate_match_score(self.student)
        
        # Should be less than 100% but greater than 0%
        self.assertGreater(score, 0.0)
        self.assertLess(score, 100.0)
        print(f"Partial match score: {score}%")

    def test_no_match_scholarship(self):
        """Test scholarship with no match"""
        scholarship = Scholarship.objects.create(
            title="No Match Scholarship",
            provider=self.provider,
            scholarship_type="academic",
            amount_per_beneficiary=Decimal('100000'),
            description="A test scholarship with no matching criteria",
            target_education_levels=["phd"],  # Student is undergraduate
            minimum_gpa=Decimal('3.8'),  # Student has 3.5, doesn't match
            minimum_age=30,  # Student is 24, doesn't match
            maximum_age=40,
            maximum_family_income=Decimal('300000'),  # Student has 500k, doesn't match
            for_females_only=True,  # Student is male, doesn't match
            for_orphans_only=True,  # Student is not orphan, doesn't match
            for_disabled_only=False,
            application_start_date=timezone.now(),
            application_deadline=timezone.now() + timedelta(days=30)
        )
        
        # Calculate match score
        score = scholarship.calculate_match_score(self.student)
        
        # Should be 0% match
        self.assertEqual(score, 0.0)

    def test_orphan_specific_scholarship(self):
        """Test scholarship specifically for orphans"""
        # Create orphan student
        orphan_user = User.objects.create_user(
            username="orphanstudent",
            email="orphan@test.com",
            password="testpass123"
        )
        
        orphan_student = Student.objects.create(
            user=orphan_user,
            first_name="Jane",
            last_name="Smith",
            date_of_birth=date(2001, 5, 15),
            gender="F",
            national_id="87654321",
            phone_number="+254787654321",
            email="orphan@test.com",
            county=self.county,
            sub_county="Westlands",
            ward="Parklands",
            current_education_level="secondary",
            current_institution="Test High School",
            course_of_study="Sciences",
            year_of_study=4,
            expected_graduation_year=2024,
            previous_percentage=Decimal('85.0'),
            family_income_annual=Decimal('200000'),
            number_of_dependents=2,
            disability_status="none",
            is_orphan=True,  # This is an orphan
            is_single_parent_child=False,
            is_child_headed_household=True
        )
        
        scholarship = Scholarship.objects.create(
            title="Orphan Support Scholarship",
            provider=self.provider,
            scholarship_type="need_based",
            amount_per_beneficiary=Decimal('50000'),
            description="Scholarship specifically for orphaned students",
            target_education_levels=["secondary"],
            minimum_percentage=Decimal('80.0'),
            minimum_age=15,
            maximum_age=25,
            maximum_family_income=Decimal('300000'),
            for_females_only=True,
            for_orphans_only=True,  # Only for orphans
            for_disabled_only=False,
            eligibility_criteria={"child_headed_household": True},
            application_start_date=timezone.now(),
            application_deadline=timezone.now() + timedelta(days=30)
        )
        
        scholarship.target_counties.add(self.county)
        
        # Test with orphan student
        orphan_score = scholarship.calculate_match_score(orphan_student)
        
        # Test with regular student (non-orphan)
        regular_score = scholarship.calculate_match_score(self.student)
        
        # Orphan should have higher score
        self.assertGreater(orphan_score, regular_score)
        print(f"Orphan student score: {orphan_score}%")
        print(f"Regular student score: {regular_score}%")

    def test_no_criteria_scholarship(self):
        """Test scholarship with no specific criteria (should match 100%)"""
        scholarship = Scholarship.objects.create(
            title="Open Scholarship",
            provider=self.provider,
            scholarship_type="merit",
            amount_per_beneficiary=Decimal('75000'),
            description="Open scholarship with no specific criteria",
            application_start_date=timezone.now(),
            application_deadline=timezone.now() + timedelta(days=30)
        )
        
        # Calculate match score
        score = scholarship.calculate_match_score(self.student)
        
        # Should be 100% since no criteria to fail
        self.assertEqual(score, 100.0)

    def test_null_student(self):
        """Test with null/None student"""
        scholarship = Scholarship.objects.create(
            title="Test Scholarship",
            provider=self.provider,
            scholarship_type="academic",
            amount_per_beneficiary=Decimal('100000'),
            description="Test scholarship",
            application_start_date=timezone.now(),
            application_deadline=timezone.now() + timedelta(days=30)
        )
        
        # Test with None student
        score = scholarship.calculate_match_score(None)
        
        # Should return 0.0
        self.assertEqual(score, 0.0)

    def test_disabled_student_scholarship(self):
        """Test scholarship for disabled students"""
        # Create disabled student
        disabled_user = User.objects.create_user(
            username="disabledstudent",
            email="disabled@test.com",
            password="testpass123"
        )
        
        disabled_student = Student.objects.create(
            user=disabled_user,
            first_name="Alex",
            last_name="Johnson",
            date_of_birth=date(1999, 8, 20),
            gender="O",
            national_id="11223344",
            phone_number="+254711223344",
            email="disabled@test.com",
            county=self.county,
            sub_county="Westlands",
            ward="Parklands",
            current_education_level="diploma",
            current_institution="Technical College",
            course_of_study="Information Technology",
            year_of_study=2,
            expected_graduation_year=2025,
            previous_percentage=Decimal('82.0'),
            family_income_annual=Decimal('350000'),
            number_of_dependents=1,
            disability_status="physical",  # Has disability
            is_orphan=False,
            is_single_parent_child=True,
            is_child_headed_household=False
        )
        
        scholarship = Scholarship.objects.create(
            title="Disability Support Scholarship",
            provider=self.provider,
            scholarship_type="need_based",
            amount_per_beneficiary=Decimal('80000'),
            description="Scholarship for students with disabilities",
            target_education_levels=["diploma"],
            minimum_percentage=Decimal('75.0'),
            minimum_age=18,
            maximum_age=30,
            maximum_family_income=Decimal('400000'),
            for_females_only=False,  # Changed from gender_restriction="any"
            for_males_only=False,
            for_orphans_only=False,
            for_disabled_only=True,  # Only for disabled students
            eligibility_criteria={"single_parent_child": True},
            application_start_date=timezone.now(),
            application_deadline=timezone.now() + timedelta(days=30)
        )
        
        scholarship.target_counties.add(self.county)
        
        # Test with disabled student
        disabled_score = scholarship.calculate_match_score(disabled_student)
        
        # Test with regular student (not disabled)
        regular_score = scholarship.calculate_match_score(self.student)
        
        # Disabled student should have higher score
        self.assertGreater(disabled_score, regular_score)
        print(f"Disabled student score: {disabled_score}%")
        print(f"Regular student score: {regular_score}%")
