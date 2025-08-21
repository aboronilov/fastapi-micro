from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .config import Base

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    pomodoro_count = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="tasks")
    user = relationship("User", back_populates="tasks")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    tasks = relationship("Task", back_populates="category")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=True, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=True)  # Nullable for OAuth2 users
    google_id = Column(String(100), nullable=True, unique=True)  # Google OAuth2 ID
    avatar_url = Column(String(500), nullable=True)  # Profile picture URL
    is_oauth_user = Column(Boolean, default=False)  # Flag to identify OAuth2 users
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    tasks = relationship("Task", back_populates="user")
