from typing import Optional
from uuid import uuid4
from src.shared.events import UserCreatedEvent, UserUpdatedEvent, UserAuthenticatedEvent
from src.shared.kafka_client import KafkaEventPublisher
from ..domain.services import UserDomainService
from .commands import (
    CreateUserCommand, UpdateUserCommand, ChangePasswordCommand, AuthenticateUserCommand,
    DeactivateUserCommand, ActivateUserCommand, VerifyUserCommand,
    CreateUserProfileCommand, UpdateUserProfileCommand
)


class UserCommandHandler:
    """Handler for user commands with event publishing"""
    
    def __init__(self, user_service: UserDomainService, event_publisher: KafkaEventPublisher):
        self.user_service = user_service
        self.event_publisher = event_publisher
    
    async def handle_create_user(self, command: CreateUserCommand):
        """Handle create user command"""
        user = await self.user_service.create_user(
            email=command.email,
            username=command.username,
            password=command.password
        )
        
        # Publish user created event
        event = UserCreatedEvent(
            aggregate_id=str(user.id),
            aggregate_type="User",
            data={
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "is_verified": user.is_verified
            }
        )
        await self.event_publisher.publish(event)
        
        return user
    
    async def handle_update_user(self, command: UpdateUserCommand):
        """Handle update user command"""
        user = await self.user_service.update_user_profile(
            user_id=command.user_id,
            email=command.email,
            username=command.username
        )
        
        if user:
            # Publish user updated event
            event = UserUpdatedEvent(
                aggregate_id=str(user.id),
                aggregate_type="User",
                data={
                    "email": user.email,
                    "username": user.username,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified
                }
            )
            await self.event_publisher.publish(event)
        
        return user
    
    async def handle_authenticate_user(self, command: AuthenticateUserCommand):
        """Handle authenticate user command"""
        user = await self.user_service.authenticate_user(
            email=command.email,
            password=command.password
        )
        
        if user:
            # Publish user authenticated event
            event = UserAuthenticatedEvent(
                aggregate_id=str(user.id),
                aggregate_type="User",
                data={
                    "email": user.email,
                    "username": user.username,
                    "authenticated_at": user.updated_at.isoformat()
                }
            )
            await self.event_publisher.publish(event)
        
        return user
    
    async def handle_change_password(self, command: ChangePasswordCommand):
        """Handle change password command"""
        success = await self.user_service.change_password(
            user_id=command.user_id,
            current_password=command.current_password,
            new_password=command.new_password
        )
        return success
    
    async def handle_deactivate_user(self, command: DeactivateUserCommand):
        """Handle deactivate user command"""
        success = await self.user_service.deactivate_user(command.user_id)
        return success
    
    async def handle_activate_user(self, command: ActivateUserCommand):
        """Handle activate user command"""
        success = await self.user_service.activate_user(command.user_id)
        return success
    
    async def handle_verify_user(self, command: VerifyUserCommand):
        """Handle verify user command"""
        success = await self.user_service.verify_user(command.user_id)
        return success
    
    async def handle_create_user_profile(self, command: CreateUserProfileCommand):
        """Handle create user profile command"""
        profile = await self.user_service.create_user_profile(
            user_id=command.user_id,
            first_name=command.first_name,
            last_name=command.last_name,
            bio=command.bio,
            avatar_url=command.avatar_url
        )
        return profile
    
    async def handle_update_user_profile(self, command: UpdateUserProfileCommand):
        """Handle update user profile command"""
        profile = await self.user_service.update_user_profile_details(
            user_id=command.user_id,
            first_name=command.first_name,
            last_name=command.last_name,
            bio=command.bio,
            avatar_url=command.avatar_url
        )
        return profile
