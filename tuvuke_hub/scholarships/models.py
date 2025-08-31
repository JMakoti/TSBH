from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class County(models.Model):
    """Model representing Kenyan counties"""
    
    COUNTY_CHOICES = [
        ('baringo', 'Baringo'),
        ('bomet', 'Bomet'),
        ('bungoma', 'Bungoma'),
        ('busia', 'Busia'),
        ('elgeyo_marakwet', 'Elgeyo Marakwet'),
        ('embu', 'Embu'),
        ('garissa', 'Garissa'),
        ('homa_bay', 'Homa Bay'),
        ('isiolo', 'Isiolo'),
        ('kajiado', 'Kajiado'),
        ('kakamega', 'Kakamega'),
        ('kericho', 'Kericho'),
        ('kiambu', 'Kiambu'),
        ('kilifi', 'Kilifi'),
        ('kirinyaga', 'Kirinyaga'),
        ('kisii', 'Kisii'),
        ('kisumu', 'Kisumu'),
        ('kitui', 'Kitui'),
        ('kwale', 'Kwale'),
        ('laikipia', 'Laikipia'),
        ('lamu', 'Lamu'),
        ('machakos', 'Machakos'),
        ('makueni', 'Makueni'),
        ('mandera', 'Mandera'),
        ('marsabit', 'Marsabit'),
        ('meru', 'Meru'),
        ('migori', 'Migori'),
        ('mombasa', 'Mombasa'),
        ('murang\'a', 'Murang\'a'),
        ('nairobi', 'Nairobi'),
        ('nakuru', 'Nakuru'),
        ('nandi', 'Nandi'),
        ('narok', 'Narok'),
        ('nyamira', 'Nyamira'),
        ('nyandarua', 'Nyandarua'),
        ('nyeri', 'Nyeri'),
        ('samburu', 'Samburu'),
        ('siaya', 'Siaya'),
        ('taita_taveta', 'Taita Taveta'),
        ('tana_river', 'Tana River'),
        ('tharaka_nithi', 'Tharaka Nithi'),
        ('trans_nzoia', 'Trans Nzoia'),
        ('turkana', 'Turkana'),
        ('uasin_gishu', 'Uasin Gishu'),
        ('vihiga', 'Vihiga'),
        ('wajir', 'Wajir'),
        ('west_pokot', 'West Pokot'),
    ]
    
    name = models.CharField(
        max_length=50,
        choices=COUNTY_CHOICES,
        unique=True,
        help_text="Kenyan county name"
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="County code (e.g., 001 for Mombasa)"
    )
    population = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="County population"
    )
    area_sq_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="County area in square kilometers"
    )
    capital_city = models.CharField(
        max_length=100,
        help_text="County capital/headquarters"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "County"
        verbose_name_plural = "Counties"
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()


class Student(models.Model):
    """Model representing scholarship applicants/students"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    EDUCATION_LEVEL_CHOICES = [
        ('primary', 'Primary School'),
        ('secondary', 'Secondary School'),
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
        ('phd', 'PhD'),
    ]
    
    DISABILITY_STATUS_CHOICES = [
        ('none', 'No Disability'),
        ('physical', 'Physical Disability'),
        ('visual', 'Visual Impairment'),
        ('hearing', 'Hearing Impairment'),
        ('intellectual', 'Intellectual Disability'),
        ('multiple', 'Multiple Disabilities'),
    ]
    
    # Basic Information
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique student identifier"
    )
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    national_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{8}$',
            message="National ID must be 8 digits"
        )],
        help_text="Kenyan National ID number"
    )
    
    # Contact Information
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?254[0-9]{9}$',
            message="Phone number must be in format +254XXXXXXXXX"
        )]
    )
    email = models.EmailField()
    alternative_phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?254[0-9]{9}$',
            message="Phone number must be in format +254XXXXXXXXX"
        )]
    )
    
    # Location Information
    county = models.ForeignKey(
        County,
        on_delete=models.SET_NULL,
        null=True,
        related_name='students'
    )
    sub_county = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    postal_address = models.TextField(blank=True)
    
    # Education Information
    current_education_level = models.CharField(
        max_length=20,
        choices=EDUCATION_LEVEL_CHOICES
    )
    current_institution = models.CharField(max_length=200)
    course_of_study = models.CharField(max_length=200)
    year_of_study = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    expected_graduation_year = models.PositiveIntegerField()
    
    # Academic Performance
    previous_gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(4.0)],
        help_text="GPA on a 4.0 scale"
    )
    previous_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage score"
    )
    
    # Financial Information
    family_income_annual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Annual family income in KES"
    )
    number_of_dependents = models.PositiveIntegerField(default=0)
    
    # Special Circumstances
    disability_status = models.CharField(
        max_length=20,
        choices=DISABILITY_STATUS_CHOICES,
        default='none'
    )
    is_orphan = models.BooleanField(default=False)
    is_single_parent_child = models.BooleanField(default=False)
    is_child_headed_household = models.BooleanField(default=False)
    
    # Documents
    profile_photo = models.ImageField(
        upload_to='student_photos/',
        null=True,
        blank=True
    )
    
    # Metadata
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.national_id})"
    
    @property
    def full_name(self):
        """Return full name of the student"""
        names = [self.first_name]
        if self.other_names:
            names.append(self.other_names)
        names.append(self.last_name)
        return " ".join(names)
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class Provider(models.Model):
    """Model representing scholarship providers/organizations"""
    
    PROVIDER_TYPE_CHOICES = [
        ('government', 'Government'),
        ('ngo', 'Non-Governmental Organization'),
        ('private_company', 'Private Company'),
        ('foundation', 'Foundation'),
        ('international', 'International Organization'),
        ('religious', 'Religious Organization'),
        ('educational', 'Educational Institution'),
        ('individual', 'Individual Donor'),
    ]
    
    FUNDING_SOURCE_CHOICES = [
        ('government', 'Government Funded'),
        ('private', 'Private Funded'),
        ('donor', 'Donor Funded'),
        ('mixed', 'Mixed Funding'),
        ('endowment', 'Endowment Fund'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True)
    provider_type = models.CharField(
        max_length=20,
        choices=PROVIDER_TYPE_CHOICES
    )
    funding_source = models.CharField(
        max_length=20,
        choices=FUNDING_SOURCE_CHOICES
    )
    
    # Contact Information
    email = models.EmailField()
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?254[0-9]{9}$',
            message="Phone number must be in format +254XXXXXXXXX"
        )]
    )
    website = models.URLField(blank=True)
    
    # Location Information
    physical_address = models.TextField()
    postal_address = models.TextField(blank=True)
    county = models.ForeignKey(
        County,
        on_delete=models.SET_NULL,
        null=True,
        related_name='scholarship_providers'
    )
    
    # Organization Details
    description = models.TextField(
        help_text="Brief description of the organization"
    )
    mission_statement = models.TextField(blank=True)
    established_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when organization was established"
    )
    registration_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Official registration number"
    )
    
    # Financial Information
    total_annual_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total annual budget in KES"
    )
    scholarship_budget_annual = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual scholarship budget in KES"
    )
    
    # Media
    logo = models.ImageField(
        upload_to='provider_logos/',
        null=True,
        blank=True
    )
    
    # Status and Verification
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Provider"
        verbose_name_plural = "Providers"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Scholarship(models.Model):
    """Model representing scholarship opportunities"""
    
    SCHOLARSHIP_TYPE_CHOICES = [
        ('merit', 'Merit-based'),
        ('need', 'Need-based'),
        ('merit_need', 'Merit and Need-based'),
        ('research', 'Research'),
        ('athletic', 'Athletic'),
        ('artistic', 'Arts/Creative'),
        ('minority', 'Minority/Diversity'),
        ('regional', 'Regional/County-specific'),
        ('professional', 'Professional Development'),
        ('emergency', 'Emergency/Hardship'),
    ]
    
    EDUCATION_LEVEL_CHOICES = [
        ('primary', 'Primary School'),
        ('secondary', 'Secondary School'),
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
        ('phd', 'PhD'),
        ('all_levels', 'All Levels'),
    ]
    
    SCHOLARSHIP_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    COVERAGE_TYPE_CHOICES = [
        ('full', 'Full Coverage'),
        ('partial', 'Partial Coverage'),
        ('tuition_only', 'Tuition Only'),
        ('living_expenses', 'Living Expenses Only'),
        ('books_supplies', 'Books and Supplies'),
        ('emergency_fund', 'Emergency Fund'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True)
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name='scholarships'
    )
    scholarship_type = models.CharField(
        max_length=20,
        choices=SCHOLARSHIP_TYPE_CHOICES
    )
    
    # Description and Requirements
    description = models.TextField(
        help_text="Detailed description of the scholarship"
    )
    eligibility_criteria = models.JSONField(
        default=dict,
        help_text="JSON object containing eligibility criteria"
    )
    required_documents = models.JSONField(
        default=list,
        help_text="List of required documents"
    )
    
    # Target Demographics
    target_education_levels = models.JSONField(
        default=list,
        help_text="List of education levels this scholarship targets"
    )
    target_counties = models.ManyToManyField(
        County,
        blank=True,
        related_name='targeted_scholarships',
        help_text="Counties this scholarship targets (empty = all counties)"
    )
    target_fields_of_study = models.JSONField(
        default=list,
        help_text="List of fields of study/courses"
    )
    
    # Financial Details
    coverage_type = models.CharField(
        max_length=20,
        choices=COVERAGE_TYPE_CHOICES
    )
    amount_per_beneficiary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount per beneficiary in KES"
    )
    total_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total scholarship budget in KES"
    )
    number_of_awards = models.PositiveIntegerField(
        help_text="Number of scholarships available"
    )
    renewable = models.BooleanField(
        default=False,
        help_text="Can scholarship be renewed?"
    )
    renewal_criteria = models.TextField(
        blank=True,
        help_text="Criteria for scholarship renewal"
    )
    
    # Application Timeline
    application_start_date = models.DateTimeField()
    application_deadline = models.DateTimeField()
    selection_start_date = models.DateTimeField(
        null=True,
        blank=True
    )
    selection_end_date = models.DateTimeField(
        null=True,
        blank=True
    )
    award_notification_date = models.DateTimeField(
        null=True,
        blank=True
    )
    disbursement_start_date = models.DateTimeField(
        null=True,
        blank=True
    )
    
    # Academic Requirements
    minimum_gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(4.0)]
    )
    minimum_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Financial Requirements
    maximum_family_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum annual family income in KES"
    )
    
    # Age Requirements
    minimum_age = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    maximum_age = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    
    # Special Requirements
    for_orphans_only = models.BooleanField(default=False)
    for_disabled_only = models.BooleanField(default=False)
    for_females_only = models.BooleanField(default=False)
    for_males_only = models.BooleanField(default=False)
    requires_community_service = models.BooleanField(default=False)
    community_service_hours = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Required community service hours"
    )
    
    # Application Process
    application_method = models.CharField(
        max_length=20,
        choices=[
            ('online', 'Online Application'),
            ('offline', 'Offline Application'),
            ('both', 'Online and Offline'),
        ],
        default='online'
    )
    external_application_url = models.URLField(
        blank=True,
        help_text="External application URL if not using internal system"
    )
    
    # Contact Information
    contact_person = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?254[0-9]{9}$',
            message="Phone number must be in format +254XXXXXXXXX"
        )]
    )
    
    # Status and Tracking
    status = models.CharField(
        max_length=20,
        choices=SCHOLARSHIP_STATUS_CHOICES,
        default='draft'
    )
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    application_count = models.PositiveIntegerField(default=0)
    
    # SEO and Tags
    tags = models.JSONField(
        default=list,
        help_text="Tags for better searchability"
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO meta description"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_scholarships'
    )
    
    class Meta:
        verbose_name = "Scholarship"
        verbose_name_plural = "Scholarships"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'application_deadline']),
            models.Index(fields=['scholarship_type']),
            models.Index(fields=['provider']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.provider.name}"
    
    @property
    def is_active(self):
        """Check if scholarship is currently accepting applications"""
        now = timezone.now()
        return (
            self.status == 'active' and
            self.application_start_date <= now <= self.application_deadline
        )
    
    @property
    def days_until_deadline(self):
        """Calculate days remaining until application deadline"""
        if self.application_deadline:
            delta = self.application_deadline.date() - timezone.now().date()
            return delta.days if delta.days >= 0 else 0
        return None
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_application_count(self):
        """Increment application count"""
        self.application_count += 1
        self.save(update_fields=['application_count'])

    def calculate_match_score(self, student):
        """
        Calculate how well a student matches this scholarship's eligibility criteria.
        
        Args:
            student: Student object to evaluate
            
        Returns:
            float: Match score as a percentage (0-100)
        """
        if not student:
            return 0.0
            
        total_criteria = 0
        matched_criteria = 0
        
        # Education Level Match (weight: 20%)
        if self.target_education_levels:
            total_criteria += 20
            if student.current_education_level in self.target_education_levels:
                matched_criteria += 20
        
        # GPA/Percentage Match (weight: 15%)
        if self.minimum_gpa and student.previous_gpa:
            total_criteria += 15
            if student.previous_gpa >= self.minimum_gpa:
                matched_criteria += 15
        elif self.minimum_percentage and student.previous_percentage:
            total_criteria += 15
            if student.previous_percentage >= self.minimum_percentage:
                matched_criteria += 15
        
        # Age Match (weight: 10%)
        if self.minimum_age or self.maximum_age:
            total_criteria += 10
            student_age = student.age  # Using the age property
            if student_age:
                age_match = True
                if self.minimum_age and student_age < self.minimum_age:
                    age_match = False
                if self.maximum_age and student_age > self.maximum_age:
                    age_match = False
                if age_match:
                    matched_criteria += 10
        
        # County Match (weight: 10%)
        if self.target_counties.exists():
            total_criteria += 10
            if student.county in self.target_counties.all():
                matched_criteria += 10
        
        # Family Income Match (weight: 15%)
        if self.maximum_family_income and student.family_income_annual:
            total_criteria += 15
            if student.family_income_annual <= self.maximum_family_income:
                matched_criteria += 15
        
        # Gender Match (weight: 5%)
        gender_criteria_exists = self.for_females_only or self.for_males_only
        if gender_criteria_exists:
            total_criteria += 5
            if (self.for_females_only and student.gender == 'F') or \
               (self.for_males_only and student.gender == 'M'):
                matched_criteria += 5
        
        # Field of Study Match (weight: 10%)
        if self.target_fields_of_study and student.course_of_study:
            total_criteria += 10
            # Check if student's course matches any target field
            if any(field.lower() in student.course_of_study.lower() 
                   for field in self.target_fields_of_study):
                matched_criteria += 10
        
        # Special Requirements (weight: 15%)
        special_weight = 15
        special_matched = 0
        special_total = 0
        
        if self.for_orphans_only:
            special_total += 5
            if student.is_orphan:
                special_matched += 5
        
        if self.for_disabled_only:
            special_total += 5
            if student.disability_status and student.disability_status != 'none':
                special_matched += 5
        
        # Check additional criteria from eligibility_criteria JSON
        if self.eligibility_criteria:
            special_total += 5
            # Give partial credit for having academic records
            if student.previous_gpa or student.previous_percentage:
                special_matched += 2.5
            # Additional JSON criteria can be checked here
            # For example: specific requirements like single parent, child-headed household
            criteria = self.eligibility_criteria
            if isinstance(criteria, dict):
                if criteria.get('single_parent_child') and student.is_single_parent_child:
                    special_matched += 1.25
                if criteria.get('child_headed_household') and student.is_child_headed_household:
                    special_matched += 1.25
        
        if special_total > 0:
            total_criteria += special_weight
            matched_criteria += (special_matched / special_total) * special_weight
        
        # Calculate final score
        if total_criteria == 0:
            return 100.0  # No specific criteria means all students match
        
        match_score = (matched_criteria / total_criteria) * 100
        return round(match_score, 2)


class Application(models.Model):
    """Model representing scholarship applications"""
    
    APPLICATION_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interview_completed', 'Interview Completed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
        ('withdrawn', 'Withdrawn'),
        ('expired', 'Expired'),
    ]
    
    INTERVIEW_STATUS_CHOICES = [
        ('not_required', 'Not Required'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('missed', 'Missed'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    # Basic Information
    application_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    
    # Application Status
    status = models.CharField(
        max_length=20,
        choices=APPLICATION_STATUS_CHOICES,
        default='draft'
    )
    submission_date = models.DateTimeField(null=True, blank=True)
    last_modified_date = models.DateTimeField(auto_now=True)
    
    # Application Data
    personal_statement = models.TextField(
        help_text="Student's personal statement/essay"
    )
    motivation_letter = models.TextField(
        blank=True,
        help_text="Why student is applying for this scholarship"
    )
    career_goals = models.TextField(
        blank=True,
        help_text="Student's career goals and aspirations"
    )
    
    # Additional Information
    additional_info = models.JSONField(
        default=dict,
        help_text="Additional application-specific information"
    )
    special_circumstances = models.TextField(
        blank=True,
        help_text="Any special circumstances or challenges"
    )
    
    # References
    reference_contacts = models.JSONField(
        default=list,
        help_text="List of reference contacts (name, title, phone, email)"
    )
    
    # Documents
    supporting_documents = models.JSONField(
        default=list,
        help_text="List of uploaded supporting documents"
    )
    
    # Academic Information (at time of application)
    current_gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(4.0)]
    )
    current_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Interview Information
    interview_status = models.CharField(
        max_length=20,
        choices=INTERVIEW_STATUS_CHOICES,
        default='not_required'
    )
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_location = models.CharField(max_length=200, blank=True)
    interview_notes = models.TextField(blank=True)
    interview_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Evaluation and Scoring
    evaluation_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall evaluation score"
    )
    evaluator_comments = models.TextField(
        blank=True,
        help_text="Comments from evaluators"
    )
    evaluation_criteria_scores = models.JSONField(
        default=dict,
        help_text="Scores for individual evaluation criteria"
    )
    
    # Decision Information
    decision_date = models.DateTimeField(null=True, blank=True)
    decision_made_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scholarship_decisions'
    )
    decision_comments = models.TextField(
        blank=True,
        help_text="Comments about the decision"
    )
    
    # Award Information (if approved)
    award_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Awarded amount in KES"
    )
    award_duration_months = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Duration of award in months"
    )
    award_start_date = models.DateField(null=True, blank=True)
    award_end_date = models.DateField(null=True, blank=True)
    
    # Disbursement Tracking
    disbursement_schedule = models.JSONField(
        default=list,
        help_text="Schedule of disbursements"
    )
    total_disbursed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total amount disbursed so far"
    )
    
    # Communication Log
    communication_log = models.JSONField(
        default=list,
        help_text="Log of communications with the student"
    )
    
    # Compliance and Monitoring
    compliance_status = models.CharField(
        max_length=20,
        choices=[
            ('compliant', 'Compliant'),
            ('warning', 'Warning'),
            ('non_compliant', 'Non-Compliant'),
            ('under_review', 'Under Review'),
        ],
        default='compliant'
    )
    monitoring_notes = models.TextField(
        blank=True,
        help_text="Notes from monitoring activities"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Application"
        verbose_name_plural = "Applications"
        unique_together = ['student', 'scholarship']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'submission_date']),
            models.Index(fields=['scholarship', 'status']),
            models.Index(fields=['student']),
        ]
    
    def __str__(self):
        return f"{self.student.full_name} - {self.scholarship.title}"
    
    def submit_application(self):
        """Submit the application"""
        if self.status == 'draft':
            self.status = 'submitted'
            self.submission_date = timezone.now()
            self.save()
            # Increment scholarship application count
            self.scholarship.increment_application_count()
    
    @property
    def can_be_edited(self):
        """Check if application can still be edited"""
        return self.status in ['draft']
    
    @property
    def is_successful(self):
        """Check if application was successful"""
        return self.status == 'approved'
    
    @property
    def days_since_submission(self):
        """Calculate days since submission"""
        if self.submission_date:
            delta = timezone.now().date() - self.submission_date.date()
            return delta.days
        return None


class Document(models.Model):
    """Model for storing application documents"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('academic_transcript', 'Academic Transcript'),
        ('birth_certificate', 'Birth Certificate'),
        ('national_id', 'National ID Copy'),
        ('passport_photo', 'Passport Photo'),
        ('recommendation_letter', 'Recommendation Letter'),
        ('financial_statement', 'Financial Statement'),
        ('bank_statement', 'Bank Statement'),
        ('admission_letter', 'Admission Letter'),
        ('fee_structure', 'Fee Structure'),
        ('disability_certificate', 'Disability Certificate'),
        ('death_certificate', 'Death Certificate (Parent/Guardian)'),
        ('affidavit', 'Affidavit'),
        ('other', 'Other'),
    ]
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPE_CHOICES
    )
    file = models.FileField(
        upload_to='application_documents/',
        help_text="Upload document file"
    )
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    description = models.CharField(max_length=300, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.application.student.full_name}"


