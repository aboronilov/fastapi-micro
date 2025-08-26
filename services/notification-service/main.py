from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
import asyncio

# Import the existing notification service components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.services.notification.application.event_handlers import NotificationEventHandler, NotificationEventConsumer
from src.services.notification.domain.services import NotificationService
from src.dependencies import get_notification_domain_service, get_kafka_event_publisher, get_kafka_event_consumer
from src.event_bus import get_event_bus, shutdown_event_bus
from src.shared.events import ServiceStartedEvent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Notification management microservice",
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

# Pydantic models for API
class NotificationCreate(BaseModel):
    user_id: Optional[UUID] = None
    type: str
    title: str
    message: str
    recipient: str
    metadata: Optional[dict] = None

class NotificationResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    type: str
    title: str
    message: str
    recipient: str
    status: str
    created_at: datetime

# Global variables for event consumer
event_consumer = None
notification_event_handler = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "notification-service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Notification endpoints
@app.post("/notifications", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    notification_service: NotificationService = Depends(get_notification_domain_service)
):
    """Create a new notification"""
    try:
        from src.services.notification.domain.entities import NotificationType
        
        notification = await notification_service.create_notification(
            user_id=notification_data.user_id,
            type=NotificationType(notification_data.type),
            title=notification_data.title,
            message=notification_data.message,
            recipient=notification_data.recipient,
            metadata=notification_data.metadata or {}
        )
        
        return NotificationResponse(
            id=str(notification.id),
            user_id=str(notification.user_id) if notification.user_id else None,
            type=notification.type.value,
            title=notification.title,
            message=notification.message,
            recipient=notification.recipient,
            status=notification.status.value,
            created_at=notification.created_at
        )
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/notifications", response_model=List[NotificationResponse])
async def list_notifications(
    user_id: Optional[UUID] = None,
    limit: int = 100,
    notification_service: NotificationService = Depends(get_notification_domain_service)
):
    """List notifications"""
    try:
        if user_id:
            notifications = await notification_service.notification_repository.list_by_user_id(user_id, limit)
        else:
            notifications = await notification_service.notification_repository.get_pending_notifications()
        
        return [
            NotificationResponse(
                id=str(notification.id),
                user_id=str(notification.user_id) if notification.user_id else None,
                type=notification.type.value,
                title=notification.title,
                message=notification.message,
                recipient=notification.recipient,
                status=notification.status.value,
                created_at=notification.created_at
            )
            for notification in notifications
        ]
    except Exception as e:
        logger.error(f"Error listing notifications: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    notification_service: NotificationService = Depends(get_notification_domain_service)
):
    """Get a specific notification"""
    try:
        notification = await notification_service.notification_repository.get_by_id(notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return NotificationResponse(
            id=str(notification.id),
            user_id=str(notification.user_id) if notification.user_id else None,
            type=notification.type.value,
            title=notification.title,
            message=notification.message,
            recipient=notification.recipient,
            status=notification.status.value,
            created_at=notification.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/notifications/{notification_id}/send")
async def send_notification(
    notification_id: UUID,
    notification_service: NotificationService = Depends(get_notification_domain_service)
):
    """Send a notification"""
    try:
        success = await notification_service.send_notification(notification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"message": "Notification sent successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    notification_service: NotificationService = Depends(get_notification_domain_service)
):
    """Delete a notification"""
    try:
        success = await notification_service.notification_repository.delete(notification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"message": "Notification deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Event consumer background task
async def start_event_consumer():
    """Start the event consumer in the background"""
    global event_consumer, notification_event_handler
    
    try:
        # Get notification service and event publisher
        notification_service = await get_notification_domain_service()
        event_publisher = await get_kafka_event_publisher()
        
        # Create event handler
        notification_event_handler = NotificationEventHandler(notification_service, event_publisher)
        
        # Create event consumer
        event_consumer = await get_kafka_event_consumer(
            topics=["user.events", "task.events"],
            group_id="notification-service"
        )
        
        # Subscribe to events
        event_consumer.subscribe("user.created", notification_event_handler.handle_user_created)
        event_consumer.subscribe("task.completed", notification_event_handler.handle_task_completed)
        
        # Start consuming events in background
        asyncio.create_task(event_consumer.consume())
        
        logger.info("✅ Notification event consumer started")
        
    except Exception as e:
        logger.error(f"❌ Failed to start event consumer: {e}")

async def stop_event_consumer():
    """Stop the event consumer"""
    global event_consumer
    
    if event_consumer:
        try:
            await event_consumer.stop()
            logger.info("✅ Notification event consumer stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping event consumer: {e}")

@app.on_event("startup")
async def startup_event():
    """Startup event - initialize event bus and consumer"""
    try:
        # Initialize event bus
        event_bus = await get_event_bus()
        
        # Publish service started event
        event = ServiceStartedEvent(
            aggregate_id="notification-service",
            aggregate_type="Service",
            data={
                "service_name": "notification-service",
                "version": "1.0.0",
                "started_at": datetime.now().isoformat()
            }
        )
        await event_bus.publish_event(event)
        
        # Start event consumer
        await start_event_consumer()
        
        logger.info("✅ Notification Service started with event-driven architecture")
        
    except Exception as e:
        logger.error(f"❌ Failed to start notification service: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - cleanup event bus and consumer"""
    try:
        await stop_event_consumer()
        await shutdown_event_bus()
        logger.info("✅ Notification Service shutdown completed")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
