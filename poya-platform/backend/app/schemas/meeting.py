from typing import Optional, List
from pydantic import BaseModel, validator
from datetime import datetime
from app.schemas.user import UserBase

# Agenda Item Schemas
class AgendaItemBase(BaseModel):
    topic: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = 15
    order: Optional[int] = None
    presenter_id: Optional[int] = None

class AgendaItemCreate(AgendaItemBase):
    pass

class AgendaItem(AgendaItemBase):
    id: int
    meeting_id: int
    presenter: Optional[UserBase] = None

    class Config:
        orm_mode = True

# Meeting Minutes Schemas
class MeetingMinutesBase(BaseModel):
    text_body: str

class MeetingMinutesCreate(MeetingMinutesBase):
    pass

class MeetingMinutes(MeetingMinutesBase):
    id: int
    meeting_id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    created_by: UserBase

    class Config:
        orm_mode = True

# Meeting Schemas
class MeetingBase(BaseModel):
    title: str
    purpose: str
    start_time: datetime
    end_time: datetime
    location: str

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class MeetingCreate(MeetingBase):
    attendee_ids: List[int]
    agenda_items: List[AgendaItemCreate]

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    purpose: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    attendee_ids: Optional[List[int]] = None
    agenda_items: Optional[List[AgendaItemCreate]] = None

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class Meeting(MeetingBase):
    id: int
    organizer_id: int
    is_cancelled: bool
    created_at: datetime
    updated_at: datetime
    organizer: UserBase
    attendees: List[UserBase]
    agenda_items: List[AgendaItem]
    minutes: Optional[MeetingMinutes] = None

    class Config:
        orm_mode = True

class MeetingList(BaseModel):
    total: int
    meetings: List[Meeting]
