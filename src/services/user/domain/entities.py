from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import bcrypt


@dataclass
class User:
    """User domain entity"""
    id: UUID = field(default_factory=uuid4)
    email: str = ""
    username: str = ""
    hashed_password: str = ""
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(cls, email: str, username: str, password: str) -> "User":
        """Create a new user with hashed password"""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return cls(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
    
    def verify_password(self, password: str) -> bool:
        """Verify user password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))
    
    def update_password(self, new_password: str):
        """Update user password"""
        self.hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.updated_at = datetime.utcnow()
    
    def update_profile(self, email: Optional[str] = None, username: Optional[str] = None):
        """Update user profile"""
        if email is not None:
            self.email = email
        if username is not None:
            self.username = username
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        """Activate user account"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate user account"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def verify(self):
        """Mark user as verified"""
        self.is_verified = True
        self.updated_at = datetime.utcnow()


@dataclass
class UserProfile:
    """User profile domain entity"""
    user_id: UUID
    first_name: str = ""
    last_name: str = ""
    bio: str = ""
    avatar_url: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def update_profile(self, first_name: Optional[str] = None, last_name: Optional[str] = None, 
                      bio: Optional[str] = None, avatar_url: Optional[str] = None):
        """Update profile information"""
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if bio is not None:
            self.bio = bio
        if avatar_url is not None:
            self.avatar_url = avatar_url
        self.updated_at = datetime.utcnow()
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""
