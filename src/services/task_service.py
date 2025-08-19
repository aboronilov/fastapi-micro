from sqlalchemy.orm import Session
from typing import List, Optional
from src.database.models import Task
from src.schemas.tasks import TaskCreate, TaskUpdate


class TaskService:
    """Service class for task-related database operations"""
    
    @staticmethod
    def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks with pagination"""
        return db.query(Task).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[Task]:
        """Get a specific task by ID"""
        return db.query(Task).filter(Task.id == task_id).first()
    
    @staticmethod
    def create_task(db: Session, task: TaskCreate) -> Task:
        """Create a new task"""
        db_task = Task(
            name=task.name,
            description=task.description,
            pomodoro_count=task.pomodoro_count,
            category_id=task.category_id,
            completed=task.completed
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        """Update a task"""
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            return None
        
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        """Delete a task"""
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True
