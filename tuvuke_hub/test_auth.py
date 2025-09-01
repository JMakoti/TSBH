#!/usr/bin/env python
"""
Quick test script to verify authentication backend is working
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tuvuke_hub.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from scholarships.models import Student
from scholarships.backends import MultiFieldAuthBackend

def test_auth_backend():
    """Test the custom authentication backend"""
    
    print("🔐 Testing Custom Authentication Backend...")
    
    # Create a test user and student profile
    test_phone = "+254712345678"
    test_email = "test@example.com"
    test_username = "testuser"
    test_password = "testpass123"
    
    try:
        # Clean up any existing test data
        try:
            existing_user = User.objects.get(username=test_username)
            existing_user.delete()
            print("   Cleaned up existing test user")
        except User.DoesNotExist:
            pass
        
        # Create test user
        user = User.objects.create_user(
            username=test_username,
            email=test_email,
            password=test_password
        )
        
        # Create student profile
        student = Student.objects.create(
            user=user,
            phone_number=test_phone,
            email=test_email,
            first_name="Test",
            last_name="User",
            date_of_birth="1995-01-01",
            gender="M",
            national_id="12345678",
            county_id=1,
            sub_county="Test Sub County",
            ward="Test Ward",
            current_education_level="undergraduate",
            current_institution="Test University",
            course_of_study="Computer Science",
            year_of_study=3,
            expected_graduation_year=2026,
            family_income_annual=500000
        )
        
        print(f"   ✅ Created test user: {user.username}")
        print(f"   ✅ Created student profile: {student.full_name}")
        
        # Test authentication with different methods
        backend = MultiFieldAuthBackend()
        
        # Test 1: Username authentication
        auth_user = backend.authenticate(None, username=test_username, password=test_password)
        print(f"   📱 Username auth: {'✅ SUCCESS' if auth_user else '❌ FAILED'}")
        
        # Test 2: Email authentication  
        auth_user = backend.authenticate(None, username=test_email, password=test_password)
        print(f"   📧 Email auth: {'✅ SUCCESS' if auth_user else '❌ FAILED'}")
        
        # Test 3: Phone number authentication
        auth_user = backend.authenticate(None, username=test_phone, password=test_password)
        print(f"   📞 Phone auth: {'✅ SUCCESS' if auth_user else '❌ FAILED'}")
        
        # Test 4: Phone number variants
        phone_variants = [
            "254712345678",      # Without +
            "0712345678",        # With leading 0
            "712345678"          # Without country code
        ]
        
        for variant in phone_variants:
            auth_user = backend.authenticate(None, username=variant, password=test_password)
            print(f"   📱 Phone variant '{variant}': {'✅ SUCCESS' if auth_user else '❌ FAILED'}")
        
        # Test 5: Wrong password
        auth_user = backend.authenticate(None, username=test_username, password="wrongpass")
        print(f"   🔒 Wrong password: {'✅ CORRECTLY FAILED' if not auth_user else '❌ SECURITY ISSUE'}")
        
        # Test Django's authenticate function (which uses all backends)
        print("\n🔍 Testing Django authenticate() function:")
        
        # Test with username
        django_auth = authenticate(username=test_username, password=test_password)
        print(f"   📱 Django username auth: {'✅ SUCCESS' if django_auth else '❌ FAILED'}")
        
        # Test with email
        django_auth = authenticate(username=test_email, password=test_password)
        print(f"   📧 Django email auth: {'✅ SUCCESS' if django_auth else '❌ FAILED'}")
        
        # Test with phone
        django_auth = authenticate(username=test_phone, password=test_password)
        print(f"   📞 Django phone auth: {'✅ SUCCESS' if django_auth else '❌ FAILED'}")
        
        print("\n✅ Authentication backend test completed successfully!")
        
        # Clean up
        user.delete()
        print("   🧹 Cleaned up test data")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth_backend()
