"""
Demo script showing how to use the calculate_match_score method
"""
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tuvuke_hub.settings')
django.setup()

from scholarships.models import County, Student, Provider, Scholarship
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone


def demo_calculate_match_score():
    """Demonstrate the calculate_match_score method"""
    
    print("🎓 Scholarship Matching System Demo")
    print("=" * 50)
    
    # Get or create test data
    county = County.objects.get(code="047")  # Nairobi
    
    # Create or get provider
    provider, _ = Provider.objects.get_or_create(
        slug="demo-foundation",
        defaults={
            "name": "Demo Foundation",
            "provider_type": "foundation",
            "funding_source": "private",
            "email": "info@demofoundation.org",
            "phone_number": "+254700000000",
            "physical_address": "Demo Address, Nairobi"
        }
    )
    
    # Create scholarship with specific criteria
    scholarship = Scholarship.objects.create(
        title="Computer Science Excellence Scholarship",
        slug="computer-science-excellence-scholarship",
        provider=provider,
        scholarship_type="academic",
        amount_per_beneficiary=Decimal('150000'),
        total_budget=Decimal('1500000'),
        number_of_awards=10,
        description="Scholarship for excellent computer science students",
        target_education_levels=["undergraduate"],
        minimum_gpa=Decimal('3.5'),
        minimum_age=18,
        maximum_age=25,
        maximum_family_income=Decimal('800000'),
        for_males_only=False,
        for_females_only=False,
        application_start_date=timezone.now(),
        application_deadline=timezone.now() + timedelta(days=30)
    )
    
    # Add target county
    scholarship.target_counties.add(county)
    
    print(f"📚 Scholarship: {scholarship.title}")
    print(f"💰 Amount: KES {scholarship.amount_per_beneficiary:,}")
    print(f"🎯 Criteria:")
    print(f"   - Education Level: {scholarship.target_education_levels}")
    print(f"   - Minimum GPA: {scholarship.minimum_gpa}")
    print(f"   - Age Range: {scholarship.minimum_age}-{scholarship.maximum_age}")
    print(f"   - Max Family Income: KES {scholarship.maximum_family_income:,}")
    print(f"   - Target Counties: {[c.name for c in scholarship.target_counties.all()]}")
    print()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Perfect Match Student",
            "data": {
                "username": "perfect_student",
                "education_level": "undergraduate",
                "gpa": Decimal('3.8'),
                "age": 22,
                "income": Decimal('600000'),
                "county": county,
                "gender": "F"
            }
        },
        {
            "name": "Good Match Student",
            "data": {
                "username": "good_student", 
                "education_level": "undergraduate",
                "gpa": Decimal('3.5'),
                "age": 23,
                "income": Decimal('750000'),
                "county": county,
                "gender": "M"
            }
        },
        {
            "name": "Partial Match Student",
            "data": {
                "username": "partial_student",
                "education_level": "diploma",  # Doesn't match
                "gpa": Decimal('3.6'),
                "age": 21,
                "income": Decimal('650000'),
                "county": county,
                "gender": "F"
            }
        },
        {
            "name": "Poor Match Student",
            "data": {
                "username": "poor_student",
                "education_level": "postgraduate",  # Doesn't match
                "gpa": Decimal('3.2'),  # Below minimum
                "age": 28,  # Above maximum
                "income": Decimal('900000'),  # Above maximum
                "county": County.objects.get(code="001"),  # Different county
                "gender": "M"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"👤 Student {i}: {scenario['name']}")
        
        # Create user and student
        user = User.objects.create_user(
            username=scenario['data']['username'],
            email=f"{scenario['data']['username']}@test.com",
            password="testpass123"
        )
        
        student = Student.objects.create(
            user=user,
            first_name="Test",
            last_name=f"Student {i}",
            date_of_birth=date(2024 - scenario['data']['age'], 1, 1),
            gender=scenario['data']['gender'],
            national_id=f"1234567{i}",
            phone_number=f"+25470000000{i}",
            email=f"{scenario['data']['username']}@test.com",
            county=scenario['data']['county'],
            sub_county="Test SubCounty",
            ward="Test Ward",
            current_education_level=scenario['data']['education_level'],
            current_institution="Test University",
            course_of_study="Computer Science",
            year_of_study=2,
            expected_graduation_year=2025,
            previous_gpa=scenario['data']['gpa'],
            family_income_annual=scenario['data']['income']
        )
        
        # Calculate match score
        score = scholarship.calculate_match_score(student)
        
        print(f"   📋 Profile:")
        print(f"      - Education: {scenario['data']['education_level']}")
        print(f"      - GPA: {scenario['data']['gpa']}")
        print(f"      - Age: {scenario['data']['age']}")
        print(f"      - Family Income: KES {scenario['data']['income']:,}")
        print(f"      - County: {scenario['data']['county'].name}")
        print(f"   🎯 Match Score: {score}%")
        
        # Interpretation
        if score >= 90:
            print(f"   ✅ Excellent match - highly recommended!")
        elif score >= 70:
            print(f"   ✅ Good match - should apply!")
        elif score >= 50:
            print(f"   ⚠️  Partial match - consider applying")
        else:
            print(f"   ❌ Poor match - unlikely to qualify")
        
        print()
    
    print("🔍 Method Usage Example:")
    print("```python")
    print("from scholarships.models import Scholarship, Student")
    print()
    print("# Get scholarship and student objects")
    print("scholarship = Scholarship.objects.get(id=1)")
    print("student = Student.objects.get(id=1)")
    print()
    print("# Calculate match score")
    print("score = scholarship.calculate_match_score(student)")
    print("print(f'Match score: {score}%')")
    print("```")


if __name__ == "__main__":
    demo_calculate_match_score()
