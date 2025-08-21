import json
from typing import Optional, Any, Union
from datetime import datetime
import redis


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def safe_redis_get(client: redis.Redis, key: str) -> Optional[str]:
    """Safely get value from Redis with proper type handling"""
    try:
        value = client.get(key)
        if value is None:
            return None
        
        if isinstance(value, bytes):
            return value.decode("utf-8")
        elif isinstance(value, str):
            return value
        else:
            return str(value)
    except Exception as e:
        print(f"Error getting Redis key {key}: {e}")
        return None


def safe_redis_setex(client: redis.Redis, key: str, time: int, value: str) -> bool:
    """Safely set Redis key with expiration"""
    try:
        client.setex(key, time, value)
        return True
    except Exception as e:
        print(f"Error setting Redis key {key}: {e}")
        return False


def safe_redis_delete(client: redis.Redis, key: str) -> bool:
    """Safely delete Redis key"""
    try:
        result = client.delete(key)
        return bool(result)
    except Exception as e:
        print(f"Error deleting Redis key {key}: {e}")
        return False


def safe_redis_exists(client: redis.Redis, key: str) -> bool:
    """Safely check if Redis key exists"""
    try:
        result = client.exists(key)
        if result is None:
            return False
        return bool(result)
    except Exception as e:
        print(f"Error checking Redis key {key}: {e}")
        return False


def safe_redis_keys(client: redis.Redis, pattern: str) -> list:
    """Safely get Redis keys matching pattern"""
    try:
        keys = client.keys(pattern)
        if keys is None:
            return []
        # Convert to list and handle bytes/string conversion
        result = []
        keys_list = list(keys) if keys else []  # type: ignore
        for key in keys_list:
            if isinstance(key, bytes):
                result.append(key.decode("utf-8"))
            else:
                result.append(str(key))
        return result
    except Exception as e:
        print(f"Error getting Redis keys for pattern {pattern}: {e}")
        return []


def safe_json_loads(data: str) -> Optional[Any]:
    """Safely load JSON data"""
    try:
        return json.loads(data)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None


def safe_json_dumps(data: Any) -> Optional[str]:
    """Safely dump data to JSON string"""
    try:
        return json.dumps(data, cls=DateTimeEncoder)
    except Exception as e:
        print(f"Error dumping JSON: {e}")
        return None
