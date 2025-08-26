import logging
from typing import Optional, List
from uuid import UUID
from .entities import Notification, NotificationTemplate, NotificationType, NotificationStatus
from .repositories import NotificationRepository, NotificationTemplateRepository

logger = logging.getLogger(__name__)


class NotificationService:
    """Notification domain service with business logic"""
    
    def __init__(
        self, 
        notification_repository: NotificationRepository,
        template_repository: NotificationTemplateRepository
    ):
        self.notification_repository = notification_repository
        self.template_repository = template_repository
    
    async def create_notification(
        self,
        user_id: Optional[UUID],
        type: NotificationType,
        title: str,
        message: str,
        recipient: str,
        metadata: Optional[dict] = None
    ) -> Notification:
        """Create a new notification"""
        notification = Notification.create(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            recipient=recipient,
            metadata=metadata or {}
        )
        
        return await self.notification_repository.save(notification)
    
    async def send_notification(self, notification_id: UUID) -> bool:
        """Send a notification"""
        notification = await self.notification_repository.get_by_id(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return False
        
        try:
            # Simulate sending notification based on type
            if notification.type == NotificationType.EMAIL:
                await self._send_email_notification(notification)
            elif notification.type == NotificationType.SMS:
                await self._send_sms_notification(notification)
            elif notification.type == NotificationType.PUSH:
                await self._send_push_notification(notification)
            elif notification.type == NotificationType.IN_APP:
                await self._send_in_app_notification(notification)
            else:
                raise ValueError(f"Unknown notification type: {notification.type}")
            
            # Mark as sent
            notification.mark_sent()
            await self.notification_repository.save(notification)
            
            logger.info(f"Notification {notification_id} sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification {notification_id}: {e}")
            notification.mark_failed(str(e))
            await self.notification_repository.save(notification)
            return False
    
    async def get_notification(self, notification_id: UUID) -> Optional[Notification]:
        """Get notification by ID"""
        return await self.notification_repository.get_by_id(notification_id)
    
    async def list_user_notifications(self, user_id: UUID, limit: int = 100) -> List[Notification]:
        """List notifications for a user"""
        return await self.notification_repository.list_by_user_id(user_id, limit)
    
    async def get_pending_notifications(self) -> List[Notification]:
        """Get all pending notifications"""
        return await self.notification_repository.get_pending_notifications()
    
    async def retry_failed_notification(self, notification_id: UUID) -> bool:
        """Retry a failed notification"""
        notification = await self.notification_repository.get_by_id(notification_id)
        if not notification:
            return False
        
        if not notification.can_retry():
            logger.warning(f"Notification {notification_id} cannot be retried")
            return False
        
        notification.reset_for_retry()
        await self.notification_repository.save(notification)
        
        return await self.send_notification(notification_id)
    
    async def create_template(
        self,
        name: str,
        type: NotificationType,
        subject: str,
        body: str,
        variables: Optional[dict] = None
    ) -> NotificationTemplate:
        """Create a notification template"""
        template = NotificationTemplate(
            name=name,
            type=type,
            subject=subject,
            body=body,
            variables=variables or {}
        )
        
        return await self.template_repository.save(template)
    
    async def get_template(self, template_id: UUID) -> Optional[NotificationTemplate]:
        """Get template by ID"""
        return await self.template_repository.get_by_id(template_id)
    
    async def get_template_by_name(self, name: str) -> Optional[NotificationTemplate]:
        """Get template by name"""
        return await self.template_repository.get_by_name(name)
    
    async def send_notification_from_template(
        self,
        template_name: str,
        user_id: Optional[UUID],
        recipient: str,
        variables: dict
    ) -> Optional[Notification]:
        """Send notification using a template"""
        template = await self.get_template_by_name(template_name)
        if not template:
            logger.error(f"Template {template_name} not found")
            return None
        
        subject, body = template.render(variables)
        
        notification = await self.create_notification(
            user_id=user_id,
            type=template.type,
            title=subject,
            message=body,
            recipient=recipient,
            metadata={"template": template_name, **variables}
        )
        
        await self.send_notification(notification.id)
        return notification
    
    async def _send_email_notification(self, notification: Notification):
        """Send email notification (simulated)"""
        logger.info(f"Sending email to {notification.recipient}: {notification.title}")
        # In a real implementation, this would use an email service
        # For now, we just log the action
    
    async def _send_sms_notification(self, notification: Notification):
        """Send SMS notification (simulated)"""
        logger.info(f"Sending SMS to {notification.recipient}: {notification.message}")
        # In a real implementation, this would use an SMS service
    
    async def _send_push_notification(self, notification: Notification):
        """Send push notification (simulated)"""
        logger.info(f"Sending push notification to {notification.recipient}: {notification.title}")
        # In a real implementation, this would use a push notification service
    
    async def _send_in_app_notification(self, notification: Notification):
        """Send in-app notification (simulated)"""
        logger.info(f"Sending in-app notification to {notification.recipient}: {notification.title}")
        # In a real implementation, this would store the notification for the user to see
