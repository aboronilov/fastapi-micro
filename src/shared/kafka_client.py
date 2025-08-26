import asyncio
import json
import logging
from typing import Callable, Dict, List, Optional, Any, Union
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError, KafkaConnectionError, KafkaTimeoutError
from .events import DomainEvent, create_event_from_type

logger = logging.getLogger(__name__)


class KafkaEventBus:
    """Kafka-based event bus for microservices communication"""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        producer_config: Optional[Dict[str, Any]] = None,
        consumer_config: Optional[Dict[str, Any]] = None
    ):
        self.bootstrap_servers = bootstrap_servers
        self.producer_config = producer_config or {}
        self.consumer_config = consumer_config or {}
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumers: Dict[str, AIOKafkaConsumer] = {}
        self.handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._consumer_tasks: List[asyncio.Task] = []
        
    async def start(self):
        """Start the Kafka event bus"""
        if self._running:
            logger.warning("Kafka event bus is already running")
            return
            
        try:
            # Initialize producer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                **self.producer_config
            )
            await self.producer.start()
            
            self._running = True
            logger.info("Kafka event bus started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Kafka event bus: {e}")
            await self._cleanup()
            raise
    
    async def stop(self):
        """Stop the Kafka event bus"""
        if not self._running:
            logger.warning("Kafka event bus is not running")
            return
            
        try:
            # Cancel all consumer tasks
            for task in self._consumer_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            self._consumer_tasks.clear()
            
            # Stop producer
            if self.producer:
                await self.producer.stop()
                self.producer = None
                
            # Stop consumers
            for consumer in self.consumers.values():
                try:
                    await consumer.stop()
                except Exception as e:
                    logger.warning(f"Error stopping consumer: {e}")
            
            self.consumers.clear()
            self._running = False
            logger.info("Kafka event bus stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping Kafka event bus: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def _cleanup(self):
        """Clean up resources"""
        self._running = False
        self.producer = None
        self.consumers.clear()
        self.handlers.clear()
    
    async def publish(self, event: DomainEvent, topic: Optional[str] = None):
        """Publish an event to Kafka"""
        if not self._running:
            raise RuntimeError("Kafka event bus is not running")
        
        if not self.producer:
            raise RuntimeError("Producer is not initialized")
            
        topic = topic or f"{event.aggregate_type.lower()}.events"
        
        try:
            event_data = event.to_dict()
            await self.producer.send_and_wait(topic, event_data)
            logger.info(f"Published event {event.event_type} to topic {topic}")
        except KafkaConnectionError as e:
            logger.error(f"Kafka connection error while publishing event {event.event_type}: {e}")
            raise
        except KafkaTimeoutError as e:
            logger.error(f"Kafka timeout error while publishing event {event.event_type}: {e}")
            raise
        except KafkaError as e:
            logger.error(f"Kafka error while publishing event {event.event_type}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while publishing event {event.event_type}: {e}")
            raise
    
    async def subscribe(
        self,
        event_types: List[str],
        handler: Callable,
        topic: Optional[str] = None,
        group_id: Optional[str] = None
    ):
        """Subscribe to events"""
        if not self._running:
            raise RuntimeError("Kafka event bus is not running")
        
        if not topic:
            # Determine topic from event types
            if len(event_types) == 1:
                event_type = event_types[0]
                aggregate_type = event_type.split('.')[0]
                topic = f"{aggregate_type}.events"
            else:
                topic = "all.events"
        
        if not group_id:
            group_id = f"{topic}-consumer-group"
        
        # Register handler
        for event_type in event_types:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)
        
        # Create consumer if not exists
        if topic not in self.consumers:
            try:
                consumer = AIOKafkaConsumer(
                    topic,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=group_id,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else {},
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    **self.consumer_config
                )
                await consumer.start()
                self.consumers[topic] = consumer
                
                # Start consuming messages
                task = asyncio.create_task(self._consume_messages(consumer, topic))
                self._consumer_tasks.append(task)
                
                logger.info(f"Started consumer for topic {topic}")
                
            except Exception as e:
                logger.error(f"Failed to create consumer for topic {topic}: {e}")
                raise
            
        logger.info(f"Subscribed to events {event_types} on topic {topic}")
    
    async def _consume_messages(self, consumer: AIOKafkaConsumer, topic: str):
        """Consume messages from Kafka"""
        try:
            async for message in consumer:
                try:
                    event_data = message.value
                    if not event_data:
                        logger.warning(f"Received empty message on topic {topic}")
                        continue
                    
                    event_type = event_data.get("event_type")
                    if not event_type:
                        logger.warning(f"Message missing event_type on topic {topic}")
                        continue
                    
                    if event_type in self.handlers:
                        # Create event object
                        try:
                            event = create_event_from_type(event_type, **event_data)
                        except Exception as e:
                            logger.error(f"Failed to create event from data: {e}")
                            continue
                        
                        # Call handlers
                        for handler in self.handlers[event_type]:
                            try:
                                if asyncio.iscoroutinefunction(handler):
                                    await handler(event)
                                else:
                                    handler(event)
                            except Exception as e:
                                logger.error(f"Handler error for event {event_type}: {e}")
                    else:
                        logger.debug(f"No handlers for event type: {event_type}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error processing message on topic {topic}: {e}")
                except Exception as e:
                    logger.error(f"Error processing message on topic {topic}: {e}")
                    
        except asyncio.CancelledError:
            logger.info(f"Consumer task cancelled for topic {topic}")
        except Exception as e:
            logger.error(f"Consumer error on topic {topic}: {e}")
        finally:
            try:
                await consumer.stop()
            except Exception as e:
                logger.warning(f"Error stopping consumer for topic {topic}: {e}")


