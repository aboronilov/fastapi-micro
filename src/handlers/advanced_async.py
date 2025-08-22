from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import asyncio
import time
from src.database.config import get_db
from src.schemas.tasks import Task, TaskCreate, TaskUpdate
from src.dependencies import get_async_task_service, get_task_cache
from src.services.async_task_service import AsyncTaskService
from src.services.task_cache import TaskCache

router = APIRouter(prefix="/advanced-async", tags=["advanced-async"])

@router.get("/tasks/concurrent", response_model=List[Task])
async def get_tasks_concurrent(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    async_task_service: AsyncTaskService = Depends(get_async_task_service),
    task_cache: TaskCache = Depends(get_task_cache)
):
    """Get tasks using concurrent cache and database operations"""
    start_time = time.time()
    
    try:
        tasks = await async_task_service.get_tasks_concurrent(
            db=db, 
            skip=skip, 
            limit=limit, 
            task_cache=task_cache
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return {
            "tasks": tasks,
            "metadata": {
                "processing_time_seconds": processing_time,
                "tasks_count": len(tasks),
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tasks: {str(e)}"
        )

@router.post("/tasks/with-validation", response_model=Task)
async def create_task_with_validation(
    task: TaskCreate,
    db: Session = Depends(get_db),
    async_task_service: AsyncTaskService = Depends(get_async_task_service)
):
    """Create task with external API validation"""
    try:
        new_task = await async_task_service.create_task_with_external_validation(db, task)
        return new_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )

@router.post("/tasks/batch-update")
async def batch_update_tasks(
    task_updates: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    async_task_service: AsyncTaskService = Depends(get_async_task_service)
):
    """Update multiple tasks concurrently"""
    if not task_updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No task updates provided"
        )
    
    try:
        start_time = time.time()
        updated_tasks = await async_task_service.batch_update_tasks(db, task_updates)
        end_time = time.time()
        
        return {
            "message": "Batch update completed",
            "updated_tasks": updated_tasks,
            "metadata": {
                "total_requested": len(task_updates),
                "successfully_updated": len(updated_tasks),
                "processing_time_seconds": end_time - start_time
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch update failed: {str(e)}"
        )

@router.get("/statistics")
async def get_task_statistics(
    db: Session = Depends(get_db),
    async_task_service: AsyncTaskService = Depends(get_async_task_service)
):
    """Get task statistics with concurrent operations"""
    try:
        start_time = time.time()
        stats = await async_task_service.get_task_statistics(db)
        end_time = time.time()
        
        stats["processing_time_seconds"] = end_time - start_time
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )

@router.get("/performance-comparison")
async def performance_comparison(
    db: Session = Depends(get_db),
    async_task_service: AsyncTaskService = Depends(get_async_task_service)
):
    """Compare sync vs async performance"""
    
    async def sync_style_operations():
        """Simulate synchronous-style operations"""
        start_time = time.time()
        
        # Simulate sequential operations
        await asyncio.sleep(0.1)  # DB query 1
        await asyncio.sleep(0.1)  # DB query 2
        await asyncio.sleep(0.1)  # DB query 3
        await asyncio.sleep(0.1)  # Cache operation
        await asyncio.sleep(0.1)  # External API call
        
        end_time = time.time()
        return end_time - start_time
    
    async def async_style_operations():
        """Simulate asynchronous-style operations"""
        start_time = time.time()
        
        # Simulate concurrent operations
        operations = [
            asyncio.sleep(0.1),  # DB query 1
            asyncio.sleep(0.1),  # DB query 2
            asyncio.sleep(0.1),  # DB query 3
            asyncio.sleep(0.1),  # Cache operation
            asyncio.sleep(0.1),  # External API call
        ]
        
        await asyncio.gather(*operations)
        
        end_time = time.time()
        return end_time - start_time
    
    # Run both performance tests
    sync_time, async_time = await asyncio.gather(
        sync_style_operations(),
        async_style_operations()
    )
    
    improvement = ((sync_time - async_time) / sync_time) * 100
    
    return {
        "sync_operations_time": sync_time,
        "async_operations_time": async_time,
        "performance_improvement_percent": improvement,
        "time_saved_seconds": sync_time - async_time
    }

@router.get("/concurrent-load-test")
async def concurrent_load_test():
    """Test handling of concurrent requests"""
    
    async def simulate_request(request_id: int, delay: float):
        """Simulate a single request"""
        start_time = time.time()
        await asyncio.sleep(delay)
        end_time = time.time()
        
        return {
            "request_id": request_id,
            "processing_time": end_time - start_time,
            "status": "completed"
        }
    
    # Simulate 20 concurrent requests with different processing times
    import random
    requests = [
        simulate_request(i, random.uniform(0.1, 0.5))
        for i in range(1, 21)
    ]
    
    start_time = time.time()
    results = await asyncio.gather(*requests)
    total_time = time.time() - start_time
    
    return {
        "total_requests": len(results),
        "total_processing_time": total_time,
        "average_request_time": sum(r["processing_time"] for r in results) / len(results),
        "requests": results
    }

@router.post("/background-processing")
async def start_background_processing(
    background_tasks: BackgroundTasks,
    task_ids: List[int]
):
    """Start background processing for multiple tasks"""
    
    async def process_task_background(task_id: int):
        """Background task processing"""
        print(f"🔄 Starting background processing for task {task_id}")
        
        # Simulate different processing steps
        await asyncio.sleep(1)  # Step 1: Data validation
        await asyncio.sleep(1)  # Step 2: External API call
        await asyncio.sleep(1)  # Step 3: Database update
        
        print(f"✅ Background processing completed for task {task_id}")
        return f"Task {task_id} processed successfully"
    
    # Add background tasks
    for task_id in task_ids:
        background_tasks.add_task(process_task_background, task_id)
    
    return {
        "message": f"Background processing started for {len(task_ids)} tasks",
        "task_ids": task_ids,
        "status": "processing"
    }

