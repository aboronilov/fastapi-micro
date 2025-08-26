import logging
from typing import Dict, Any
from src.shared.events import DomainEvent, UserCreatedEvent, TaskCompletedEvent
from src.shared.kafka_client import KafkaEventPublisher
from ..domain.entities import Notification, NotificationType
from ..domain.services import NotificationService

logger = logging.getLogger(__name__)


class NotificationEventHandler:
    """Event handler for notification service"""
    
    def __init__(self, notification_service: NotificationService, event_publisher: KafkaEventPublisher):
        self.notification_service = notification_service
        self.event_publisher = event_publisher
    
    async def handle_user_created(self, event: UserCreatedEvent):
        """Handle user created event - send welcome email"""
        try:
            user_data = event.data
            email = user_data.get("email")
            username = user_data.get("username")
            
            if email:
                # Create welcome notification
                notification = await self.notification_service.create_notification(
                    user_id=event.aggregate_id,
                    type=NotificationType.EMAIL,
                    title="Welcome to Our Platform!",
                    message=f"Hi {username}, welcome to our platform! We're excited to have you on board.",
                    recipient=email,
                    metadata={
                        "template": "welcome_email",
                        "user_id": event.aggregate_id,
                        "username": username
                    }
                )
                
                # Send the notification
                await self.notification_service.send_notification(notification.id)
                
                logger.info(f"Welcome notification sent to user {event.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error handling user created event: {e}")
    
    async def handle_task_completed(self, event: TaskCompletedEvent):
        """Handle task completed event - send completion notification"""
        try:
            task_data = event.data
            user_id = task_data.get("user_id")
            task_title = task_data.get("title", "Task")
            
            if user_id:
                # Create task completion notification
                notification = await self.notification_service.create_notification(
                    user_id=user_id,
                    type=NotificationType.IN_APP,
                    title="Task Completed!",
                    message=f"Congratulations! You've completed the task: {task_title}",
                    recipient=user_id,
                    metadata={
                        "template": "task_completed",
                        "task_id": event.aggregate_id,
                        "task_title": task_title
                    }
                )
                
                # Send the notification
                await self.notification_service.send_notification(notification.id)
                
                logger.info(f"Task completion notification sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling task completed event: {e}")
    
    async def handle_generic_event(self, event: DomainEvent):
        """Handle generic events for logging and monitoring"""
        try:
            logger.info(f"Received event: {event.event_type} for aggregate {event.aggregate_id}")
            
            # You can add more generic event handling logic here
            # For example, audit logging, analytics, etc.
            
        except Exception as e:
            logger.error(f"Error handling generic event: {e}")


class NotificationEventConsumer:
    """Consumer for notification-related events"""
    
    def __init__(self, event_handler: NotificationEventHandler):
        self.event_handler = event_handler
    
    async def start_consuming(self):
        """Start consuming events"""
        # This would be called when the notification service starts
        # In a real implementation, this would connect to Kafka and start consuming
        logger.info("Notification event consumer started")
    
    async def stop(self):
        """Stop consuming events"""
        logger.info("Notification event consumer stopped")
