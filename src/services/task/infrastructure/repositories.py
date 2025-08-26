from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..domain.repositories import TaskRepository, CategoryRepository
from ..domain.entities import Task, Category, TaskStatus, TaskPriority


class SQLAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy implementation of TaskRepository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save(self, task: Task) -> Task:
        """Save a task"""
        # Convert domain entity to SQLAlchemy model
        from src.database.models import Task as TaskModel
        
        task_model = TaskModel(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            priority=task.priority.value,
            user_id=task.user_id,
            category_id=task.category_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at
        )
        
        self.db.add(task_model)
        self.db.commit()
        self.db.refresh(task_model)
        
        # Convert back to domain entity
        return self._to_domain_entity(task_model)
    
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """Get task by ID"""
        from src.database.models import Task as TaskModel
        
        task_model = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task_model:
            return None
        
        return self._to_domain_entity(task_model)
    
    async def get_by_user_id(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get tasks by user ID"""
        from src.database.models import Task as TaskModel
        
        task_models = self.db.query(TaskModel).filter(
            TaskModel.user_id == user_id
        ).offset(skip).limit(limit).all()
        
        return [self._to_domain_entity(task_model) for task_model in task_models]
    
    async def update(self, task: Task) -> Optional[Task]:
        """Update a task"""
        from src.database.models import Task as TaskModel
        
        task_model = self.db.query(TaskModel).filter(TaskModel.id == task.id).first()
        if not task_model:
            return None
        
        # Update fields
        task_model.title = task.title
        task_model.description = task.description
        task_model.status = task.status.value
        task_model.priority = task.priority.value
        task_model.category_id = task.category_id
        task_model.updated_at = task.updated_at
        task_model.completed_at = task.completed_at
        
        self.db.commit()
        self.db.refresh(task_model)
        
        return self._to_domain_entity(task_model)
    
    async def delete(self, task_id: UUID) -> bool:
        """Delete a task"""
        from src.database.models import Task as TaskModel
        
        task_model = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task_model:
            return False
        
        self.db.delete(task_model)
        self.db.commit()
        return True
    
    def _to_domain_entity(self, task_model) -> Task:
        """Convert SQLAlchemy model to domain entity"""
        return Task(
            id=task_model.id,
            title=task_model.title,
            description=task_model.description,
            status=TaskStatus(task_model.status),
            priority=TaskPriority(task_model.priority),
            user_id=task_model.user_id,
            category_id=task_model.category_id,
            created_at=task_model.created_at,
            updated_at=task_model.updated_at,
            completed_at=task_model.completed_at
        )


class SQLAlchemyCategoryRepository(CategoryRepository):
    """SQLAlchemy implementation of CategoryRepository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save(self, category: Category) -> Category:
        """Save a category"""
        from src.database.models import Category as CategoryModel
        
        category_model = CategoryModel(
            id=category.id,
            name=category.name,
            description=category.description,
            color=category.color,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
        
        self.db.add(category_model)
        self.db.commit()
        self.db.refresh(category_model)
        
        return self._to_domain_entity(category_model)
    
    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        """Get category by ID"""
        from src.database.models import Category as CategoryModel
        
        category_model = self.db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        if not category_model:
            return None
        
        return self._to_domain_entity(category_model)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """Get all categories"""
        from src.database.models import Category as CategoryModel
        
        category_models = self.db.query(CategoryModel).offset(skip).limit(limit).all()
        return [self._to_domain_entity(category_model) for category_model in category_models]
    
    async def update(self, category: Category) -> Optional[Category]:
        """Update a category"""
        from src.database.models import Category as CategoryModel
        
        category_model = self.db.query(CategoryModel).filter(CategoryModel.id == category.id).first()
        if not category_model:
            return None
        
        # Update fields
        category_model.name = category.name
        category_model.description = category.description
        category_model.color = category.color
        category_model.updated_at = category.updated_at
        
        self.db.commit()
        self.db.refresh(category_model)
        
        return self._to_domain_entity(category_model)
    
    async def delete(self, category_id: UUID) -> bool:
        """Delete a category"""
        from src.database.models import Category as CategoryModel
        
        category_model = self.db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        if not category_model:
            return False
        
        self.db.delete(category_model)
        self.db.commit()
        return True
    
    def _to_domain_entity(self, category_model) -> Category:
        """Convert SQLAlchemy model to domain entity"""
        return Category(
            id=category_model.id,
            name=category_model.name,
            description=category_model.description,
            color=category_model.color,
            created_at=category_model.created_at,
            updated_at=category_model.updated_at
        )
