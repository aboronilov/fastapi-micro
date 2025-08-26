from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import httpx
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service configurations
SERVICES = {
    "user": {
        "url": "http://user-service:8001",
        "health_check": "/health",
        "routes": ["/users", "/auth"]
    },
    "task": {
        "url": "http://task-service:8002", 
        "health_check": "/health",
        "routes": ["/tasks", "/categories"]
    },
    "notification": {
        "url": "http://notification-service:8003",
        "health_check": "/health", 
        "routes": ["/notifications"]
    }
}

# Create FastAPI app
app = FastAPI(
    title="API Gateway",
    description="API Gateway for Microservices Architecture",
    version="1.0.0"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Health check model
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]

# Service discovery and health monitoring
class ServiceRegistry:
    def __init__(self):
        self.services = SERVICES
        self.health_status = {}
    
    async def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        try:
            service_config = self.services.get(service_name)
            if not service_config:
                return False
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_config['url']}{service_config['health_check']}")
                if response.status_code == 200:
                    self.health_status[service_name] = "healthy"
                    return True
                else:
                    self.health_status[service_name] = "unhealthy"
                    return False
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            self.health_status[service_name] = "unreachable"
            return False
    
    async def check_all_services(self) -> Dict[str, str]:
        """Check health of all services"""
        tasks = []
        for service_name in self.services.keys():
            tasks.append(self.check_service_health(service_name))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        return self.health_status
    
    def get_service_url(self, service_name: str) -> Optional[str]:
        """Get service URL by name"""
        service_config = self.services.get(service_name)
        return service_config["url"] if service_config else None
    
    def find_service_by_path(self, path: str) -> Optional[str]:
        """Find which service should handle a given path"""
        for service_name, config in self.services.items():
            for route in config["routes"]:
                if path.startswith(route):
                    return service_name
        return None

# Initialize service registry
service_registry = ServiceRegistry()

# Authentication middleware
async def verify_token(request: Request) -> Optional[Dict]:
    """Verify JWT token from request"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    
    # Forward token verification to user service
    try:
        user_service_url = service_registry.get_service_url("user")
        if not user_service_url:
            return None
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{user_service_url}/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None

# Rate limiting
class RateLimiter:
    def __init__(self):
        self.requests = {}
        self.max_requests = 100  # requests per minute
        self.window = 60  # seconds
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed based on rate limiting"""
        now = datetime.now()
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old requests outside the window
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if (now - req_time).seconds < self.window
        ]
        
        # Check if under limit
        if len(self.requests[client_ip]) < self.max_requests:
            self.requests[client_ip].append(now)
            return True
        
        return False

rate_limiter = RateLimiter()

# Request forwarding
async def forward_request(request: Request, service_name: str, path: str):
    """Forward request to appropriate service"""
    service_url = service_registry.get_service_url(service_name)
    if not service_url:
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    # Check rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Prepare headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header
    
    # Prepare query parameters
    query_params = dict(request.query_params)
    
    # Get request body
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
        except Exception:
            pass
    
    # Forward request
    try:
        target_url = f"{service_url}{path}"
        logger.info(f"Forwarding {request.method} {path} to {target_url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=query_params,
                content=body
            )
            
            # Return response
            return JSONResponse(
                content=response.json() if response.headers.get("content-type") == "application/json" else response.text,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.TimeoutException:
        logger.error(f"Timeout forwarding request to {service_name}")
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except httpx.ConnectError:
        logger.error(f"Connection error to {service_name}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Error forwarding request to {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal gateway error")

# API Gateway routes
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    services_health = await service_registry.check_all_services()
    
    overall_status = "healthy" if all(status == "healthy" for status in services_health.values()) else "degraded"
    
    return HealthCheck(
        status=overall_status,
        timestamp=datetime.now(),
        services=services_health
    )

@app.get("/services")
async def list_services():
    """List all available services"""
    return {
        "services": list(SERVICES.keys()),
        "configurations": SERVICES
    }

# Dynamic routing - catch all requests and forward to appropriate service
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def route_request(request: Request, path: str):
    """Route requests to appropriate microservice"""
    
    # Skip health checks and gateway-specific routes
    if path in ["health", "services", "docs", "openapi.json"]:
        return await request.app.router.handle(request)
    
    # Find which service should handle this request
    service_name = service_registry.find_service_by_path(f"/{path}")
    if not service_name:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Check if service is healthy
    is_healthy = await service_registry.check_service_health(service_name)
    if not is_healthy:
        raise HTTPException(status_code=503, detail=f"Service {service_name} is unavailable")
    
    # Forward the request
    return await forward_request(request, service_name, f"/{path}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
