from dataclasses import dataclass
from typing import Optional
import re


@dataclass(frozen=True)
class Email:
    """Email value object with validation"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError("Invalid email format")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Username:
    """Username value object with validation"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid_username(self.value):
            raise ValueError("Invalid username format")
    
    @staticmethod
    def _is_valid_username(username: str) -> bool:
        """Validate username format"""
        # Username must be 3-20 characters, alphanumeric and underscores only
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return bool(re.match(pattern, username))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Password:
    """Password value object with validation"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid_password(self.value):
            raise ValueError("Password must be at least 8 characters long")
    
    @staticmethod
    def _is_valid_password(password: str) -> bool:
        """Validate password strength"""
        return len(password) >= 8
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class UserId:
    """User ID value object"""
    value: str
    
    def __str__(self) -> str:
        return self.value
