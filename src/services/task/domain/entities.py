from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Category:
    """Task category domain entity"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    color: str = "#000000"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def update(self, name: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None):
        """Update category"""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if color is not None:
            self.color = color
        self.updated_at = datetime.utcnow()


@dataclass
class Task:
    """Task domain entity"""
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    user_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(cls, title: str, description: str, user_id: UUID, 
               category_id: Optional[UUID] = None, priority: TaskPriority = TaskPriority.MEDIUM,
               due_date: Optional[datetime] = None) -> "Task":
        """Create a new task"""
        return cls(
            title=title,
            description=description,
            user_id=user_id,
            category_id=category_id,
            priority=priority,
            due_date=due_date
        )
    
    def start(self):
        """Start the task"""
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.IN_PROGRESS
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError(f"Cannot start task with status: {self.status}")
    
    def complete(self):
        """Complete the task"""
        if self.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
            self.status = TaskStatus.COMPLETED
            self.completed_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError(f"Cannot complete task with status: {self.status}")
    
    def cancel(self):
        """Cancel the task"""
        if self.status != TaskStatus.COMPLETED:
            self.status = TaskStatus.CANCELLED
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError("Cannot cancel completed task")
    
    def reopen(self):
        """Reopen the task"""
        if self.status == TaskStatus.COMPLETED:
            self.status = TaskStatus.PENDING
            self.completed_at = None
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError(f"Cannot reopen task with status: {self.status}")
    
    def update(self, title: Optional[str] = None, description: Optional[str] = None,
               priority: Optional[TaskPriority] = None, category_id: Optional[UUID] = None,
               due_date: Optional[datetime] = None):
        """Update task details"""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority
        if category_id is not None:
            self.category_id = category_id
        if due_date is not None:
            self.due_date = due_date
        self.updated_at = datetime.utcnow()
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.due_date and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return datetime.utcnow() > self.due_date
        return False
    
    @property
    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status == TaskStatus.COMPLETED
    
    @property
    def is_active(self) -> bool:
        """Check if task is active (not completed or cancelled)"""
        return self.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
