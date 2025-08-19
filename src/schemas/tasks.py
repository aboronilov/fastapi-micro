from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    name: Optional[str] = Field(default=None, description="Task name")
    description: Optional[str] = None
    pomodoro_count: int = Field(default=0, ge=0, description="Number of pomodoros")
    category_id: Optional[int] = Field(default=None, description="Category ID")
    completed: bool = Field(default=False)

    @model_validator(mode="after")
    def validate_name_or_count_are_not_empty(self):
        if not self.name and not self.pomodoro_count:
            raise ValueError("Name or count cannot be empty")
        return self

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    pomodoro_count: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None
    completed: Optional[bool] = None

class Task(TaskBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


