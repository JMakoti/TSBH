import django_filters
from django.db.models import Q
from .models import Scholarship, Application, County


class ScholarshipFilter(django_filters.FilterSet):
    """Filter class for Scholarship API"""
    
    # County filter - can filter by multiple counties
    county = django_filters.ModelMultipleChoiceFilter(
        field_name='target_counties',
        queryset=County.objects.all(),
        help_text="Filter by target counties"
    )
    
    # Education level filter
    education_level = django_filters.CharFilter(
        method='filter_education_level',
        help_text="Filter by education level (primary, secondary, undergraduate, etc.)"
    )
    
    # Gender-specific scholarships
    gender = django_filters.CharFilter(
        method='filter_gender',
        help_text="Filter by gender (M for male-only, F for female-only, A for all)"
    )
    
    # Scholarship type filter
    scholarship_type = django_filters.CharFilter(
        field_name='scholarship_type',
        lookup_expr='iexact',
        help_text="Filter by scholarship type"
    )
    
    # Provider type filter
    provider_type = django_filters.CharFilter(
        field_name='provider__provider_type',
        lookup_expr='iexact',
        help_text="Filter by provider type"
    )
    
    # Amount range filters
    min_amount = django_filters.NumberFilter(
        field_name='amount_per_beneficiary',
        lookup_expr='gte',
        help_text="Minimum scholarship amount"
    )
    
    max_amount = django_filters.NumberFilter(
        field_name='amount_per_beneficiary',
        lookup_expr='lte',
        help_text="Maximum scholarship amount"
    )
    
    # Deadline filter
    deadline_after = django_filters.DateTimeFilter(
        field_name='application_deadline',
        lookup_expr='gte',
        help_text="Scholarships with deadline after this date"
    )
    
    # Special requirements filters
    for_orphans = django_filters.BooleanFilter(
        field_name='for_orphans_only',
        help_text="Filter scholarships for orphans only"
    )
    
    for_disabled = django_filters.BooleanFilter(
        field_name='for_disabled_only',
        help_text="Filter scholarships for disabled students only"
    )
    
    # Search filter
    search = django_filters.CharFilter(
        method='filter_search',
        help_text="Search in title, description, and tags"
    )
    
    # Coverage type filter
    coverage_type = django_filters.CharFilter(
        field_name='coverage_type',
        lookup_expr='iexact',
        help_text="Filter by coverage type (full, partial, tuition_only, etc.)"
    )
    
    # Featured scholarships
    is_featured = django_filters.BooleanFilter(
        field_name='is_featured',
        help_text="Filter featured scholarships"
    )
    
    class Meta:
        model = Scholarship
        fields = []  # We define filters explicitly above
    
    def filter_education_level(self, queryset, name, value):
        """Filter scholarships by education level - SQLite compatible"""
        if value:
            # Get all scholarships first, then filter in Python
            all_scholarships = list(queryset)
            filtered_ids = []
            for scholarship in all_scholarships:
                target_levels = scholarship.target_education_levels or []
                if (not target_levels or 
                    'all_levels' in target_levels or 
                    value in target_levels):
                    filtered_ids.append(scholarship.id)
            
            return Scholarship.objects.filter(id__in=filtered_ids)
        return queryset
    
    def filter_gender(self, queryset, name, value):
        """Filter scholarships by gender requirements"""
        if value:
            if value.upper() == 'M':
                # Male students - exclude female-only scholarships
                return queryset.filter(for_females_only=False)
            elif value.upper() == 'F':
                # Female students - exclude male-only scholarships
                return queryset.filter(for_males_only=False)
            elif value.upper() == 'A':
                # All genders - exclude both male-only and female-only
                return queryset.filter(for_males_only=False, for_females_only=False)
        return queryset
    
    def filter_search(self, queryset, name, value):
        """Search in multiple fields - SQLite compatible"""
        if value:
            # For basic text fields, use standard icontains
            text_filtered = queryset.filter(
                Q(title__icontains=value) |
                Q(description__icontains=value) |
                Q(provider__name__icontains=value)
            )
            
            # For tags (JSON field), filter in Python
            all_scholarships = list(text_filtered)
            tag_matched_ids = []
            for scholarship in all_scholarships:
                tags = scholarship.tags or []
                if any(value.lower() in tag.lower() for tag in tags):
                    tag_matched_ids.append(scholarship.id)
            
            # Combine results
            if tag_matched_ids:
                return queryset.filter(
                    Q(title__icontains=value) |
                    Q(description__icontains=value) |
                    Q(provider__name__icontains=value) |
                    Q(id__in=tag_matched_ids)
                )
            else:
                return text_filtered
        return queryset
    
    @property
    def qs(self):
        """Override queryset to always filter for active and verified scholarships"""
        parent = super().qs
        # Only show active scholarships from verified providers
        return parent.filter(
            status='active',
            provider__is_verified=True
        ).select_related('provider').prefetch_related('target_counties')


class ApplicationFilter(django_filters.FilterSet):
    """Filter class for Application API"""
    
    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='iexact',
        help_text="Filter by application status"
    )
    
    scholarship = django_filters.NumberFilter(
        field_name='scholarship__id',
        help_text="Filter by scholarship ID"
    )
    
    submission_date_after = django_filters.DateTimeFilter(
        field_name='submission_date',
        lookup_expr='gte',
        help_text="Applications submitted after this date"
    )
    
    submission_date_before = django_filters.DateTimeFilter(
        field_name='submission_date',
        lookup_expr='lte',
        help_text="Applications submitted before this date"
    )
    
    class Meta:
        model = Application
        fields = ['status', 'scholarship']
