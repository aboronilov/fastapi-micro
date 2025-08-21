from src.database.models import User
from src.schemas.user import UserCreate, UserUpdate
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.utils.security import hash_password
from src.services.user_cache import UserCache
from typing import List
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100, user_cache: UserCache | None = None) -> List[User]:
        """Get all users with pagination and caching"""
        # Try to get from cache first
        if user_cache:
            cached_users = user_cache.get_users(skip=skip, limit=limit)
            if cached_users is not None:
                # Convert cached dicts back to User objects
                return [User(**user) for user in cached_users]
        
        # Cache miss - get from database
        users = db.query(User).offset(skip).limit(limit).all()
        
        # Cache the results
        if user_cache:
            user_cache.set_users(users)
        
        return users

    @staticmethod
    def get_user(db: Session, user_id: int, user_cache: UserCache | None = None) -> User | None:
        """Get a user by ID with caching"""
        # Try to get from cache first
        if user_cache:
            cached_user = user_cache.get_user(user_id)
            if cached_user is not None:
                return User(**cached_user)
        
        # Cache miss - get from database
        user = db.query(User).filter(User.id == user_id).first()
        
        # Cache the result
        if user and user_cache:
            user_cache.set_user(user)
        
        return user
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Create a new user with hashed password"""
        # Hash password
        if user.password is None:
            raise ValueError("Password is required for user creation")
        hashed_password = hash_password(user.password)
        
        new_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password
        )
        
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logger.info(f"New user created via service: {user.username}")
            return new_user
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database error during user creation: {e}")
            raise ValueError("User creation failed")
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User | None:
        """Update a user"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Hash password if it's being updated
        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        try:
            db.commit()
            db.refresh(db_user)
            logger.info(f"User updated: {db_user.username}")
            return db_user
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database error during user update: {e}")
            raise ValueError("User update failed")
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False