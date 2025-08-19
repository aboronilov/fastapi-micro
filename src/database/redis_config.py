import os
import redis
from typing import Optional

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )

def test_redis_connection() -> bool:
    """Test Redis connection"""
    try:
        client = get_redis_client()
        client.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False

def get_redis_info() -> Optional[dict]:
    """Get Redis server information"""
    try:
        client = get_redis_client()
        return client.info()  # type: ignore
    except Exception as e:
        print(f"Failed to get Redis info: {e}")
        return None
