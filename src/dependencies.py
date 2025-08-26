from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from .shared.kafka_client import KafkaEventPublisher, KafkaEventConsumer, KafkaEventBus
from .event_bus import get_event_bus
from .services.user.domain.services import UserDomainService
from .services.user.application.handlers import UserCommandHandler
from .services.task.domain.services import TaskDomainService
from .services.notification.domain.services import NotificationService
from .services.integration.service_orchestrator import ServiceOrchestrator
from .services.user.infrastructure.repositories import SQLAlchemyUserRepository, SQLAlchemyUserProfileRepository
from .services.task.infrastructure.repositories import SQLAlchemyTaskRepository, SQLAlchemyCategoryRepository
from .services.notification.infrastructure.repositories import SQLAlchemyNotificationRepository, SQLAlchemyNotificationTemplateRepository


# Kafka Dependencies
async def get_kafka_event_publisher() -> KafkaEventPublisher:
    """Get Kafka event publisher"""
    publisher = KafkaEventPublisher(bootstrap_servers="kafka:9092")
    await publisher.start()
    return publisher


async def get_kafka_event_consumer(
    topics: Optional[list[str]] = None,
    group_id: str = "default-consumer-group"
) -> KafkaEventConsumer:
    """Get Kafka event consumer"""
    if topics is None:
        topics = ["user.events", "task.events", "notification.events"]
    
    consumer = KafkaEventConsumer(
        topics=topics,
        group_id=group_id,
        bootstrap_servers="kafka:9092"
    )
    await consumer.start()
    return consumer


async def get_event_bus() -> KafkaEventBus:
    """Get Kafka event bus"""
    event_bus = KafkaEventBus(bootstrap_servers="kafka:9092")
    await event_bus.start()
    return event_bus


# Domain Service Dependencies
async def get_user_domain_service(
    db: Session = Depends(lambda: None)  # Placeholder for database session
) -> UserDomainService:
    """Get UserDomainService with dependencies injected"""
    # Create repositories
    user_repository = SQLAlchemyUserRepository(db) if db else None
    profile_repository = SQLAlchemyUserProfileRepository(db) if db else None
    
    # Create domain service
    return UserDomainService(
        user_repository=user_repository,
        profile_repository=profile_repository
    )


async def get_user_command_handler(
    user_service: UserDomainService = Depends(get_user_domain_service),
    event_publisher: KafkaEventPublisher = Depends(get_kafka_event_publisher)
) -> UserCommandHandler:
    """Get UserCommandHandler with dependencies injected"""
    return UserCommandHandler(
        user_service=user_service,
        event_publisher=event_publisher
    )


async def get_task_domain_service(
    db: Session = Depends(lambda: None)  # Placeholder for database session
) -> TaskDomainService:
    """Get TaskDomainService with dependencies injected"""
    # Create repositories
    task_repository = SQLAlchemyTaskRepository(db) if db else None
    category_repository = SQLAlchemyCategoryRepository(db) if db else None
    
    # Create domain service
    return TaskDomainService(
        task_repository=task_repository,
        category_repository=category_repository
    )


async def get_notification_domain_service(
    db: Session = Depends(lambda: None)  # Placeholder for database session
) -> NotificationService:
    """Get NotificationService with dependencies injected"""
    # Create repositories
    notification_repository = SQLAlchemyNotificationRepository(db) if db else None
    template_repository = SQLAlchemyNotificationTemplateRepository(db) if db else None
    
    # Create domain service
    return NotificationService(
        notification_repository=notification_repository,
        template_repository=template_repository
    )


async def get_service_orchestrator(
    user_service: UserDomainService = Depends(get_user_domain_service),
    task_service: TaskDomainService = Depends(get_task_domain_service),
    notification_service: NotificationService = Depends(get_notification_domain_service),
    event_publisher: KafkaEventPublisher = Depends(get_kafka_event_publisher)
) -> ServiceOrchestrator:
    """Get ServiceOrchestrator with all dependencies injected"""
    return ServiceOrchestrator(
        user_service=user_service,
        task_service=task_service,
        notification_service=notification_service,
        event_publisher=event_publisher
    )
