from typing import Optional, List, Union, Any, cast
from src.database.redis_config import get_redis_client
from src.schemas.user import UserResponse
from src.database.models import User
import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class UserCache:
    def __init__(self, expiration_time: int = 300):  # 5 minutes default expiration
        self.redis_client = get_redis_client()
        self.expiration_time = expiration_time
        self.users_key = "users"
        self.users_count_key = "users_count"
        self.user_prefix = "user:"

    def get_users(self, skip: int = 0, limit: int = 100) -> Optional[List[dict]]:
        """Get users from cache with pagination"""
        try:
            # Get all cached users
            cached_users = self.redis_client.get(self.users_key)
            if cached_users is None:
                return None

            # Ensure cached_users is a string before loading JSON
            if isinstance(cached_users, bytes):
                cached_users = cached_users.decode("utf-8")
            elif not isinstance(cached_users, str):
                return None
            
            users = json.loads(cached_users)

            # Apply pagination
            start = skip
            end = skip + limit
            return users[start:end]
        except Exception as e:
            print(f"Error retrieving users from cache: {e}")
            return None

    def set_users(self, users: List[Union[UserResponse, User, Any]]):
        """Cache users with expiration time"""
        try:
            # Convert User objects to dictionaries
            user_dicts = []
            for user in users:
                if isinstance(user, UserResponse):
                    # Already a Pydantic model
                    user_dicts.append(user.model_dump())
                elif isinstance(user, User):
                    # SQLAlchemy model - convert to Pydantic model first
                    pydantic_user = UserResponse.model_validate(user)
                    user_dicts.append(pydantic_user.model_dump())
                else:
                    # Handle dict or other types
                    if hasattr(user, 'model_dump'):
                        user_dicts.append(user.model_dump())
                    elif hasattr(user, '__dict__'):
                        # Convert SQLAlchemy model to dict
                        user_dict = {}
                        for key, value in user.__dict__.items():
                            if not key.startswith('_'):
                                user_dict[key] = value
                        user_dicts.append(user_dict)
                    else:
                        print(f"Warning: Skipping user with unsupported type: {type(user)}")
                        continue
            
            # Store users as JSON string with expiration
            json_data = json.dumps(user_dicts, cls=DateTimeEncoder)
            self.redis_client.setex(
                self.users_key,
                self.expiration_time,
                json_data
            )
            
            # Also cache the count for quick access
            self.redis_client.setex(
                self.users_count_key,
                self.expiration_time,
                len(user_dicts)
            )
        except Exception as e:
            print(f"Error caching users: {e}")

    def get_user(self, user_id: int) -> Optional[dict]:
        """Get a specific user from cache by ID"""
        try:
            user_key = f"{self.user_prefix}{user_id}"
            cached_user = cast(Optional[str], self.redis_client.get(user_key))
            
            if cached_user is None:
                return None

            if isinstance(cached_user, bytes):
                cached_user = cached_user.decode("utf-8")
            
            return json.loads(cached_user)
        except Exception as e:
            print(f"Error retrieving user from cache: {e}")
            return None

    def set_user(self, user: Union[UserResponse, User, Any]):
        """Cache a specific user"""
        try:
            user_id = getattr(user, 'id', None)
            if user_id is None:
                print("Warning: User object has no 'id' attribute")
                return

            # Ensure user_id is an integer
            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                print(f"Warning: Invalid user_id type: {type(user_id)}")
                return

            user_key = f"{self.user_prefix}{user_id}"
            
            # Convert to dict
            if isinstance(user, UserResponse):
                user_dict = user.model_dump()
            elif isinstance(user, User):
                pydantic_user = UserResponse.model_validate(user)
                user_dict = pydantic_user.model_dump()
            else:
                if hasattr(user, 'model_dump'):
                    user_dict = user.model_dump()
                elif hasattr(user, '__dict__'):
                    user_dict = {}
                    for key, value in user.__dict__.items():
                        if not key.startswith('_'):
                            user_dict[key] = value
                else:
                    print(f"Warning: Cannot cache user with unsupported type: {type(user)}")
                    return

            # Store user with expiration
            json_data = json.dumps(user_dict, cls=DateTimeEncoder)
            self.redis_client.setex(
                user_key,
                self.expiration_time,
                json_data
            )
        except Exception as e:
            print(f"Error caching user: {e}")

    def delete_user(self, user_id: int):
        """Delete a specific user from cache"""
        try:
            # Ensure user_id is an integer
            user_id = int(user_id)
            user_key = f"{self.user_prefix}{user_id}"
            self.redis_client.delete(user_key)
        except (ValueError, TypeError) as e:
            print(f"Error: Invalid user_id type: {e}")
        except Exception as e:
            print(f"Error deleting user from cache: {e}")

    def clear_users_cache(self):
        """Clear all users cache"""
        try:
            # Delete the main users list
            self.redis_client.delete(self.users_key)
            self.redis_client.delete(self.users_count_key)
            
            # Delete individual user caches (this is a simple approach)
            # In production, you might want to use Redis SCAN for better performance
            pattern = f"{self.user_prefix}*"
            keys = cast(list, self.redis_client.keys(pattern))
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Error clearing users cache: {e}")

    def get_users_count(self) -> Optional[int]:
        """Get the count of cached users"""
        try:
            count = cast(Optional[str], self.redis_client.get(self.users_count_key))
            if count is not None:
                return int(count)
            return None
        except Exception as e:
            print(f"Error retrieving users count from cache: {e}")
            return None

    def get_cache_info(self) -> dict:
        """Get cache information including TTL"""
        try:
            ttl = cast(int, self.redis_client.ttl(self.users_key))
            count = self.get_users_count()
            
            return {
                "cache_type": "users",
                "ttl_seconds": ttl if ttl > 0 else None,
                "cached_users_count": count,
                "expiration_time": self.expiration_time
            }
        except Exception as e:
            print(f"Error getting cache info: {e}")
            return {"error": str(e)}
