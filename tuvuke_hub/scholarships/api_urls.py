from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ScholarshipViewSet, ApplicationViewSet, ScholarshipApplicationView

# Create API router
router = DefaultRouter()
router.register(r'scholarships', ScholarshipViewSet, basename='scholarship')
router.register(r'applications', ApplicationViewSet, basename='application')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/apply/', ScholarshipApplicationView.as_view(), name='scholarship-apply'),
    
    # DRF authentication views
    path('api-auth/', include('rest_framework.urls')),
]
