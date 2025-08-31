from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Application, Scholarship
from .sms import send_application_status_sms
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Application)
def capture_old_status(sender, instance, **kwargs):
    """
    Capture the old status before saving the application
    This is needed to detect status changes in post_save
    """
    if instance.pk:
        try:
            old_instance = Application.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Application.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Application)
def handle_application_status_change(sender, instance, created, **kwargs):
    """
    Handle application status changes and send SMS notifications
    """
    # Skip if this is a new application
    if created:
        logger.info(f"New application created: {instance.application_id}")
        return
    
    old_status = getattr(instance, '_old_status', None)
    current_status = instance.status
    
    # Skip if status hasn't changed
    if old_status == current_status:
        return
    
    # Skip if moving to draft status (shouldn't trigger SMS)
    if current_status == 'draft':
        return
    
    logger.info(f"Application {instance.application_id} status changed: {old_status} -> {current_status}")
    
    # Define which status changes should trigger SMS notifications
    notification_statuses = [
        'submitted',
        'under_review', 
        'shortlisted',
        'interview_scheduled',
        'approved',
        'rejected',
        'waitlisted'
    ]
    
    if current_status in notification_statuses:
        try:
            # Send SMS notification
            result = send_application_status_sms(instance, old_status)
            
            if result['success']:
                logger.info(f"SMS notification sent for application {instance.application_id}")
                
                # Log the communication
                communication_entry = {
                    'type': 'sms',
                    'status': 'sent',
                    'message': f'Status change notification: {old_status} -> {current_status}',
                    'timestamp': timezone.now().isoformat(),
                    'phone_number': instance.student.phone_number,
                    'recipients': result.get('recipients', [])
                }
                
                # Add to communication log
                if not instance.communication_log:
                    instance.communication_log = []
                
                instance.communication_log.append(communication_entry)
                
                # Save without triggering signals again
                Application.objects.filter(pk=instance.pk).update(
                    communication_log=instance.communication_log
                )
                
            else:
                logger.error(f"Failed to send SMS for application {instance.application_id}: {result.get('error', 'Unknown error')}")
                
                # Log the failed communication
                communication_entry = {
                    'type': 'sms',
                    'status': 'failed',
                    'message': f'Failed status change notification: {old_status} -> {current_status}',
                    'error': result.get('error', 'Unknown error'),
                    'timestamp': timezone.now().isoformat(),
                    'phone_number': instance.student.phone_number
                }
                
                if not instance.communication_log:
                    instance.communication_log = []
                
                instance.communication_log.append(communication_entry)
                
                # Save without triggering signals again
                Application.objects.filter(pk=instance.pk).update(
                    communication_log=instance.communication_log
                )
                
        except Exception as e:
            logger.error(f"Error sending SMS notification for application {instance.application_id}: {str(e)}")


@receiver(post_save, sender=Application)
def handle_application_submission(sender, instance, created, **kwargs):
    """
    Handle application submission (when status changes from draft to submitted)
    """
    if created:
        return
    
    old_status = getattr(instance, '_old_status', None)
    
    # If application was just submitted
    if old_status == 'draft' and instance.status == 'submitted':
        try:
            # Increment the scholarship's application count
            instance.scholarship.increment_application_count()
            logger.info(f"Application count incremented for scholarship: {instance.scholarship.title}")
            
            # Update submission date if not set
            if not instance.submission_date:
                instance.submission_date = timezone.now()
                Application.objects.filter(pk=instance.pk).update(
                    submission_date=instance.submission_date
                )
                
        except Exception as e:
            logger.error(f"Error handling application submission for {instance.application_id}: {str(e)}")


@receiver(post_save, sender=Application)
def handle_application_approval(sender, instance, created, **kwargs):
    """
    Handle application approval - additional processing when application is approved
    """
    if created:
        return
    
    old_status = getattr(instance, '_old_status', None)
    
    # If application was just approved
    if old_status != 'approved' and instance.status == 'approved':
        try:
            # Set decision date if not already set
            if not instance.decision_date:
                instance.decision_date = timezone.now()
                Application.objects.filter(pk=instance.pk).update(
                    decision_date=instance.decision_date
                )
            
            # Create notification for the student
            from .models import Notification
            
            notification = Notification.objects.create(
                recipient=instance.student.user,
                notification_type='application_approved',
                title=f'Scholarship Application Approved - {instance.scholarship.title}',
                message=f'Congratulations! Your application for {instance.scholarship.title} has been approved. '
                       f'Award amount: KES {instance.award_amount:,.0f} if specified. '
                       f'Please check your email for next steps and disbursement details.',
                related_application=instance,
                related_scholarship=instance.scholarship
            )
            
            logger.info(f"Approval notification created for student {instance.student.full_name}")
            
        except Exception as e:
            logger.error(f"Error handling application approval for {instance.application_id}: {str(e)}")


# Optional: Signal for scholarship view count increment
@receiver(post_save, sender=Scholarship)
def handle_scholarship_updates(sender, instance, created, **kwargs):
    """
    Handle scholarship updates - can be used for additional processing
    """
    if created:
        logger.info(f"New scholarship created: {instance.title} by {instance.provider.name}")
        
        # You can add additional logic here, such as:
        # - Sending notifications to matching students
        # - Creating audit logs
        # - Triggering external API calls
        
        try:
            # Example: Create audit log entry
            from .models import AuditLog
            
            AuditLog.objects.create(
                user=instance.created_by,
                action='create',
                model_name='Scholarship',
                object_id=str(instance.id),
                object_repr=str(instance),
                changes={
                    'title': instance.title,
                    'provider': instance.provider.name,
                    'amount': float(instance.amount_per_beneficiary),
                    'source': instance.source
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating audit log for scholarship {instance.title}: {str(e)}")


# Clean up old status attribute after saving
@receiver(post_save, sender=Application)
def cleanup_old_status(sender, instance, **kwargs):
    """
    Clean up the temporary _old_status attribute after processing
    """
    if hasattr(instance, '_old_status'):
        delattr(instance, '_old_status')
