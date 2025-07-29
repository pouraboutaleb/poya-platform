from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from .task import TaskCreate

class MeetingMinutesBase(BaseModel):
    text_body: str
    attachments: Optional[List[str]] = []

class MeetingMinutesCreate(MeetingMinutesBase):
    tasks: Optional[List[TaskCreate]] = []

class MeetingMinutesUpdate(MeetingMinutesBase):
    pass

class MeetingMinutes(MeetingMinutesBase):
    id: int
    meeting_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
