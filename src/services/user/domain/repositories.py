from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from .entities import User, UserProfile


class UserRepository(ABC):
    """User repository interface"""
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """Save user to repository"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass
    
    @abstractmethod
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID"""
        pass


class UserProfileRepository(ABC):
    """User profile repository interface"""
    
    @abstractmethod
    async def save(self, profile: UserProfile) -> UserProfile:
        """Save user profile to repository"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[UserProfile]:
        """Get user profile by user ID"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user profile by user ID"""
        pass
