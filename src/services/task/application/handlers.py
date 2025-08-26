from typing import Optional
from uuid import uuid4
from src.shared.events import TaskCreatedEvent, TaskUpdatedEvent, TaskCompletedEvent, TaskDeletedEvent
from src.shared.kafka_client import KafkaEventPublisher
from ..domain.services import TaskDomainService
from .commands import (
    CreateTaskCommand, UpdateTaskCommand, CompleteTaskCommand, CancelTaskCommand,
    DeleteTaskCommand, CreateCategoryCommand, UpdateCategoryCommand, DeleteCategoryCommand
)


class TaskCommandHandler:
    """Handler for task commands with event publishing"""
    
    def __init__(self, task_service: TaskDomainService, event_publisher: KafkaEventPublisher):
        self.task_service = task_service
        self.event_publisher = event_publisher
    
    async def handle_create_task(self, command: CreateTaskCommand):
        """Handle create task command"""
        task = await self.task_service.create_task(
            user_id=command.user_id,
            name=command.title,
            description=command.description,
            priority=command.priority,
            category_id=command.category_id
        )
        
        # Publish task created event
        event = TaskCreatedEvent(
            aggregate_id=str(task.id),
            aggregate_type="Task",
            data={
                "title": task.title,
                "description": task.description,
                "user_id": str(task.user_id),
                "priority": task.priority.value,
                "category_id": str(task.category_id) if task.category_id else None,
                "status": task.status.value
            }
        )
        await self.event_publisher.publish(event)
        
        return task
    
    async def handle_update_task(self, command: UpdateTaskCommand):
        """Handle update task command"""
        task = await self.task_service.update_task(
            task_id=command.task_id,
            user_id=command.user_id,
            name=command.title,
            description=command.description,
            priority=command.priority,
            category_id=command.category_id
        )
        
        if task:
            # Publish task updated event
            event = TaskUpdatedEvent(
                aggregate_id=str(task.id),
                aggregate_type="Task",
                data={
                    "title": task.title,
                    "description": task.description,
                    "user_id": str(task.user_id),
                    "priority": task.priority.value,
                    "category_id": str(task.category_id) if task.category_id else None,
                    "status": task.status.value,
                    "updated_at": task.updated_at.isoformat()
                }
            )
            await self.event_publisher.publish(event)
        
        return task
    
    async def handle_complete_task(self, command: CompleteTaskCommand):
        """Handle complete task command"""
        task = await self.task_service.complete_task(
            task_id=command.task_id,
            user_id=command.user_id
        )
        
        if task:
            # Publish task completed event
            event = TaskCompletedEvent(
                aggregate_id=str(task.id),
                aggregate_type="Task",
                data={
                    "title": task.title,
                    "user_id": str(task.user_id),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "priority": task.priority.value
                }
            )
            await self.event_publisher.publish(event)
        
        return task
    
    async def handle_cancel_task(self, command: CancelTaskCommand):
        """Handle cancel task command"""
        task = await self.task_service.cancel_task(
            task_id=command.task_id,
            user_id=command.user_id
        )
        
        if task:
            # Publish task cancelled event (using TaskUpdatedEvent for now)
            event = TaskUpdatedEvent(
                aggregate_id=str(task.id),
                aggregate_type="Task",
                data={
                    "title": task.title,
                    "user_id": str(task.user_id),
                    "status": task.status.value,
                    "updated_at": task.updated_at.isoformat()
                }
            )
            await self.event_publisher.publish(event)
        
        return task
    
    async def handle_delete_task(self, command: DeleteTaskCommand):
        """Handle delete task command"""
        # Get task info before deletion for event
        task = await self.task_service.get_task_by_id(command.task_id)
        
        success = await self.task_service.delete_task(
            task_id=command.task_id,
            user_id=command.user_id
        )
        
        if success and task:
            # Publish task deleted event
            event = TaskDeletedEvent(
                aggregate_id=str(task.id),
                aggregate_type="Task",
                data={
                    "title": task.title,
                    "user_id": str(task.user_id),
                    "deleted_at": task.updated_at.isoformat()
                }
            )
            await self.event_publisher.publish(event)
        
        return success
    
    async def handle_create_category(self, command: CreateCategoryCommand):
        """Handle create category command"""
        category = await self.task_service.create_category(
            name=command.name,
            description=command.description
        )
        
        return category
    
    async def handle_update_category(self, command: UpdateCategoryCommand):
        """Handle update category command"""
        category = await self.task_service.get_category_by_id(command.category_id)
        if not category:
            return None
        
        # Update category fields
        if command.name is not None:
            category.name = command.name
        if command.description is not None:
            category.description = command.description
        if command.color is not None:
            category.color = command.color
        
        # Save updated category
        return await self.task_service.category_repository.save(category)
    
    async def handle_delete_category(self, command: DeleteCategoryCommand):
        """Handle delete category command"""
        return await self.task_service.category_repository.delete(command.category_id)
