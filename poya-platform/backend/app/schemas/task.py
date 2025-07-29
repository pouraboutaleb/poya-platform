from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    NEEDS_REVISION = "needs_revision"
    COMPLETED = "completed"
    CANCELED = "canceled"

class TaskPriority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    assignee_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class UserBase(BaseModel):
    id: int
    full_name: str
    email: str

    class Config:
        orm_mode = True

class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator: UserBase
    assignee: Optional[UserBase] = None

    class Config:
        orm_mode = True
