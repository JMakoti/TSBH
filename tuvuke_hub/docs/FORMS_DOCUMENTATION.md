# Django Forms Documentation - Student Registration System

## Overview
This document describes the Django forms created for the Tuvuke Hub scholarship management system, specifically focusing on student registration and profile management.

## Form Classes

### 1. StudentRegistrationForm
**Purpose**: Complete student registration form that creates both User and Student profile records.

**Inheritance**: Extends `UserCreationForm`

**Key Features**:
- ✅ **Complete Profile Creation**: Creates both Django User and Student profile
- ✅ **Comprehensive Validation**: Phone numbers, National ID, age verification
- ✅ **Phone Number Normalization**: Converts local format to international (+254)
- ✅ **Duplicate Prevention**: Checks for existing emails, National IDs, phone numbers
- ✅ **Cross-field Validation**: Academic requirements based on education level
- ✅ **Bootstrap Classes**: Ready-to-use CSS classes for styling

#### Form Sections:

**A. User Authentication**
```python
# User account fields
username = forms.CharField(...)
email = forms.EmailField(...)
password1 = forms.CharField(...)
password2 = forms.CharField(...)
```

**B. Personal Information**
```python
# Personal details
first_name, last_name, other_names
date_of_birth  # Age validation (minimum 15 years)
gender         # Male/Female/Other
national_id    # 8-digit validation + uniqueness
```

**C. Contact Information**
```python
# Contact details
phone_number       # +254XXXXXXXXX format, uniqueness check
alternative_phone  # Optional, same format validation
```

**D. Location Information**
```python
# Geographic information
county         # ForeignKey to County model
sub_county     # Text field
ward           # Text field
location       # Optional village/area
postal_address # Optional textarea
```

**E. Education Information**
```python
# Academic details
current_education_level  # Choice field
current_institution     # Current school/university
course_of_study        # Program/course name
year_of_study          # 1-10 range
expected_graduation_year # Future year validation
```

**F. Academic Performance**
```python
# Performance metrics
previous_gpa        # 0.0-4.0 scale (optional)
previous_percentage # 0-100% scale (optional)
```

**G. Financial Information**
```python
# Financial background
family_income_annual # Annual income in KES
number_of_dependents # Number of dependents
```

**H. Special Circumstances**
```python
# Special considerations
disability_status          # Choice field
is_orphan                 # Boolean
is_single_parent_child    # Boolean
is_child_headed_household # Boolean
```

**I. Profile Photo**
```python
# Optional image upload
profile_photo # ImageField with file type validation
```

#### Validation Rules:

**Phone Number Validation**:
```python
def clean_phone_number(self):
    # Normalizes: 0712345678 → +254712345678
    # Validates: Must match +254XXXXXXXXX pattern
    # Checks: Uniqueness in database
    return normalized_phone_number
```

**National ID Validation**:
```python
def clean_national_id(self):
    # Format: Must be exactly 8 digits
    # Uniqueness: Cannot already exist
    # Pattern: Numeric only
    return national_id
```

**Age Validation**:
```python
def clean_date_of_birth(self):
    # Minimum age: 15 years
    # Maximum age: 100 years (sanity check)
    # Calculates age considering month/day
    return date_of_birth
```

**Cross-field Validation**:
```python
def clean(self):
    # For postgraduate/PhD: Requires GPA or percentage
    # Year of study must match education level
    # Expected graduation year must be in future
    return cleaned_data
```

#### Usage Example:
```python
# In views.py
from scholarships.forms import StudentRegistrationForm

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # Creates User + Student profile
            login(request, user)
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'register.html', {'form': form})
```

### 2. StudentProfileUpdateForm
**Purpose**: Update existing student profile information (excludes sensitive fields).

**Inheritance**: Extends `ModelForm`

**Key Features**:
- ✅ **Excludes Sensitive Fields**: No username, password, National ID changes
- ✅ **Uniqueness Validation**: Phone number uniqueness excluding current student
- ✅ **Same Validation Logic**: Reuses phone number normalization
- ✅ **Partial Updates**: Only specified fields can be updated

#### Excluded Fields:
- User credentials (username, password)
- National ID (permanent identifier)
- Date of birth (permanent)
- Gender (requires verification)
- Email (linked to user account)

#### Usage Example:
```python
def update_profile(request):
    student = request.user.student_profile
    if request.method == 'POST':
        form = StudentProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=student
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = StudentProfileUpdateForm(instance=student)
    
    return render(request, 'update_profile.html', {'form': form})
```

### 3. QuickRegistrationForm
**Purpose**: Simplified registration form with minimal required fields.

**Inheritance**: Extends `Form`

**Key Features**:
- ✅ **Minimal Fields**: Only essential information required
- ✅ **Quick Setup**: Faster registration process
- ✅ **Same Validation**: Phone number and National ID validation
- ✅ **Profile Completion**: Can be completed later

#### Fields Included:
```python
# Essential fields only
username, email, password1, password2
first_name, last_name
national_id, phone_number
county, current_education_level
```

