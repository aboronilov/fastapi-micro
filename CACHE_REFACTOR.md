# Cache Refactoring: Time-Based Expiration

## Overview

The caching system has been refactored to use **time-based expiration** instead of manual cache invalidation. This provides better performance, reduced complexity, and automatic cache management.

## Key Changes

### 1. Time-Based Expiration
- Cache entries now automatically expire after a configurable time period
- Default expiration: 5 minutes (300 seconds)
- Configurable via `CACHE_EXPIRATION_SECONDS` environment variable

### 2. Cache-First Strategy
- API endpoints now check cache first before hitting the database
- Improved response times for frequently accessed data
- Automatic fallback to database when cache is empty or expired

### 3. Removed Manual Cache Invalidation
- No more manual cache clearing on create/update/delete operations
- Cache automatically becomes stale and expires
- Reduced complexity in business logic

## Configuration

### Environment Variables
```bash
# Cache expiration time in seconds (default: 300)
CACHE_EXPIRATION_SECONDS=600
```

### Settings
The cache configuration is managed through the `Settings` class in `src/settings.py`:
```python
CACHE_EXPIRATION_SECONDS: int = Field(
    default=300, 
    description="Cache expiration time in seconds (default: 5 minutes)"
)
```

## API Endpoints

### Cache Information
- `GET /task/cache/info` - Get cache status and TTL information
- `DELETE /task/cache/clear` - Manually clear cache (for testing/emergency use)

### Task Endpoints (Updated)
- `GET /task/all` - Now uses cache-first strategy with automatic expiration
- `POST /task/` - No longer invalidates cache (automatic expiration)
- `PATCH /task/{task_id}` - No longer invalidates cache (automatic expiration)
- `DELETE /task/{task_id}` - No longer invalidates cache (automatic expiration)

## Benefits

1. **Better Performance**: Cache-first strategy reduces database load
2. **Simplified Logic**: No need to track cache invalidation points
3. **Automatic Management**: Cache expires naturally, no manual intervention needed
4. **Configurable**: Easy to adjust cache duration based on data volatility
5. **Resilient**: Graceful fallback to database if cache fails

## Cache Behavior

1. **First Request**: Cache miss → Database query → Cache population
2. **Subsequent Requests**: Cache hit → Return cached data
3. **After Expiration**: Cache miss → Database query → Cache refresh
4. **Write Operations**: No cache invalidation needed, data will expire naturally

## Monitoring

Use the `/task/cache/info` endpoint to monitor:
- Cache existence status
- Time to live (TTL) remaining
- Configured expiration time

## Migration Notes

- Existing cache invalidation calls have been removed
- Cache expiration is now the primary mechanism for data freshness
- Manual cache clearing is available for testing and emergency situations
- No breaking changes to existing API contracts
