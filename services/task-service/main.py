from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

# Import the existing task service components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.services.task.application.handlers import TaskCommandHandler
from src.services.task.application.commands import (
    CreateTaskCommand, UpdateTaskCommand, CompleteTaskCommand, 
    CancelTaskCommand, DeleteTaskCommand
)
from src.dependencies import get_task_domain_service, get_kafka_event_publisher
from src.event_bus import get_event_bus, shutdown_event_bus
from src.shared.events import ServiceStartedEvent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Task Service",
    description="Task management microservice",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"
    category_id: Optional[UUID] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category_id: Optional[UUID] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    user_id: str
    category_id: Optional[str] = None
    created_at: datetime

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "task-service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Task endpoints
@app.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    user_id: UUID,  # This would come from authentication
    task_service = Depends(get_task_domain_service),
    event_publisher = Depends(get_kafka_event_publisher)
):
    """Create a new task"""
    try:
        command_handler = TaskCommandHandler(task_service, event_publisher)
        
        command = CreateTaskCommand(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            category_id=task_data.category_id
        )
        
        task = await command_handler.handle_create_task(command)
        
        return TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            status=task.status.value,
            priority=task.priority.value,
            user_id=str(task.user_id),
            category_id=str(task.category_id) if task.category_id else None,
            created_at=task.created_at
        )
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    user_id: UUID,  # This would come from authentication
    skip: int = 0,
    limit: int = 100,
    task_service = Depends(get_task_domain_service)
):
    """List tasks for a user"""
    try:
        tasks = await task_service.list_user_tasks(user_id, skip, limit)
        
        return [
            TaskResponse(
                id=str(task.id),
                title=task.title,
                description=task.description,
                status=task.status.value,
                priority=task.priority.value,
                user_id=str(task.user_id),
                category_id=str(task.category_id) if task.category_id else None,
                created_at=task.created_at
            )
            for task in tasks
        ]
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    user_id: UUID,  # This would come from authentication
    task_service = Depends(get_task_domain_service)
):
    """Get a specific task"""
    try:
        task = await task_service.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            status=task.status.value,
            priority=task.priority.value,
            user_id=str(task.user_id),
            category_id=str(task.category_id) if task.category_id else None,
            created_at=task.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: UUID,  # This would come from authentication
    task_service = Depends(get_task_domain_service),
    event_publisher = Depends(get_kafka_event_publisher)
):
    """Update a task"""
    try:
        command_handler = TaskCommandHandler(task_service, event_publisher)
        
        command = UpdateTaskCommand(
            task_id=task_id,
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            category_id=task_data.category_id
        )
        
        task = await command_handler.handle_update_task(command)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            status=task.status.value,
            priority=task.priority.value,
            user_id=str(task.user_id),
            category_id=str(task.category_id) if task.category_id else None,
            created_at=task.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    user_id: UUID,  # This would come from authentication
    task_service = Depends(get_task_domain_service),
    event_publisher = Depends(get_kafka_event_publisher)
):
    """Complete a task"""
    try:
        command_handler = TaskCommandHandler(task_service, event_publisher)
        
        command = CompleteTaskCommand(
            task_id=task_id,
            user_id=user_id
        )
        
        task = await command_handler.handle_complete_task(command)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            status=task.status.value,
            priority=task.priority.value,
            user_id=str(task.user_id),
            category_id=str(task.category_id) if task.category_id else None,
            created_at=task.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/tasks/{task_id}")
async def delete_task(
    task_id: UUID,
    user_id: UUID,  # This would come from authentication
    task_service = Depends(get_task_domain_service),
    event_publisher = Depends(get_kafka_event_publisher)
):
    """Delete a task"""
    try:
        command_handler = TaskCommandHandler(task_service, event_publisher)
        
        command = DeleteTaskCommand(
            task_id=task_id,
            user_id=user_id
        )
        
        success = await command_handler.handle_delete_task(command)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Startup event - initialize event bus"""
    try:
        # Initialize event bus
        event_bus = await get_event_bus()
        
        # Publish service started event
        event = ServiceStartedEvent(
            aggregate_id="task-service",
            aggregate_type="Service",
            data={
                "service_name": "task-service",
                "version": "1.0.0",
                "started_at": datetime.now().isoformat()
            }
        )
        await event_bus.publish_event(event)
        
        logger.info("✅ Task Service started with event-driven architecture")
        
    except Exception as e:
        logger.error(f"❌ Failed to start event bus: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - cleanup event bus"""
    try:
        await shutdown_event_bus()
        logger.info("✅ Task Service shutdown completed")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
