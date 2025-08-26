from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

# Import the existing user service components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.services.user.api.routes import router as user_router
from src.event_bus import get_event_bus, shutdown_event_bus
from src.shared.events import ServiceStartedEvent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="User Service",
    description="User management microservice",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include user routes
app.include_router(user_router, prefix="/users", tags=["users"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "user-service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Auth verification endpoint for API Gateway
@app.post("/auth/verify")
async def verify_token():
    """Verify JWT token - called by API Gateway"""
    # This would implement JWT verification logic
    # For now, return a placeholder response
    return {"valid": True, "user_id": "123"}

@app.on_event("startup")
async def startup_event():
    """Startup event - initialize event bus"""
    try:
        # Initialize event bus
        event_bus = await get_event_bus()
        
        # Publish service started event
        event = ServiceStartedEvent(
            aggregate_id="user-service",
            aggregate_type="Service",
            data={
                "service_name": "user-service",
                "version": "1.0.0",
                "started_at": datetime.now().isoformat()
            }
        )
        await event_bus.publish_event(event)
        
        logger.info("✅ User Service started with event-driven architecture")
        
    except Exception as e:
        logger.error(f"❌ Failed to start event bus: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - cleanup event bus"""
    try:
        await shutdown_event_bus()
        logger.info("✅ User Service shutdown completed")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
