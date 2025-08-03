from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.models.general_submission import SubmissionType, ImportanceLevel
from app.schemas.user import UserBase

class SubmissionBase(BaseModel):
    title: str
    type: SubmissionType
    description: str
    importance_level: ImportanceLevel

class SubmissionCreate(SubmissionBase):
    assignee_id: Optional[int] = None  # For task creation when importance is HIGH/MEDIUM

class SubmissionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    importance_level: Optional[ImportanceLevel] = None

class SubmissionInDBBase(SubmissionBase):
    id: int
    creator_id: int
    task_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    creator: Optional[UserBase] = None

    class Config:
        orm_mode = True

class Submission(SubmissionInDBBase):
    pass

class SubmissionList(BaseModel):
    total: int
    submissions: List[Submission]
