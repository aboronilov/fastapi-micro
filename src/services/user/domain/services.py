from typing import Optional
from uuid import UUID
from .entities import User, UserProfile
from .repositories import UserRepository, UserProfileRepository


class UserDomainService:
    """User domain service with business logic"""
    
    def __init__(self, user_repository: UserRepository, profile_repository: Optional[UserProfileRepository] = None):
        self.user_repository = user_repository
        self.profile_repository = profile_repository
    
    async def create_user(self, email: str, username: str, password: str) -> User:
        """Create a new user with business validation"""
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        existing_username = await self.user_repository.get_by_username(username)
        if existing_username:
            raise ValueError("Username already taken")
        
        # Create user
        user = User.create(email=email, username=username, password=password)
        return await self.user_repository.save(user)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        
        if not user.is_active:
            raise ValueError("User account is deactivated")
        
        if not user.verify_password(password):
            return None
        
        return user
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return await self.user_repository.get_by_id(user_id)
    
    async def update_user_profile(self, user_id: UUID, **kwargs) -> Optional[User]:
        """Update user profile"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        user.update_profile(**kwargs)
        return await self.user_repository.save(user)
    
    async def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        if not user.verify_password(current_password):
            return False
        
        user.update_password(new_password)
        await self.user_repository.save(user)
        return True
    
    async def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        user.deactivate()
        await self.user_repository.save(user)
        return True
    
    async def activate_user(self, user_id: UUID) -> bool:
        """Activate user account"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        user.activate()
        await self.user_repository.save(user)
        return True
    
    async def verify_user(self, user_id: UUID) -> bool:
        """Mark user as verified"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        user.verify()
        await self.user_repository.save(user)
        return True
    
    async def create_user_profile(self, user_id: UUID, **kwargs) -> Optional[UserProfile]:
        """Create user profile"""
        if not self.profile_repository:
            raise NotImplementedError("UserProfileRepository not implemented")
        profile = UserProfile(user_id=user_id, **kwargs)
        return await self.profile_repository.save(profile)
    
    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfile]:
        """Get user profile"""
        if not self.profile_repository:
            return None
        return await self.profile_repository.get_by_user_id(user_id)
    
    async def update_user_profile_details(self, user_id: UUID, **kwargs) -> Optional[UserProfile]:
        """Update user profile details"""
        if not self.profile_repository:
            raise NotImplementedError("UserProfileRepository not implemented")
        profile = await self.profile_repository.get_by_user_id(user_id)
        if not profile:
            # Create profile if it doesn't exist
            profile = UserProfile(user_id=user_id)
        
        profile.update_profile(**kwargs)
        return await self.profile_repository.save(profile)
