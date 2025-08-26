from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from uuid import UUID, uuid4


class NotificationType(Enum):
    """Notification type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(Enum):
    """Notification status enumeration"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"


@dataclass
class Notification:
    """Notification domain entity"""
    id: UUID = field(default_factory=uuid4)
    user_id: Optional[UUID] = None
    type: NotificationType = NotificationType.EMAIL
    title: str = ""
    message: str = ""
    status: NotificationStatus = NotificationStatus.PENDING
    recipient: str = ""  # email, phone, or user_id
    metadata: Dict[str, Any] = field(default_factory=dict)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(cls, user_id: Optional[UUID], type: NotificationType, title: str, 
               message: str, recipient: str, metadata: Optional[Dict[str, Any]] = None) -> "Notification":
        """Create a new notification"""
        return cls(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            recipient=recipient,
            metadata=metadata or {}
        )
    
    def mark_sent(self):
        """Mark notification as sent"""
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_delivered(self):
        """Mark notification as delivered"""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_failed(self, error_message: str):
        """Mark notification as failed"""
        self.status = NotificationStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.utcnow()
    
    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
        self.updated_at = datetime.utcnow()
    
    def can_retry(self) -> bool:
        """Check if notification can be retried"""
        return self.status == NotificationStatus.FAILED and self.retry_count < self.max_retries
    
    def reset_for_retry(self):
        """Reset notification for retry"""
        if self.can_retry():
            self.status = NotificationStatus.PENDING
            self.error_message = None
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError("Cannot retry notification - max retries exceeded or not failed")


@dataclass
class NotificationTemplate:
    """Notification template domain entity"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    type: NotificationType = NotificationType.EMAIL
    subject: str = ""
    body: str = ""
    variables: Dict[str, str] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def render(self, variables: Dict[str, str]) -> tuple[str, str]:
        """Render template with variables"""
        subject = self.subject
        body = self.body
        
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))
        
        return subject, body
    
    def update(self, subject: Optional[str] = None, body: Optional[str] = None,
               variables: Optional[Dict[str, str]] = None, is_active: Optional[bool] = None):
        """Update template"""
        if subject is not None:
            self.subject = subject
        if body is not None:
            self.body = body
        if variables is not None:
            self.variables = variables
        if is_active is not None:
            self.is_active = is_active
        self.updated_at = datetime.utcnow()
