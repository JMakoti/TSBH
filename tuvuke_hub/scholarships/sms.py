import africastalking
import logging
from django.conf import settings
from typing import Optional, Dict, Any

# Set up logging
logger = logging.getLogger(__name__)


class SMSService:
    """
    SMS Service using Africa's Talking API
    """
    
    def __init__(self):
        """Initialize the SMS service with Africa's Talking credentials"""
        username = getattr(settings, 'AFRICASTALKING_USERNAME', '')
        api_key = getattr(settings, 'AFRICASTALKING_API_KEY', '')
        
        if not username or not api_key:
            logger.warning("Africa's Talking credentials not configured")
            self.initialized = False
            return
        
        try:
            # Initialize Africa's Talking
            africastalking.initialize(username, api_key)
            self.sms = africastalking.SMS
            self.initialized = True
            logger.info("Africa's Talking SMS service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Africa's Talking: {str(e)}")
            self.initialized = False
    
    def send_sms(self, phone_number: str, message: str, sender_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send SMS to a phone number
        
        Args:
            phone_number (str): Phone number in international format (+254XXXXXXXXX)
            message (str): SMS message content
            sender_id (str, optional): Sender ID (if configured)
        
        Returns:
            dict: Response from Africa's Talking API
        """
        if not self.initialized:
            logger.error("SMS service not initialized")
            return {
                'success': False,
                'error': 'SMS service not configured',
                'recipients': []
            }
        
        try:
            # Ensure phone number is in correct format
            if not phone_number.startswith('+'):
                if phone_number.startswith('254'):
                    phone_number = '+' + phone_number
                elif phone_number.startswith('0'):
                    phone_number = '+254' + phone_number[1:]
                else:
                    phone_number = '+254' + phone_number
            
            # Prepare SMS parameters
            sms_params = {
                'to': [phone_number],
                'message': message
            }
            
            if sender_id:
                sms_params['from_'] = sender_id
            
            # Send SMS
            response = self.sms.send(**sms_params)
            
            logger.info(f"SMS sent to {phone_number}: {response}")
            return {
                'success': True,
                'response': response,
                'recipients': response.get('SMSMessageData', {}).get('Recipients', [])
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'recipients': []
            }
    
    def send_bulk_sms(self, phone_numbers: list, message: str, sender_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send SMS to multiple phone numbers
        
        Args:
            phone_numbers (list): List of phone numbers
            message (str): SMS message content
            sender_id (str, optional): Sender ID (if configured)
        
        Returns:
            dict: Response from Africa's Talking API
        """
        if not self.initialized:
            logger.error("SMS service not initialized")
            return {
                'success': False,
                'error': 'SMS service not configured',
                'recipients': []
            }
        
        if not phone_numbers:
            return {
                'success': False,
                'error': 'No phone numbers provided',
                'recipients': []
            }
        
        try:
            # Format all phone numbers
            formatted_numbers = []
            for number in phone_numbers:
                if not number.startswith('+'):
                    if number.startswith('254'):
                        number = '+' + number
                    elif number.startswith('0'):
                        number = '+254' + number[1:]
                    else:
                        number = '+254' + number
                formatted_numbers.append(number)
            
            # Prepare SMS parameters
            sms_params = {
                'to': formatted_numbers,
                'message': message
            }
            
            if sender_id:
                sms_params['from_'] = sender_id
            
            # Send SMS
            response = self.sms.send(**sms_params)
            
            logger.info(f"Bulk SMS sent to {len(formatted_numbers)} numbers: {response}")
            return {
                'success': True,
                'response': response,
                'recipients': response.get('SMSMessageData', {}).get('Recipients', [])
            }
            
        except Exception as e:
            logger.error(f"Failed to send bulk SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'recipients': []
            }


# Create a global instance
sms_service = SMSService()


def send_sms(phone_number: str, message: str, sender_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Utility function to send SMS
    
    Args:
        phone_number (str): Phone number in any format
        message (str): SMS message content
        sender_id (str, optional): Sender ID
    
    Returns:
        dict: Response indicating success/failure
    """
    return sms_service.send_sms(phone_number, message, sender_id)


def send_bulk_sms(phone_numbers: list, message: str, sender_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Utility function to send bulk SMS
    
    Args:
        phone_numbers (list): List of phone numbers
        message (str): SMS message content
        sender_id (str, optional): Sender ID
    
    Returns:
        dict: Response indicating success/failure
    """
    return sms_service.send_bulk_sms(phone_numbers, message, sender_id)


def send_application_status_sms(application, old_status: Optional[str] = None) -> Dict[str, Any]:
    """
    Send SMS notification for application status change
    
    Args:
        application: Application instance
        old_status (str, optional): Previous status for comparison
    
    Returns:
        dict: Response indicating success/failure
    """
    if not application.student.phone_number:
        logger.warning(f"No phone number for student {application.student.full_name}")
        return {
            'success': False,
            'error': 'No phone number available',
            'recipients': []
        }
    
    # Create status-specific messages
    status_messages = {
        'submitted': f"Dear {application.student.first_name}, your application for {application.scholarship.title} has been submitted successfully. Application ID: {application.application_id}",
        
        'under_review': f"Dear {application.student.first_name}, your application for {application.scholarship.title} is now under review. We will notify you of any updates.",
        
        'shortlisted': f"Congratulations {application.student.first_name}! You have been shortlisted for {application.scholarship.title}. Please check your email for next steps.",
        
        'interview_scheduled': f"Dear {application.student.first_name}, an interview has been scheduled for your {application.scholarship.title} application. Check your email for details.",
        
        'approved': f"Congratulations {application.student.first_name}! Your application for {application.scholarship.title} has been APPROVED! Award amount: KES {application.award_amount:,.0f}. Check your email for details.",
        
        'rejected': f"Dear {application.student.first_name}, we regret to inform you that your application for {application.scholarship.title} was not successful. Keep applying for other opportunities!",
        
        'waitlisted': f"Dear {application.student.first_name}, your application for {application.scholarship.title} has been waitlisted. You may be considered if slots become available.",
        
        'withdrawn': f"Dear {application.student.first_name}, your application for {application.scholarship.title} has been withdrawn as requested."
    }
    
    message = status_messages.get(application.status)
    if not message:
        logger.warning(f"No SMS template for status: {application.status}")
        return {
            'success': False,
            'error': f'No message template for status: {application.status}',
            'recipients': []
        }
    
    # Add Tuvuke Hub signature
    message += " - Tuvuke Hub"
    
    # Send SMS
    result = send_sms(application.student.phone_number, message)
    
    if result['success']:
        logger.info(f"SMS sent to {application.student.full_name} for status change: {old_status} -> {application.status}")
    else:
        logger.error(f"Failed to send SMS to {application.student.full_name}: {result.get('error', 'Unknown error')}")
    
    return result


def send_scholarship_deadline_reminder(scholarship, days_remaining: int) -> Dict[str, Any]:
    """
    Send deadline reminder SMS to students who haven't applied
    
    Args:
        scholarship: Scholarship instance
        days_remaining (int): Number of days until deadline
    
    Returns:
        dict: Response indicating success/failure
    """
    from .models import Student, Application
    
    # Get students who might be interested but haven't applied
    applied_student_ids = Application.objects.filter(
        scholarship=scholarship
    ).values_list('student_id', flat=True)
    
    # Get students who match the scholarship criteria
    potential_students = Student.objects.filter(
        is_verified=True,
        phone_number__isnull=False
    ).exclude(id__in=applied_student_ids)
    
    # Filter by education level if specified
    if scholarship.target_education_levels:
        potential_students = potential_students.filter(
            current_education_level__in=scholarship.target_education_levels
        )
    
    # Filter by county if specified
    if scholarship.target_counties.exists():
        potential_students = potential_students.filter(
            county__in=scholarship.target_counties.all()
        )
    
    # Limit to first 100 students to avoid spam
    potential_students = potential_students[:100]
    
    if not potential_students.exists():
        return {
            'success': True,
            'message': 'No eligible students found',
            'recipients': []
        }
    
    # Create reminder message
    message = f"Reminder: Only {days_remaining} days left to apply for {scholarship.title} ({scholarship.provider.name}). Award: KES {scholarship.amount_per_beneficiary:,.0f}. Apply now! - Tuvuke Hub"
    
    # Get phone numbers
    phone_numbers = [student.phone_number for student in potential_students if student.phone_number]
    
    if not phone_numbers:
        return {
            'success': False,
            'error': 'No phone numbers available',
            'recipients': []
        }
    
    # Send bulk SMS
    result = send_bulk_sms(phone_numbers, message)
    
    logger.info(f"Deadline reminder sent for {scholarship.title} to {len(phone_numbers)} students")
    return result
