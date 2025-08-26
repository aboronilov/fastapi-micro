from typing import Optional
from uuid import UUID
from src.services.user.domain.services import UserDomainService
from src.services.task.domain.services import TaskDomainService
from src.services.task.domain.entities import TaskPriority
from src.services.notification.domain.services import NotificationService
from src.services.notification.domain.entities import NotificationType
from src.shared.kafka_client import KafkaEventPublisher
from src.shared.events import UserCreatedEvent, TaskCompletedEvent


class ServiceOrchestrator:
    """Orchestrates interactions between different domain services"""
    
    def __init__(
        self,
        user_service: UserDomainService,
        task_service: TaskDomainService,
        notification_service: NotificationService,
        event_publisher: KafkaEventPublisher
    ):
        self.user_service = user_service
        self.task_service = task_service
        self.notification_service = notification_service
        self.event_publisher = event_publisher
    
    async def create_user_with_welcome_task(
        self, 
        email: str, 
        username: str, 
        password: str
    ):
        """Create a user and automatically create a welcome task"""
        # Create user
        user = await self.user_service.create_user(email, username, password)
        
        # Publish user created event
        event = UserCreatedEvent(
            aggregate_id=str(user.id),
            aggregate_type="User",
            data={
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "is_verified": user.is_verified
            }
        )
        await self.event_publisher.publish(event)
        
        # Create welcome task for the new user
        welcome_task = await self.task_service.create_task(
            user_id=user.id,
            name="Welcome to the platform!",
            description="This is your first task. Complete it to get started!",
            priority=TaskPriority.LOW
        )
        
        return {
            "user": user,
            "welcome_task": welcome_task
        }
    
    async def complete_task_with_notification(
        self, 
        task_id: UUID, 
        user_id: UUID
    ):
        """Complete a task and send notification"""
        # Complete the task
        task = await self.task_service.complete_task(task_id, user_id)
        if not task:
            raise ValueError("Task not found or does not belong to user")
        
        # Publish task completed event
        event = TaskCompletedEvent(
            aggregate_id=str(task.id),
            aggregate_type="Task",
            data={
                "task_title": task.title,
                "user_id": str(task.user_id),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
        )
        await self.event_publisher.publish(event)
        
        # Get user for notification
        user = await self.user_service.get_user_by_id(user_id)
        if user:
            # Send completion notification
            await self.notification_service.create_notification(
                user_id=user_id,
                type=NotificationType.EMAIL,
                title="Task Completed!",
                message=f"Congratulations! You've completed the task: {task.title}",
                recipient=user.email
            )
        
        return task
    
    async def get_user_dashboard_data(self, user_id: UUID):
        """Get comprehensive dashboard data for a user"""
        # Get user
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Get user tasks
        tasks = await self.task_service.list_user_tasks(user_id)
        
        # Get user notifications (if implemented)
        # notifications = await self.notification_service.get_user_notifications(user_id)
        
        return {
            "user": user,
            "tasks": tasks,
            "task_count": len(tasks),
            "completed_tasks": len([t for t in tasks if t.status == "COMPLETED"]),
            "pending_tasks": len([t for t in tasks if t.status == "PENDING"])
        }
    
    async def delete_user_with_cleanup(self, user_id: UUID):
        """Delete user and clean up related data"""
        # Get user first
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Delete all user tasks
        user_tasks = await self.task_service.list_user_tasks(user_id)
        for task in user_tasks:
            await self.task_service.delete_task(task.id, user_id)
        
        # Delete user
        await self.user_service.user_repository.delete(user_id)
        
        return {"message": "User and all related data deleted successfully"}
