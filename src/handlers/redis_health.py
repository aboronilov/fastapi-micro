from fastapi import APIRouter, HTTPException
from src.database.redis_config import test_redis_connection, get_redis_info

router = APIRouter(prefix="/redis", tags=["redis"])

@router.get("/health")
async def redis_health_check():
    """Redis health check"""
    try:
        if test_redis_connection():
            return {"status": "healthy", "redis": "connected"}
        else:
            return {"status": "unhealthy", "redis": "disconnected"}
    except Exception as e:
        return {"status": "unhealthy", "redis": "error", "error": str(e)}

@router.get("/info")
async def redis_info():
    """Get Redis server information"""
    try:
        info = get_redis_info()
        if info:
            return {
                "status": "success",
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "uptime_in_seconds": info.get("uptime_in_seconds")
            }
        else:
            raise HTTPException(status_code=503, detail="Redis not available")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis error: {str(e)}")

@router.post("/test")
async def redis_test():
    """Test Redis operations"""
    try:
        from src.database.redis_config import get_redis_client
        client = get_redis_client()
        
        # Test basic operations
        client.set("test_key", "test_value")
        value = client.get("test_key")
        client.delete("test_key")
        
        return {
            "status": "success",
            "message": "Redis operations test passed",
            "test_value": value
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis test failed: {str(e)}")
