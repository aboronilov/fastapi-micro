from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.database.config import get_db
from src.database.redis_config import get_redis_client
from src.services.task_service import TaskService
from src.services.task_cache import TaskCache
from src.services.auth_service import AuthService
from src.services.user_service import UserService
import asyncio
from src.services.user_cache import UserCache
from src.services.auth_cache import AuthCache
from src.services.google_oauth_service import GoogleOAuthService
from src.services.async_task_service import AsyncTaskService
from src.utils.security import verify_token
from src.database.models import User
from src.settings import settings

security = HTTPBearer()

def get_task_service() -> type[TaskService]:
    """Get TaskService class"""
    return TaskService


def get_task_cache() -> TaskCache:
    """Get TaskCache instance with configurable expiration time"""
    # Get cache expiration time from settings (default: 5 minutes)
    cache_expiration = settings.CACHE_EXPIRATION_SECONDS if settings else 300
    return TaskCache(expiration_time=cache_expiration)


def get_auth_service() -> type[AuthService]:
    """Get AuthService class"""
    return AuthService


def get_user_service() -> type[UserService]:
    """Get UserService class"""
    return UserService


def get_user_cache() -> UserCache:
    """Get UserCache instance with configurable expiration time"""
    # Get cache expiration time from settings (default: 5 minutes)
    cache_expiration = getattr(settings, 'USER_CACHE_EXPIRATION_SECONDS', 300)
    return UserCache(expiration_time=cache_expiration)


def get_auth_cache() -> AuthCache:
    """Get AuthCache instance with configurable expiration time"""
    # Get cache expiration time from settings (default: 30 minutes)
    cache_expiration = getattr(settings, 'AUTH_CACHE_EXPIRATION_SECONDS', 1800)
    return AuthCache(expiration_time=cache_expiration)


def get_google_oauth_service() -> type[GoogleOAuthService]:
    """Get GoogleOAuthService class"""
    return GoogleOAuthService


def get_async_task_service() -> AsyncTaskService:
    """Get AsyncTaskService instance"""
    return AsyncTaskService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await asyncio.to_thread(lambda: db.query(User).filter(User.id == int(str(user_id))).first())
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_redis_client_dep() -> Generator:
    """Get Redis client as a dependency"""
    client = get_redis_client()
    try:
        yield client
    finally:
        client.close()
