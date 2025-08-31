# Django REST Framework API Documentation

This document provides comprehensive documentation for the Tuvuke Hub scholarship management API.

## Table of Contents

1. [Authentication](#authentication)
2. [API Endpoints](#api-endpoints)
3. [Scholarship API](#scholarship-api)
4. [Application API](#application-api)
5. [SMS Integration](#sms-integration)
6. [Filtering and Search](#filtering-and-search)
7. [Error Handling](#error-handling)
8. [Examples](#examples)

## Authentication

The API uses Django REST Framework's Token Authentication.

### Getting a Token

1. **Admin Method**: Use the management command
   ```bash
   python manage.py create_api_tokens --username your_username
   ```

2. **Programmatic Method**: Create tokens via Django admin or shell
   ```python
   from rest_framework.authtoken.models import Token
   from django.contrib.auth.models import User
   
   user = User.objects.get(username='your_username')
   token, created = Token.objects.get_or_create(user=user)
   print(f"Token: {token.key}")
   ```

### Using the Token

Include the token in your request headers:

```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" http://localhost:8000/scholarships/api/scholarships/
```

## API Endpoints

### Base URL
- Development: `http://localhost:8000/scholarships/api/`
- Production: `https://your-domain.com/scholarships/api/`

### Available Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/api/scholarships/` | List scholarships | Optional |
| GET | `/api/scholarships/{id}/` | Get scholarship details | Optional |
| GET | `/api/scholarships/{id}/check_eligibility/` | Check eligibility | Required |
| GET | `/api/applications/` | List user's applications | Required |
| POST | `/api/applications/` | Create application | Required |
| GET | `/api/applications/{id}/` | Get application details | Required |
| PATCH | `/api/applications/{id}/` | Update application | Required |
| POST | `/api/applications/{id}/submit/` | Submit application | Required |
| POST | `/api/applications/{id}/withdraw/` | Withdraw application | Required |
| POST | `/api/apply/` | Quick apply to scholarship | Required |

## Scholarship API

### List Scholarships

**GET** `/api/scholarships/`

Returns a paginated list of active scholarships from verified providers.

#### Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `county` | int[] | Filter by county IDs | `?county=1,2,3` |
| `education_level` | string | Filter by education level | `?education_level=undergraduate` |
| `gender` | string | Filter by gender (M/F/A) | `?gender=F` |
| `scholarship_type` | string | Filter by type | `?scholarship_type=merit` |
| `provider_type` | string | Filter by provider type | `?provider_type=government` |
| `min_amount` | number | Minimum amount | `?min_amount=50000` |
| `max_amount` | number | Maximum amount | `?max_amount=500000` |
| `deadline_after` | datetime | Deadline after date | `?deadline_after=2025-12-31` |
| `for_orphans` | boolean | Orphans only | `?for_orphans=true` |
| `for_disabled` | boolean | Disabled students only | `?for_disabled=true` |
| `search` | string | Search in multiple fields | `?search=engineering` |
| `coverage_type` | string | Coverage type | `?coverage_type=full` |
| `is_featured` | boolean | Featured scholarships | `?is_featured=true` |
| `ordering` | string | Order results | `?ordering=-created_at` |

#### Response Example

```json
{
  "count": 25,
  "next": "http://localhost:8000/scholarships/api/scholarships/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Kenya Government Scholarship 2025",
      "slug": "kenya-government-scholarship-2025",
      "provider": {
        "id": 1,
        "name": "Ministry of Education",
        "provider_type": "government",
        "is_verified": true
      },
      "scholarship_type": "merit",
      "description": "Full scholarship for undergraduate students...",
      "target_education_levels": ["undergraduate"],
      "target_counties": [
        {
          "id": 1,
          "name": "nairobi",
          "code": "047",
          "capital_city": "Nairobi"
        }
      ],
      "amount_per_beneficiary": "200000.00",
      "number_of_awards": 50,
      "application_deadline": "2025-12-31T23:59:59Z",
      "is_verified": true,
      "days_until_deadline": 120,
      "created_at": "2025-08-31T10:00:00Z"
    }
  ]
}
```

### Get Scholarship Details

**GET** `/api/scholarships/{id}/`

Returns detailed information about a specific scholarship.

#### Response Example

```json
{
  "id": 1,
  "title": "Kenya Government Scholarship 2025",
  "eligibility_criteria": {
    "minimum_gpa": 3.0,
    "maximum_family_income": 100000,
    "required_documents": ["transcript", "recommendation"]
  },
  "required_documents": [
    "academic_transcript",
    "recommendation_letter",
    "national_id"
  ],
  "total_budget": "10000000.00",
  "renewable": true,
  "source": "manual",
  // ... other fields
}
```

### Check Eligibility

**GET** `/api/scholarships/{id}/check_eligibility/`

Checks if the authenticated student is eligible for a scholarship.

**Requires Authentication**

#### Response Example

```json
{
  "match_score": 85.5,
  "has_applied": false,
  "is_eligible": true,
  "eligibility_details": {
    "education_level_match": true,
    "age_requirements_met": true,
    "gender_requirements_met": true,
    "county_match": true
  }
}
```

## Application API

### List Applications

**GET** `/api/applications/`

Returns the authenticated student's applications.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status |
| `scholarship` | int | Filter by scholarship ID |
| `submission_date_after` | datetime | Submitted after date |
| `submission_date_before` | datetime | Submitted before date |

#### Response Example

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "application_id": "550e8400-e29b-41d4-a716-446655440000",
      "student": {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com"
      },
      "scholarship": {
        "id": 1,
        "title": "Kenya Government Scholarship 2025"
      },
      "status": "submitted",
      "submission_date": "2025-08-31T10:00:00Z",
      "personal_statement": "I am passionate about...",
      "can_be_edited": false,
      "is_successful": false,
      "days_since_submission": 5
    }
  ]
}
```

### Create Application

**POST** `/api/applications/`

Creates a new scholarship application.

#### Request Body

```json
{
  "scholarship": 1,
  "personal_statement": "I am passionate about engineering...",
  "motivation_letter": "I want to study at this university because...",
  "career_goals": "My goal is to become a software engineer...",
  "special_circumstances": "I come from a single-parent household...",
  "reference_contacts": [
    {
      "name": "Dr. Jane Smith",
      "title": "Professor",
      "email": "jane.smith@university.edu",
      "phone": "+254712345678"
    }
  ]
}
```

#### Response

```json
{
  "id": 1,
  "application_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "draft",
  "created_at": "2025-08-31T10:00:00Z"
}
```

### Submit Application

**POST** `/api/applications/{id}/submit/`

Submits a draft application.

#### Response

```json
{
  "detail": "Application submitted successfully"
}
```

### Withdraw Application

**POST** `/api/applications/{id}/withdraw/`

Withdraws an application (only if not yet decided).

#### Response

```json
{
  "detail": "Application withdrawn successfully"
}
```

## Quick Apply Endpoint

### Apply to Scholarship

**POST** `/api/apply/`

Quick application endpoint that creates an application in one request.

#### Request Body

```json
{
  "scholarship_id": 1,
  "personal_statement": "I am passionate about engineering...",
  "motivation_letter": "I want to study at this university because...",
  "career_goals": "My goal is to become a software engineer...",
  "special_circumstances": "I come from a single-parent household...",
  "reference_contacts": [
    {
      "name": "Dr. Jane Smith",
      "title": "Professor",
      "email": "jane.smith@university.edu",
      "phone": "+254712345678"
    }
  ]
}
```

#### Response

```json
{
  "message": "Application created successfully",
  "application": {
    "id": 1,
    "application_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "draft",
    "scholarship": {
      "id": 1,
      "title": "Kenya Government Scholarship 2025"
    }
  }
}
```

## SMS Integration

The API automatically sends SMS notifications when application statuses change.

### Supported Status Changes

- `submitted`: Application submitted successfully
- `under_review`: Application is under review
- `shortlisted`: Student has been shortlisted
- `interview_scheduled`: Interview scheduled
- `approved`: Application approved (with award amount)
- `rejected`: Application rejected
- `waitlisted`: Application waitlisted

### SMS Configuration

Add to your `.env` file:

```env
AFRICASTALKING_USERNAME=your_username
AFRICASTALKING_API_KEY=your_api_key
```

### Manual SMS Sending

```python
from scholarships.sms import send_sms

result = send_sms(
    phone_number="+254712345678",
    message="Your application has been approved!"
)

if result['success']:
    print("SMS sent successfully")
else:
    print(f"Failed to send SMS: {result['error']}")
```

## Error Handling

### Common Error Responses

#### 400 Bad Request

```json
{
  "error": "scholarship_id is required"
}
```

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 404 Not Found

```json
{
  "error": "Scholarship not found or not available"
}
```

#### 422 Validation Error

```json
{
  "personal_statement": ["This field is required."],
  "scholarship": ["You have already applied for this scholarship"]
}
```

## Examples

### Complete Application Flow

```python
import requests

# Base URL
base_url = "http://localhost:8000/scholarships/api"
headers = {"Authorization": "Token YOUR_TOKEN_HERE"}

# 1. List available scholarships
response = requests.get(f"{base_url}/scholarships/", headers=headers)
scholarships = response.json()

# 2. Check eligibility for a scholarship
scholarship_id = scholarships['results'][0]['id']
response = requests.get(
    f"{base_url}/scholarships/{scholarship_id}/check_eligibility/",
    headers=headers
)
eligibility = response.json()

if eligibility['is_eligible'] and not eligibility['has_applied']:
    # 3. Apply for the scholarship
    application_data = {
        "scholarship_id": scholarship_id,
        "personal_statement": "I am passionate about my field of study...",
        "motivation_letter": "I believe this scholarship will help me...",
        "career_goals": "My career goal is to...",
        "reference_contacts": [
            {
                "name": "Dr. John Smith",
                "title": "Professor",
                "email": "john.smith@university.edu",
                "phone": "+254712345678"
            }
        ]
    }
    
    response = requests.post(
        f"{base_url}/apply/",
        json=application_data,
        headers=headers
    )
    
    if response.status_code == 201:
        application = response.json()
        print(f"Application created: {application['application']['application_id']}")
        
        # 4. Submit the application
        app_id = application['application']['id']
        response = requests.post(
            f"{base_url}/applications/{app_id}/submit/",
            headers=headers
        )
        
        if response.status_code == 200:
            print("Application submitted successfully!")
```

### Filtering Scholarships

```python
# Get scholarships for female undergraduate students in Nairobi
params = {
    'gender': 'F',
    'education_level': 'undergraduate',
    'county': '30',  # Nairobi county ID
    'min_amount': '100000',
    'is_featured': 'true',
    'ordering': '-amount_per_beneficiary'
}

response = requests.get(
    f"{base_url}/scholarships/",
    params=params,
    headers=headers
)

scholarships = response.json()
```

### Checking Application Status

```python
# Get all applications for the authenticated user
response = requests.get(f"{base_url}/applications/", headers=headers)
applications = response.json()

for app in applications['results']:
    print(f"Application {app['application_id']}: {app['status']}")
    if app['status'] == 'approved':
        print(f"Award amount: KES {app['award_amount']}")
```

## Rate Limiting

The API implements basic rate limiting:

- Anonymous users: 100 requests per hour
- Authenticated users: 1000 requests per hour
- Bulk operations: 10 requests per minute

## Pagination

All list endpoints support pagination with the following parameters:

- `page`: Page number (default: 1)
- `page_size`: Number of results per page (max: 100, default: 20)

## Testing

Use the Django REST Framework browsable API for testing:

1. Visit `http://localhost:8000/scholarships/api/` in your browser
2. Login using your Django credentials
3. Browse and test API endpoints interactively

For automated testing, you can use tools like:

- Postman
- curl
- Python requests library
- Django REST Framework test client
