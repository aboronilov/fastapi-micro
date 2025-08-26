import asyncio
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from src.database.models import User as UserModel
from src.database.config import get_db
from ..domain.entities import User, UserProfile
from ..domain.repositories import UserRepository, UserProfileRepository


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save(self, user: User) -> User:
        """Save user to database"""
        # Convert domain entity to model
        user_model = UserModel(
            id=user.id,
            email=user.email,
            username=user.username,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        # Check if user exists
        existing_user = await asyncio.to_thread(
            lambda: self.db.query(UserModel).filter(UserModel.id == user.id).first()
        )
        
        if existing_user:
            # Update existing user
            await asyncio.to_thread(
                lambda: self.db.execute(
                    update(UserModel)
                    .where(UserModel.id == user.id)
                    .values(
                        email=user.email,
                        username=user.username,
                        hashed_password=user.hashed_password,
                        is_active=user.is_active,
                        is_verified=user.is_verified,
                        updated_at=user.updated_at
                    )
                )
            )
        else:
            # Create new user
            await asyncio.to_thread(lambda: self.db.add(user_model))
        
        await asyncio.to_thread(lambda: self.db.commit())
        await asyncio.to_thread(lambda: self.db.refresh(user_model))
        
        # Convert back to domain entity
        return self._to_domain_entity(user_model)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        user_model = await asyncio.to_thread(
            lambda: self.db.query(UserModel).filter(UserModel.id == user_id).first()
        )
        return self._to_domain_entity(user_model) if user_model else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_model = await asyncio.to_thread(
            lambda: self.db.query(UserModel).filter(UserModel.email == email).first()
        )
        return self._to_domain_entity(user_model) if user_model else None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        user_model = await asyncio.to_thread(
            lambda: self.db.query(UserModel).filter(UserModel.username == username).first()
        )
        return self._to_domain_entity(user_model) if user_model else None
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination"""
        users = await asyncio.to_thread(
            lambda: self.db.query(UserModel).offset(skip).limit(limit).all()
        )
        return [self._to_domain_entity(user) for user in users]
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID"""
        result = await asyncio.to_thread(
            lambda: self.db.execute(
                delete(UserModel).where(UserModel.id == user_id)
            )
        )
        await asyncio.to_thread(lambda: self.db.commit())
        return result.rowcount > 0
    
    def _to_domain_entity(self, user_model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity"""
        # Convert integer ID to UUID string for domain entity
        user_id = UUID(int=user_model.id) if user_model.id else UUID(int=0)
        
        return User(
            id=user_id,
            email=str(user_model.email) if user_model.email else "",
            username=str(user_model.username) if user_model.username else "",
            hashed_password=str(user_model.password) if user_model.password else "",
            is_active=True,  # Default to True since the model doesn't have this field
            is_verified=False,  # Default to False since the model doesn't have this field
            created_at=user_model.created_at,
            updated_at=user_model.created_at  # Use created_at as updated_at since model doesn't have updated_at
        )


class SQLAlchemyUserProfileRepository(UserProfileRepository):
    """SQLAlchemy implementation of UserProfileRepository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save(self, profile: UserProfile) -> UserProfile:
        """Save user profile to database"""
        # This would need a UserProfile model in database/models.py
        # For now, we'll implement a placeholder
        raise NotImplementedError("UserProfile model not yet implemented")
    
    async def get_by_user_id(self, user_id: UUID) -> Optional[UserProfile]:
        """Get user profile by user ID"""
        # This would need a UserProfile model in database/models.py
        # For now, we'll implement a placeholder
        raise NotImplementedError("UserProfile model not yet implemented")
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user profile by user ID"""
        # This would need a UserProfile model in database/models.py
        # For now, we'll implement a placeholder
        raise NotImplementedError("UserProfile model not yet implemented")
