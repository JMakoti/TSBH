"""
Views for HTMX-powered scholarship search and filtering.
Provides dynamic search and filtering without page reloads.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Sum, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
import json

from .models import Scholarship, County, Provider


def scholarship_search_homepage(request):
    """
    Homepage with HTMX-powered scholarship search.
    Shows initial scholarships and search/filter interface.
    """
    # Get initial scholarships (featured and recent)
    featured_scholarships = Scholarship.objects.filter(
        is_featured=True,
        status='active',
        application_deadline__gte=timezone.now()
    ).select_related('provider').prefetch_related('target_counties')[:6]
    
    recent_scholarships = Scholarship.objects.filter(
        status='active',
        application_deadline__gte=timezone.now()
    ).select_related('provider').prefetch_related('target_counties').order_by('-created_at')[:6]
    
    # Get filter options
    counties = County.objects.all().order_by('name')
    providers = Provider.objects.filter(is_active=True).order_by('name')
    
    # Education level choices for filtering
    education_levels = [
        ('primary', 'Primary School'),
        ('secondary', 'Secondary School'),
        ('college', 'College/Diploma'),
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
        ('masters', 'Masters'),
        ('phd', 'PhD'),
        ('professional', 'Professional Course'),
    ]
    
    # Scholarship type choices
    scholarship_types = [
        ('merit', 'Merit-Based'),
        ('need', 'Need-Based'),
        ('sports', 'Sports'),
        ('arts', 'Arts & Culture'),
        ('leadership', 'Leadership'),
        ('community', 'Community Service'),
        ('research', 'Research'),
        ('minority', 'Minority Groups'),
        ('disabled', 'Disability Support'),
        ('other', 'Other'),
    ]
    
    context = {
        'featured_scholarships': featured_scholarships,
        'recent_scholarships': recent_scholarships,
        'counties': counties,
        'providers': providers,
        'education_levels': education_levels,
        'scholarship_types': scholarship_types,
        'page_title': 'Find Your Perfect Scholarship',
        'total_active_scholarships': Scholarship.objects.filter(
            status='active',
            application_deadline__gte=timezone.now()
        ).count(),
    }
    
    return render(request, 'scholarships/search_homepage.html', context)


@require_http_methods(["GET"])
def htmx_scholarship_search(request):
    """
    HTMX endpoint for dynamic scholarship search and filtering.
    Returns HTML partial with filtered scholarships.
    """
    # Get search parameters
    search_query = request.GET.get('search', '').strip()
    county_id = request.GET.get('county', '').strip()
    education_level = request.GET.get('education_level', '').strip()
    scholarship_type = request.GET.get('scholarship_type', '').strip()
    provider_id = request.GET.get('provider', '').strip()
    min_grade = request.GET.get('min_grade', '').strip()
    max_amount = request.GET.get('max_amount', '').strip()
    sort_by = request.GET.get('sort', 'relevance').strip()
    page = request.GET.get('page', 1)
    
    # Start with active scholarships
    scholarships = Scholarship.objects.filter(
        status='active',
        application_deadline__gte=timezone.now()
    ).select_related('provider').prefetch_related('target_counties')
    
    # Apply search query
    if search_query:
        scholarships = scholarships.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(provider__name__icontains=search_query) |
            Q(target_fields_of_study__icontains=search_query)
        )
    
    # Apply county filter
    if county_id:
        try:
            county_id = int(county_id)
            scholarships = scholarships.filter(
                Q(target_counties__id=county_id) |
                Q(target_counties__isnull=True)  # Include scholarships with no county restrictions
            )
        except (ValueError, TypeError):
            pass
    
    # Apply education level filter - SQLite compatible
    if education_level:
        # Get all scholarships first, then filter in Python
        all_scholarships = list(scholarships)
        filtered_ids = []
        for scholarship in all_scholarships:
            target_levels = scholarship.target_education_levels or []
            if (not target_levels or 
                'all_levels' in target_levels or 
                education_level in target_levels):
                filtered_ids.append(scholarship.id)
        
        scholarships = Scholarship.objects.filter(id__in=filtered_ids)
    
    # Apply scholarship type filter
    if scholarship_type:
        scholarships = scholarships.filter(scholarship_type=scholarship_type)
    
    # Apply provider filter
    if provider_id:
        try:
            provider_id = int(provider_id)
            scholarships = scholarships.filter(provider_id=provider_id)
        except (ValueError, TypeError):
            pass
    
    # Apply minimum grade filter (based on GPA requirements)
    if min_grade:
        try:
            min_grade_decimal = Decimal(min_grade)
            scholarships = scholarships.filter(
                Q(minimum_gpa_required__lte=min_grade_decimal) |
                Q(minimum_gpa_required__isnull=True)
            )
        except (ValueError, TypeError):
            pass
    
    # Apply maximum amount filter
    if max_amount:
        try:
            max_amount_decimal = Decimal(max_amount)
            scholarships = scholarships.filter(
                amount_per_beneficiary__lte=max_amount_decimal
            )
        except (ValueError, TypeError):
            pass
    
    # Apply sorting
    if sort_by == 'deadline':
        scholarships = scholarships.order_by('application_deadline')
    elif sort_by == 'amount_high':
        scholarships = scholarships.order_by('-amount_per_beneficiary')
    elif sort_by == 'amount_low':
        scholarships = scholarships.order_by('amount_per_beneficiary')
    elif sort_by == 'newest':
        scholarships = scholarships.order_by('-created_at')
    elif sort_by == 'oldest':
        scholarships = scholarships.order_by('created_at')
    elif sort_by == 'provider':
        scholarships = scholarships.order_by('provider__name')
    else:  # relevance (default)
        # Order by featured first, then deadline, then creation date
        scholarships = scholarships.order_by('-is_featured', 'application_deadline', '-created_at')
    
    # Remove duplicates (in case of multiple county targets)
    scholarships = scholarships.distinct()
    
    # Pagination
    items_per_page = 12
    paginator = Paginator(scholarships, items_per_page)
    
    try:
        page_number = int(page)
    except (ValueError, TypeError):
        page_number = 1
    
    page_obj = paginator.get_page(page_number)
    
    # Calculate match scores if user is authenticated
    scholarships_with_scores = []
    user_student = None
    
    if request.user.is_authenticated:
        try:
            user_student = request.user.student_profile
        except:
            pass
    
    for scholarship in page_obj:
        scholarship_data = {
            'scholarship': scholarship,
            'match_score': None,
            'eligibility_status': 'unknown'
        }
        
        if user_student:
            try:
                match_score = scholarship.calculate_match_score(user_student)
                scholarship_data['match_score'] = match_score
                scholarship_data['eligibility_status'] = 'eligible' if match_score >= 70 else 'partial'
            except:
                pass
        
        scholarships_with_scores.append(scholarship_data)
    
    # Prepare search statistics
    search_stats = {
        'total_found': paginator.count,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'search_query': search_query,
        'filters_applied': bool(county_id or education_level or scholarship_type or provider_id or min_grade or max_amount)
    }
    
    context = {
        'scholarships_with_scores': scholarships_with_scores,
        'page_obj': page_obj,
        'search_stats': search_stats,
        'user_student': user_student,
    }
    
    # Return HTML partial for HTMX
    return render(request, 'scholarships/partials/scholarship_results.html', context)


@require_http_methods(["GET"])
def htmx_scholarship_filters(request):
    """
    HTMX endpoint for dynamic filter options.
    Updates filter dropdowns based on current search context.
    """
    search_query = request.GET.get('search', '').strip()
    county_id = request.GET.get('county', '').strip()
    education_level = request.GET.get('education_level', '').strip()
    
    # Get base scholarships for context
    scholarships = Scholarship.objects.filter(
        status='active',
        application_deadline__gte=timezone.now()
    )
    
    # Apply existing filters to get relevant options
    if search_query:
        scholarships = scholarships.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(provider__name__icontains=search_query)
        )
    
    if county_id:
        try:
            county_id = int(county_id)
            scholarships = scholarships.filter(
                Q(target_counties__id=county_id) |
                Q(target_counties__isnull=True)
            )
        except (ValueError, TypeError):
            pass
    
    # Get available providers for current context
    available_providers = Provider.objects.filter(
        id__in=scholarships.values_list('provider_id', flat=True),
        is_active=True
    ).distinct().order_by('name')
    
    # Get available scholarship types
    available_types = scholarships.values_list('scholarship_type', flat=True).distinct()
    
    context = {
        'available_providers': available_providers,
        'available_types': available_types,
    }
    
    return render(request, 'scholarships/partials/filter_options.html', context)


@require_http_methods(["GET"])
def htmx_scholarship_stats(request):
    """
    HTMX endpoint for real-time search statistics.
    Returns updated stats based on current filters.
    """
    # Get current filter parameters
    search_query = request.GET.get('search', '').strip()
    county_id = request.GET.get('county', '').strip()
    education_level = request.GET.get('education_level', '').strip()
    scholarship_type = request.GET.get('scholarship_type', '').strip()
    
    # Build filtered queryset
    scholarships = Scholarship.objects.filter(
        status='active',
        application_deadline__gte=timezone.now()
    )
    
    # Apply same filters as search
    if search_query:
        scholarships = scholarships.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(provider__name__icontains=search_query)
        )
    
    if county_id:
        try:
            county_id = int(county_id)
            scholarships = scholarships.filter(
                Q(target_counties__id=county_id) |
                Q(target_counties__isnull=True)
            )
        except (ValueError, TypeError):
            pass
    
    if education_level:
        # Get all scholarships first, then filter in Python - SQLite compatible
        all_scholarships = list(scholarships)
        filtered_ids = []
        for scholarship in all_scholarships:
            target_levels = scholarship.target_education_levels or []
            if (not target_levels or 
                'all_levels' in target_levels or 
                education_level in target_levels):
                filtered_ids.append(scholarship.id)
        
        scholarships = Scholarship.objects.filter(id__in=filtered_ids)
    
    if scholarship_type:
        scholarships = scholarships.filter(scholarship_type=scholarship_type)
    
    # Calculate statistics
    total_scholarships = scholarships.count()
    total_funding = scholarships.aggregate(
        total=Sum('amount_per_beneficiary')
    )['total'] or 0
    
    avg_amount = scholarships.aggregate(
        avg=Avg('amount_per_beneficiary')
    )['avg'] or 0
    
    # Get deadline distribution
    from datetime import datetime, timedelta
    now = timezone.now()
    
    closing_soon = scholarships.filter(
        application_deadline__lte=now + timedelta(days=30)
    ).count()
    
    stats = {
        'total_scholarships': total_scholarships,
        'total_funding': total_funding,
        'avg_amount': avg_amount,
        'closing_soon': closing_soon,
        'has_results': total_scholarships > 0
    }
    
    return JsonResponse(stats)


@require_http_methods(["GET"])
@csrf_exempt
def htmx_scholarship_quick_view(request, scholarship_id):
    """
    HTMX endpoint for scholarship quick view modal.
    Returns scholarship details in a modal format.
    """
    try:
        scholarship = Scholarship.objects.select_related('provider').prefetch_related(
            'target_counties'
        ).get(id=scholarship_id, status='active')
        
        # Calculate match score if user is authenticated
        match_score = None
        eligibility_details = {}
        user_student = None
        
        if request.user.is_authenticated:
            try:
                user_student = request.user.student_profile
                match_score = user_student.calculate_match_score(scholarship)
                
                # Get detailed eligibility information
                eligibility_details = {
                    'meets_education_level': user_student.education_level in (scholarship.target_education_levels or []),
                    'meets_county': not scholarship.target_counties.exists() or user_student.county in scholarship.target_counties.all(),
                    'meets_gender': not (scholarship.for_males_only and user_student.gender != 'M') and not (scholarship.for_females_only and user_student.gender != 'F'),
                    'meets_income': not scholarship.maximum_family_income or user_student.family_annual_income <= scholarship.maximum_family_income,
                    'meets_gpa': not scholarship.minimum_gpa or (user_student.current_gpa and user_student.current_gpa >= scholarship.minimum_gpa),
                }
            except:
                pass
        
        context = {
            'scholarship': scholarship,
            'match_score': match_score,
            'eligibility_details': eligibility_details,
            'user_student': user_student,
        }
        
        return render(request, 'scholarships/partials/scholarship_quick_view.html', context)
        
    except Scholarship.DoesNotExist:
        return JsonResponse({'error': 'Scholarship not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
