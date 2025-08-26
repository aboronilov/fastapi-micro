from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
import json


@dataclass
class DomainEvent:
    """Base class for all domain events"""
    event_id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    aggregate_id: str = ""
    aggregate_type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    occurred_on: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "data": self.data,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        """Create event from dictionary"""
        return cls(
            event_id=UUID(data["event_id"]),
            event_type=data["event_type"],
            aggregate_id=data["aggregate_id"],
            aggregate_type=data["aggregate_type"],
            data=data["data"],
            occurred_on=datetime.fromisoformat(data["occurred_on"]),
            version=data["version"],
            metadata=data.get("metadata", {})
        )

    def to_json(self) -> str:
        """Serialize event to JSON"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "DomainEvent":
        """Deserialize event from JSON"""
        return cls.from_dict(json.loads(json_str))


# User Domain Events
@dataclass
class UserCreatedEvent(DomainEvent):
    event_type: str = "user.created"


@dataclass
class UserUpdatedEvent(DomainEvent):
    event_type: str = "user.updated"


@dataclass
class UserDeletedEvent(DomainEvent):
    event_type: str = "user.deleted"


@dataclass
class UserAuthenticatedEvent(DomainEvent):
    event_type: str = "user.authenticated"


# Task Domain Events
@dataclass
class TaskCreatedEvent(DomainEvent):
    event_type: str = "task.created"


@dataclass
class TaskUpdatedEvent(DomainEvent):
    event_type: str = "task.updated"


@dataclass
class TaskCompletedEvent(DomainEvent):
    event_type: str = "task.completed"


@dataclass
class TaskDeletedEvent(DomainEvent):
    event_type: str = "task.deleted"


# Notification Domain Events
@dataclass
class NotificationSentEvent(DomainEvent):
    event_type: str = "notification.sent"


@dataclass
class NotificationFailedEvent(DomainEvent):
    event_type: str = "notification.failed"


# System Events
@dataclass
class HealthCheckEvent(DomainEvent):
    event_type: str = "system.health_check"


@dataclass
class ServiceStartedEvent(DomainEvent):
    event_type: str = "system.service_started"


# Event Registry
EVENT_REGISTRY = {
    "user.created": UserCreatedEvent,
    "user.updated": UserUpdatedEvent,
    "user.deleted": UserDeletedEvent,
    "user.authenticated": UserAuthenticatedEvent,
    "task.created": TaskCreatedEvent,
    "task.updated": TaskUpdatedEvent,
    "task.completed": TaskCompletedEvent,
    "task.deleted": TaskDeletedEvent,
    "notification.sent": NotificationSentEvent,
    "notification.failed": NotificationFailedEvent,
    "system.health_check": HealthCheckEvent,
    "system.service_started": ServiceStartedEvent,
}


def create_event_from_type(event_type: str, **kwargs) -> DomainEvent:
    """Create an event instance from event type"""
    if event_type not in EVENT_REGISTRY:
        raise ValueError(f"Unknown event type: {event_type}")
    
    event_class = EVENT_REGISTRY[event_type]
    return event_class(**kwargs)
