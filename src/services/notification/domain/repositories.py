from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from .entities import Notification, NotificationTemplate


class NotificationRepository(ABC):
    """Notification repository interface"""
    
    @abstractmethod
    async def save(self, notification: Notification) -> Notification:
        """Save notification to repository"""
        pass
    
    @abstractmethod
    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        """Get notification by ID"""
        pass
    
    @abstractmethod
    async def get_pending_notifications(self) -> List[Notification]:
        """Get all pending notifications"""
        pass
    
    @abstractmethod
    async def list_by_user_id(self, user_id: UUID, limit: int = 100) -> List[Notification]:
        """List notifications by user ID"""
        pass
    
    @abstractmethod
    async def delete(self, notification_id: UUID) -> bool:
        """Delete notification by ID"""
        pass


class NotificationTemplateRepository(ABC):
    """Notification template repository interface"""
    
    @abstractmethod
    async def save(self, template: NotificationTemplate) -> NotificationTemplate:
        """Save template to repository"""
        pass
    
    @abstractmethod
    async def get_by_id(self, template_id: UUID) -> Optional[NotificationTemplate]:
        """Get template by ID"""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[NotificationTemplate]:
        """Get template by name"""
        pass
    
    @abstractmethod
    async def list_active_templates(self) -> List[NotificationTemplate]:
        """List all active templates"""
        pass
    
    @abstractmethod
    async def delete(self, template_id: UUID) -> bool:
        """Delete template by ID"""
        pass
