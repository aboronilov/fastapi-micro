from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class CreateUserCommand:
    """Command to create a new user"""
    email: str
    username: str
    password: str


@dataclass
class UpdateUserCommand:
    """Command to update user profile"""
    user_id: UUID
    email: Optional[str] = None
    username: Optional[str] = None


@dataclass
class ChangePasswordCommand:
    """Command to change user password"""
    user_id: UUID
    current_password: str
    new_password: str


@dataclass
class AuthenticateUserCommand:
    """Command to authenticate user"""
    email: str
    password: str


@dataclass
class DeactivateUserCommand:
    """Command to deactivate user"""
    user_id: UUID


@dataclass
class ActivateUserCommand:
    """Command to activate user"""
    user_id: UUID


@dataclass
class VerifyUserCommand:
    """Command to verify user"""
    user_id: UUID


@dataclass
class CreateUserProfileCommand:
    """Command to create user profile"""
    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass
class UpdateUserProfileCommand:
    """Command to update user profile"""
    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
