from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from uuid import UUID
from ..domain.entities import TaskPriority


@dataclass
class CreateTaskCommand:
    """Command to create a new task"""
    user_id: UUID
    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    category_id: Optional[UUID] = None
    due_date: Optional[datetime] = None


@dataclass
class UpdateTaskCommand:
    """Command to update an existing task"""
    task_id: UUID
    user_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    category_id: Optional[UUID] = None
    due_date: Optional[datetime] = None


@dataclass
class CompleteTaskCommand:
    """Command to complete a task"""
    task_id: UUID
    user_id: UUID


@dataclass
class CancelTaskCommand:
    """Command to cancel a task"""
    task_id: UUID
    user_id: UUID


@dataclass
class DeleteTaskCommand:
    """Command to delete a task"""
    task_id: UUID
    user_id: UUID


@dataclass
class CreateCategoryCommand:
    """Command to create a new category"""
    name: str
    description: str = ""
    color: str = "#000000"


@dataclass
class UpdateCategoryCommand:
    """Command to update an existing category"""
    category_id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


@dataclass
class DeleteCategoryCommand:
    """Command to delete a category"""
    category_id: UUID
