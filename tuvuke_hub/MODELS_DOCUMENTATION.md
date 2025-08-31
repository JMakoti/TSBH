# Django Models Documentation - Scholarship Management System

## Overview
This document describes the Django models designed for the Tuvuke Hub scholarship management system. The models are designed to handle scholarship opportunities, applications, and the complete scholarship lifecycle.

## Model Relationships

```
User (Django's built-in)
├── Student (OneToOne)
├── Provider (created_by)
├── Scholarship (created_by)
├── Application (decision_made_by)
├── Document (verified_by)
├── Disbursement (processed_by)
├── Notification (recipient)
└── AuditLog (user)

County
├── Student (ForeignKey)
├── Provider (ForeignKey)
└── Scholarship (ManyToMany - target_counties)

Provider
└── Scholarship (ForeignKey)

Student
└── Application (ForeignKey)

Scholarship
├── Application (ForeignKey)
└── Notification (related_scholarship)

Application
├── Document (ForeignKey)
├── Disbursement (ForeignKey)
└── Notification (related_application)
```

## Core Models

### 1. County
Represents the 47 Kenyan counties.

**Key Fields:**
- `name`: CharField with county choices
- `code`: Unique county code
- `population`: County population
- `area_sq_km`: County area
- `capital_city`: County headquarters

**Purpose:** Geographic organization and targeting of scholarships.

### 2. Student
Represents scholarship applicants with comprehensive profile information.

**Key Fields:**
- `user`: OneToOne link to Django User
- `student_id`: UUID for unique identification
- `national_id`: Kenyan National ID (8 digits)
- `phone_number`: Kenyan format (+254XXXXXXXXX)
- `county`: Foreign key to County
- `current_education_level`: Current level of study
- `family_income_annual`: Annual family income
- `disability_status`: Disability status
- `is_orphan`: Orphan status
- `is_verified`: Account verification status

**Special Features:**
- Automatic age calculation
- Full name property
- Validation for Kenyan phone numbers and National ID

### 3. Provider
Represents organizations offering scholarships.

**Key Fields:**
- `name`: Organization name
- `provider_type`: Type of organization (government, NGO, etc.)
- `funding_source`: Source of funding
- `county`: Location
- `total_annual_budget`: Total annual budget
- `scholarship_budget_annual`: Annual scholarship budget
- `is_verified`: Verification status

**Provider Types:**
- Government
- Non-Governmental Organization
- Private Company
- Foundation
- International Organization
- Religious Organization
- Educational Institution
- Individual Donor

### 4. Scholarship
Represents scholarship opportunities with detailed criteria and requirements.

**Key Fields:**
- `title`: Scholarship title
- `provider`: Foreign key to Provider
- `scholarship_type`: Type of scholarship
- `description`: Detailed description
- `eligibility_criteria`: JSON field for criteria
- `target_counties`: ManyToMany to Counties
- `amount_per_beneficiary`: Award amount
- `number_of_awards`: Available awards
- `application_deadline`: Deadline for applications
- `minimum_gpa`: Minimum GPA requirement
- `maximum_family_income`: Income ceiling

**Scholarship Types:**
- Merit-based
- Need-based
- Merit and Need-based
- Research
- Athletic
- Arts/Creative
- Minority/Diversity
- Regional/County-specific
- Professional Development
- Emergency/Hardship

**Key Methods:**
- `is_active`: Check if accepting applications
- `days_until_deadline`: Days remaining
- `increment_view_count()`: Track views
- `increment_application_count()`: Track applications

### 5. Application
Represents student applications for scholarships.

**Key Fields:**
- `application_id`: UUID for unique identification
- `student`: Foreign key to Student
- `scholarship`: Foreign key to Scholarship
- `status`: Application status
- `personal_statement`: Required essay
- `evaluation_score`: Overall score
- `award_amount`: Awarded amount (if approved)
- `disbursement_schedule`: JSON field for payment schedule

