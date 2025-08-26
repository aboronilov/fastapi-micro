from fastapi import FastAPI
from src.event_bus import get_event_bus, shutdown_event_bus
from src.shared.events import ServiceStartedEvent
from datetime import datetime

app = FastAPI(title="FastAPI Microservices (Legacy)", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Startup event - initialize event bus"""
    try:
        # Initialize event bus
        event_bus = await get_event_bus()
        
        # Publish service started event
        event = ServiceStartedEvent(
            aggregate_id="fastapi-micro-legacy",
            aggregate_type="Service",
            data={
                "service_name": "fastapi-micro-legacy",
                "version": "1.0.0",
                "started_at": datetime.utcnow().isoformat()
            }
        )
        await event_bus.publish_event(event)
        
        print("✅ FastAPI Microservices (Legacy) started with event-driven architecture")
        
    except Exception as e:
        print(f"❌ Failed to start event bus: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - cleanup event bus"""
    try:
        await shutdown_event_bus()
        print("✅ Event bus shutdown completed")
    except Exception as e:
        print(f"❌ Error during shutdown: {e}")

# Event bus health check
@app.get("/health/events")
async def event_health_check():
    try:
        event_bus = await get_event_bus()
        return {"status": "healthy", "event_bus": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "event_bus": str(e)}

# System health check
@app.get("/health")
async def system_health_check():
    try:
        # Check event bus
        event_status = "healthy"
        try:
            await get_event_bus()
        except Exception:
            event_status = "unhealthy"
        
        return {
            "status": event_status,
            "service": "fastapi-micro-legacy",
            "services": {
                "event_bus": event_status
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "FastAPI Microservices (Legacy)",
        "version": "1.0.0",
        "note": "This is the legacy service. Use the API Gateway for the new microservices architecture."
    }
