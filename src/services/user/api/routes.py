from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from src.database.config import get_db
from src.services.user.infrastructure.repositories import SQLAlchemyUserRepository
from src.services.user.domain.services import UserDomainService
from src.services.user.application.handlers import UserCommandHandler
from src.services.user.application.commands import (
    CreateUserCommand, UpdateUserCommand, AuthenticateUserCommand
)
from src.shared.kafka_client import KafkaEventPublisher
from src.schemas.user import UserCreate, UserUpdate, UserResponse
from src.dependencies import get_user_domain_service, get_user_command_handler

router = APIRouter(prefix="/users", tags=["users"])


# Use the dependency injection functions from dependencies.py


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    command_handler: UserCommandHandler = Depends(get_user_command_handler)
):
    """Create a new user"""
    try:
        command = CreateUserCommand(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password
        )
        user = await command_handler.handle_create_user(command)
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    domain_service: UserDomainService = Depends(get_user_domain_service)
):
    """List all users with pagination"""
    users = await domain_service.user_repository.list_users(skip, limit)
    return [
        UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
        for user in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    domain_service: UserDomainService = Depends(get_user_domain_service)
):
    """Get user by ID"""
    user = await domain_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    command_handler: UserCommandHandler = Depends(get_user_command_handler)
):
    """Update user"""
    try:
        command = UpdateUserCommand(
            user_id=user_id,
            email=user_data.email,
            username=user_data.username
        )
        user = await command_handler.handle_update_user(command)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/authenticate")
async def authenticate_user(
    email: str,
    password: str,
    domain_service: UserDomainService = Depends(get_user_domain_service)
):
    """Authenticate user"""
    try:
        user = await domain_service.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials"
            )
        
        return {
            "message": "Authentication successful",
            "user_id": str(user.id),
            "email": user.email
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
