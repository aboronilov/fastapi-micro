from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import asyncio
import time
from src.database.config import get_db
from src.schemas.tasks import Task, TaskCreate, TaskUpdate
from src.dependencies import get_task_service, get_task_cache
from src.services.task_cache import TaskCache

router = APIRouter(prefix="/async-tasks", tags=["async-tasks"])

# Background task function
async def process_task_async(task_id: int, task_data: dict):
    """Background task to process task asynchronously"""
    try:
        print(f"🔄 Processing task {task_id} in background...")
        # Simulate some async work
        await asyncio.sleep(2)
        print(f"✅ Task {task_id} processed successfully!")
    except Exception as e:
        print(f"❌ Background task {task_id} failed: {e}")
        raise

# Concurrent task processing
async def process_multiple_tasks_concurrently(task_ids: List[int]):
    """Process multiple tasks concurrently"""
    try:
        tasks = [process_task_async(task_id, {}) for task_id in task_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    except Exception as e:
        print(f"❌ Concurrent task processing failed: {e}")
        raise

@router.get("/all", response_model=List[Task])
async def get_tasks_async(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    task_service: type = Depends(get_task_service),
    task_cache: TaskCache = Depends(get_task_cache)
):
    """Get all tasks with async processing - demonstrates concurrent operations"""
    print(f"🚀 Starting async task retrieval...")
    
    # Simulate concurrent operations
    start_time = time.time()
    
    # Run multiple async operations concurrently
    tasks = [
        asyncio.create_task(asyncio.sleep(0.1)),  # Simulate cache check
        asyncio.create_task(asyncio.sleep(0.2)),  # Simulate database query
        asyncio.create_task(asyncio.sleep(0.1))   # Simulate data processing
    ]
    
    # Wait for all operations to complete
    await asyncio.gather(*tasks)
    
    # Get actual data (this would be async in real implementation)
    cached_tasks = task_cache.get_tasks(skip=skip, limit=limit)
    
    if cached_tasks is not None:
        result = [Task(**task) for task in cached_tasks]
    else:
        tasks_data = await task_service.get_tasks(db, skip=skip, limit=limit)
        task_cache.set_tasks(tasks_data)
        result = tasks_data
    
    end_time = time.time()
    print(f"⏱️ Async task retrieval completed in {end_time - start_time:.3f} seconds")
    
    return result

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task_async(
    task: TaskCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    task_service: type = Depends(get_task_service),
    task_cache: TaskCache = Depends(get_task_cache)
):
    """Create a new task with background processing"""
    print(f"🚀 Creating task asynchronously...")
    
    # Create the task
    new_task = await task_service.create_task(db, task)
    
    # Add background task for processing
    background_tasks.add_task(process_task_async, new_task.id, task.dict())
    
    print(f"✅ Task created with ID: {new_task.id}")
    return new_task

@router.post("/batch-process")
async def batch_process_tasks(
    task_ids: List[int],
    background_tasks: BackgroundTasks
):
    """Process multiple tasks in background"""
    print(f"🚀 Starting batch processing for {len(task_ids)} tasks...")
    
    # Add background task for batch processing
    background_tasks.add_task(process_multiple_tasks_concurrently, task_ids)
    
    return {
        "message": f"Batch processing started for {len(task_ids)} tasks",
        "task_ids": task_ids,
        "status": "processing"
    }

@router.get("/performance-test")
async def performance_test():
    """Test async performance with concurrent operations"""
    print(f"🚀 Starting performance test...")
    
    start_time = time.time()
    
    # Simulate multiple concurrent operations
    async def simulate_operation(name: str, delay: float):
        print(f"🔄 Starting {name}...")
        await asyncio.sleep(delay)
        print(f"✅ {name} completed!")
        return f"{name}_result"
    
    # Run operations concurrently
    operations = [
        simulate_operation("database_query", 0.5),
        simulate_operation("cache_lookup", 0.3),
        simulate_operation("external_api_call", 0.7),
        simulate_operation("data_processing", 0.2)
    ]
    
    results = await asyncio.gather(*operations)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    return {
        "message": "Performance test completed",
        "results": results,
        "total_time_seconds": total_time,
        "operations_count": len(operations)
    }

@router.get("/concurrent-users")
async def simulate_concurrent_users():
    """Simulate handling multiple concurrent user requests"""
    print(f"🚀 Simulating concurrent user requests...")
    
    async def simulate_user_request(user_id: int):
        """Simulate a single user request"""
        print(f"👤 User {user_id} request started...")
        await asyncio.sleep(0.1)  # Simulate request processing
        print(f"✅ User {user_id} request completed!")
        return f"user_{user_id}_response"
    
    # Simulate 10 concurrent users
    user_requests = [simulate_user_request(i) for i in range(1, 11)]
    results = await asyncio.gather(*user_requests)
    
    return {
        "message": "Concurrent user simulation completed",
        "users_processed": len(results),
        "results": results
    }

