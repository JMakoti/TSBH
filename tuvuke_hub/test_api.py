#!/usr/bin/env python
"""
Test script for the DRF API endpoints
Run this after setting up the API to verify everything works
"""

import os
import sys
import django
import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tuvuke_hub.settings')
django.setup()

from scholarships.models import Student, Provider, Scholarship, County, Application


class APITestRunner:
    def __init__(self):
        self.client = APIClient()
        self.setup_test_data()
    
    def setup_test_data(self):
        """Set up test data"""
        print("Setting up test data...")
        
        # Create test user
        self.user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            self.user.set_password('testpass123')
            self.user.save()
        
        # Create or get API token
        self.token, created = Token.objects.get_or_create(user=self.user)
        
        # Create test county
        self.county, created = County.objects.get_or_create(
            name='nairobi',
            defaults={
                'code': '047',
                'capital_city': 'Nairobi'
            }
        )
        
        # Create test student
        self.student, created = Student.objects.get_or_create(
            user=self.user,
            defaults={
                'first_name': 'Test',
                'last_name': 'Student',
                'date_of_birth': '2000-01-01',
                'gender': 'M',
                'national_id': '12345678',
                'phone_number': '+254712345678',
                'email': 'test@example.com',
                'county': self.county,
                'sub_county': 'Westlands',
                'ward': 'Parklands',
                'current_education_level': 'undergraduate',
                'current_institution': 'Test University',
                'course_of_study': 'Computer Science',
                'year_of_study': 2,
                'expected_graduation_year': 2026,
                'family_income_annual': 500000,
                'is_verified': True
            }
        )
        
        # Create test provider
        self.provider, created = Provider.objects.get_or_create(
            name='Test Provider',
            defaults={
                'slug': 'test-provider',
                'provider_type': 'government',
                'funding_source': 'government',
                'email': 'provider@example.com',
                'phone_number': '+254712345679',
                'physical_address': 'Test Address',
                'county': self.county,
                'description': 'Test provider for scholarships',
                'is_verified': True,
                'is_active': True
            }
        )
        
        # Create test scholarship
        self.scholarship, created = Scholarship.objects.get_or_create(
            title='Test Scholarship 2025',
            defaults={
                'slug': 'test-scholarship-2025',
                'provider': self.provider,
                'scholarship_type': 'merit',
                'description': 'A test scholarship for testing purposes',
                'target_education_levels': ['undergraduate'],
                'coverage_type': 'partial',
                'amount_per_beneficiary': 200000,
                'total_budget': 2000000,
                'number_of_awards': 10,
                'application_start_date': timezone.now(),
                'application_deadline': timezone.now() + timedelta(days=90),
                'status': 'active',
                'application_method': 'online'
            }
        )
        
        # Add target counties
        self.scholarship.target_counties.add(self.county)
        
        print("Test data setup complete!")
    
    def authenticate(self):
        """Authenticate the test client"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        print(f"Authenticated with token: {self.token.key}")
    
    def test_scholarship_list(self):
        """Test scholarship list endpoint"""
        print("\n=== Testing Scholarship List ===")
        
        response = self.client.get('/scholarships/api/scholarships/')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Count: {data['count']}")
            print(f"Results: {len(data['results'])}")
            if data['results']:
                scholarship = data['results'][0]
                print(f"First scholarship: {scholarship['title']}")
                print(f"Provider verified: {scholarship['is_verified']}")
            print("✓ Scholarship list test passed")
        else:
            print(f"✗ Scholarship list test failed: {response.content}")
    
    def test_scholarship_detail(self):
        """Test scholarship detail endpoint"""
        print("\n=== Testing Scholarship Detail ===")
        
        response = self.client.get(f'/scholarships/api/scholarships/{self.scholarship.id}/')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Title: {data['title']}")
            print(f"Amount: KES {data['amount_per_beneficiary']}")
            print(f"Target counties: {len(data['target_counties'])}")
            print("✓ Scholarship detail test passed")
        else:
            print(f"✗ Scholarship detail test failed: {response.content}")
    
    def test_scholarship_filters(self):
        """Test scholarship filtering"""
        print("\n=== Testing Scholarship Filters ===")
        
        # Test county filter
        response = self.client.get(f'/scholarships/api/scholarships/?county={self.county.id}')
        print(f"County filter status: {response.status_code}")
        
        # Test education level filter
        response = self.client.get('/scholarships/api/scholarships/?education_level=undergraduate')
        print(f"Education level filter status: {response.status_code}")
        
        # Test search
        response = self.client.get('/scholarships/api/scholarships/?search=test')
        print(f"Search filter status: {response.status_code}")
        
        # Test amount range
        response = self.client.get('/scholarships/api/scholarships/?min_amount=100000&max_amount=300000')
        print(f"Amount range filter status: {response.status_code}")
        
        print("✓ Scholarship filters test completed")
    
    def test_eligibility_check(self):
        """Test eligibility check endpoint"""
        print("\n=== Testing Eligibility Check ===")
        
        # Authenticate first
        self.authenticate()
        
        response = self.client.get(f'/scholarships/api/scholarships/{self.scholarship.id}/check_eligibility/')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Match Score: {data['match_score']}")
            print(f"Is Eligible: {data['is_eligible']}")
            print(f"Has Applied: {data['has_applied']}")
            print(f"Eligibility Details: {data['eligibility_details']}")
            print("✓ Eligibility check test passed")
        else:
            print(f"✗ Eligibility check test failed: {response.content}")
    
    def test_application_creation(self):
        """Test application creation via quick apply endpoint"""
        print("\n=== Testing Application Creation ===")
        
        # Authenticate first
        self.authenticate()
        
        application_data = {
            'scholarship_id': self.scholarship.id,
            'personal_statement': 'I am passionate about computer science and believe this scholarship will help me achieve my goals.',
            'motivation_letter': 'I am motivated to study because...',
            'career_goals': 'My goal is to become a software engineer.',
            'special_circumstances': 'I come from a low-income family.',
            'reference_contacts': [
                {
                    'name': 'Dr. Jane Smith',
                    'title': 'Professor',
                    'email': 'jane.smith@university.edu',
                    'phone': '+254712345680'
                }
            ]
        }
        
        response = self.client.post(
            '/scholarships/api/apply/',
            data=json.dumps(application_data),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"Message: {data['message']}")
            print(f"Application ID: {data['application']['application_id']}")
            print(f"Status: {data['application']['status']}")
            self.created_application_id = data['application']['id']
            print("✓ Application creation test passed")
            return True
        else:
            print(f"✗ Application creation test failed: {response.content}")
            return False
    
    def test_application_list(self):
        """Test application list endpoint"""
        print("\n=== Testing Application List ===")
        
        # Authenticate first
        self.authenticate()
        
        response = self.client.get('/scholarships/api/applications/')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Count: {data['count']}")
            print(f"Results: {len(data['results'])}")
            if data['results']:
                app = data['results'][0]
                print(f"First application: {app['application_id']}")
                print(f"Status: {app['status']}")
                print(f"Scholarship: {app['scholarship']['title']}")
            print("✓ Application list test passed")
        else:
            print(f"✗ Application list test failed: {response.content}")
    
    def test_application_submission(self):
        """Test application submission"""
        print("\n=== Testing Application Submission ===")
        
        if not hasattr(self, 'created_application_id'):
            print("Skipping submission test - no application created")
            return
        
        # Authenticate first
        self.authenticate()
        
        response = self.client.post(f'/scholarships/api/applications/{self.created_application_id}/submit/')
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Message: {data['detail']}")
            print("✓ Application submission test passed")
        else:
            print(f"✗ Application submission test failed: {response.content}")
    
    def test_duplicate_application(self):
        """Test duplicate application prevention"""
        print("\n=== Testing Duplicate Application Prevention ===")
        
        # Authenticate first
        self.authenticate()
        
        application_data = {
            'scholarship_id': self.scholarship.id,
            'personal_statement': 'Another application for the same scholarship.',
            'motivation_letter': 'Testing duplicate prevention.',
            'career_goals': 'Same goals as before.'
        }
        
        response = self.client.post(
            '/scholarships/api/apply/',
            data=json.dumps(application_data),
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✓ Duplicate application correctly prevented")
        else:
            print(f"✗ Duplicate application test failed: {response.content}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting API Tests for Tuvuke Hub")
        print("=" * 50)
        
        try:
            # Test without authentication
            self.test_scholarship_list()
            self.test_scholarship_detail()
            self.test_scholarship_filters()
            
            # Test with authentication
            self.test_eligibility_check()
            
            # Test application creation and management
            if self.test_application_creation():
                self.test_application_list()
                self.test_application_submission()
                self.test_duplicate_application()
            
            print("\n" + "=" * 50)
            print("🎉 API Tests Completed!")
            print("\nNext Steps:")
            print("1. Test SMS functionality by updating application status in Django admin")
            print("2. Try the API endpoints in a browser: http://localhost:8000/scholarships/api/")
            print("3. Use Postman or curl to test with your own data")
            print(f"\nYour API token: {self.token.key}")
            
        except Exception as e:
            print(f"\n💥 Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    # Check if Django is properly configured
    try:
        from django.conf import settings
        if not settings.configured:
            print("Django is not properly configured!")
            sys.exit(1)
    except Exception as e:
        print(f"Error with Django configuration: {e}")
        sys.exit(1)
    
    # Run tests
    test_runner = APITestRunner()
    test_runner.run_all_tests()
