from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

class NewTask(BaseModel):
    description: str = Field(..., example="Walk the dog")

class UpdateTask(BaseModel):
    description: Optional[str] = Field(None, example="Walk the dog and feed the cat")
    completed: Optional[bool] = Field(None, example=True)

    class Config:
        extra = "forbid" # Ensure no extra fields are passed

class TaskBase(BaseModel):
    description: str
    completed: bool = False

class Task(TaskBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Enable ORM mode
