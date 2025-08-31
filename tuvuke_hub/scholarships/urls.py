"""
URL configuration for scholarships app.
"""

from django.urls import path, include
from . import views, views_htmx

app_name = 'scholarships'

urlpatterns = [
    # API URLs
    path('', include('scholarships.api_urls')),
    
    # Student Registration URLs
    path('register/', views.StudentRegistrationView.as_view(), name='register_student'),
    path('register-function/', views.register_student, name='register_student_function'),  # Keep function-based as alternative
    path('quick-register/', views.quick_register_student, name='quick_register_student'),
    # path('onboarding/', views.StudentOnboardingView.as_view(), name='student_onboarding'),
    
    # Student Profile URLs
    path('profile/', views.student_profile_view, name='student_profile'),
    path('profile/update/', views.update_student_profile, name='update_student_profile'),
    path('profile/complete/', views.complete_profile, name='complete_profile'),
    
    # Student Dashboard
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Search and Browse
    path('search/', views.search_students, name='search_students'),
    path('scholarships/', views.ScholarshipListView.as_view(), name='scholarship_list'),
    path('', views_htmx.scholarship_search_homepage, name='search_homepage'),
    
    # HTMX endpoints
    path('htmx/search/', views_htmx.htmx_scholarship_search, name='htmx_scholarship_search'),
    path('htmx/filters/', views_htmx.htmx_scholarship_filters, name='htmx_scholarship_filters'),
    path('htmx/stats/', views_htmx.htmx_scholarship_stats, name='htmx_scholarship_stats'),
    path('htmx/quick-view/<int:scholarship_id>/', views_htmx.htmx_scholarship_quick_view, name='htmx_scholarship_quick_view'),
    
    # AJAX endpoints
    path('ajax/sub-counties/', views.get_sub_counties, name='get_sub_counties'),
    path('ajax/validate-national-id/', views.validate_national_id, name='validate_national_id'),
    path('ajax/validate-phone/', views.validate_phone_number, name='validate_phone_number'),
]
