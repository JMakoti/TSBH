from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    County, Student, Provider, Scholarship, Application,
    Document, Disbursement, Notification, AuditLog
)


class TuvukeAdminSite(admin.AdminSite):
    site_header = "Tuvuke Hub Administration"
    site_title = "Tuvuke Hub Admin"
    index_title = "Welcome to Tuvuke Hub Administration"
    
    def index(self, request, extra_context=None):
        """
        Override the default admin index view to include analytics data
        """
        extra_context = extra_context or {}
        
        # Calculate analytics data
        analytics = self.get_analytics_data()
        extra_context['analytics'] = analytics
        
        return super().index(request, extra_context)
    
    def get_analytics_data(self):
        """
        Calculate analytics data for the dashboard
        """
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # Basic counts
        total_students = Student.objects.count()
        total_scholarships = Scholarship.objects.count()
        total_applications = Application.objects.count()
        total_providers = Provider.objects.count()
        counties_represented = County.objects.filter(students__isnull=False).distinct().count()
        
        # Financial data
        total_disbursed = Disbursement.objects.filter(
            status='completed'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_scholarship_value = Scholarship.objects.aggregate(
            total=Sum('total_budget')
        )['total'] or 0
        
        average_award = Scholarship.objects.aggregate(
            avg=Avg('amount_per_beneficiary')
        )['avg'] or 0
        
        # Application statistics
        application_stats = Application.objects.aggregate(
            submitted=Count('id', filter=Q(status='submitted')),
            approved=Count('id', filter=Q(status='approved')),
            under_review=Count('id', filter=Q(status='under_review'))
        )
        
        # Calculate success rate
        total_decided = Application.objects.filter(
            status__in=['approved', 'rejected']
        ).count()
        approved_apps = application_stats['approved']
        success_rate = (approved_apps / total_decided * 100) if total_decided > 0 else 0
        
        # Scholarship statistics
        active_scholarships = Scholarship.objects.filter(status='active').count()
        verified_providers = Provider.objects.filter(is_verified=True).count()
        
        # Student demographics
        student_stats = Student.objects.aggregate(
            verified=Count('id', filter=Q(is_verified=True)),
            female=Count('id', filter=Q(gender='F')),
            disabled=Count('id', filter=~Q(disability_status='none')),
            orphaned=Count('id', filter=Q(is_orphan=True))
        )
        
        female_percentage = (student_stats['female'] / total_students * 100) if total_students > 0 else 0
        
        # Recent activity (last 30 days)
        recent_stats = {
            'new_students_month': Student.objects.filter(
                created_at__gte=thirty_days_ago
            ).count(),
            'new_applications_month': Application.objects.filter(
                created_at__gte=thirty_days_ago
            ).count(),
            'new_scholarships_month': Scholarship.objects.filter(
                created_at__gte=thirty_days_ago
            ).count(),
            'disbursements_month': Disbursement.objects.filter(
                created_at__gte=thirty_days_ago,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
        }
        
        return {
            'total_students': total_students,
            'total_scholarships': total_scholarships,
            'total_applications': total_applications,
            'total_providers': total_providers,
            'counties_represented': counties_represented,
            'total_disbursed': total_disbursed,
            'total_scholarship_value': total_scholarship_value,
            'average_award': average_award,
            'submitted_applications': application_stats['submitted'],
            'approved_applications': application_stats['approved'],
            'under_review_applications': application_stats['under_review'],
            'success_rate': success_rate,
            'active_scholarships': active_scholarships,
            'verified_providers': verified_providers,
            'verified_students': student_stats['verified'],
            'female_students': student_stats['female'],
            'female_percentage': female_percentage,
            'disabled_students': student_stats['disabled'],
            'orphaned_students': student_stats['orphaned'],
            'last_updated': now,
            **recent_stats
        }


# Create custom admin site instance
admin_site = TuvukeAdminSite(name='tuvuke_admin')


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'capital_city', 'population', 'area_sq_km']
    list_filter = ['name']
    search_fields = ['name', 'code', 'capital_city']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'national_id', 'email', 'county', 
        'current_education_level', 'is_verified', 'created_at'
    ]
    list_filter = [
        'current_education_level', 'gender', 'county', 
        'is_verified', 'disability_status', 'is_orphan'
    ]
    search_fields = [
        'first_name', 'last_name', 'national_id', 
        'email', 'phone_number'
    ]
    readonly_fields = ['student_id', 'age', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'student_id', 'first_name', 'last_name', 
                      'other_names', 'date_of_birth', 'gender', 'national_id')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'alternative_phone')
        }),
        ('Location', {
            'fields': ('county', 'sub_county', 'ward', 'location', 'postal_address')
        }),
        ('Education', {
            'fields': ('current_education_level', 'current_institution', 
                      'course_of_study', 'year_of_study', 'expected_graduation_year')
        }),
        ('Academic Performance', {
            'fields': ('previous_gpa', 'previous_percentage')
        }),
        ('Financial Information', {
            'fields': ('family_income_annual', 'number_of_dependents')
        }),
        ('Special Circumstances', {
            'fields': ('disability_status', 'is_orphan', 'is_single_parent_child', 
                      'is_child_headed_household')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_date', 'profile_photo')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'provider_type', 'county', 'email', 
        'is_verified', 'is_active', 'created_at'
    ]
    list_filter = [
        'provider_type', 'funding_source', 'county', 
        'is_verified', 'is_active'
    ]
    search_fields = ['name', 'email', 'description']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    actions = ['mark_as_verified']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'provider_type', 'funding_source')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'website')
        }),
        ('Location', {
            'fields': ('physical_address', 'postal_address', 'county')
        }),
        ('Organization Details', {
            'fields': ('description', 'mission_statement', 'established_date', 
                      'registration_number')
        }),
        ('Financial Information', {
            'fields': ('total_annual_budget', 'scholarship_budget_annual')
        }),
        ('Media', {
            'fields': ('logo',)
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active', 'verification_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def mark_as_verified(self, request, queryset):
        """Mark selected providers as verified"""
        from django.utils import timezone
        
        updated_count = 0
        for provider in queryset:
            if not provider.is_verified:
                provider.is_verified = True
                provider.verification_date = timezone.now()
                provider.save()
                updated_count += 1
        
        if updated_count == 1:
            message = "1 provider was successfully marked as verified."
        else:
            message = f"{updated_count} providers were successfully marked as verified."
        
        self.message_user(request, message)
    
    mark_as_verified.short_description = "Mark selected providers as verified"


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'provider', 'deadline', 'is_verified', 'is_active'
    ]
    list_filter = ['provider__is_verified', 'target_counties']
    search_fields = ['title']
    readonly_fields = [
        'slug', 'view_count', 'application_count', 'is_active',
        'days_until_deadline', 'created_at', 'updated_at'
    ]
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['target_counties']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'provider', 'scholarship_type')
        }),
        ('Description', {
            'fields': ('description', 'eligibility_criteria', 'required_documents')
        }),
        ('Target Demographics', {
            'fields': ('target_education_levels', 'target_counties', 'target_fields_of_study')
        }),
        ('Financial Details', {
            'fields': ('coverage_type', 'amount_per_beneficiary', 'total_budget',
                      'number_of_awards', 'renewable', 'renewal_criteria')
        }),
        ('Timeline', {
            'fields': ('application_start_date', 'application_deadline',
                      'selection_start_date', 'selection_end_date',
                      'award_notification_date', 'disbursement_start_date')
        }),
        ('Requirements', {
            'fields': ('minimum_gpa', 'minimum_percentage', 'maximum_family_income',
                      'minimum_age', 'maximum_age')
        }),
        ('Special Requirements', {
            'fields': ('for_orphans_only', 'for_disabled_only', 'for_females_only',
                      'for_males_only', 'requires_community_service', 'community_service_hours')
        }),
        ('Application Process', {
            'fields': ('application_method', 'external_application_url')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'contact_email', 'contact_phone')
        }),
        ('Status and SEO', {
            'fields': ('status', 'is_featured', 'view_count', 'application_count',
                      'tags', 'meta_description', 'source', 'source_url')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def deadline(self, obj):
        """Display formatted deadline"""
        return obj.application_deadline.strftime('%Y-%m-%d %H:%M') if obj.application_deadline else '-'
    deadline.short_description = 'Deadline'
    deadline.admin_order_field = 'application_deadline'
    
    def is_verified(self, obj):
        """Display verification status based on provider"""
        return obj.provider.is_verified
    is_verified.boolean = True
    is_verified.short_description = 'Is Verified'
    is_verified.admin_order_field = 'provider__is_verified'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly_fields.extend(['is_active', 'days_until_deadline'])
        return readonly_fields


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'application_id', 'student_name', 'scholarship_title', 'status',
        'submission_date', 'evaluation_score', 'award_amount'
    ]
    list_filter = [
        'status', 'scholarship__provider', 'interview_status',
        'compliance_status', 'submission_date'
    ]
    search_fields = [
        'student__first_name', 'student__last_name', 'student__national_id',
        'scholarship__title', 'application_id'
    ]
    readonly_fields = [
        'application_id', 'can_be_edited', 'is_successful',
        'days_since_submission', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('application_id', 'student', 'scholarship', 'status')
        }),
        ('Application Content', {
            'fields': ('personal_statement', 'motivation_letter', 'career_goals',
                      'additional_info', 'special_circumstances')
        }),
        ('References and Documents', {
            'fields': ('reference_contacts', 'supporting_documents')
        }),
        ('Academic Information', {
            'fields': ('current_gpa', 'current_percentage')
        }),
        ('Interview', {
            'fields': ('interview_status', 'interview_date', 'interview_location',
                      'interview_notes', 'interview_score')
        }),
        ('Evaluation', {
            'fields': ('evaluation_score', 'evaluator_comments', 'evaluation_criteria_scores')
        }),
        ('Decision', {
            'fields': ('decision_date', 'decision_made_by', 'decision_comments')
        }),
        ('Award Information', {
            'fields': ('award_amount', 'award_duration_months', 'award_start_date',
                      'award_end_date', 'disbursement_schedule', 'total_disbursed')
        }),
        ('Monitoring', {
            'fields': ('compliance_status', 'monitoring_notes', 'communication_log')
        }),
        ('Metadata', {
            'fields': ('submission_date', 'last_modified_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def student_name(self, obj):
        return obj.student.full_name
    student_name.short_description = 'Student'

    def scholarship_title(self, obj):
        return obj.scholarship.title
    scholarship_title.short_description = 'Scholarship'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'document_type', 'application_student', 'original_filename',
        'file_size_kb', 'is_verified', 'created_at'
    ]
    list_filter = ['document_type', 'is_verified', 'created_at']
    search_fields = [
        'application__student__first_name', 'application__student__last_name',
        'original_filename', 'description'
    ]
    readonly_fields = ['file_size', 'original_filename', 'created_at']

    def application_student(self, obj):
        return obj.application.student.full_name
    application_student.short_description = 'Student'

    def file_size_kb(self, obj):
        return f"{obj.file_size / 1024:.1f} KB"
    file_size_kb.short_description = 'File Size'


@admin.register(Disbursement)
class DisbursementAdmin(admin.ModelAdmin):
    list_display = [
        'disbursement_id', 'application_student', 'amount',
        'disbursement_date', 'method', 'status'
    ]
    list_filter = ['method', 'status', 'disbursement_date']
    search_fields = [
        'application__student__first_name', 'application__student__last_name',
        'disbursement_id', 'reference_number'
    ]
    readonly_fields = ['disbursement_id', 'created_at', 'updated_at']

    def application_student(self, obj):
        return obj.application.student.full_name
    application_student.short_description = 'Student'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'recipient', 'notification_type', 'is_read', 'created_at'
    ]
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']
    readonly_fields = ['created_at', 'read_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'action', 'model_name', 'object_repr', 'timestamp'
    ]
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'model_name', 'object_repr']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'object_repr',
                      'changes', 'ip_address', 'user_agent', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Register all models with both default admin and custom admin site
admin_site.register(County, CountyAdmin)
admin_site.register(Student, StudentAdmin)
admin_site.register(Provider, ProviderAdmin)
admin_site.register(Scholarship, ScholarshipAdmin)
admin_site.register(Application, ApplicationAdmin)
admin_site.register(Document, DocumentAdmin)
admin_site.register(Disbursement, DisbursementAdmin)
admin_site.register(Notification, NotificationAdmin)
admin_site.register(AuditLog, AuditLogAdmin)
