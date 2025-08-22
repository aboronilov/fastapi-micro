import asyncio
import httpx
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.database.models import Task
from src.schemas.tasks import TaskCreate, TaskUpdate
from src.services.task_cache import TaskCache
import logging

logger = logging.getLogger(__name__)

class AsyncTaskService:
    """Async service for task operations with concurrent processing"""
    
    def __init__(self):
        self.external_api_url = "https://jsonplaceholder.typicode.com/posts"
    
    async def get_tasks_concurrent(self, db: Session, skip: int = 0, limit: int = 100, task_cache: Optional[TaskCache] = None) -> List[Task]:
        """Get tasks with concurrent cache and database operations"""
        logger.info(f"🔄 Getting tasks with concurrent operations (skip={skip}, limit={limit})")
        
        # Try cache first if available
        if task_cache:
            cached_result = await self._get_from_cache(task_cache, skip, limit)
            if cached_result is not None:
                logger.info("✅ Returning cached results")
                return cached_result
        
        # Get from database
        db_result = await self._get_from_database(db, skip, limit)
        
        # Cache the results asynchronously (fire and forget)
        if task_cache and db_result:
            asyncio.create_task(self._safe_cache_results(task_cache, db_result))
        
        logger.info(f"✅ Returning {len(db_result)} tasks from database")
        return db_result
    
    async def _get_from_cache(self, task_cache: Optional[TaskCache], skip: int, limit: int) -> Optional[List[Task]]:
        """Get tasks from cache asynchronously"""
        if not task_cache:
            return None
        
        try:
            # Simulate async cache operation
            await asyncio.sleep(0.01)
            cached_tasks = task_cache.get_tasks(skip=skip, limit=limit)
            
            if cached_tasks is not None:
                return [Task(**task) for task in cached_tasks]
            return None
        except Exception as e:
            logger.error(f"❌ Cache operation failed: {e}")
            return None
    
    async def _get_from_database(self, db: Session, skip: int, limit: int) -> List[Task]:
        """Get tasks from database asynchronously"""
        try:
            # Use asyncio.to_thread for database operations
            tasks = await asyncio.to_thread(
                lambda: db.query(Task).offset(skip).limit(limit).all()
            )
            return tasks
        except Exception as e:
            logger.error(f"❌ Database operation failed: {e}")
            return []
    
    async def _safe_cache_results(self, task_cache: TaskCache, tasks: List[Task]):
        """Safely cache results with error handling"""
        try:
            await self._cache_results(task_cache, tasks)
        except Exception as e:
            logger.error(f"❌ Background caching failed: {e}")
    
    async def _cache_results(self, task_cache: TaskCache, tasks: List[Task]):
        """Cache results asynchronously"""
        try:
            await asyncio.sleep(0.01)
            task_cache.set_tasks(tasks)
            logger.info("✅ Results cached successfully")
        except Exception as e:
            logger.error(f"❌ Caching failed: {e}")
    
    async def create_task_with_external_validation(self, db: Session, task: TaskCreate) -> Task:
        """Create task with external API validation"""
        logger.info(f"🔄 Creating task with external validation: {task.name}")
        
        # Run external validation and task creation concurrently
        validation_task = asyncio.create_task(self._validate_with_external_api(task))
        creation_task = asyncio.create_task(self._create_task_in_db(db, task))
        
        # Wait for both operations to complete
        validation_result, new_task = await asyncio.gather(validation_task, creation_task)
        
        if not validation_result:
            raise ValueError("External validation failed")
        
        logger.info(f"✅ Task created successfully with ID: {new_task.id}")
        return new_task
    
    async def _validate_with_external_api(self, task: TaskCreate) -> bool:
        """Validate task with external API"""
        try:
            async with httpx.AsyncClient() as client:
                # Simulate external API call
                response = await client.get(self.external_api_url, timeout=5.0)
                await asyncio.sleep(0.1)  # Simulate processing time
                
                # For demo purposes, always return True
                # In real implementation, you'd validate the response
                return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ External validation failed: {e}")
            return False
    
    async def _create_task_in_db(self, db: Session, task: TaskCreate) -> Task:
        """Create task in database asynchronously"""
        try:
            new_task = Task(
                name=task.name,
                description=task.description,
                pomodoro_count=task.pomodoro_count,
                category_id=task.category_id,
                completed=task.completed,
                user_id=1  # Default user ID for demo purposes
            )
            
            # Use asyncio.to_thread for database operations
            await asyncio.to_thread(lambda: db.add(new_task))
            await asyncio.to_thread(lambda: db.commit())
            await asyncio.to_thread(lambda: db.refresh(new_task))
            
            return new_task
        except Exception as e:
            logger.error(f"❌ Database creation failed: {e}")
            raise
    
    async def batch_update_tasks(self, db: Session, task_updates: List[Dict[str, Any]]) -> List[Task]:
        """Update multiple tasks concurrently"""
        logger.info(f"🔄 Starting batch update for {len(task_updates)} tasks")
        
        # Create concurrent update tasks
        update_tasks = [
            self._update_single_task(db, update_data) 
            for update_data in task_updates
        ]
        
        # Execute all updates concurrently
        results = await asyncio.gather(*update_tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful updates
        successful_updates = [result for result in results if not isinstance(result, Exception)]
        
        logger.info(f"✅ Batch update completed: {len(successful_updates)}/{len(task_updates)} successful")
        return successful_updates
    
    async def _update_single_task(self, db: Session, update_data: Dict[str, Any]) -> Optional[Task]:
        """Update a single task asynchronously"""
        try:
            task_id = update_data.get('id')
            if not task_id:
                return None
            
            # Use asyncio.to_thread for database operations
            task = await asyncio.to_thread(
                lambda: db.query(Task).filter(Task.id == task_id).first()
            )
            if not task:
                return None
            
            # Update task fields
            for field, value in update_data.items():
                if field != 'id' and hasattr(task, field):
                    setattr(task, field, value)
            
            await asyncio.to_thread(lambda: db.commit())
            await asyncio.to_thread(lambda: db.refresh(task))
            
            return task
        except Exception as e:
            logger.error(f"❌ Task update failed for ID {update_data.get('id')}: {e}")
            return None
    
    async def get_task_statistics(self, db: Session) -> Dict[str, Any]:
        """Get task statistics with concurrent operations"""
        logger.info("🔄 Getting task statistics with concurrent operations")
        
        # Define concurrent operations
        operations = [
            self._get_total_tasks(db),
            self._get_completed_tasks(db),
            self._get_pending_tasks(db),
            self._get_average_pomodoro_count(db)
        ]
        
        # Execute all operations concurrently
        total, completed, pending, avg_pomodoros = await asyncio.gather(*operations)
        
        stats = {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "average_pomodoros": avg_pomodoros
        }
        
        logger.info(f"✅ Statistics calculated: {stats}")
        return stats
    
    async def _get_total_tasks(self, db: Session) -> int:
        """Get total number of tasks"""
        return await asyncio.to_thread(lambda: db.query(Task).count())
    
    async def _get_completed_tasks(self, db: Session) -> int:
        """Get number of completed tasks"""
        return await asyncio.to_thread(lambda: db.query(Task).filter(Task.completed == True).count())
    
    async def _get_pending_tasks(self, db: Session) -> int:
        """Get number of pending tasks"""
        return await asyncio.to_thread(lambda: db.query(Task).filter(Task.completed == False).count())
    
    async def _get_average_pomodoro_count(self, db: Session) -> float:
        """Get average pomodoro count"""
        result = await asyncio.to_thread(lambda: db.query(Task.pomodoro_count).all())
        if not result:
            return 0.0
        
        total_pomodoros = sum(row[0] for row in result)
        return total_pomodoros / len(result)

