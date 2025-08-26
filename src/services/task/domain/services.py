from typing import List, Optional
from uuid import UUID
from .entities import Task, Category, TaskStatus, TaskPriority
from .repositories import TaskRepository, CategoryRepository


class TaskDomainService:
    """Task domain service with business logic"""
    
    def __init__(self, task_repository: Optional[TaskRepository] = None, category_repository: Optional[CategoryRepository] = None):
        self.task_repository = task_repository
        self.category_repository = category_repository
    
    async def create_task(
        self, 
        user_id: UUID, 
        name: str, 
        description: str = "", 
        priority: TaskPriority = TaskPriority.MEDIUM,
        category_id: Optional[UUID] = None
    ) -> Task:
        """Create a new task with business validation"""
        # Validate category if provided
        if category_id:
            category = await self.category_repository.get_by_id(category_id)
            if not category:
                raise ValueError("Category not found")
        
        # Create task
        task = Task.create(
            user_id=user_id,
            name=name,
            description=description,
            priority=priority,
            category_id=category_id
        )
        
        return await self.task_repository.save(task)
    
    async def get_task_by_id(self, task_id: UUID) -> Optional[Task]:
        """Get task by ID"""
        return await self.task_repository.get_by_id(task_id)
    
    async def list_user_tasks(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Task]:
        """List tasks for a specific user"""
        return await self.task_repository.list_by_user_id(user_id, skip, limit)
    
    async def complete_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """Complete a task"""
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            return None
        
        # Verify task belongs to user
        if task.user_id != user_id:
            raise ValueError("Task does not belong to user")
        
        # Complete the task
        task.complete()
        return await self.task_repository.save(task)
    
    async def cancel_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """Cancel a task"""
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            return None
        
        # Verify task belongs to user
        if task.user_id != user_id:
            raise ValueError("Task does not belong to user")
        
        # Cancel the task
        task.cancel()
        return await self.task_repository.save(task)
    
    async def update_task(
        self, 
        task_id: UUID, 
        user_id: UUID, 
        name: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[TaskPriority] = None,
        category_id: Optional[UUID] = None
    ) -> Optional[Task]:
        """Update a task"""
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            return None
        
        # Verify task belongs to user
        if task.user_id != user_id:
            raise ValueError("Task does not belong to user")
        
        # Validate category if provided
        if category_id:
            category = await self.category_repository.get_by_id(category_id)
            if not category:
                raise ValueError("Category not found")
        
        # Update task
        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority
        if category_id is not None:
            task.category_id = category_id
        
        return await self.task_repository.save(task)
    
    async def delete_task(self, task_id: UUID, user_id: UUID) -> bool:
        """Delete a task"""
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            return False
        
        # Verify task belongs to user
        if task.user_id != user_id:
            raise ValueError("Task does not belong to user")
        
        return await self.task_repository.delete(task_id)
    
    # Category management
    async def create_category(self, name: str, description: str = "") -> Category:
        """Create a new category"""
        # Check if category already exists
        existing_category = await self.category_repository.get_by_name(name)
        if existing_category:
            raise ValueError("Category with this name already exists")
        
        category = Category.create(name=name, description=description)
        return await self.category_repository.save(category)
    
    async def get_category_by_id(self, category_id: UUID) -> Optional[Category]:
        """Get category by ID"""
        return await self.category_repository.get_by_id(category_id)
    
    async def list_categories(self) -> List[Category]:
        """List all categories"""
        return await self.category_repository.list_categories()
