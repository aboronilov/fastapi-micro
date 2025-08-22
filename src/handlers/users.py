from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.database.config import get_db
from src.schemas.user import UserCreate, UserUpdate, UserResponse as UserSchema
from src.services.user_service import UserService
from src.services.user_cache import UserCache
from src.dependencies import get_user_service, get_current_user, get_user_cache
from src.database.models import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserSchema])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_service: type = Depends(get_user_service),
    user_cache: UserCache = Depends(get_user_cache)
):
    """Get all users with pagination - cache-first strategy"""
    users = await user_service.get_users(db, skip=skip, limit=limit, user_cache=user_cache)
    return users

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user info"""
    return current_user

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    user_service: type = Depends(get_user_service),
    user_cache: UserCache = Depends(get_user_cache),
    current_user: User = Depends(get_current_user)
):
    """Get a specific user by ID (requires authentication) - cache-first strategy"""
    user = await user_service.get_user(db, user_id, user_cache=user_cache)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    user_service: type = Depends(get_user_service)
):
    """Create a new user"""
    try:
        new_user = await user_service.create_user(db, user)
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.patch("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    user_service: type = Depends(get_user_service)
):
    """Update a user"""
    try:
        user = await user_service.update_user(db, user_id, user_update)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user_service: type = Depends(get_user_service)
):
    """Delete a user"""
    if not await user_service.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return None


@router.get("/cache/info")
async def get_user_cache_info(
    user_cache: UserCache = Depends(get_user_cache)
):
    """Get user cache information including TTL and statistics"""
    return user_cache.get_cache_info()


@router.delete("/cache/clear")
async def clear_user_cache(
    user_cache: UserCache = Depends(get_user_cache)
):
    """Manually clear the user cache (for testing or emergency use)"""
    user_cache.clear_users_cache()
    return {"message": "User cache cleared successfully"}