#### Usage Scenario:
- Mobile app registration
- Quick signup campaigns
- Emergency registration
- Bulk registration events

### 4. StudentSearchForm
**Purpose**: Advanced search form for finding students with multiple criteria.

**Key Features**:
- ✅ **Multiple Filters**: Name, county, education level, gender
- ✅ **Age Range**: Minimum and maximum age filters
- ✅ **Verification Status**: Filter by verified/unverified students
- ✅ **Flexible Search**: Text search across multiple fields

#### Usage Example:
```python
def search_students(request):
    form = StudentSearchForm(request.GET)
    students = Student.objects.all()
    
    if form.is_valid():
        if form.cleaned_data['search_query']:
            students = students.filter(
                Q(first_name__icontains=form.cleaned_data['search_query']) |
                Q(last_name__icontains=form.cleaned_data['search_query']) |
                Q(national_id__icontains=form.cleaned_data['search_query'])
            )
        
        if form.cleaned_data['county']:
            students = students.filter(county=form.cleaned_data['county'])
        
        # Additional filters...
    
    return render(request, 'search_students.html', {
        'form': form,
        'students': students
    })
```

## Form Validation Features

### Phone Number Normalization
**Converts various formats to standard international format**:
```python
Input Formats:          Output:
0712345678         →   +254712345678
254712345678       →   +254712345678
+254712345678      →   +254712345678
```

### Validation Error Messages
**User-friendly error messages for common issues**:
```python
# National ID errors
"National ID must be exactly 8 digits."
"A student with this National ID already exists."

# Phone number errors
"Phone number must be in format +254XXXXXXXXX"
"A student with this phone number already exists."

# Age errors
"You must be at least 15 years old to register."

# Email errors
"A user with this email already exists."
```

### Cross-field Validation Examples
```python
# Academic requirements
if education_level in ['postgraduate', 'phd']:
    if not gpa and not percentage:
        raise ValidationError(
            "Please provide either GPA or percentage score."
        )

# Phone number consistency
if alternative_phone == primary_phone:
    raise ValidationError(
        "Alternative phone must be different from primary phone."
    )
```

## HTML Template Integration

### Bootstrap-Ready Forms
All forms include Bootstrap CSS classes:
```html
<!-- Form fields automatically include Bootstrap classes -->
<div class="mb-3">
    {{ form.first_name.label_tag }}
    {{ form.first_name }}  <!-- class="form-control" already included -->
    {% if form.first_name.errors %}
        <div class="text-danger">{{ form.first_name.errors }}</div>
    {% endif %}
</div>
```

### Form Sections in Templates
```html
<!-- Personal Information Section -->
<div class="card mb-4">
    <div class="card-header">
        <h5>Personal Information</h5>
    </div>
    <div class="card-body">
        <div class="row">
            <div class="col-md-4">{{ form.first_name|add_class:"form-control" }}</div>
            <div class="col-md-4">{{ form.last_name|add_class:"form-control" }}</div>
            <div class="col-md-4">{{ form.other_names|add_class:"form-control" }}</div>
        </div>
    </div>
</div>
```

### JavaScript Integration
```javascript
// Phone number formatting
document.getElementById('id_phone_number').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.startsWith('0')) {
        value = '254' + value.slice(1);
    }
    e.target.value = '+' + value;
});

// County-based sub-county loading
document.getElementById('id_county').addEventListener('change', function(e) {
    // AJAX call to load sub-counties
    loadSubCounties(e.target.value);
});
```

## Testing

### Form Test Coverage
- ✅ Valid form submission
- ✅ Invalid field validation
- ✅ Duplicate detection
- ✅ Phone number normalization
- ✅ Age validation
- ✅ Cross-field validation
- ✅ Form save functionality

### Test Example:
```python
class StudentRegistrationFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            # ... other fields
        }
        form = StudentRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertIsInstance(user, User)
        self.assertTrue(hasattr(user, 'student_profile'))
```

## Security Considerations

### Data Protection
- ✅ **Phone Number Normalization**: Prevents format variations
- ✅ **Duplicate Prevention**: Ensures data integrity
- ✅ **Input Validation**: Prevents malicious input
- ✅ **File Upload Validation**: Image files only for profile photos

### Privacy Features
- ✅ **Sensitive Field Protection**: Update form excludes permanent identifiers
- ✅ **Optional Fields**: Personal details are optional where appropriate
- ✅ **Validation Messages**: Don't reveal sensitive information

## Performance Optimizations

### Database Queries
- ✅ **Efficient Uniqueness Checks**: Uses database-level constraints
- ✅ **County Queryset**: Optimized for dropdown loading
- ✅ **Bulk Validation**: Cross-field validation in single clean() method

### Form Rendering
- ✅ **CSS Classes**: Pre-configured for faster frontend development
- ✅ **Field Ordering**: Logical flow for better user experience
- ✅ **Conditional Fields**: Academic requirements based on education level

This comprehensive form system provides a robust foundation for student registration and profile management in the scholarship system.
