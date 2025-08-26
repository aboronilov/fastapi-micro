import asyncio
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from src.database.models import Notification as NotificationModel, NotificationTemplate as NotificationTemplateModel
from ..domain.entities import Notification, NotificationTemplate
from ..domain.repositories import NotificationRepository, NotificationTemplateRepository


class SQLAlchemyNotificationRepository(NotificationRepository):
    """SQLAlchemy implementation of NotificationRepository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save(self, notification: Notification) -> Notification:
        """Save notification to database"""
        # Convert domain entity to model
        notification_model = NotificationModel(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type.value,
            title=notification.title,
            message=notification.message,
            recipient=notification.recipient,
            status=notification.status.value,
            metadata=notification.metadata,
            created_at=notification.created_at,
            updated_at=notification.updated_at
        )
        
        # Check if notification exists
        existing_notification = await asyncio.to_thread(
            lambda: self.db.query(NotificationModel).filter(NotificationModel.id == notification.id).first()
        )
        
        if existing_notification:
            # Update existing notification
            await asyncio.to_thread(
                lambda: self.db.execute(
                    update(NotificationModel)
                    .where(NotificationModel.id == notification.id)
                    .values(
                        user_id=notification.user_id,
                        type=notification.type.value,
                        title=notification.title,
                        message=notification.message,
                        recipient=notification.recipient,
                        status=notification.status.value,
                        metadata=notification.metadata,
                        updated_at=notification.updated_at
                    )
                )
            )
        else:
            # Create new notification
            await asyncio.to_thread(lambda: self.db.add(notification_model))
        
        await asyncio.to_thread(lambda: self.db.commit())
        await asyncio.to_thread(lambda: self.db.refresh(notification_model))
        
        # Convert back to domain entity
        return self._to_domain_entity(notification_model)
    
    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        """Get notification by ID"""
        notification_model = await asyncio.to_thread(
            lambda: self.db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
        )
        return self._to_domain_entity(notification_model) if notification_model else None
    
    async def get_pending_notifications(self) -> List[Notification]:
        """Get all pending notifications"""
        notifications = await asyncio.to_thread(
            lambda: self.db.query(NotificationModel).filter(NotificationModel.status == 'pending').all()
        )
        return [self._to_domain_entity(notification) for notification in notifications]
    
    async def list_by_user_id(self, user_id: UUID, limit: int = 100) -> List[Notification]:
        """List notifications by user ID"""
        notifications = await asyncio.to_thread(
            lambda: self.db.query(NotificationModel)
            .filter(NotificationModel.user_id == user_id)
            .limit(limit)
            .all()
        )
        return [self._to_domain_entity(notification) for notification in notifications]
    
    async def delete(self, notification_id: UUID) -> bool:
        """Delete notification by ID"""
        result = await asyncio.to_thread(
            lambda: self.db.execute(
                delete(NotificationModel).where(NotificationModel.id == notification_id)
            )
        )
        await asyncio.to_thread(lambda: self.db.commit())
        return result.rowcount > 0
    
    def _to_domain_entity(self, notification_model: NotificationModel) -> Notification:
        """Convert SQLAlchemy model to domain entity"""
        from ..domain.entities import NotificationType, NotificationStatus
        
        return Notification(
            id=notification_model.id,
            user_id=notification_model.user_id,
            type=NotificationType(notification_model.type),
            title=notification_model.title,
            message=notification_model.message,
            recipient=notification_model.recipient,
            status=NotificationStatus(notification_model.status),
            metadata=notification_model.metadata or {},
            created_at=notification_model.created_at,
            updated_at=notification_model.updated_at
        )


class SQLAlchemyNotificationTemplateRepository(NotificationTemplateRepository):
    """SQLAlchemy implementation of NotificationTemplateRepository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save(self, template: NotificationTemplate) -> NotificationTemplate:
        """Save template to database"""
        # Convert domain entity to model
        template_model = NotificationTemplateModel(
            id=template.id,
            name=template.name,
            type=template.type.value,
            subject=template.subject,
            body=template.body,
            variables=template.variables,
            is_active=template.is_active,
            created_at=template.created_at,
            updated_at=template.updated_at
        )
        
        # Check if template exists
        existing_template = await asyncio.to_thread(
            lambda: self.db.query(NotificationTemplateModel).filter(NotificationTemplateModel.id == template.id).first()
        )
        
        if existing_template:
            # Update existing template
            await asyncio.to_thread(
                lambda: self.db.execute(
                    update(NotificationTemplateModel)
                    .where(NotificationTemplateModel.id == template.id)
                    .values(
                        name=template.name,
                        type=template.type.value,
                        subject=template.subject,
                        body=template.body,
                        variables=template.variables,
                        is_active=template.is_active,
                        updated_at=template.updated_at
                    )
                )
            )
        else:
            # Create new template
            await asyncio.to_thread(lambda: self.db.add(template_model))
        
        await asyncio.to_thread(lambda: self.db.commit())
        await asyncio.to_thread(lambda: self.db.refresh(template_model))
        
        # Convert back to domain entity
        return self._to_domain_entity(template_model)
    
    async def get_by_id(self, template_id: UUID) -> Optional[NotificationTemplate]:
        """Get template by ID"""
        template_model = await asyncio.to_thread(
            lambda: self.db.query(NotificationTemplateModel).filter(NotificationTemplateModel.id == template_id).first()
        )
        return self._to_domain_entity(template_model) if template_model else None
    
    async def get_by_name(self, name: str) -> Optional[NotificationTemplate]:
        """Get template by name"""
        template_model = await asyncio.to_thread(
            lambda: self.db.query(NotificationTemplateModel).filter(NotificationTemplateModel.name == name).first()
        )
        return self._to_domain_entity(template_model) if template_model else None
    
    async def list_active_templates(self) -> List[NotificationTemplate]:
        """List all active templates"""
        templates = await asyncio.to_thread(
            lambda: self.db.query(NotificationTemplateModel).filter(NotificationTemplateModel.is_active == True).all()
        )
        return [self._to_domain_entity(template) for template in templates]
    
    async def delete(self, template_id: UUID) -> bool:
        """Delete template by ID"""
        result = await asyncio.to_thread(
            lambda: self.db.execute(
                delete(NotificationTemplateModel).where(NotificationTemplateModel.id == template_id)
            )
        )
        await asyncio.to_thread(lambda: self.db.commit())
        return result.rowcount > 0
    
    def _to_domain_entity(self, template_model: NotificationTemplateModel) -> NotificationTemplate:
        """Convert SQLAlchemy model to domain entity"""
        from ..domain.entities import NotificationType
        
        return NotificationTemplate(
            id=template_model.id,
            name=template_model.name,
            type=NotificationType(template_model.type),
            subject=template_model.subject,
            body=template_model.body,
            variables=template_model.variables or {},
            is_active=template_model.is_active,
            created_at=template_model.created_at,
            updated_at=template_model.updated_at
        )
