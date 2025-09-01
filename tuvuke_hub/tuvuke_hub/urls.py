"""
URL configuration for tuvuke_hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from scholarships.admin import admin_site
from scholarships.access_control import is_student, is_provider, is_staff_or_admin

def home_redirect(request):
    """Redirect root URL based on user role"""
    if request.user.is_authenticated:
        # Role-based redirection
        if is_student(request.user):
            return redirect('scholarships:student_dashboard')
        elif is_provider(request.user):
            return redirect('scholarships:provider_dashboard')
        elif is_staff_or_admin(request.user):
            return redirect('scholarships:admin_dashboard')
        else:
            # User is authenticated but has no specific role
            return redirect('scholarships:scholarship_list')
    else:
        # Unauthenticated users see scholarship listings
        return redirect('scholarships:scholarship_list')

urlpatterns = [
    path("admin/", admin.site.urls),  # Default Django admin (staff only)
    path("tuvuke-admin/", admin_site.urls),  # Custom admin with analytics (staff only)
    path("", home_redirect, name='home'),  # Root URL redirects based on user role
    
    # Authentication URLs (using built-in Django auth as fallback)
    path("auth/", include('django.contrib.auth.urls')),  # Django's built-in auth views
    
    # Main application URLs
    path("", include('scholarships.urls')),  # Scholarships app URLs (includes auth)
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
