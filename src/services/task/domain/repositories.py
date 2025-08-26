from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from .entities import Task, Category


class TaskRepository(ABC):
    """Task repository interface"""
    
    @abstractmethod
    async def save(self, task: Task) -> Task:
        """Save task to repository"""
        pass
    
    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """Get task by ID"""
        pass
    
    @abstractmethod
    async def list_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Task]:
        """List tasks by user ID with pagination"""
        pass
    
    @abstractmethod
    async def list_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """List all tasks with pagination"""
        pass
    
    @abstractmethod
    async def delete(self, task_id: UUID) -> bool:
        """Delete task by ID"""
        pass


class CategoryRepository(ABC):
    """Category repository interface"""
    
    @abstractmethod
    async def save(self, category: Category) -> Category:
        """Save category to repository"""
        pass
    
    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        """Get category by ID"""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name"""
        pass
    
    @abstractmethod
    async def list_categories(self) -> List[Category]:
        """List all categories"""
        pass
    
    @abstractmethod
    async def delete(self, category_id: UUID) -> bool:
        """Delete category by ID"""
        pass
