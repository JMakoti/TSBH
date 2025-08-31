from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Scholarship, Application, Student
from .serializers import (
    ScholarshipListSerializer, ScholarshipDetailSerializer,
    ApplicationSerializer, ApplicationCreateSerializer,
    ApplicationSubmitSerializer
)
from .filters import ScholarshipFilter, ApplicationFilter


class ScholarshipViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Scholarship model
    
    Only shows active scholarships from verified providers
    Provides filtering by county, gender, education level, and more
    """
    
    filterset_class = ScholarshipFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description', 'provider__name']
    ordering_fields = [
        'created_at', 'application_deadline', 'amount_per_beneficiary',
        'view_count', 'application_count'
    ]
    ordering = ['-created_at']  # Default ordering
    
    def get_queryset(self):
        """
        Return only active scholarships from verified providers
        """
        return Scholarship.objects.filter(
            status='active',
            provider__is_verified=True
        ).select_related('provider').prefetch_related('target_counties')
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'retrieve':
            return ScholarshipDetailSerializer
        return ScholarshipListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to increment view count"""
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def check_eligibility(self, request, pk=None):
        """
        Check if the authenticated student is eligible for this scholarship
        """
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response(
                {'detail': 'Student profile required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        scholarship = self.get_object()
        match_score = scholarship.calculate_match_score(student)
        
        # Check if already applied
        has_applied = Application.objects.filter(
            student=student, 
            scholarship=scholarship
        ).exists()
        
        return Response({
            'match_score': match_score,
            'has_applied': has_applied,
            'is_eligible': match_score > 0,
            'eligibility_details': {
                'education_level_match': student.current_education_level in scholarship.target_education_levels,
                'age_requirements_met': self._check_age_requirements(student, scholarship),
                'gender_requirements_met': self._check_gender_requirements(student, scholarship),
                'county_match': scholarship.target_counties.filter(id=student.county_id).exists() if student.county else True,
            }
        })
    
    def _check_age_requirements(self, student, scholarship):
        """Check if student meets age requirements"""
        if not scholarship.minimum_age and not scholarship.maximum_age:
            return True
        
        student_age = student.age
        if scholarship.minimum_age and student_age < scholarship.minimum_age:
            return False
        if scholarship.maximum_age and student_age > scholarship.maximum_age:
            return False
        return True
    
    def _check_gender_requirements(self, student, scholarship):
        """Check if student meets gender requirements"""
        if scholarship.for_females_only and student.gender != 'F':
            return False
        if scholarship.for_males_only and student.gender != 'M':
            return False
        return True


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Application model
    
    Allows authenticated students to view and manage their applications
    """
    
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ApplicationFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at', 'submission_date', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return only the authenticated student's applications"""
        try:
            student = self.request.user.student_profile
            return Application.objects.filter(student=student).select_related(
                'scholarship', 'scholarship__provider'
            )
        except Student.DoesNotExist:
            return Application.objects.none()
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return ApplicationCreateSerializer
        return ApplicationSerializer
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit a draft application
        """
        application = self.get_object()
        serializer = ApplicationSubmitSerializer(instance=application, data={})
        
        if serializer.is_valid():
            application.submit_application()
            return Response(
                {'detail': 'Application submitted successfully'}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        """
        Withdraw an application (only if not yet decided)
        """
        application = self.get_object()
        
        if application.status in ['approved', 'rejected']:
            return Response(
                {'detail': 'Cannot withdraw a decided application'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application.status = 'withdrawn'
        application.save()
        
        return Response(
            {'detail': 'Application withdrawn successfully'}, 
            status=status.HTTP_200_OK
        )


class ScholarshipApplicationView(APIView):
    """
    API endpoint for applying to scholarships
    POST /api/apply/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Create a new scholarship application
        
        Expected payload:
        {
            "scholarship_id": 1,
            "personal_statement": "...",
            "motivation_letter": "...",
            "career_goals": "...",
            "special_circumstances": "...",
            "reference_contacts": [...]
        }
        """
        # Get scholarship_id from request data
        scholarship_id = request.data.get('scholarship_id')
        if not scholarship_id:
            return Response(
                {'error': 'scholarship_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get scholarship object
        try:
            scholarship = Scholarship.objects.get(
                id=scholarship_id,
                status='active',
                provider__is_verified=True
            )
        except Scholarship.DoesNotExist:
            return Response(
                {'error': 'Scholarship not found or not available'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user has student profile
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile required to apply'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for duplicate application
        if Application.objects.filter(student=student, scholarship=scholarship).exists():
            return Response(
                {'error': 'You have already applied for this scholarship'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if scholarship is still accepting applications
        if not scholarship.is_active:
            return Response(
                {'error': 'This scholarship is not currently accepting applications'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare data for serializer
        application_data = request.data.copy()
        application_data['scholarship'] = scholarship.id
        
        # Create application using serializer
        serializer = ApplicationCreateSerializer(
            data=application_data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            application = serializer.save()
            
            # Return created application data
            response_serializer = ApplicationSerializer(application)
            return Response(
                {
                    'message': 'Application created successfully',
                    'application': response_serializer.data
                }, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
