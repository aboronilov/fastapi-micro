from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.database.config import get_db
from src.schemas.tasks import Task, TaskCreate, TaskUpdate
from src.dependencies import get_task_service, get_task_cache
from src.services.task_cache import TaskCache

router = APIRouter(prefix="/task", tags=["task"])

@router.get("/all", response_model=List[Task])
async def get_tasks(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    task_service: type = Depends(get_task_service),
    task_cache: TaskCache = Depends(get_task_cache)
):
    """Get all tasks with pagination - cache-first strategy with time expiration"""
    # Try to get from cache first
    cached_tasks = task_cache.get_tasks(skip=skip, limit=limit)
    
    if cached_tasks is not None:
        # Convert cached dicts back to Task objects
        return [Task(**task) for task in cached_tasks]
    
    # Cache miss - get from database
    tasks = await task_service.get_tasks(db, skip=skip, limit=limit)
    
    # Cache the results with expiration
    task_cache.set_tasks(tasks)
    
    return tasks

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate, 
    db: Session = Depends(get_db),
    task_service: type = Depends(get_task_service),
    task_cache: TaskCache = Depends(get_task_cache)
):
    """Create a new task - cache will expire automatically"""
    new_task = await task_service.create_task(db, task)
    # No need to invalidate cache - it will expire automatically
    return new_task

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int, 
    db: Session = Depends(get_db),
    task_service: type = Depends(get_task_service)
):
    """Get a specific task by ID"""
    task = await task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=Task)
async def update_task(
    task_id: int, 
    task_update: TaskUpdate, 
    db: Session = Depends(get_db),
    task_service: type = Depends(get_task_service),
    task_cache: TaskCache = Depends(get_task_cache)
):
    """Update a task - cache will expire automatically"""
    task = await task_service.update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # No need to invalidate cache - it will expire automatically
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int, 
    db: Session = Depends(get_db),
    task_service: type = Depends(get_task_service),
    task_cache: TaskCache = Depends(get_task_cache)
):
    """Delete a task - cache will expire automatically"""
    if not await task_service.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    # No need to invalidate cache - it will expire automatically
    return None

@router.get("/cache/info")
async def get_cache_info(
    task_cache: TaskCache = Depends(get_task_cache)
):
    """Get cache information including TTL"""
    return task_cache.get_cache_info()

@router.delete("/cache/clear")
async def clear_cache(
    task_cache: TaskCache = Depends(get_task_cache)
):
    """Manually clear the cache (for testing or emergency use)"""
    task_cache.clear_cache()
    return {"message": "Cache cleared successfully"}
