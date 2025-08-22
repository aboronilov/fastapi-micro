import asyncio
from src.database.models import User
from src.schemas.user import UserCreate
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.utils.security import hash_password, verify_password, create_access_token
from src.services.auth_cache import AuthCache
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    async def login(db: Session, username: str, password: str, auth_cache: AuthCache | None = None) -> dict | None:
        """Login user and return token with caching"""
        # Check if account is locked
        if auth_cache and auth_cache.is_account_locked(username):
            logger.warning(f"Login attempt for locked account: {username}")
            return None
        
        # Try to get user from cache first
        cached_user = None
        if auth_cache:
            cached_user = auth_cache.get_user_by_username(username)
        
        user = None
        if cached_user:
            # Use cached user data - but we need to get the actual user from DB for password verification
            # We'll use the cached data to avoid the DB query for user lookup
            user = await asyncio.to_thread(lambda: db.query(User).filter_by(username=username).first())
        else:
            # Get from database
            user = await asyncio.to_thread(lambda: db.query(User).filter_by(username=username).first())
            if user and auth_cache:
                # Cache the user for future lookups
                auth_cache.cache_user_by_username(username, user)
        
        if user is None:
            logger.warning(f"Login attempt with non-existent username: {username}")
            if auth_cache:
                auth_cache.record_failed_login(username)
            return None
        
        if not verify_password(password, str(user.password)):
            logger.warning(f"Failed login attempt for user: {username}")
            if auth_cache:
                auth_cache.record_failed_login(username)
            return None
        
        # Clear failed login attempts on successful login
        if auth_cache:
            auth_cache.clear_failed_login_attempts(username)
            # Cache user session
            user_id = getattr(user, 'id', None)
            if user_id is not None:
                await auth_cache.cache_user_session(int(user_id), user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        logger.info(f"Successful login for user: {username}")
        user_id = getattr(user, 'id', None)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 30 * 60,  # 30 minutes
            "user_id": int(user_id) if user_id is not None else None,
            "user": user
        }

    @staticmethod
    async def register(db: Session, user: UserCreate) -> User:
        """Register a new user with hashed password"""
        # Check if user already exists
        existing_username = await asyncio.to_thread(lambda: db.query(User).filter_by(username=user.username).first())
        existing_email = await asyncio.to_thread(lambda: db.query(User).filter_by(email=user.email).first())
        
        if existing_username is not None:
            raise ValueError("Username already exists")
        if existing_email is not None:
            raise ValueError("Email already exists")
        
        # Hash password
        if user.password is None:
            raise ValueError("Password is required for registration")
        hashed_password = hash_password(user.password)
        
        new_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password
        )
        
        try:
            await asyncio.to_thread(lambda: db.add(new_user))
            await asyncio.to_thread(lambda: db.commit())
            await asyncio.to_thread(lambda: db.refresh(new_user))
            logger.info(f"New user registered: {user.username}")
            return new_user
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database error during user registration: {e}")
            raise ValueError("User registration failed")