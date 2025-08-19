from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database.config import get_db
from src.database.redis_config import get_redis_client
from src.services.task_service import TaskService
from src.services.task_cache import TaskCache
from src.settings import settings


def get_task_service() -> type[TaskService]:
    """Get TaskService class"""
    return TaskService


def get_task_cache() -> TaskCache:
    """Get TaskCache instance with configurable expiration time"""
    # Get cache expiration time from settings (default: 5 minutes)
    cache_expiration = settings.CACHE_EXPIRATION_SECONDS if settings else 300
    return TaskCache(expiration_time=cache_expiration)


def get_redis_client_dep() -> Generator:
    """Get Redis client as a dependency"""
    client = get_redis_client()
    try:
        yield client
    finally:
        client.close()
