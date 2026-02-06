from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum
from bson import ObjectId

class StatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: Optional[str] = None
    priority: Literal[1, 2, 3] = 2
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
    priority: Optional[Literal[1, 2, 3]] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: StatusEnum
    priority: int
    due_date: Optional[datetime]

    class Config:
        from_attributes = True  # For Pydantic v2+

    @validator('id', pre=True, always=True)
    def set_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
