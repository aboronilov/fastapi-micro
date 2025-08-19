from typing import Optional, List, Union, Any
import json
from datetime import datetime
from src.database.redis_config import get_redis_client
from src.schemas.tasks import Task
from src.database.models import Task as TaskModel


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class TaskCache:
    def __init__(self, expiration_time: int = 300):  # 5 minutes default expiration
        self.redis_client = get_redis_client()
        self.expiration_time = expiration_time
        self.tasks_key = "tasks"
        self.tasks_count_key = "tasks_count"

    def get_tasks(self, skip: int = 0, limit: int = 100) -> Optional[List[dict]]:
        """Get tasks from cache with pagination"""
        try:
            # Get all cached tasks
            cached_tasks = self.redis_client.get(self.tasks_key)
            if cached_tasks is None:
                return None

            # Ensure cached_tasks is a string before loading JSON
            if isinstance(cached_tasks, bytes):
                cached_tasks = cached_tasks.decode("utf-8")
            elif not isinstance(cached_tasks, str):
                # If cached_tasks is not a string or bytes, cannot proceed
                return None
            tasks = json.loads(cached_tasks)

            # Apply pagination
            start = skip
            end = skip + limit
            return tasks[start:end]
        except Exception as e:
            print(f"Error retrieving tasks from cache: {e}")
            return None

    def set_tasks(self, tasks: List[Union[Task, TaskModel, Any]]):
        """Cache tasks with expiration time"""
        try:
            # Convert Task objects to dictionaries
            task_dicts = []
            for task in tasks:
                if isinstance(task, Task):
                    # Already a Pydantic model
                    task_dicts.append(task.model_dump())
                elif isinstance(task, TaskModel):
                    # SQLAlchemy model - convert to Pydantic model first
                    pydantic_task = Task.model_validate(task)
                    task_dicts.append(pydantic_task.model_dump())
                else:
                    # Handle dict or other types
                    if hasattr(task, 'model_dump'):
                        task_dicts.append(task.model_dump())
                    elif hasattr(task, '__dict__'):
                        # Convert SQLAlchemy model to dict
                        task_dict = {}
                        for key, value in task.__dict__.items():
                            if not key.startswith('_'):
                                task_dict[key] = value
                        task_dicts.append(task_dict)
                    else:
                        print(f"Warning: Skipping task with unsupported type: {type(task)}")
                        continue
            
            # Store tasks as JSON string with expiration using custom encoder
            self.redis_client.setex(
                self.tasks_key,
                self.expiration_time,
                json.dumps(task_dicts, cls=DateTimeEncoder)
            )
            
            # Also cache the count for quick access
            self.redis_client.setex(
                self.tasks_count_key,
                self.expiration_time,
                len(task_dicts)
            )
        except Exception as e:
            print(f"Error caching tasks: {e}")

    def get_tasks_count(self) -> Optional[int]:
        """Get the count of cached tasks"""
        try:
            count = self.redis_client.get(self.tasks_count_key)
            if count is not None:
                return int(count)  # type: ignore
            return None
        except Exception as e:
            print(f"Error retrieving tasks count from cache: {e}")
            return None

    def is_cache_valid(self) -> bool:
        """Check if cache exists and is not expired"""
        try:
            exists = self.redis_client.exists(self.tasks_key)
            return exists > 0 if exists is not None else False  # type: ignore
        except Exception as e:
            print(f"Error checking cache validity: {e}")
            return False

    def clear_cache(self):
        """Clear the cache (for manual invalidation if needed)"""
        try:
            self.redis_client.delete(self.tasks_key, self.tasks_count_key)
        except Exception as e:
            print(f"Error clearing cache: {e}")

    def get_cache_info(self) -> dict:
        """Get cache information including TTL"""
        try:
            ttl = self.redis_client.ttl(self.tasks_key)
            exists = self.redis_client.exists(self.tasks_key)
            return {
                "exists": exists > 0 if exists is not None else False,  # type: ignore
                "ttl": ttl if ttl is not None and ttl > 0 else None,  # type: ignore
                "expiration_time": self.expiration_time
            }
        except Exception as e:
            print(f"Error getting cache info: {e}")
            return {"exists": False, "ttl": None, "expiration_time": self.expiration_time}
    
    