class KafkaEventPublisher:
    """Simple Kafka event publisher"""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer: Optional[AIOKafkaProducer] = None
        self._running = False
    
    async def start(self):
        """Start the publisher"""
        if self._running:
            logger.warning("Kafka event publisher is already running")
            return
            
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()
            self._running = True
            logger.info("Kafka event publisher started successfully")
        except Exception as e:
            logger.error(f"Failed to start Kafka event publisher: {e}")
            await self._cleanup()
            raise
    
    async def stop(self):
        """Stop the publisher"""
        if not self._running:
            logger.warning("Kafka event publisher is not running")
            return
            
        try:
            if self.producer:
                await self.producer.stop()
            logger.info("Kafka event publisher stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping Kafka event publisher: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def _cleanup(self):
        """Clean up resources"""
        self._running = False
        self.producer = None
    
    async def publish(self, event: DomainEvent, topic: Optional[str] = None):
        """Publish an event"""
        if not self._running:
            raise RuntimeError("Publisher is not started")
        
        if not self.producer:
            raise RuntimeError("Producer is not initialized")
            
        topic = topic or f"{event.aggregate_type.lower()}.events"
        
        try:
            event_data = event.to_dict()
            await self.producer.send_and_wait(topic, event_data)
            logger.info(f"Published event {event.event_type} to topic {topic}")
        except KafkaConnectionError as e:
            logger.error(f"Kafka connection error while publishing event {event.event_type}: {e}")
            raise
        except KafkaTimeoutError as e:
            logger.error(f"Kafka timeout error while publishing event {event.event_type}: {e}")
            raise
        except KafkaError as e:
            logger.error(f"Kafka error while publishing event {event.event_type}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while publishing event {event.event_type}: {e}")
            raise


class KafkaEventConsumer:
    """Simple Kafka event consumer"""
    
    def __init__(
        self,
        topics: List[str],
        group_id: str,
        bootstrap_servers: str = "localhost:9092"
    ):
        self.topics = topics
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._consume_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the consumer"""
        if self._running:
            logger.warning("Kafka event consumer is already running")
            return
            
        try:
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else {},
                auto_offset_reset='earliest',
                enable_auto_commit=True
            )
            await self.consumer.start()
            self._running = True
            logger.info(f"Kafka event consumer started for topics: {self.topics}")
        except Exception as e:
            logger.error(f"Failed to start Kafka event consumer: {e}")
            await self._cleanup()
            raise
    
    async def stop(self):
        """Stop the consumer"""
        if not self._running:
            logger.warning("Kafka event consumer is not running")
            return
            
        try:
            # Cancel consume task
            if self._consume_task and not self._consume_task.done():
                self._consume_task.cancel()
                try:
                    await self._consume_task
                except asyncio.CancelledError:
                    pass
            
            # Stop consumer
            if self.consumer:
                await self.consumer.stop()
            
            logger.info("Kafka event consumer stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping Kafka event consumer: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def _cleanup(self):
        """Clean up resources"""
        self._running = False
        self.consumer = None
        self._consume_task = None
        self.handlers.clear()
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.info(f"Subscribed to event type: {event_type}")
    
    async def consume(self):
        """Start consuming messages"""
        if not self._running:
            raise RuntimeError("Consumer is not started")
        
        if not self.consumer:
            raise RuntimeError("Consumer is not initialized")
        
        if self._consume_task and not self._consume_task.done():
            logger.warning("Consumer task is already running")
            return
            
        self._consume_task = asyncio.create_task(self._consume_messages())
        logger.info("Started consuming messages")
    
    async def _consume_messages(self):
        """Consume messages from Kafka"""
        if not self.consumer:
            logger.error("Consumer is not initialized")
            return
            
        try:
            async for message in self.consumer:
                try:
                    event_data = message.value
                    if not event_data:
                        logger.warning("Received empty message")
                        continue
                    
                    event_type = event_data.get("event_type")
                    if not event_type:
                        logger.warning("Message missing event_type")
                        continue
                    
                    if event_type in self.handlers:
                        try:
                            event = create_event_from_type(event_type, **event_data)
                        except Exception as e:
                            logger.error(f"Failed to create event from data: {e}")
                            continue
                        
                        for handler in self.handlers[event_type]:
                            try:
                                if asyncio.iscoroutinefunction(handler):
                                    await handler(event)
                                else:
                                    handler(event)
                            except Exception as e:
                                logger.error(f"Handler error for event {event_type}: {e}")
                    else:
                        logger.debug(f"No handlers for event type: {event_type}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error processing message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Consumer task cancelled")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            try:
                if self.consumer:
                    await self.consumer.stop()
            except Exception as e:
                logger.warning(f"Error stopping consumer: {e}")