class Disbursement(models.Model):
    """Model for tracking scholarship disbursements"""
    
    DISBURSEMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    DISBURSEMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('cheque', 'Cheque'),
        ('cash', 'Cash'),
        ('direct_payment', 'Direct Payment to Institution'),
    ]
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='disbursements'
    )
    disbursement_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Disbursement amount in KES"
    )
    disbursement_date = models.DateField()
    method = models.CharField(
        max_length=20,
        choices=DISBURSEMENT_METHOD_CHOICES
    )
    status = models.CharField(
        max_length=20,
        choices=DISBURSEMENT_STATUS_CHOICES,
        default='pending'
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Transaction reference number"
    )
    recipient_details = models.JSONField(
        default=dict,
        help_text="Recipient details (bank account, mobile number, etc.)"
    )
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_disbursements'
    )
    processed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Disbursement"
        verbose_name_plural = "Disbursements"
        ordering = ['-disbursement_date']
    
    def __str__(self):
        return f"KES {self.amount:,.2f} - {self.application.student.full_name}"


class Notification(models.Model):
    """Model for system notifications"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('application_submitted', 'Application Submitted'),
        ('application_approved', 'Application Approved'),
        ('application_rejected', 'Application Rejected'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('disbursement_processed', 'Disbursement Processed'),
        ('deadline_reminder', 'Deadline Reminder'),
        ('document_required', 'Document Required'),
        ('scholarship_opportunity', 'New Scholarship Opportunity'),
        ('system_update', 'System Update'),
    ]
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(blank=True)
    related_application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class AuditLog(models.Model):
    """Model for tracking system changes and activities"""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    changes = models.JSONField(
        default=dict,
        help_text="JSON object of changes made"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['model_name', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} {self.action} {self.model_name} at {self.timestamp}"
