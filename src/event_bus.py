import asyncio
import logging
from typing import Optional
from src.shared.kafka_client import KafkaEventBus, KafkaEventPublisher, KafkaEventConsumer
from src.shared.events import DomainEvent
from src.services.notification.application.event_handlers import NotificationEventHandler

logger = logging.getLogger(__name__)


class ApplicationEventBus:
    """Main application event bus for coordinating microservices"""
    
    def __init__(self, kafka_bootstrap_servers: str = "localhost:9092"):
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_event_bus: Optional[KafkaEventBus] = None
        self.event_publisher: Optional[KafkaEventPublisher] = None
        self.event_consumers: list[KafkaEventConsumer] = []
        self._running = False
    
    async def start(self):
        """Start the application event bus"""
        if self._running:
            return
        
        try:
            # Initialize Kafka event bus
            self.kafka_event_bus = KafkaEventBus(
                bootstrap_servers=self.kafka_bootstrap_servers
            )
            await self.kafka_event_bus.start()
            
            # Initialize event publisher
            self.event_publisher = KafkaEventPublisher(
                bootstrap_servers=self.kafka_bootstrap_servers
            )
            await self.event_publisher.start()
            
            self._running = True
            logger.info("Application event bus started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start application event bus: {e}")
            raise
    
    async def stop(self):
        """Stop the application event bus"""
        if not self._running:
            return
        
        try:
            # Stop event consumers
            for consumer in self.event_consumers:
                await consumer.stop()
            self.event_consumers.clear()
            
            # Stop event publisher
            if self.event_publisher:
                await self.event_publisher.stop()
            
            # Stop Kafka event bus
            if self.kafka_event_bus:
                await self.kafka_event_bus.stop()
            
            self._running = False
            logger.info("Application event bus stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping application event bus: {e}")
    
    async def publish_event(self, event: DomainEvent, topic: Optional[str] = None):
        """Publish an event"""
        if not self._running or not self.event_publisher:
            raise RuntimeError("Application event bus is not running")
        
        await self.event_publisher.publish(event, topic)
    
    def get_event_publisher(self) -> KafkaEventPublisher:
        """Get the event publisher instance"""
        if not self.event_publisher:
            raise RuntimeError("Event publisher is not initialized")
        return self.event_publisher
    
    def get_kafka_event_bus(self) -> KafkaEventBus:
        """Get the Kafka event bus instance"""
        if not self.kafka_event_bus:
            raise RuntimeError("Kafka event bus is not initialized")
        return self.kafka_event_bus


# Global event bus instance
event_bus: Optional[ApplicationEventBus] = None


async def get_event_bus() -> ApplicationEventBus:
    """Get the global event bus instance"""
    global event_bus
    if event_bus is None:
        event_bus = ApplicationEventBus()
        await event_bus.start()
    return event_bus


async def shutdown_event_bus():
    """Shutdown the global event bus"""
    global event_bus
    if event_bus:
        await event_bus.stop()
        event_bus = None
