from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime
from typing import Optional
import re

class UserBase(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100, description="Username must be 3-100 characters")
    email: EmailStr = Field(..., description="User email address")

    @field_validator('username')
    def validate_username(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

class UserCreate(UserBase):
    password: Optional[str] = Field(None, min_length=8, description="Password must be at least 8 characters")
    
    @field_validator('password')
    def validate_password(cls, v):
        if v:
            if not re.search(r'[A-Z]', v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not re.search(r'[a-z]', v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not re.search(r'\d', v):
                raise ValueError('Password must contain at least one number')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    
    @field_validator('username')
    def validate_username(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @field_validator('password')
    def validate_password(cls, v):
        if v:
            if not re.search(r'[A-Z]', v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not re.search(r'[a-z]', v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not re.search(r'\d', v):
                raise ValueError('Password must contain at least one number')
        return v

class User(UserBase):
    id: int
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    is_oauth_user: bool = False
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Password for login")

class UserResponse(BaseModel):
    id: int
    username: Optional[str] = None
    email: str
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    is_oauth_user: bool = False
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int