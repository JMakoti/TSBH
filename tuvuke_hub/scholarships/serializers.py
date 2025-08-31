from rest_framework import serializers
from .models import Scholarship, Application, Student, Provider, County


class CountySerializer(serializers.ModelSerializer):
    """Serializer for County model"""
    
    class Meta:
        model = County
        fields = ['id', 'name', 'code', 'capital_city']


class ProviderSerializer(serializers.ModelSerializer):
    """Serializer for Provider model"""
    
    class Meta:
        model = Provider
        fields = [
            'id', 'name', 'provider_type', 'funding_source', 
            'email', 'website', 'county', 'description',
            'is_verified', 'is_active'
        ]


class ScholarshipListSerializer(serializers.ModelSerializer):
    """Serializer for Scholarship list view"""
    provider = ProviderSerializer(read_only=True)
    target_counties = CountySerializer(many=True, read_only=True)
    days_until_deadline = serializers.ReadOnlyField()
    is_verified = serializers.SerializerMethodField()
    
    class Meta:
        model = Scholarship
        fields = [
            'id', 'title', 'slug', 'provider', 'scholarship_type',
            'description', 'target_education_levels', 'target_counties',
            'target_fields_of_study', 'coverage_type', 'amount_per_beneficiary',
            'number_of_awards', 'application_start_date', 'application_deadline',
            'minimum_gpa', 'minimum_percentage', 'maximum_family_income',
            'minimum_age', 'maximum_age', 'for_orphans_only',
            'for_disabled_only', 'for_females_only', 'for_males_only',
            'application_method', 'external_application_url',
            'contact_person', 'contact_email', 'contact_phone',
            'is_featured', 'view_count', 'application_count',
            'tags', 'days_until_deadline', 'is_verified', 'created_at'
        ]
    
    def get_is_verified(self, obj):
        """Get verification status from provider"""
        return obj.provider.is_verified


class ScholarshipDetailSerializer(ScholarshipListSerializer):
    """Serializer for Scholarship detail view with additional fields"""
    
    class Meta(ScholarshipListSerializer.Meta):
        fields = ScholarshipListSerializer.Meta.fields + [
            'eligibility_criteria', 'required_documents', 'total_budget',
            'renewable', 'renewal_criteria', 'selection_start_date',
            'selection_end_date', 'award_notification_date',
            'disbursement_start_date', 'requires_community_service',
            'community_service_hours', 'meta_description', 'source',
            'source_url'
        ]


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model"""
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    county = CountySerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'first_name', 'last_name', 'other_names',
            'full_name', 'date_of_birth', 'age', 'gender', 'national_id',
            'phone_number', 'email', 'county', 'current_education_level',
            'current_institution', 'course_of_study', 'year_of_study',
            'previous_gpa', 'previous_percentage', 'family_income_annual',
            'disability_status', 'is_orphan', 'is_single_parent_child',
            'is_child_headed_household', 'is_verified'
        ]
        read_only_fields = ['student_id', 'full_name', 'age', 'is_verified']


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating scholarship applications"""
    
    class Meta:
        model = Application
        fields = [
            'scholarship', 'personal_statement', 'motivation_letter',
            'career_goals', 'special_circumstances', 'reference_contacts'
        ]
    
    def validate(self, data):
        """Validate application data"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated")
        
        # Check if user has a student profile
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            raise serializers.ValidationError("User must have a student profile to apply")
        
        # Check if application already exists
        scholarship = data['scholarship']
        if Application.objects.filter(student=student, scholarship=scholarship).exists():
            raise serializers.ValidationError(
                "You have already applied for this scholarship"
            )
        
        # Check if scholarship is active and accepting applications
        if not scholarship.is_active:
            raise serializers.ValidationError("This scholarship is not currently accepting applications")
        
        return data
    
    def create(self, validated_data):
        """Create application with authenticated student"""
        request = self.context.get('request')
        student = request.user.student_profile
        validated_data['student'] = student
        validated_data['status'] = 'draft'
        return super().create(validated_data)


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Application model"""
    student = StudentSerializer(read_only=True)
    scholarship = ScholarshipListSerializer(read_only=True)
    can_be_edited = serializers.ReadOnlyField()
    is_successful = serializers.ReadOnlyField()
    days_since_submission = serializers.ReadOnlyField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'application_id', 'student', 'scholarship', 'status',
            'submission_date', 'personal_statement', 'motivation_letter',
            'career_goals', 'special_circumstances', 'reference_contacts',
            'current_gpa', 'current_percentage', 'evaluation_score',
            'award_amount', 'can_be_edited', 'is_successful',
            'days_since_submission', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'application_id', 'student', 'submission_date', 'evaluation_score',
            'award_amount', 'can_be_edited', 'is_successful',
            'days_since_submission', 'created_at', 'updated_at'
        ]


class ApplicationSubmitSerializer(serializers.Serializer):
    """Serializer for submitting applications"""
    
    def validate(self, data):
        """Validate that application can be submitted"""
        application = self.instance
        
        if not application:
            raise serializers.ValidationError("Application not found")
        
        if application.status != 'draft':
            raise serializers.ValidationError("Only draft applications can be submitted")
        
        # Check required fields
        required_fields = ['personal_statement', 'motivation_letter']
        for field in required_fields:
            if not getattr(application, field):
                raise serializers.ValidationError(f"{field.replace('_', ' ').title()} is required")
        
        return data