**Application Statuses:**
- Draft
- Submitted
- Under Review
- Shortlisted
- Interview Scheduled
- Interview Completed
- Approved
- Rejected
- Waitlisted
- Withdrawn
- Expired

**Key Methods:**
- `submit_application()`: Submit draft application
- `can_be_edited`: Check if editable
- `is_successful`: Check if approved
- `days_since_submission`: Track time since submission

## Supporting Models

### 6. Document
Manages file uploads for applications.

**Key Fields:**
- `application`: Foreign key to Application
- `document_type`: Type of document
- `file`: File upload
- `is_verified`: Verification status

**Document Types:**
- Academic Transcript
- Birth Certificate
- National ID Copy
- Passport Photo
- Recommendation Letter
- Financial Statement
- Bank Statement
- Admission Letter
- Fee Structure
- Disability Certificate
- Death Certificate
- Affidavit
- Other

### 7. Disbursement
Tracks scholarship payments.

**Key Fields:**
- `application`: Foreign key to Application
- `amount`: Disbursement amount
- `disbursement_date`: Payment date
- `method`: Payment method
- `status`: Payment status
- `reference_number`: Transaction reference

**Disbursement Methods:**
- Bank Transfer
- Mobile Money
- Cheque
- Cash
- Direct Payment to Institution

### 8. Notification
System notifications for users.

**Key Fields:**
- `recipient`: Foreign key to User
- `notification_type`: Type of notification
- `message`: Notification content
- `is_read`: Read status
- `related_application`: Link to application
- `related_scholarship`: Link to scholarship

### 9. AuditLog
Tracks system activities for security and compliance.

**Key Fields:**
- `user`: User who performed action
- `action`: Type of action (create, update, delete, view)
- `model_name`: Model affected
- `changes`: JSON of changes made
- `ip_address`: User's IP address
- `timestamp`: When action occurred

## JSON Field Structures

### Eligibility Criteria (Scholarship)
```json
{
  "minimum_age": 18,
  "maximum_age": 35,
  "required_documents": ["transcript", "id_copy"],
  "academic_requirements": {
    "minimum_gpa": 3.0,
    "required_subjects": ["Mathematics", "English"]
  },
  "special_requirements": {
    "community_service": true,
    "leadership_experience": true
  }
}
```

### Reference Contacts (Application)
```json
[
  {
    "name": "Dr. Jane Smith",
    "title": "Professor",
    "institution": "University of Nairobi",
    "phone": "+254712345678",
    "email": "jane.smith@uon.ac.ke"
  }
]
```

### Disbursement Schedule (Application)
```json
[
  {
    "installment": 1,
    "amount": 50000,
    "due_date": "2024-02-01",
    "status": "pending"
  },
  {
    "installment": 2,
    "amount": 50000,
    "due_date": "2024-08-01",
    "status": "scheduled"
  }
]
```

## Key Features

### 1. Data Validation
- Kenyan phone number format validation
- National ID format validation (8 digits)
- GPA and percentage range validation
- Age and income validation

### 2. Automatic Calculations
- Student age from date of birth
- Days until scholarship deadline
- Days since application submission
- Total disbursed amounts

### 3. Status Tracking
- Application lifecycle management
- Disbursement status tracking
- Verification status for students and providers

### 4. Audit Trail
- Complete audit log of system activities
- Change tracking for all models
- User action monitoring

### 5. Flexible Configuration
- JSON fields for dynamic criteria
- Configurable document requirements
- Flexible disbursement schedules

## Database Indexes
Strategic indexes are placed on:
- Application status and submission dates
- Scholarship types and deadlines
- User activities in audit logs
- Provider and student relationships

## Security Considerations
- UUIDs for public-facing identifiers
- Audit logging for compliance
- Document verification workflow
- User permission integration points

This model structure provides a robust foundation for managing the complete scholarship lifecycle from opportunity creation to disbursement tracking.
