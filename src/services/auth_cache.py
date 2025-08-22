from typing import Optional, Union, Any, cast
import json
from datetime import datetime, timedelta
from src.database.redis_config import get_redis_client
from src.schemas.user import UserResponse
from src.database.models import User


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class AuthCache:
    def __init__(self, expiration_time: int = 1800):  # 30 minutes default expiration for auth
        self.redis_client = get_redis_client()
        self.expiration_time = expiration_time
        self.token_prefix = "auth_token:"
        self.user_session_prefix = "user_session:"
        self.failed_login_prefix = "failed_login:"
        self.max_failed_attempts = 5
        self.lockout_duration = 900  # 15 minutes lockout

    async def cache_user_session(self, user_id: int, user_data: Union[UserResponse, User, Any]):
        """Cache user session data"""
        try:
            # Ensure user_id is an integer
            user_id = int(user_id)
            session_key = f"{self.user_session_prefix}{user_id}"
            
            # Convert to dict
            if isinstance(user_data, UserResponse):
                user_dict = user_data.model_dump()
            elif isinstance(user_data, User):
                pydantic_user = UserResponse.model_validate(user_data)
                user_dict = pydantic_user.model_dump()
            else:
                if hasattr(user_data, 'model_dump'):
                    user_dict = user_data.model_dump()
                elif hasattr(user_data, '__dict__'):
                    user_dict = {}
                    for key, value in user_data.__dict__.items():
                        if not key.startswith('_'):
                            user_dict[key] = value
                else:
                    print(f"Warning: Cannot cache user session with unsupported type: {type(user_data)}")
                    return

            # Store session with expiration
            json_data = json.dumps(user_dict, cls=DateTimeEncoder)
            self.redis_client.setex(session_key, self.expiration_time, json_data)
        except Exception as e:
            print(f"Error caching user session: {e}")

    async def get_user_session(self, user_id: int) -> Optional[dict]:
        """Get cached user session data"""
        try:
            session_key = f"{self.user_session_prefix}{user_id}"
            cached_session = self.redis_client.get(session_key)
            
            if cached_session is None:
                return None

            if isinstance(cached_session, bytes):
                cached_session = cached_session.decode("utf-8")
            elif not isinstance(cached_session, str):
                return None
            
            return json.loads(cached_session)
        except Exception as e:
            print(f"Error retrieving user session from cache: {e}")
            return None

    def invalidate_user_session(self, user_id: int):
        """Invalidate user session cache"""
        try:
            session_key = f"{self.user_session_prefix}{user_id}"
            self.redis_client.delete(session_key)
        except Exception as e:
            print(f"Error invalidating user session: {e}")

    def cache_token_blacklist(self, token: str, expires_at: datetime):
        """Cache blacklisted token until it expires"""
        try:
            token_key = f"{self.token_prefix}{token}"
            # Calculate TTL based on token expiration
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                self.redis_client.setex(token_key, ttl, "blacklisted")
        except Exception as e:
            print(f"Error caching blacklisted token: {e}")

    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            token_key = f"{self.token_prefix}{token}"
            exists = cast(Optional[int], self.redis_client.exists(token_key))
            # Handle the response properly
            if exists is None:
                return False
            return bool(exists and exists > 0)
        except Exception as e:
            print(f"Error checking token blacklist: {e}")
            return False

    def record_failed_login(self, username: str):
        """Record a failed login attempt"""
        try:
            failed_key = f"{self.failed_login_prefix}{username}"
            current_attempts = cast(Optional[str], self.redis_client.get(failed_key))
            
            if current_attempts is None:
                attempts = 1
            else:
                # Handle the response properly
                attempts = int(current_attempts) + 1
            
            # Set or update failed attempts count
            self.redis_client.setex(failed_key, self.lockout_duration, attempts)
            
            return attempts
        except Exception as e:
            print(f"Error recording failed login: {e}")
            return 0

    def get_failed_login_attempts(self, username: str) -> int:
        """Get number of failed login attempts for username"""
        try:
            failed_key = f"{self.failed_login_prefix}{username}"
            attempts = cast(Optional[str], self.redis_client.get(failed_key))
            # Handle the response properly
            if attempts is None:
                return 0
            return int(attempts)
        except Exception as e:
            print(f"Error getting failed login attempts: {e}")
            return 0

    def is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to too many failed attempts"""
        return self.get_failed_login_attempts(username) >= self.max_failed_attempts

    def clear_failed_login_attempts(self, username: str):
        """Clear failed login attempts for successful login"""
        try:
            failed_key = f"{self.failed_login_prefix}{username}"
            self.redis_client.delete(failed_key)
        except Exception as e:
            print(f"Error clearing failed login attempts: {e}")

    def cache_user_by_username(self, username: str, user_data: Union[UserResponse, User, Any]):
        """Cache user data by username for quick lookup"""
        try:
            username_key = f"user_by_username:{username}"
            
            # Convert to dict
            if isinstance(user_data, UserResponse):
                user_dict = user_data.model_dump()
            elif isinstance(user_data, User):
                pydantic_user = UserResponse.model_validate(user_data)
                user_dict = pydantic_user.model_dump()
            else:
                if hasattr(user_data, 'model_dump'):
                    user_dict = user_data.model_dump()
                elif hasattr(user_data, '__dict__'):
                    user_dict = {}
                    for key, value in user_data.__dict__.items():
                        if not key.startswith('_'):
                            user_dict[key] = value
                else:
                    print(f"Warning: Cannot cache user by username with unsupported type: {type(user_data)}")
                    return

            # Store with shorter expiration for username lookups
            json_data = json.dumps(user_dict, cls=DateTimeEncoder)
            self.redis_client.setex(username_key, 600, json_data)  # 10 minutes
        except Exception as e:
            print(f"Error caching user by username: {e}")

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get cached user data by username"""
        try:
            username_key = f"user_by_username:{username}"
            cached_user = cast(Optional[str], self.redis_client.get(username_key))
            
            if cached_user is None:
                return None

            if isinstance(cached_user, bytes):
                cached_user = cached_user.decode("utf-8")
            
            return json.loads(cached_user)
        except Exception as e:
            print(f"Error retrieving user by username from cache: {e}")
            return None

    def clear_auth_cache(self):
        """Clear all auth-related cache"""
        try:
            # Clear session caches
            session_pattern = f"{self.user_session_prefix}*"
            session_keys = cast(list, self.redis_client.keys(session_pattern))
            if session_keys:
                self.redis_client.delete(*session_keys)
            
            # Clear token blacklist
            token_pattern = f"{self.token_prefix}*"
            token_keys = cast(list, self.redis_client.keys(token_pattern))
            if token_keys:
                self.redis_client.delete(*token_keys)
            
            # Clear failed login attempts
            failed_pattern = f"{self.failed_login_prefix}*"
            failed_keys = cast(list, self.redis_client.keys(failed_pattern))
            if failed_keys:
                self.redis_client.delete(*failed_keys)
            
            # Clear username lookups
            username_pattern = "user_by_username:*"
            username_keys = cast(list, self.redis_client.keys(username_pattern))
            if username_keys:
                self.redis_client.delete(*username_keys)
        except Exception as e:
            print(f"Error clearing auth cache: {e}")

    def store_auth_token(self, user_id: int, token: str, expiration_time: int):
        """Store authentication token in cache"""
        try:
            token_key = f"{self.token_prefix}{token}"
            self.redis_client.setex(token_key, expiration_time, str(user_id))
        except Exception as e:
            print(f"Error storing auth token: {e}")

    def get_cache_info(self) -> dict:
        """Get auth cache information"""
        try:
            session_keys = cast(list, self.redis_client.keys(f"{self.user_session_prefix}*"))
            token_keys = cast(list, self.redis_client.keys(f"{self.token_prefix}*"))
            failed_keys = cast(list, self.redis_client.keys(f"{self.failed_login_prefix}*"))
            username_keys = cast(list, self.redis_client.keys("user_by_username:*"))
            
            return {
                "cache_type": "auth",
                "active_sessions": len(session_keys) if session_keys else 0,
                "blacklisted_tokens": len(token_keys) if token_keys else 0,
                "failed_login_attempts": len(failed_keys) if failed_keys else 0,
                "cached_usernames": len(username_keys) if username_keys else 0,
                "expiration_time": self.expiration_time,
                "max_failed_attempts": self.max_failed_attempts,
                "lockout_duration": self.lockout_duration
            }
        except Exception as e:
            print(f"Error getting auth cache info: {e}")
            return {"error": str(e)}
