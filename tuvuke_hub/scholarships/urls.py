"""
URL configuration for scholarships app.
"""

from django.urls import path, include
from . import views, views_htmx, auth_views

app_name = 'scholarships'

urlpatterns = [
    # API URLs
    path('api/', include('scholarships.api_urls')),
    
    # Authentication URLs
    path('auth/login/', auth_views.CustomLoginView.as_view(), name='login'),
    path('auth/logout/', auth_views.custom_logout_view, name='logout'),
    path('auth/register/', auth_views.StudentRegistrationView.as_view(), name='register'),
    path('auth/password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('auth/password-reset-done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('auth/check-phone/', auth_views.check_phone_availability, name='check_phone_availability'),
    
    # Role-based Dashboard URLs
    path('student/dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('provider/dashboard/', views.ProviderDashboardView.as_view(), name='provider_dashboard'), 
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # Student URLs (require student role)
    path('student/profile/', views.student_profile_view, name='student_profile'),
    path('student/profile/complete/', auth_views.StudentProfileView.as_view(), name='student_profile_complete'),
    path('student/ajax/data/', views.student_ajax_data, name='student_ajax_data'),
    
    # Provider URLs (require provider role)
    path('provider/create-scholarship/', views.create_scholarship_view, name='create_scholarship'),
    path('provider/ajax/data/', views.provider_ajax_data, name='provider_ajax_data'),
    
    # Admin URLs (require staff role)
    path('admin/moderation/', views.admin_moderation_view, name='admin_moderation'),
    path('admin/ajax/stats/', views.admin_ajax_stats, name='admin_ajax_stats'),
    
    # Legacy Student Registration URLs (for backwards compatibility)
    path('register/', views.StudentRegistrationView.as_view(), name='register_student'),
    path('register-function/', views.register_student, name='register_student_function'),
    path('quick-register/', views.quick_register_student, name='quick_register_student'),
    
    # Student Profile URLs (legacy)
    path('profile/', views.student_profile_view, name='legacy_student_profile'),
    path('profile/update/', views.update_student_profile, name='update_student_profile'),
    path('profile/complete/', views.complete_profile, name='complete_profile'),
    
    # Legacy Dashboard (redirects to role-based dashboard)
    path('dashboard/', views.student_dashboard, name='legacy_student_dashboard'),
    
    # Public URLs (no authentication required)
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
